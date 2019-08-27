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
        self.send_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.process_worker = threading.Thread(target=self.process, args=(self.send_queue,))
        self.process_worker.setDaemon(True)
        self.process_worker.start()
        if self.config["show_pulse_charts"] is True:
            self.motion_charts = MotionCharts()
            self.motion_charts.initialize_charts()

        self.motion_processor = None
        self.start_sample_time = None
        self.pulse_rate_bpm = "Not available"
        self.tracker = None

    def initialize_frame(self):
        self.motion_processor = MotionProcessor()
        self.motion_processor.initialize()
        self.start_sample_time = time.time()

    def check_frame(self):
        if (time.time() - self.start_sample_time) > self.config["pulse_sample_seconds"]:
            return True
        else:
            return False

    def queue_results(self):
        motion = {"verb": 'process', "mp": self.motion_processor, "response_queue": self.response_queue}
        self.send_queue.put(motion)

    def check_response(self):
        try:
            response = self.response_queue.get_nowait()
            if response["dimension"] == 'X':
                if response["beats_per_minute"] == 0:
                    self.pulse_rate_bpm = "Not available"
                else:
                    self.pulse_rate_bpm = str(round(response["beats_per_minute"]))

            if self.config["show_pulse_charts"] is True:
                self.motion_charts.update_time_chart(response)
            return True
        except queue.Empty:
            return False

    # noinspection PyPep8
    def capture(self, video_file_or_camera):
        print("MotionCapture:capture")

        face_cascade = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

        if video_file_or_camera is None:
            video_file_or_camera = 0  # First camera

        video = self.create_camera(video_file_or_camera, self.config["video_fps"], self.config["resolution"]["width"],
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

            self.initialize_frame()

        frame_count = 0
        start_capture_time = time.time()
        tracking = False
        while video.is_opened():
            ret, frame = video.read_frame()
            if ret:
                frame_count = frame_count+1
                if not self.config['use_tracking_after_detect'] or not tracking:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                    if len(faces) == 1:
                        for (x, y, w, h) in faces:
                            self.motion_processor.add_motion_rectangle(x, y, w, h)
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                        track_box = (x, y, w, h)
                        if self.config['use_tracking_after_detect']:
                            print("Tracking after face detect")
                            tracking = True
                            self.tracker = cv2.TrackerKCF_create()
                            self.tracker.init(frame, track_box)
                    else:
                        self.motion_processor.add_no_motion()

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
                        self.initialize_frame()
                        tracking = False

                cv2.putText(frame, "Pulse rate (BPM): "+ self.pulse_rate_bpm + " Frame: " +str(frame_count),
                            (30,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                cv2.imshow('Frame', frame)

                if self.check_frame():
                    self.queue_results()
                    self.initialize_frame()
                    tracking = False
                else:
                    self.check_response()

                # Press Q on keyboard to  exit
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
            else:
                break

        end_capture_time = time.time()
        print("Elapsed time: " + str(round(end_capture_time - start_capture_time,2)) + " seconds. fps:" + str(
            round(frame_count / (end_capture_time - start_capture_time), 2)) + ". Frame count: " + str(frame_count))
        cv2.destroyWindow('Frame')
        # When everything done, release the video capture object
        video.close_video()

        end = {"verb":'done'}
        self.send_queue.put(end)
        self.send_queue.join()
        input("Hit Enter to exit")

    def process(self, q):
        def enqueue_dimension(dimension, config):
            mp = motion['mp']
            # x_time, y_amplitude,  x_frequency, y_frequency = \
            #    mp.fft_filter_motion('X', fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
            beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive = mp.time_filter_motion(
                dimension, config["video_fps"], config["low_pulse_bpm"], config["high_pulse_bpm"])
            print("beats_per_minute: ", beats_per_minute)
            motion["response_queue"].put({
                "beats_per_minute": beats_per_minute,
                "x_time": x_time,
                "y_amplitude": y_amplitude,
                "y_amplitude_filtered": y_amplitude_filtered,
                "peaks_positive": peaks_positive,
                "dimension": dimension
            })

        while True:
            motion = q.get()
            if motion["verb"] == 'done':
                print("process terminated")
                q.task_done()
                break
            elif motion["verb"] == "process":
                print("processing motion")
                enqueue_dimension('X', self.config)
                enqueue_dimension('Y', self.config)
                enqueue_dimension('W', self.config)
                enqueue_dimension('H', self.config)
                q.task_done()

    def create_camera(self, video_file_or_camera, fps, width, height):
        # For files nor non raspberry pi devices, use open cv, for realtime video on raspberry pi, use CameraRaspbian
        if os.path.isfile("/etc/rpi-issue") and video_file_or_camera == 0:
            return CameraRaspbian(fps, width, height)
        else:
            return CameraOpenCv(cv2, fps, width, height)
