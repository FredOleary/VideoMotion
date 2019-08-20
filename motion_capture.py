import cv2
import matplotlib.pyplot as plt

import queue
import threading
import time

from motion_processor import MotionProcessor


# noinspection PyUnresolvedReferences
class MotionCapture:
    def __init__(self, config):
        print("MotionCapture:__init__ openCV version: " + cv2.__version__)
        print("Configuration: ", config)
        self.config = config

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
    def show_time_results(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive, dimension):
        fig, ax = plt.subplots(2, 1)
        if len(x_time) > 0:
            fig.suptitle(dimension + " Dimension BPM " + str(round(beats_per_minute, 2)), fontsize=14)
            ax[0].plot(x_time, y_amplitude)
            ax[0].set_xlabel('Time')
            ax[0].set_ylabel('Amplitude - Unfiltered ' + dimension)

            ax[1].plot(x_time,  y_amplitude_filtered, color=(1.0, 0.0, 0.0))

            ax[1].plot(x_time[peaks_positive], y_amplitude_filtered[peaks_positive], 'ro', ms=3, label='positive peaks',
                       color=(0.0, 0.0, 1.0))
            ax[1].set_xlabel('Pulse (BMP) ' + str(round(beats_per_minute, 2)))
            ax[1].set_ylabel('Amplitude - filtered ' + dimension)

    @staticmethod
    def show_fft_and_time(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered,
                          peaks_positive, x_frequency, y_frequency, dimension):
        fig, ax = plt.subplots(3, 1)
        if len(x_time) > 0:
            fig.suptitle(dimension + " Dimension BPM " + str(round(beats_per_minute, 2)), fontsize=14)
            ax[0].plot(x_time, y_amplitude)
            ax[0].set_xlabel('Time')
            ax[0].set_ylabel('Amplitude - Unfiltered')

            ax[1].plot(x_time,  y_amplitude_filtered, color=(1.0, 0.0, 0.0))
            ax[1].plot(x_time[peaks_positive], y_amplitude_filtered[peaks_positive], 'ro', ms=3, label='positive peaks',
                       color=(0.0, 0.0, 1.0))
            ax[1].set_ylabel('Amplitude - filtered')

            chart_bar_width = (x_frequency[len(x_frequency)-1]/(len(x_frequency)*2))*60
            ax[2].bar(x_frequency * 60, y_frequency, color=(1.0, 0.0, 0.0), width=chart_bar_width)
            ax[2].set_xlabel('Pulse (BMP)')
            ax[2].set_ylabel('|Y(BMP)|')
        else:
            fig.suptitle(dimension + " Dimension - No data available", fontsize=14)

    # def test_filters(self):
    #     mp = MotionProcessor()
    #     fps = 12.0  # frames/second (sample rate)
    #     sample_interval = 1.0 / fps  # sampling interval
    #     length_of_signal_seconds = 15
    #     x_time = np.arange(0, length_of_signal_seconds, sample_interval)  # time vector 15 seconds
    #
    #     pulse_rate_seconds = 0.9  # test pulse rate in seconds frequency (.9Hz = 54 bpm)
    #     # y = np.sin(pulse_rate_seconds * 2.0 * np.pi * x_time)
    #
    #     # Add some noise at 3 X the pulse rate and 1/3 amplitude, (comment out to remove noise)
    #     y = np.sin(pulse_rate_seconds * 2.0 * np.pi * x_time) + .3*np.sin(pulse_rate_seconds*3 * 2.0 * np.pi * x_time)
    #
    #     x_time, y_time, x_frequency, y_frequency = mp.fft_filter_series(y, fps, 'X', self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
    #     self.show_fft_results(x_time, y_time, x_frequency, y_frequency, 'X')
    #
    #     beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive = mp.time_filter_series(
    #         y, fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
    #     self.show_time_results(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive)
    #     plt.show()

    # noinspection PyPep8
    def capture(self, video_file_or_camera):
        print("MotionCapture:capture")

        send_queue = queue.Queue()
        response_queue = queue.Queue()
        process_worker = threading.Thread(target=self.process, args=(send_queue,))
        process_worker.setDaemon(True)
        process_worker.start()

        face_cascade = cv2.CascadeClassifier(self.config["face_classifier_path"])

        if video_file_or_camera is None:
            video_file_or_camera = 0  # First camera

        cap = cv2.VideoCapture(video_file_or_camera)
        # Check if camera opened successfully
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

        mp = MotionProcessor()
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
                else:
                    mp.add_no_motion()
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

        # x_time, y_amplitude,  x_frequency, y_frequency = mp.fft_filter_motion('X', fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
        # beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive = mp.time_filter_motion(
        #     'X', fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
        # self.show_fft_and_time(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive, x_frequency,
        #                        y_frequency, 'X')
        #
        # x_time, y_amplitude,  x_frequency, y_frequency = mp.fft_filter_motion('Y', fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
        # beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive = mp.time_filter_motion(
        #     'Y', fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
        # self.show_fft_and_time(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive, x_frequency,
        #                        y_frequency, 'Y')
        #
        # x_time, y_amplitude,  x_frequency, y_frequency = mp.fft_filter_motion('W', fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
        # beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive = mp.time_filter_motion(
        #     'W', fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
        # self.show_fft_and_time(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive, x_frequency,
        #                        y_frequency, 'W')
        #
        # x_time, y_amplitude,  x_frequency, y_frequency = mp.fft_filter_motion('H', fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
        # beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive = mp.time_filter_motion(
        #     'H', fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
        # self.show_fft_and_time(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive, x_frequency,
        #                        y_frequency, 'H')
        # plt.show()

        motion = {"verb":'process', "mp":mp, "response_queue":response_queue}
        send_queue.put(motion)

        response = response_queue.get()
        self.show_time_results(response['beats_per_minute'], response['x_time'], response['y_amplitude'],
                                        response['y_amplitude_filtered'], response['peaks_positive'],
                                        response['dimension'])
        plt.ion()
        plt.pause(0.0001)
        plt.show()
