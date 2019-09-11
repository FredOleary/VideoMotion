import time
import os

import cv2

from camera_opencv import CameraOpenCv
from camera_raspbian import CameraRaspbian

from roi_motion import ROIMotion
from roi_color import ROIColor
from hr_charts import HRCharts


# noinspection PyUnresolvedReferences
class FrameProcessor:
    def __init__(self, config):
        print("FrameProcessor:__init__ - openCV version: {}".format( cv2.__version__))
        print("FrameProcessor:__init__ - Configuration: ", config)
        self.config = config
        self.start_sample_time = None
        self.pulse_rate_bpm = "Not available"
        self.tracker = None
        self.frame_number = 0
        self.start_process_time = None
        self.tracker_list = list()
        self.hr_charts = None


    def capture(self, video_file_or_camera: str):
        """Open video file or start camera. Then start processing frames for motion"""
        print("FrameProcessor:capture")

        if video_file_or_camera is None:
            video_file_or_camera = 0  # First camera

        video = self.create_camera(video_file_or_camera, self.config["video_fps"],
                                   self.config["resolution"]["width"],
                                   self.config["resolution"]["height"])

        is_opened = video.open_video(video_file_or_camera)
        if not is_opened:
            print("FrameProcessor:capture - Error opening video stream or file, '{}'".format(video_file_or_camera))
        else:
            # retrieve the camera/video properties.
            width, height = video.get_resolution()
            self.config["resolution"]["width"] = width
            self.config["resolution"]["height"] = height
            self.config["video_fps"] = video.get_frame_rate()

            print("FrameProcessor:capture - Video: Resolution = {} X {}. Frame rate {}".
                  format(self.config["resolution"]["width"],
                         self.config["resolution"]["height"],
                         round(self.config["video_fps"])))

            self.process_feature_detect_then_track(video)

        cv2.destroyWindow('Frame')
        video.close_video()
        time.sleep(.5)
        input("Hit Enter to exit")

    def start_capture(self, video):
        """Start streaming the video file or camera"""
        self.__create_trackers()
        self.frame_number = 0
        self.start_process_time = time.time()
        video.start_capture(self.config["pulse_sample_frames"]+1)

    def process_feature_detect_then_track(self, video):
        """Read video frame by frame and collect changes to the identified features. After sufficient
        frames have been collect, analyse the results"""
        tracking = False
        face_cascade = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
        mouth_cascade = cv2.CascadeClassifier('data/haarcascade_mcs_mouth.xml')

        self.start_capture(video)
        if self.config["show_pulse_charts"] is True:
            self.hr_charts = HRCharts()
            for tracker in self.tracker_list:
                self.hr_charts.add_chart(tracker.name)

        while video.is_opened():
            ret, frame = video.read_frame()
            if ret:
                # If the original frame is not writable and we wish to modify the frame. E.g. change the ROI to green
                frame = frame.copy()
                self.frame_number += 1
                if not tracking:
                    if self.config['feature_method'] == 'face' or \
                            self.config['feature_method'] == 'mouth' or \
                            self.config['feature_method'] == 'forehead':
                        found = False
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                        if len(faces) == 1:
                            for (x, y, w, h) in faces:
                                if self.config['feature_method'] == 'mouth':
                                    roi_gray = gray[y:y+h, x:x+w]
                                    mouth = mouth_cascade.detectMultiScale(roi_gray, 1.3, 5)
                                    for( x_mouth, y_mouth, w, h) in mouth:
                                        x += x_mouth
                                        y += y_mouth
                                        found = True
                                        break
                                elif self.config['feature_method'] == 'forehead':
                                    # For forehead detection, use the top fraction of face
                                    h = int(h/5)
                                    found = True
                                    break
                                else:
                                    found = True
                                    break
                        if found:
                            for tracker in self.tracker_list:
                                tracker.initialize(x, y, w, h, frame )


#                            frame[y:y + h, x:x + w] = roi_green
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1)
                            track_box = (x, y, w, h)
                            print("FrameProcessor:process_feature_detect_then_track - Tracking after face detect")
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
                        for tracker in self.tracker_list:
                            tracker.initialize(x, y, w, h, frame)

                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                        track_box = (x, y, w, h)
                        print("FrameProcessor:process_feature_detect_then_track - Tracking after roi select")
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
                        for tracker in self.tracker_list:
                            tracker.update(x, y, w, h, frame)

#                        frame[y:y + h, x:x + w] = roi_green
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (225, 0, 0), 1)
                    else:
                        print("FrameProcessor:process_feature_detect_then_track - Tracker failed")
                        self.start_capture(video)
                        tracking = False

                cv2.putText(frame, "Pulse rate (BPM): {}. Frame: {}".format(self.pulse_rate_bpm, self.frame_number),
                            (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                cv2.imshow('Frame', frame)

                if self.frame_number > self.config["pulse_sample_frames"]:
                    self.update_results(video.get_frame_rate())
                    tracking = False
                    print("FrameProcessor:process_feature_detect_then_track - Processing time: {} seconds. FPS: {}. Frame count: {}".
                          format(round(time.time() - self.start_process_time, 2),
                          round(self.frame_number / (time.time() - self.start_process_time), 2), self.frame_number))
                    if self.config["pause_between_samples"]:
                        input("Hit enter to continue")
                    self.start_capture(video)
                # Press Q on keyboard to  exit
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
            else:
                print("FrameProcessor:process_feature_detect_then_track - Video stream ended")
                break
        return

    def update_results(self, fps):
        """Process the the inter-fame changes, and filter results in both time and frequency domain """
        for tracker in self.tracker_list:
            tracker.process(fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
            tracker.calculate_bpm_from_peaks_positive()
            tracker.calculate_bpm_from_fft()

            chart_data = {
                "bpm_peaks": tracker.bpm_peaks,
                "bpm_fft": tracker.bpm_fft,
                "x_time": tracker.time_series,
                "y_amplitude": tracker.raw_amplitude_series,
                "y_amplitude_detrended": tracker.de_trended_series,
                "y_amplitude_filtered": tracker.filtered_amplitude_series,
                "peaks_positive": tracker.peaks_positive_amplitude,
                "name": tracker.name,
                "x_frequency": tracker.fft_frequency_series,
                "y_frequency": tracker.fft_amplitude_series
            }

            self.hr_charts.update_chart(chart_data)
#            plt.show()

    def __create_trackers(self):
        self.tracker_list.clear()
        self.tracker_list.append(ROIMotion('Y', "Longitude"))
        self.tracker_list.append(ROIColor('G', "Green"))

    @staticmethod
    def create_camera(video_file_or_camera, fps, width, height):
        """Create the appropriate class using opencv or the raspberry Pi piCamera"""
        # For files nor non raspberry pi devices, use open cv, for real-time video on raspberry pi, use CameraRaspbian
        if os.path.isfile("/etc/rpi-issue") and video_file_or_camera == 0:
            return CameraRaspbian(fps, width, height)
        else:
            return CameraOpenCv(cv2, fps, width, height)
