import time
import os

import cv2

from camera_opencv import CameraOpenCv
from camera_raspbian import CameraRaspbian

from motion_processor import MotionProcessor
from motion_charts import MotionCharts


# noinspection PyUnresolvedReferences
class MotionCapture:
    def __init__(self, config):
        print("MotionCapture:__init__ - openCV version: {}".format( cv2.__version__))
        print("MotionCapture:__init__ - Configuration: ", config)
        self.config = config
        self.motion_processor = None
        self.start_sample_time = None
        self.pulse_rate_bpm = "Not available"
        self.tracker = None
        self.frame_number = 0
        self.start_process_time = None

        if self.config["show_pulse_charts"] is True:
            self.motion_charts = MotionCharts()
            self.motion_charts.initialize_charts()

    def capture(self, video_file_or_camera: str):
        print("MotionCapture:capture")

        if video_file_or_camera is None:
            video_file_or_camera = 0  # First camera

        video = self.create_camera(video_file_or_camera, self.config["video_fps"],
                                   self.config["resolution"]["width"],
                                   self.config["resolution"]["height"])

        is_opened = video.open_video(video_file_or_camera)
        if not is_opened:
            print("MotionCapture:capture - Error opening video stream or file, '{}'".format(video_file_or_camera))
        else:
            # Verify/retrieve that setting camera/video properties.
            width, height = video.get_resolution()
            self.config["resolution"]["width"] = width
            self.config["resolution"]["height"] = height
            self.config["video_fps"] = video.get_frame_rate()

            print("MotionCapture.capture - Video: Resolution = {} X {}. Frame rate {}".
                  format(self.config["resolution"]["width"],
                         self.config["resolution"]["height"],
                         round(self.config["video_fps"])))

            self.process_feature_detect_then_track(video)

        cv2.destroyWindow('Frame')
        video.close_video()

        input("Hit Enter to exit")

    def start_capture(self, video):
        self.motion_processor = MotionProcessor()
        self.motion_processor.initialize()
        self.frame_number = 0
        self.start_process_time = time.time()
        video.start_capture(self.config["pulse_sample_frames"] + 5)

    def process_feature_detect_then_track(self, video):
        frame_count = 0
        tracking = False
        face_cascade = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
        self.start_capture(video)
        while video.is_opened():
            ret, frame = video.read_frame()
            if ret:
                frame_count += 1
                self.frame_number += 1
                if not tracking:
                    if self.config['feature_method'] == 'face':
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                        if len(faces) == 1:
                            for (x, y, w, h) in faces:
                                # inset rect to capture points in face, empirical
                                x += int(w/4)
                                w = int(w/2)
                                y += int(h/4)
                                h = int(h/2)
                                self.motion_processor.add_motion_rectangle(x, y, w, h)
                                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                                track_box = (x, y, w, h)
                                print("MotionCapture:process_feature_detect_then_track - Tracking after face detect")
                                tracking = True
                                self.tracker = cv2.TrackerCSRT_create()
                                self.tracker.init(frame, track_box)
                        else:
                            self.start_capture(video)
                    elif self.config['feature_method'] == 'selectROI':
                        r = cv2.selectROI(frame)
                        x = r[0]
                        y = r[1]
                        w = r[2]
                        h = r[3]
                        self.motion_processor.add_motion_rectangle(x, y, w, h)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                        track_box = (x, y, w, h)
                        print("MotionCapture:process_feature_detect_then_track - Tracking after roi select")
                        tracking = True
                        self.tracker = cv2.TrackerCSRT_create()
                        self.tracker.init(frame, track_box)

                else:
                    # Update tracker
                    ok, bbox = self.tracker.update(frame)
                    if ok:
                        x = int(bbox[0])
                        y = int(bbox[1])
                        w = int(bbox[2])
                        h = int(bbox[3])
                        self.motion_processor.add_motion_rectangle(x, y, w, h)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                    else:
                        print("MotionCapture:process_feature_detect_then_track - Tracker failed")
                        self.start_capture(video)
                        tracking = False

                cv2.putText(frame, "Pulse rate (BPM): " + self.pulse_rate_bpm + " Frame: " + str(frame_count),
                            (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                cv2.imshow('Frame', frame)

                if self.frame_number > self.config["pulse_sample_frames"]:
                    self.update_results(video.get_frame_rate())
                    tracking = False
                    print("MotionCapture - Processing time: {} seconds. FPS: {}. Frame count: {}".
                          format(round(time.time() - self.start_process_time, 2),
                          round(frame_count / (time.time() - self.start_process_time), 2), frame_count))
                    if self.config["pause_between_samples"]:
                        input("Hit enter to continue")
                    frame_count = 0
                    self.start_capture(video)
                # Press Q on keyboard to  exit
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
            else:
                print("MotionCapture:process_feature_detect_then_track - Video stream ended")
                break
        return

    def update_results(self, fps):
        self.update_dimension('X', fps)
        self.update_dimension('Y', fps)

    def update_dimension(self, dimension, fps):
        beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive = \
            self.motion_processor.time_filter_motion(
                dimension, fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
        # if a fft isn't required, comment out the line below
        x_temp, y_temp,  x_frequency, y_frequency = \
            self.motion_processor.fft_filter_series(y_amplitude_filtered, fps, 'X',
                                                    self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])

        print("MotionCapture:update_dimension - Dimension {}, BPM {}".format(dimension, beats_per_minute))
        if dimension == 'X':
            self.pulse_rate_bpm = str(round(beats_per_minute, 2))

        if self.config["show_pulse_charts"] is True:
            chart_data = {
                "beats_per_minute": beats_per_minute,
                "x_time": x_time,
                "y_amplitude": y_amplitude,
                "y_amplitude_filtered": y_amplitude_filtered,
                "peaks_positive": peaks_positive,
                "x_frequency": x_frequency,
                "y_frequency": y_frequency,
                "dimension": dimension
            }
            self.motion_charts.update_time_chart(chart_data)

    @staticmethod
    def create_camera(video_file_or_camera, fps, width, height):
        # For files nor non raspberry pi devices, use open cv, for real-time video on raspberry pi, use CameraRaspbian
        if os.path.isfile("/etc/rpi-issue") and video_file_or_camera == 0:
            return CameraRaspbian(fps, width, height)
        else:
            return CameraOpenCv(cv2, fps, width, height)