#        plt.pause(0.0001)
        end = {"verb":'done'}
        send_queue.put(end)
        send_queue.join()

        input("Press enter to exiting...\n")

    def process(self, q):
        while True:
            print("Waiting for motion")
            motion = q.get()
            print("motion received")
            time.sleep(5)
            q.task_done()
            if motion["verb"] == 'done':
                print("process terminated")
                break
            elif motion["verb"] == "process":
                print("processing motion")
                mp = motion['mp']
                # x_time, y_amplitude,  x_frequency, y_frequency = mp.fft_filter_motion('X', fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
                beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive = mp.time_filter_motion(
                    'X', self.config["video_fps"], self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
                print("beats_per_minute: ", beats_per_minute)
                motion["response_queue"].put({
                    "beats_per_minute": beats_per_minute,
                    "x_time": x_time,
                    "y_amplitude": y_amplitude,
                    "y_amplitude_filtered": y_amplitude_filtered,
                    "peaks_positive": peaks_positive,
                    "dimension": 'X'
                })
                # self.show_fft_and_time(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive, x_frequency,
                #                        y_frequency, 'X')

                # x_time, y_amplitude,  x_frequency, y_frequency = mp.fft_filter_motion('Y', fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
                # beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive = mp.time_filter_motion(
                #     'Y', fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
                # self.show_fft_and_time(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive, x_frequency,
                #                        y_frequency, 'Y')
                #
                # x_time, y_amplitude,  x_frequency, y_frequency = mp.fft_filter_motion('W', fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
                # beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive = mp.time_filter_motion(
                #     'W', fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
                # self.show_fft_and_time(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive, x_frequency,
                #                        y_frequency, 'W')
                #
                # x_time, y_amplitude,  x_frequency, y_frequency = mp.fft_filter_motion('H', fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
                # beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive = mp.time_filter_motion(
                #     'H', fps, self.config["low_pulse_bpm"], self.config["high_pulse_bpm"])
                # self.show_fft_and_time(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive, x_frequency,
                #                        y_frequency, 'H')

