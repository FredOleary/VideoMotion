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


from frame_grabber import FrameGrabber

class RaspberianGrapper( FrameGrabber ):
    def __init__(self, cv2, fps, width, height):
        super().__init__(cv2, fps, width, height)
        self.camera = None
        self.rawCapture = None
        self.is_open = False

    def open_video(self, video_file_or_camera):
        self.is_live_stream = True
        try:
            self.camera = PiCamera()
            self.camera.resolution = (self.width, self.height)
            self.camera.framerate = self.fps
            self.rawCapture = PiRGBArray(self.camera, size=(self.width, self.height))
            thread = Thread(target=self.__update, args=())
            thread.setDaemon(True)
            thread.start()
            # allow the camera to warm up
            time.sleep(0.3)

            self.stopped = False
            # allow the camera to warm up
            time.sleep(0.3)
            self.is_open = True
            return True
        except PiCameraMMALError:
            print("CameraRaspbian - open camera failed")
            self.is_open = False
            return False

    def close_video(self):
        self.is_open = False
        super().close_video()

    def is_opened(self):
        return self.is_open or self.frame_queue.qsize() > 0

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

    def get_next_frame(self):
        print("CameraRaspbian:get_next_frame")
        frame = self.camera.capture(self.rawCapture, format="bgr", use_video_port=True)
        return True, frame.array

    def __update(self):
        super().__update()