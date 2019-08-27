import time
from threading import Thread

try:
    # noinspection PyUnresolvedReferences
    from picamera.array import PiRGBArray
    # noinspection PyUnresolvedReferences
    from picamera import PiCamera
    # noinspection PyUnresolvedReferences
    from picamera import PiCameraMMALError
except ImportError:
    print("Not raspberry Pi")


class CameraRaspbian:

    def __init__(self, fps, width, height):
        print("CameraRaspbian camera created")
        self.camera = None
        self.fps = fps
        self.width = width
        self.height = height
        self.is_open = False
        self.stream = None
        self.stopped = False
        self.rawCapture = None
        self.frame = None

    # noinspection PyUnusedLocal
    def open_video(self, video_file_or_camera):
        try:
            self.camera = PiCamera()
            self.camera.resolution = (self.width, self.height)
            self.camera.framerate = self.fps
            self.rawCapture = PiRGBArray(self.camera, size=(self.width, self.height))
            self.stream = self.camera.capture_continuous(self.rawCapture,
                                                         format="bgr", use_video_port=True)
            self.frame = self.rawCapture.array

            Thread(target=self.update, args=()).start()

            self.frame = None
            self.stopped = False
            # allow the camera to warm up
            time.sleep(0.3)
            self.is_open = True
            return True
        except PiCameraMMALError:
            print("CameraRaspbian - open camera failed")
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
        if self.stopped:
            return False, self.frame
        else:
            return True, self.frame

    def close_video(self):
        self.is_open = False
        self.stopped = True
        return True

    def is_opened(self):
        return self.is_open

    def update(self):
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return
