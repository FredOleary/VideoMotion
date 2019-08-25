import cv2


class CameraOpenCv:

    def __init__(self, cv2):
        self.cv2 = cv2

    def open_video(self, video_file_or_camera):
        self.capture = self.cv2.VideoCapture(video_file_or_camera)
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
