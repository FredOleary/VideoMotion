import cv2
import matplotlib.pyplot as plt
from moviepy.editor import VideoFileClip
import numpy as np
from motion_processor import MotionProcessor

# cut off rate for pulse rate
LOW_PULSE_BPM = 30
HIGH_PULSE_BPM = 150


class MotionCapture:
    def __init__(self):
        print("MotionCapture:__init__")

    @staticmethod
    def show_fft_results(x_time, y_time, x_frequency, y_frequency, dimension):
        fig, ax = plt.subplots(2, 1)
        ax[0].plot(x_time, y_time)
        ax[0].set_xlabel('Time')
        ax[0].set_ylabel('Amplitude ' + dimension)
#        ax[1].plot(x_frequency, y_frequency, color=(1.0, 0.0, 0.0))  # plotting the spectrum in BPM

        chart_bar_width = (x_frequency[len(x_frequency)-1]/(len(x_frequency)*2))*60
        ax[1].bar(x_frequency * 60, y_frequency, color=(1.0, 0.0, 0.0), width=chart_bar_width)
        ax[1].set_xlabel('Pulse (BMP)')
        ax[1].set_ylabel('|Y(BMP)| ' + dimension)

    @staticmethod
    def show_time_results(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive):
        fig, ax = plt.subplots(2, 1)
        ax[0].plot(x_time, y_amplitude)
        ax[0].set_xlabel('Time')
        ax[0].set_ylabel('Amplitude - Unfiltered ' + 'X')

        ax[1].plot(x_time,  y_amplitude_filtered, color=(1.0, 0.0, 0.0))

        ax[1].plot(x_time[peaks_positive], y_amplitude_filtered[peaks_positive], 'ro', ms=3, label='positive peaks',
                   color=(0.0, 0.0, 1.0))
        ax[1].set_xlabel('Pulse (BMP) ' + str(round(beats_per_minute, 2)))
        ax[1].set_ylabel('Amplitude - filtered ' + 'X')

    def test_filters(self):
        mp = MotionProcessor()
        fps = 12.0  # frames/second (sample rate)
        sample_interval = 1.0 / fps  # sampling interval
        length_of_signal_seconds = 15
        x_time = np.arange(0, length_of_signal_seconds, sample_interval)  # time vector 15 seconds

        pulse_rate_seconds = 0.9  # test pulse rate in seconds frequency (.9Hz = 54 bpm)
        # y = np.sin(pulse_rate_seconds * 2.0 * np.pi * x_time)

        # Add some noise at 3 X the pulse rate and 1/3 amplitude, (comment out to remove noise)
        y = np.sin(pulse_rate_seconds * 2.0 * np.pi * x_time) + .3*np.sin(pulse_rate_seconds*3 * 2.0 * np.pi * x_time)

        x_time, y_time, x_frequency, y_frequency = mp.fft_filter_series(y, fps, 'X', LOW_PULSE_BPM, HIGH_PULSE_BPM)
        self.show_fft_results(x_time, y_time, x_frequency, y_frequency, 'X')

        beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive = mp.time_filter_series(
            y, fps, LOW_PULSE_BPM, HIGH_PULSE_BPM)
        self.show_time_results(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive)
        plt.show()

    def capture(self, video_file_or_camera):
        print("MotionCapture:capture")
        face_cascade = cv2.CascadeClassifier('/usr/local/lib/python3.7/site-packages/cv2/data/haarcascade_frontalface_default.xml')

        clip = VideoFileClip(video_file_or_camera)
        print(video_file_or_camera + " duration " + str(clip.duration) + ", framesPerSecond " + str(clip.fps))

        mp = MotionProcessor()

        cap = cv2.VideoCapture(video_file_or_camera)

        # Check if camera opened successfully
        if not cap.isOpened():
            print("Error opening video stream or file, '" + video_file_or_camera + "'")

#        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        mp.initialize()
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                if len(faces) == 1:
                    for (x, y, w, h) in faces:
                        mp.add_motion_rectangle(x, y, w, h)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 1)
#                        print("width",w, "height", h)
                else:
                    print("----------------------------------------------No face in frame!")

                cv2.imshow('Frame', frame)

                # Press Q on keyboard to  exit
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
            else:
                break

        cv2.destroyWindow('Frame')
        # When everything done, release the video capture object
        cap.release()

        x_time, y_time,  x_frequency, y_frequency = mp.fft_filter_motion('X', clip.fps, LOW_PULSE_BPM, HIGH_PULSE_BPM)
        self.show_fft_results(x_time, y_time, x_frequency, y_frequency, 'X')

        x_time, y_time,  x_frequency, y_frequency = mp.fft_filter_motion('Y', clip.fps, LOW_PULSE_BPM, HIGH_PULSE_BPM)
        self.show_fft_results(x_time, y_time, x_frequency, y_frequency, 'Y')

        x_time, y_time,  x_frequency, y_frequency = mp.fft_filter_motion('W', clip.fps, LOW_PULSE_BPM, HIGH_PULSE_BPM)
        self.show_fft_results(x_time, y_time, x_frequency, y_frequency, 'W')

        x_time, y_time,  x_frequency, y_frequency = mp.fft_filter_motion('H', clip.fps, LOW_PULSE_BPM, HIGH_PULSE_BPM)
        self.show_fft_results(x_time, y_time, x_frequency, y_frequency, 'H')
        # plt.show()

        beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive = mp.time_filter_motion(
            'X', clip.fps, LOW_PULSE_BPM, HIGH_PULSE_BPM)
        self.show_time_results(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive)

        beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive = mp.time_filter_motion(
            'Y', clip.fps, LOW_PULSE_BPM, HIGH_PULSE_BPM)
        self.show_time_results(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive)

        beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive = mp.time_filter_motion(
            'W', clip.fps, LOW_PULSE_BPM, HIGH_PULSE_BPM)
        self.show_time_results(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive)

        beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive = mp.time_filter_motion(
            'H', clip.fps, LOW_PULSE_BPM, HIGH_PULSE_BPM)
        self.show_time_results(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive)

        plt.show()