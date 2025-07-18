# **Build Your Own WheelSense Camera**

We aim to integrate an image classification model into a camera module to detect the presence of wheelchair at public transport stations. It records the image in real time and classify either 'Wheelchair detected!" or "No wheelchair". The camera module also sends out a bluetooth signal based on the generated classification. The system functions offline, requires no manual input, and is intended to help public transport operator & wheelchair users in the process of accessibility support.



## **1\. What You’ll Need**

* **Hardware**: Arduino Nicla Vision

<img width="760" height="847" alt="image" src="https://github.com/user-attachments/assets/d5a9a5df-1818-4e83-8596-e2dfb8b64a78" />


This is our main hardware. It will capture image, classify whether a wheelchair is detected or not, and send a corresponding bluetooth signal.

* **Appilication**: nRF Connect (AppStore/CH Play)

<img width="519" height="915" alt="image" src="https://github.com/user-attachments/assets/aeab2bbb-b740-4f6a-aff7-07f4ef543b1a" />


This application is for the purpose of testing the bluetooth signal sent from the camera module.

* **Software**: OpenMV

<img width="1020" height="876" alt="image" src="https://github.com/user-attachments/assets/ff73197d-1333-4b53-b6a7-f6aee86d83d0" />


This software would be the platform to deploy a trained image classification model to the camera module. It is also a friendly environment to test the functionality of the camera as well as the deployed firmware for classification.

