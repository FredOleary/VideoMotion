import time
from threading import Thread
import queue

class CameraOpenCv:

    def __init__(self, cv2, fps, width, height):
        self.cv2 = cv2
        self.fps = fps
        self.width = width
        self.height = height
        self.capture = None
        self.stopped = True
        self.paused = False
        self.result = False
        self.frame_queue = queue.Queue()

    def open_video(self, video_file_or_camera):
        self.capture = self.cv2.VideoCapture(video_file_or_camera)
        self.capture.set(self.cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(self.cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.capture.set(self.cv2.CAP_PROP_FPS, self.fps)
        is_opened = self.capture.isOpened()
        if is_opened:
            self.stopped = False
            Thread(target=self.update, args=()).start()
        return self.capture.isOpened()

    def set_frame_rate(self, fps):
        self.capture.set(self.cv2.CAP_PROP_FPS, fps)

    def set_resolution(self, width, height):
        self.capture.set(self.cv2.CAP_PROP_FRAME_WIDTH, width)
        self.capture.set(self.cv2.CAP_PROP_FRAME_HEIGHT, height)

    def get_frame_rate(self):
        return self.capture.get(self.cv2.CAP_PROP_FPS)

    def get_resolution(self):
        width = self.capture.get(self.cv2.CAP_PROP_FRAME_WIDTH)
        height = self.capture.get(self.cv2.CAP_PROP_FRAME_HEIGHT)
        return width, height

    def read_frame(self):
        if self.result:
            return True, self.frame_queue.get()
        else:
            return False, None

    def close_video(self):
        self.stopped = True

    def pause_video(self):
        self.paused = True

    def resume_video(self):
        self.frame_queue = queue.Queue()
        self.paused = False

    def is_opened(self):
        return self.capture.isOpened()

    def update(self):
        start_time = time.time()
        frame_count = 0
        while not self.stopped:
            ret, frame = self.capture.read()
            self.result = ret
            if ret:
                self.frame_queue.put(frame)
            frame_count += 1
        if self.stopped:
            print("Frame Count: " + str(frame_count) + ". FPS: " + str(round(frame_count/(time.time()-start_time),2)))
            self.capture.release()
            return
