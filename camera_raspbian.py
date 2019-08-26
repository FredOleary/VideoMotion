import time

try:
    from picamera.array import PiRGBArray
    from picamera import PiCamera
    from picamera import PiCameraMMALError
except ImportError:
    print("Not raspberry Pi")


class CameraRaspbian:

    def __init__(self):
        print("CameraRaspberian camera created")
        self.is_open = False

    def open_video(self, video_file_or_camera):
        try:
            self.camera = PiCamera()
            # allow the camera to warmup
            time.sleep(0.1)
            self.is_open = True
            return True
        except PiCameraMMALError:
            print("CameraRaspberian - open camera failed")
            self.is_open = False
            return False

    def set_frame_rate(self, fps):
        self.camera.framerate = fps

    def set_resolution(self, width, height):
        self.camera.resolution = (width, height)
        self.rawCapture = PiRGBArray(self.camera, size=(width, height))

    def get_frame_rate(self):
        return self.camera.framerate

    def get_resolution(self):
        width, height = self.camera.resolution
        return width, height

    def read_frame(self):
        self.rawCapture.truncate(0)
        self.camera.capture(self.rawCapture, format="bgr", use_video_port=True)
        return True, self.rawCapture.array

    def close_video(self):
        self.is_open = False
        return True

    def is_opened(self):
        return self.is_open
