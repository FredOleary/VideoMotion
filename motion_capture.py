import cv2
import matplotlib.pyplot as plt

import queue
import threading
import time

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
        self.motion_charts = MotionCharts()
        self.motion_charts.initialize_charts()
        self.motion_processor = None
        self.start_time = None
        self.pulse_rate_bpm = "Not available"


    def initialize_frame(self):
        self.motion_processor = MotionProcessor()
        self.motion_processor.initialize()
        self.start_time = time.time()

    def check_frame(self):
        if (time.time() - self.start_time) > self.config["pulse_frame_seconds"]:
            return True
        else:
            return False

    def queue_results(self):
        motion = {"verb":'process', "mp":self.motion_processor, "response_queue":self.response_queue}
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

        face_cascade = cv2.CascadeClassifier(self.config["face_classifier_path"])

        if video_file_or_camera is None:
            video_file_or_camera = 0  # First camera

        cap = cv2.VideoCapture(video_file_or_camera)
        if not cap.isOpened():
            print("Error opening video stream or file, '" + video_file_or_camera + "'")
        else:
            fps = cap.get(cv2.CAP_PROP_FPS)

            if video_file_or_camera == 0:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config["resolution"]["width"])
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config["resolution"]["height"])
                cap.set(cv2.CAP_PROP_FPS, self.config["video_fps"])
                fps = cap.get(cv2.CAP_PROP_FPS)
            else:
                self.config["resolution"]["width"] = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                self.config["resolution"]["height"] = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                self.config["video_fps"] = cap.get(cv2.CAP_PROP_FPS)

            print( "Video: Resolution = " + str(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) + " X "
               + str(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) + ". Frames rate = " + str(round(fps)))

            self.initialize_frame()

        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                if len(faces) == 1:
                    for (x, y, w, h) in faces:
                        self.motion_processor.add_motion_rectangle(x, y, w, h)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 1)
                else:
                    self.motion_processor.add_no_motion()

                cv2.putText(frame, "Pulse rate (BPM): "+ self.pulse_rate_bpm, (30,30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                cv2.imshow('Frame', frame)
                if self.check_frame():
                    self.queue_results()
                    self.initialize_frame()
                else:
                    self.check_response()

                # Press Q on keyboard to  exit
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
            else:
                break

        cv2.destroyWindow('Frame')
        # When everything done, release the video capture object
        cap.release()

        end = {"verb":'done'}
        self.send_queue.put(end)
        self.send_queue.join()

    def process(self, q):
        def enqueue_dimension(dimension, config):
            mp = motion['mp']
            # x_time, y_amplitude,  x_frequency, y_frequency = mp.fft_filter_motion('X', fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
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

