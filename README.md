# VideoMotion

todo
1) Get source from git. clone/fork
2) create venv
python3 -m venv venv (Make sure python3 is used, not python2)
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

