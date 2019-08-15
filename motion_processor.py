import time
import numpy as np
import matplotlib.pyplot as plt
import scipy.io

#cut off rate for pulse rate
LOW_PULSE = 30/60
HIGH_PULSE = 300/60

class MotionProcessor:

    def __init__(self):
        self.x = None
        self.y = None
        self.w = None
        self.h = None
        self.base_x = None
        self.base_y = None
        self.base_w = None
        self.base_h = None
        self.start_time = None

    def initialize(self):
        self.x = list()
        self.y = list()
        self.w = list()
        self.h = list()
        self.base_x = None
        self.base_y = None
        self.base_w = None
        self.base_h = None
        self.start_time = time.time()
        print("MotionProcessor : initialized at: " + str(self.start_time))

    def add_motion_rectangle(self, x, y, w, h):
        if self.base_x is None:
            self.base_x = x
            self.base_y = y
            self.base_w = w
            self.base_h = h
        else:
            self.x.append(x - self.base_x)
            self.y.append(y - self.base_y)
            self.w.append(w - self.base_w)
            self.h.append(h - self.base_h)

    def filter(self, x_frequency, y_frequency):
        start_index = 0
        end_index = x_frequency.size -1
        for index in range(x_frequency.size):
            if x_frequency[index] > LOW_PULSE and start_index == 0:
                start_index = index
            if x_frequency[index] > HIGH_PULSE :
                end_index = index
                break
        return x_frequency[start_index:end_index], y_frequency[start_index:end_index]

    def fft_filter_motion(self, dimension, fps):
        ts = 1.0 / fps  # sampling interval
        if dimension == 'X':
            series = self.x
        elif dimension == 'Y':
            series = self.y
        elif dimension == 'W':
            series = self.w
        else:
            series = self.h

        videoLength = len(series) * ts
        t = np.arange(0, videoLength, ts)  # time vector
        t = t[range(len(series))]

        y_time_series = np.array(series)

        # persist to file for post processing
        scipy.io.savemat('Pulse_' +dimension, {
            'x': t,
            'y': y_time_series
        })
        # test_set = scipy.io.loadmat('Pulse_' +dimension)
        # test_set_x = test_set['x']
        # test_set_y = test_set['y']

        n = len(y_time_series)  # length of the signal
        k = np.arange(n)
        T = n / fps
        x_frequency = k / T  # two sides frequency range
        x_frequency = x_frequency[range(int(n / 2))]  # one side frequency range

        y_frequency = np.fft.fft(y_time_series) / n  # fft computing and normalization
        y_frequency = abs(y_frequency[range(int(n / 2))])

        x_frequency, y_frequency  = self.filter(x_frequency, y_frequency);
        fig, ax = plt.subplots(2, 1)
        ax[0].plot(t, y_time_series)
        ax[0].set_xlabel('Time')
        ax[0].set_ylabel('Amplitude ' + dimension)
        ax[1].bar(x_frequency *60, y_frequency, color=(1.0, 0.0, 0.0), width=1.0 )  # plotting the spectrum in BPM
        ax[1].set_xlabel('Pulse (BMP)')
        ax[1].set_ylabel('|Y(BMP)| ' + dimension)
