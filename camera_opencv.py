import cv2


class CameraOpenCv:

    def __init__(self, cv2, fps, width, height):
        self.cv2 = cv2
        self.fps = fps
        self.width = width
        self.height = height
        self.capture = None

    def open_video(self, video_file_or_camera):
        self.capture = self.cv2.VideoCapture(video_file_or_camera)
        self.capture.set(self.cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(self.cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.capture.set(self.cv2.CAP_PROP_FPS, self.fps)
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
        ret, frame = self.capture.read()
        return ret, frame

    def close_video(self):
        self.capture.release()

    def is_opened(self):
        return self.capture.isOpened()