Download link: [Download – OpenMV](https://openmv.io/pages/download)

* **Others:**
* Micro-USB cable
* Laptop with Windows. For macOS some specific steps may need to be revised to compatible with the OS.
* Python
* VS Code
* Edge Impulse CLI

## **2\. Data Collection**

### **2.1. Set up repository & environment**

Clone the repository to your computer: [hohuyhoanghwr/wheelsense](https://github.com/hohuyhoanghwr/wheelsense)

Open the repository on VS Code

<img width="1470" height="649" alt="image" src="https://github.com/user-attachments/assets/97990464-3f49-468f-8b0c-cfed6be50676" />


Open a new terminal. Run the following command to create a virtual environment:

```
uv venv
```



Activate the environment:

```
.venv\Scripts\activate
```



Install the required packages:

```
uv pip compile requirements.in > requirements.txt
```

then

```
uv pip sync requirements.txt
```

### **2.2. Crawl data**

In this project, we collect image data from <https://commons.wikimedia.org/w/index.php>

Make sure you are in the project root folder (wheelsense). Open the file 'crawler_wiki.py'

Navigate to the following part:

<img width="557" height="202" alt="image" src="https://github.com/user-attachments/assets/ab38a4b5-8ea2-404c-8ab7-a946a658b4be" />


In this project, we search with the following keywords: "Berlin platform", "German train stations", "Wheelchairs in station".

Choose only one keyword at a time. Make sure the 'SAVE_DIR' is updated to a proper folder name that you want to store collected images.

In the terminal, run the following command:

```
python crawler_wiki.py
```

<img width="1919" height="1064" alt="image" src="https://github.com/user-attachments/assets/c484de7a-5a70-4f8f-81dd-56e0c0d9b35c" />


After a run, you may update 'SEARCH_QUERY' and 'SAVE_DIR' to collect another dataset with a different keyword. Or you may create multiple copies of the 'crawler_wiki.py', open more terminals and run multiple queries in parallel.

When all queries are completed, it is highly recommended to walk into each folder and manually remove irrelevant images that were crawled. This would help improve the data quality, which later would significantly impact the performance of our classification model.

## **3\. Create an image classification model for detecting wheelchair**

### **3.1 Login**

Login to Edge Impulse and create a new project

### **3.2 Data acquisition**

Navigate to section 'Data acquisition' on Edge Impulse

Select the option 'Upload Data'

<img width="775" height="129" alt="image" src="https://github.com/user-attachments/assets/d89a7a83-f62d-4848-a0b0-08bf17632628" />


Select the folder on your computer that is already saved with collected images.

Select the option 'Automatically split between training and testing'

Enter an label that is appropriate with the data you're uploading

<img width="1182" height="892" alt="image" src="https://github.com/user-attachments/assets/fe9e53d0-06e6-4203-be68-2cf486c65e3d" />


Click on 'Upload data'.

Repeat this steps to upload all collected data for label 'No wheelchair' and 'Wheelchair detected!'

### **3.3 Impulse design**

* **Create impulse**

Navigate to section 'Impulse design'. Click on add an input block. Select option 'Images'. Add.

<img width="792" height="187" alt="image" src="https://github.com/user-attachments/assets/3975c57f-c8de-4552-bfc2-62110c504c4a" />


Configure the input block

<img width="369" height="440" alt="image" src="https://github.com/user-attachments/assets/4243f83f-99b1-4a83-8fcf-0f3a3b56c12b" />


Add a processing block. Select 'Image'. Add.

<img width="791" height="277" alt="image" src="https://github.com/user-attachments/assets/ba108415-8161-4632-aea0-a54a7b15f5fd" />


Add a learning block. Select 'Transfer Learning (Images)'. Add.

<img width="797" height="626" alt="image" src="https://github.com/user-attachments/assets/1fbfddc6-4b73-4a38-80f6-cfc23eebf2f6" />


Click on 'Save Impulse'.

<img width="424" height="342" alt="image" src="https://github.com/user-attachments/assets/7e820106-ad89-4db4-93a7-3ba306e0f173" />


* **Transfer learning**

Go to block Transfer learning. Configure the neural network settings

<img width="773" height="664" alt="image" src="https://github.com/user-attachments/assets/bff06e32-7299-4901-8006-ffd368c50e5f" />


Select a model: MobileNetV1 96x96 0.1 (53.2K RAM and 101K ROM) is recommended to fit with ram usage and flash usage of our device

<img width="799" height="670" alt="image" src="https://github.com/user-attachments/assets/5c492e18-6394-4e42-8b6e-cb357dbb7383" />


Click on 'Save & train'.

After training is completed, you may refer to the performance report of the model on train dataset (still within tab 'Transfer learning') and test dataset (navigate to tab 'Model testing').

<img width="778" height="691" alt="image" src="https://github.com/user-attachments/assets/d4db4302-3151-41c0-b75d-dad081ba5e12" />


<img width="825" height="683" alt="image" src="https://github.com/user-attachments/assets/16a9ae50-1f23-4c59-9478-38600d32c270" />


If satisfied with the model's performance. We now move to deployment steps.

### **3.4 Deployment**

Navigate to section 'Deployment'.

In the top right corner, select an appropriate target device: Arduino Nicla Vision

<img width="444" height="53" alt="image" src="https://github.com/user-attachments/assets/a1538035-061b-425a-8eaa-3a29e4ae9ba7" />


<img width="797" height="886" alt="image" src="https://github.com/user-attachments/assets/a74fea29-f52a-4da6-88f0-a7028925baa0" />


Click on 'Save'.

Click on 'Search deployment options'. Search and select 'OpenMV library'

<img width="923" height="421" alt="image" src="https://github.com/user-attachments/assets/35273fb7-c7bf-407a-8bac-021a86b8be6c" />


Click on 'Build' and wait for the process to complete.

When the building process is completed, click on the Build ( e.g.: 'v8(OpenMV library) ) and download the zip file. Save it to a location on your computer that you can easily find out later.

<img width="550" height="362" alt="image" src="https://github.com/user-attachments/assets/b4ec1671-70be-40a0-af67-8b74afbf3d00" />


After saving, unzip the downloaded zip files

<img width="646" height="137" alt="image" src="https://github.com/user-attachments/assets/9a35b70d-0144-4339-8a05-8584746cb55d" />


<img width="601" height="191" alt="image" src="https://github.com/user-attachments/assets/e5780783-27f1-4d01-87a2-5af62bebe7d5" />


## **4\. Deploy firmware**

### **4.1 Flashing device**

Make sure the Arduino Nicla Vision device is connected to your computer (e.g. via USB cable).

Make sure Open MV is installed in your computer. Start the software. Click on the 'Connect' button that the bottom left corner.

<img width="1609" height="1079" alt="image" src="https://github.com/user-attachments/assets/ae7b11db-1c28-48fa-81b4-f4be3e60fd3f" />


OpenMV will ask for installing the latest firmware. Select 'Install the latest release firmware'. Select also the option 'Erase internal file system'. Click 'OK'

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/6f87216d-aa61-447a-8ba6-2ddb560a5f76" />


Nicla Vision's green LED will start flashing while the OpenMV firmware is being uploaded to the board. A loading bar will start showing you the flashing progress.

Wait until the green LED stops flashing and fading. You will see a message saying "DFU firmware update complete!" when the process is done.

After confirming the completion dialog, the Nicla Vision should already be connected to the OpenMV IDE and a green play button appears. Otherwise click the "connect" button (plug symbol) once again (the blue blinking should stop).

<img width="972" height="165" alt="image" src="https://github.com/user-attachments/assets/6072a12e-073e-4bb5-82c3-bb89d8d1339d" />


**4.2. Import the built firmware**

Open the Drive of the device

<img width="749" height="139" alt="image" src="https://github.com/user-attachments/assets/fc3f6fe2-505e-416c-9378-5f8417773642" />


In the previously unzipped firmware folders, copy the files 'lables.txt' and 'trained.tflite' and paste to the device's drive

<img width="1548" height="749" alt="image" src="https://github.com/user-attachments/assets/2ef733cb-fdf1-4fea-a955-7984c5587287" />


Close the Drive window. Now on OpenMV, select 'Open File' or Ctrl + O. Navigate to the initial cloned repository, in the sub-folder 'deployed_firmware' select the file 'ei_image_classification.py' (not from the unzipped folder downloaded from Edge Impulse).

<img width="950" height="856" alt="image" src="https://github.com/user-attachments/assets/418bef3b-2e77-4808-9c32-f849f048367b" />


Save the file. Click on 'Serial Terminal' at the bottom to open a terminal view. Then click on 'Start' button.

<img width="408" height="114" alt="image" src="https://github.com/user-attachments/assets/7ce17155-7596-47ce-b1bd-f6b4c4aeaaac" />


Now you should see the camera is running and classifying what it sees - with a printed string on the live view

<img width="1917" height="1035" alt="image" src="https://github.com/user-attachments/assets/2b147e23-79f0-44ec-af8e-a5d4d4f97ca1" />


## **5\. Configure bluetooth function.**

In the file 'ei_image_classification.py' you may find the configured bluetooth ID for the device

<img width="813" height="86" alt="image" src="https://github.com/user-attachments/assets/0df380f0-09e5-4ee0-a4a7-ec990f8ec955" />


If you want to use another IDs, you may go to [Free Online GUID Generator](https://guidgenerator.com/) to generate new SERVICE_UUID and CHARACTERISTIC_UUID

<img width="819" height="548" alt="image" src="https://github.com/user-attachments/assets/9762c79b-b54c-476d-a87d-5d5f32dac3ae" />


Copy the 2 new IDs and paste to the python scripts. Save it.

Now open the 'nRF Connect' app on your phone. Place your phone near the camera module. Make sure the camera is still running its python scripts.

Use 'Scan' function on 'nRF Connect' to find the camera module. It should has the configured name defined in python scripts.

<img width="408" height="95" alt="image" src="https://github.com/user-attachments/assets/d667a092-209c-43b3-8412-7a35d0edf8fb" />


Connect with the device.

<img width="425" height="938" alt="image" src="https://github.com/user-attachments/assets/6191c890-033e-4f27-b373-7e7b61422deb" />


Once connected, click on the device. Scroll down to find a service with the Characteristic with UUID as the same as defined in the python scripts

<img width="1179" height="2556" alt="image" src="https://github.com/user-attachments/assets/d93c371b-af0b-4f2f-9ffe-6c385d937119" />


Click on the 'arrow down' button to receive message from the camera module.

You can also click the " button to change the format of value to Boolean ('True', 'False')

<img width="1179" height="2556" alt="image" src="https://github.com/user-attachments/assets/6506a97f-4c9d-4b9a-b878-01e48c20ab44" />


Now on the nRF Connect app, you should receive a Bluetooth signal with value corresponding to the label that the camera is classifying: 'No wheelchair' = 'False' and 'Wheelchair Detected' = 'True'.

<img width="1919" height="1031" alt="image" src="https://github.com/user-attachments/assets/d03fdf78-1451-4bc9-9389-392fba751a39" />




<img width="1919" height="1021" alt="image" src="https://github.com/user-attachments/assets/929a46de-765f-4169-a532-535d3356bb2d" />


## **6\. References**

* Project link: [WheelSense IoT - Dashboard - Edge Impulse](https://studio.edgeimpulse.com/studio/719131)
* Project repo: [hohuyhoanghwr/wheelsense](https://github.com/hohuyhoanghwr/wheelsense/tree/main)
* Nicla Vision with OpenMV documentation: [Video Live Streaming with OpenMV and Nicla Vision \| Arduino Documentation](https://docs.arduino.cc/tutorials/nicla-vision/live-streaming/)
