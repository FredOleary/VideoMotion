# Measuring pulse rate by analysing micro changes in head motion
This project estimates pulse rate from a video stream by measuring face micro motion

##Pre-requisites (Mac Laptop)
1. Python 3 installed (3.7 version minimum)
2. Webcam

##Pre-requisites RaspberryPi
1. Raspberry Pi 3b+
2. Raspberry Pi camera. (picamera) (USB cameras are not supported )
3. Python 3 installed (3.5 version minimum)


##Software installation steps
1. Clone this repositary to a local directory
2. `cd VideoMotion`
3. `python3 -m venv venv`  (Create a virtual environment)
4. `source venv/bin/activate` (Activate virtual environment)
5. Install the following python packages
    1. `pip install opencv-contrib-python`
    2. `pip install matplotlib`
    3. `pip install scipy`
    
### For the raspberry pi do the additional:
1.`sudo apt-get install at-spi2-core` (remove errors about “org.freedesktop.DBus.Error)

2.`pip install picamera`
    
    
##Usage
To verify the installation and camera: `python play_video.py` 
python3 -m venv venv (Make su
re python3 is used, not python2)
source venv/bin/activate

3) Install python packages into the virtual environment
pip install opencv-contrib-python #(Note that this instead of opencv-python)
pip install matplotlib
pip install scipy


On the raspberryPi 

install at-spi2-core to remove errors about “org.freedesktop.DBus.Error…. using apt-get
sudo apt-get install at-spi2-core
pip install picamera


to verify installation
python play_video.py

config. OpenCV  face classifier

To do this, create a new folder 'data', locate the opencv classifier 'haarcascade_frontalface_default.xml', and
copy it to the data folder. Eg

cp ...python3.7/site-packages/cv2/data/haarcascade_frontalface_default.xml data/

