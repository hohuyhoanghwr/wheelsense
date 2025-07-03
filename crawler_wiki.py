import os
import time
import requests
from tqdm import tqdm
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# Configuration
SEARCH_URL = "https://commons.wikimedia.org/w/index.php"
# --- CHANGE THIS LINE FOR THE NEW SEARCH QUERY ---
SEARCH_QUERY = "berlin platform"
# --- CHANGE SAVE_DIR IN ACCORDANCE TO EACH CRAWL ---
SAVE_DIR = r"berlin_platform" 
RESIZE_TO = (96, 96) # Adjust the size as needed
MAX_IMAGES = 2000 # Adjust based on your needs for the new query
SCROLL_PAUSE_TIME = 2.0
SLEEP_BETWEEN_REQUESTS = 1.5

# Ensure save dir exists
os.makedirs(SAVE_DIR, exist_ok=True)

def fetch_image_urls(query, max_images):
    image_urls = set()

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)

    # The search URL construction is dynamic based on SEARCH_URL and SEARCH_QUERY
    search_url = f"{SEARCH_URL}?search={query.replace(' ', '+')}&title=Special%3AMediaSearch&type=image&filemime=jpeg"
    print(f"[*] Navigating to: {search_url}")
    driver.get(search_url)

    try:
        while len(image_urls) < max_images:
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img.sd-image"))
                )
            except TimeoutException:
                print("[!] No images found on the page or initial load took too long. Exiting.")
                break

            imgs = driver.find_elements(By.CSS_SELECTOR, "img.sd-image")
            print(f"[*] Found {len(imgs)} image elements on current page. Total URLs collected so far: {len(image_urls)}")
            
            newly_added_urls_count = 0
            for img in imgs:
                try:
                    src = img.get_attribute("src") or img.get_attribute("data-src")
                    if src and src.startswith("https"):
                        if not any(ext in src.lower() for ext in ['.svg', '.gif']):
                            if src not in image_urls:
                                image_urls.add(src)
                                newly_added_urls_count += 1
                                if len(image_urls) >= max_images:
                                    print(f"[+] Reached MAX_IMAGES ({max_images}). Stopping.")
                                    break
                except StaleElementReferenceException:
                    print("[!] Stale element encountered while processing images. Skipping this element.")
                    continue 
            
            if newly_added_urls_count == 0 and len(imgs) > 0 and len(image_urls) < max_images:
                print("[!] No new unique image URLs found in this pass. Assuming all results are loaded or no more unique images available.")
                break

            if len(image_urls) >= max_images:
                break

            try:
                load_more = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'sdms-load-more')]"))
                )
                driver.execute_script("arguments[0].click();", load_more)
                print(f"[*] Clicked 'Load more'. New total URLs collected: {len(image_urls)}")
                time.sleep(SCROLL_PAUSE_TIME)
            except NoSuchElementException:
                print("[!] 'Load more' button not found. Assuming all results are loaded.")
                break
            except TimeoutException:
                print("[!] 'Load more' button not clickable within timeout. Assuming all results are loaded.")
                break
            except StaleElementReferenceException:
                print("[!] 'Load more' button became stale just before clicking. Retrying if loop continues.")
                continue 

    except Exception as e:
        print(f"[!] An unexpected error occurred during URL fetching: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

    return list(image_urls)

def download_and_resize_image(url, index, save_directory, resize_dims):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image = image.resize(resize_dims, Image.LANCZOS)
        # Naming convention adapted for the new search query
        filename = f"{SEARCH_QUERY}_{index:04d}.jpg" 
        save_path = os.path.join(save_directory, filename)
        image.save(save_path, format="JPEG", quality=90)
    except requests.exceptions.RequestException as e:
        print(f"[!] Network error downloading {url}: {e}")
    except Image.UnidentifiedImageError:
        print(f"[!] Could not identify image from {url}. It might not be a valid image file.")
    except Exception as e:
        print(f"[!] Failed to download or process {url}: {e}")

if __name__ == "__main__":
    print(f"[+] Starting image scraping for query: '{SEARCH_QUERY}'")
    print(f"[+] Images will be saved to: {SAVE_DIR}")
    print(f"[+] Resizing images to: {RESIZE_TO}")
    print(f"[+] Targeting a maximum of {MAX_IMAGES} images.")

    urls = fetch_image_urls(SEARCH_QUERY, MAX_IMAGES)
    print(f"[+] Retrieved {len(urls)} unique image URLs. Starting download...")

    if not urls:
        print("[!] No URLs were retrieved. Exiting.")
    else:
        for i, url in enumerate(tqdm(urls, desc="  Downloading and resizing images")):
            download_and_resize_image(url, i, SAVE_DIR, RESIZE_TO)
            time.sleep(SLEEP_BETWEEN_REQUESTS)

    print(f"[✓] Done. Attempted to save {len(urls)} images to {SAVE_DIR}")
    print(f"[✓] Final count of files in {SAVE_DIR}: {len(os.listdir(SAVE_DIR))}")