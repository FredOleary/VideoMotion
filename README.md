# Measuring pulse rate by analysing micro changes in head motion
This project estimates pulse rate from a video stream by measuring face micro motion. It uses the open source vision library, opencv to process video streams

## Pre-requisites (Mac Laptop)
1. Python 3 installed (3.7 version minimum)
2. Webcam

## Pre-requisites RaspberryPi
1. Raspberry Pi 3b+
2. Raspberry Pi camera. (picamera) (USB cameras are not supported )
3. Python 3 installed (3.5 version minimum)


## Software installation steps
1. Clone this repositary to a local directory
2. `cd VideoMotion`
3. `python3 -m venv venv`  (Create a virtual environment)
4. `source venv/bin/activate` (Activate virtual environment)
5. Install the following python packages
    1. `pip install opencv-contrib-python`
    2. `pip install matplotlib`
    3. `pip install scipy`
6. Locate the opencv face classifier *haarcascade_frontalface_default.xml* and copy it to the data folder. (Different distros of opencv install this in different places)  
    1. `mkdir data`
    2. `cp /....../cv2/data/haarcascade_frontalface_default.xml data/`  
    
### For the raspberry pi do the additional:
1.`sudo apt-get install at-spi2-core` (remove errors about “org.freedesktop.DBus.Error)

2.`pip install picamera`
    
    
## Usage
1. To verify the installation and camera: `python play_video.py` Verify that video streams and that the camera is correctly positioned for face detection.

2. To measure pulse rate run `python main.py`. When a face is detected, a 'green' rectangle will enclose the face and after about 10 seconds the pulse rate will be displayed over the video if it can be estimated.

## Options
The configuration file config.txt contains the following options. (Note this is organized as a python dictionary)

1. **low_pulse_bpm** - Low end of pulse rate, (beats-per-minute)
2. **high_pulse_bpm** - Low end of pulse rate, (beats-per-minute)
3. **video_fps** - Preferred video frame rate. (Not all cameras will honor this)
4. **resolution** - Video resolution
5. **pulse_sample_seconds** - Length of interval used to measure pulse rate. E.g. if 10 then pulse rate will be updated every 10 seconds
6. **show_pulse_charts** - When `True` charts of the head motion will show: 
    1. The raw changes in head motion over time
    2. The filtered changes in head motion over time using **low_pulse_bpm/high_pulse_bpm**
    3. The FFT of the filtered changes
7. **use_tracking_after_detect** When `True`, the algorithm uses face detection followed by face tracking to measure motion. When `False` Face detection per frame is used. (Face detection per frame is less efficient)
