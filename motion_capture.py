import queue
import threading
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
        print("MotionCapture:__init__ openCV version: " + cv2.__version__)
        print("Configuration: ", config)
        self.config = config
        self.motion_processor = None
        self.start_sample_time = None
        self.pulse_rate_bpm = "Not available"
        self.tracker = None
        if self.config["show_pulse_charts"] is True:
            self.motion_charts = MotionCharts()
            self.motion_charts.initialize_charts()


    # noinspection PyPep8
    def capture(self, video_file_or_camera):
        print("MotionCapture:capture")

        if video_file_or_camera is None:
            video_file_or_camera = 0  # First camera

        video = self.create_camera(video_file_or_camera, self.config["video_fps"],
                                   self.config["resolution"]["width"],
                                   self.config["resolution"]["height"])

        is_opened = video.open_video(video_file_or_camera)
        if not is_opened:
            print("Error opening video stream or file, '" + video_file_or_camera + "'")
        else:
            # Verify/retrieve that setting camera/video properties.
            width, height = video.get_resolution()
            self.config["resolution"]["width"] = width
            self.config["resolution"]["height"] = height
            self.config["video_fps"] = video.get_frame_rate()

            print( "Video: Resolution = " + str(self.config["resolution"]["width"]) + " X "
               + str(self.config["resolution"]["height"]) + ". Frame rate = " + str(round(self.config["video_fps"])))

        if self.config['use_tracking_after_detect']:
            self.process_face_detect_then_track(video)
        else:
            self.process_face_per_frame(video)

        cv2.destroyWindow('Frame')
        # When everything done, release the video capture object
        video.close_video()

        input("Hit Enter to exit")

    def start_capture(self, video):
        self.motion_processor = MotionProcessor()
        self.motion_processor.initialize()
        self.frame_number = 0
        self.start_process_time = time.time()
        video.start_capture(self.config["pulse_sample_frames"] +5)

    def process_face_detect_then_track(self, video):
        frame_count = 0
        tracking = False
        face_cascade = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
        self.start_capture(video)
        while video.is_opened():
            ret, frame = video.read_frame()
            if ret:
                frame_count +=1
                self.frame_number +=1
                if not tracking:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                    if len(faces) == 1:
                        for (x, y, w, h) in faces:
                            #inset rect to capture points in face, empirical
                            x += int(w/4)
                            w = int(w/2)
                            y += int(h/4)
                            h = int(h/2)
                            self.motion_processor.add_motion_rectangle(x, y, w, h)
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                            track_box = (x, y, w, h)
                            print("Tracking after face detect")
                            tracking = True
                            self.tracker = cv2.TrackerKCF_create()
                            self.tracker.init(frame, track_box)
                    else:
                        self.start_capture(video)

                else:
                    # Update tracker
                    ok, bbox = self.tracker.update(frame)
                    if ok:
                        # print("Tracker succeeded")
                        x = int(bbox[0])
                        y = int(bbox[1])
                        w = int(bbox[2])
                        h = int(bbox[3])
                        self.motion_processor.add_motion_rectangle(x, y, w, h)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                    else:
                        print("Tracker failed")
                        self.start_capture(video)
                        tracking = False

                cv2.putText(frame, "Pulse rate (BPM): " + self.pulse_rate_bpm + " Frame: " + str(frame_count),
                            (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                cv2.imshow('Frame', frame)

                if self.frame_number > self.config["pulse_sample_frames"]:
                    self.update_results( video.get_frame_rate())
                    tracking = False
                    print("Processing time: " + str( round(time.time() - self.start_process_time, 2)) +
                          " seconds. Frames/second:" +
                          str(round(frame_count /(time.time() - self.start_process_time), 2)) +
                          ". Frame count: " + str( frame_count))

                    input("Hit enter to continue")
                    frame_count = 0
                    self.start_capture(video)
                # Press Q on keyboard to  exit
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
            else:
                break
        return frame_count

    def update_results(self, fps):
        self.update_dimension('X', fps)
        self.update_dimension('Y', fps)

    def update_dimension(self, dimension, fps):
        x_frequency = None
        y_frequency = None
        beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive = \
            self.motion_processor.time_filter_motion(
            dimension, fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
        # if a fft isn't required, comment out the line below
        x_temp, y_temp,  x_frequency, y_frequency = \
            self.motion_processor.fft_filter_series(y_amplitude_filtered, fps, 'X',
                                                    self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])

        print( dimension + "-beats_per_minute: ", beats_per_minute)
        if dimension == 'X':
            self.pulse_rate_bpm = str( round(beats_per_minute,2))

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
