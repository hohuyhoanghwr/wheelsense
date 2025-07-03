# Edge Impulse - OpenMV Image Classification Example
#
# This work is licensed under the MIT license.
# Copyright (c) 2013-2024 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE

#Package imports for OpenMV. Ignore warnings about missing modules when viewing in VS Code
import sensor, time, ml, uos, gc
import uasyncio as asyncio # For asynchronous operations
import aioble              # High-level BLE library
import bluetooth

# --- BLE Setup ---
# Custom Service and Characteristic UUIDs
SERVICE_UUID = bluetooth.UUID('be94c06d-e5fb-4b31-a2c1-ed4d2f68ef0a') #self config
CHARACTERISTIC_UUID = bluetooth.UUID('6d8e2ae0-28cb-4ba8-ac81-dcbc312e0bb4') #self config

# Define the BLE Service and Characteristic using aioble
wheelchair_service = aioble.Service(SERVICE_UUID)
wheelchair_characteristic = aioble.Characteristic(
    wheelchair_service, CHARACTERISTIC_UUID, read=True, notify=True
)
aioble.register_services(wheelchair_service)

# How frequently to send advertising beacons (e.g., 250ms)
_ADV_INTERVAL_US = 250_000 # Microseconds

# Global variable to store connection
active_connection = None
# --- End BLE Setup ---

# Global variable to hold the camera image for drawing
current_img = None

# Asynchronous Task for Image Classification
async def image_classification_task(net, labels):
    global current_img
    clock = time.clock()

    while True:
        clock.tick()
        img = sensor.snapshot()
        current_img = img # Update global image for drawing

        # Run inference
        predictions = net.predict([img])[0].flatten().tolist()
        predictions_list = list(zip(labels, predictions))

        # Get the most confident prediction
        top_label, top_conf = max(predictions_list, key=lambda x: x[1])

        # Print to serial (for debugging)
        print("%s = %.2f" % (top_label, top_conf))

        # --- Send Bluetooth signal ---
        # This part attempts to send notification. It will only actually send
        # if a client is connected AND has enabled notifications for this characteristic.

        try:
            value_to_send = b'\x00' # Default to no detection
            if top_label == 'Wheelchair Detected!':
                value_to_send = b'\x01'
                # Send a byte '1' for detected

            if active_connection:
                wheelchair_characteristic.write(value_to_send)
                print(f"DEBUG: Attempting to notify {active_connection.device} with value {value_to_send.hex()}")
                wheelchair_characteristic.notify(active_connection) # Send notification
                print("BLE: Wheelchair Detected! signal sent.")
            else:
                print("DEBUG: No active BLE connection to notify.")

        except Exception as e:
            print("BLE Write/Notify Error:", e)
        # --- End Bluetooth signal ---

        # Drawing lable on live image
        if top_label == 'Wheelchair Detected!':
            label_part1 = "Wheelchair"
            label_part2 = "Detected!"
            line_height = 20
            img.draw_string(10, 10, label_part1, color=(255, 0, 0), scale=2)
            img.draw_string(10, 10 + line_height, label_part2, color=(255, 0, 0), scale=2)
            # img.draw_string(10, 10, "%s (%.2f)" % (top_label, top_conf), color=(255, 0, 0), scale=2)
        else:
            img.draw_string(10, 10, "%s (%.2f)" % (top_label, top_conf), color=(0, 128, 0), scale=2)

        print(clock.fps(), "fps")
        await asyncio.sleep_ms(100) # Yield control to other tasks

# Asynchronous Task for BLE Peripheral (Advertising & Connection Management)
async def ble_peripheral_task():
    global active_connection
    while True:
        try:
            # This handles advertising and automatically stops advertising when connected,
            # and resumes when disconnected.
            async with await aioble.advertise(
                _ADV_INTERVAL_US,
                name="NiclaVision_Wheelchair", # Device name for scanning apps
                services=[SERVICE_UUID],       # List of 128-bit service UUIDs to advertise (aioble handles formatting)
                appearance=0, # Generic appearance
            ) as connection:
                print("Connection from", connection.device)
                active_connection = connection # Store the active connection
                await connection.disconnected() # Wait here until the client disconnects
                print("Disconnected from", connection.device)
        except bluetooth.BLE.Veto as e:
            # This can happen if advertising is stopped externally, or if the BLE chip encounters an issue.
            print("Advertising vetoed (likely due to internal BLE state):", e)
            await asyncio.sleep_ms(100) # Wait a bit before trying to advertise again
        except Exception as e:
            print("BLE Peripheral Error (during advertise/connect):", e)
            await asyncio.sleep_ms(100) # Wait before retrying advertising
        finally:
            active_connection = None # Clear connection when disconnected or error

# Main entry point for asynchronous tasks
async def main():
    # --- Synchronous Initialization (Camera, Model Loading) ---
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.set_windowing((240, 240))
    sensor.skip_frames(time=2000) # Give camera time to adjust

    net = None
    labels = None

    try:
        # Load the model. Allocate on heap if enough free memory exists after loading,
        # otherwise it will try to load to frame buffer.
        net = ml.Model("trained.tflite", load_to_fb=uos.stat('trained.tflite')[6] > (gc.mem_free() - (64*1024)))
    except Exception as e:
        print(e)
        raise Exception('Failed to load "trained.tflite", did you copy the .tflite and labels.txt file onto the mass-storage device? (' + str(e) + ')')

    try:
        labels = [line.rstrip('\n') for line in open("labels.txt")]
    except Exception as e:
        raise Exception('Failed to load "labels.txt", did you copy the .tflite and labels.txt file onto the mass-storage device? (' + str(e) + ')')

    # --- Start Asynchronous Tasks ---
    # Create the two main tasks to run concurrently
    task_ble = asyncio.create_task(ble_peripheral_task())
    task_image = asyncio.create_task(image_classification_task(net, labels))

    # Run both tasks until completion (which is effectively forever in this loop)
    await asyncio.gather(task_ble, task_image)

# --- Program Entry Point ---
# Run the main asynchronous loop
try:
    asyncio.run(main())
    time.sleep(100)
except KeyboardInterrupt:
    print("Program stopped by KeyboardInterrupt.")
except Exception as e:
    print("Fatal Error in main loop:", e)
finally:
    # Optional: Clean up or ensure sensor is in a known state on exit
    sensor.reset()
    print("Sensor reset after program termination.")
