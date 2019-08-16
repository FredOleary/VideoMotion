import time
import numpy as np
import matplotlib.pyplot as plt
import scipy.io

from bandpass_filter import BandPassFilter

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

    def filter(self, x_frequency, y_frequency, low_pulse_bpm, high_pulse_bpm):
        start_index = 0
        end_index = x_frequency.size -1
        low_pulse_bps = None
        high_pulse_bps = None
        if low_pulse_bpm is not None :
            low_pulse_bps = low_pulse_bpm/60
        if high_pulse_bpm is not None :
            high_pulse_bps = high_pulse_bpm/60

        for index in range(x_frequency.size):
            if low_pulse_bps is not None and x_frequency[index] > low_pulse_bps and start_index == 0:
                start_index = index
            if high_pulse_bps is not None and x_frequency[index] > high_pulse_bps :
                end_index = index
                break
        return x_frequency[start_index:end_index], y_frequency[start_index:end_index]

    def fft_filter_series(self, series, fps, dimension, low_pulse_bpm = None, high_pulse_bpm = None):
        ts = 1.0 / fps  # sampling interval

        videoLength = len(series) * ts
        x_time = np.arange(0, videoLength, ts)  # time vector
        x_time = x_time[range(len(series))]

        y_time = np.array(series)

        # persist to file for post processing
        scipy.io.savemat('Pulse_time series_' +dimension, {
            'x': x_time,
            'y': y_time
        })

        number_of_samples = len(y_time)  # length of the signal
        k = np.arange(number_of_samples)
        T = number_of_samples / fps
        x_frequency = k / T  # two sides frequency range
        x_frequency = x_frequency[range(int(number_of_samples / 2))]  # one side frequency range

        y_frequency = np.fft.fft(y_time) / number_of_samples  # fft computing and normalization
        y_frequency = abs(y_frequency[range(int(number_of_samples / 2))])

        x_frequency, y_frequency  = self.filter(x_frequency, y_frequency, low_pulse_bpm, high_pulse_bpm);
        return x_time, y_time, x_frequency, y_frequency

    def fft_filter_motion(self, dimension, fps, low_pulse_bpm, high_pulse_bpm):
        if dimension == 'X':
            series = self.x
        elif dimension == 'Y':
            series = self.y
        elif dimension == 'W':
            series = self.w
        else:
            series = self.h

        x_time, y_time, x_frequency, y_frequency = self.fft_filter_series( series, fps, dimension)

        x_frequency, y_frequency  = self.filter(x_frequency, y_frequency, low_pulse_bpm, high_pulse_bpm);
        return x_time, y_time, x_frequency, y_frequency

    def time_filter_motion(self, dimension, fps, low_pulse_bpm, high_pulse_bpm):
        band_pass_filter = BandPassFilter()
        if dimension == 'X':
            series = self.x
        elif dimension == 'Y':
            series = self.y
        elif dimension == 'W':
            series = self.w
        else:
            series = self.h

        return band_pass_filter.time_filter( series, fps, low_pulse_bpm, high_pulse_bpm)

    def time_filter_series(self, series, fps, low_pulse_bpm, high_pulse_bpm):
        band_pass_filter = BandPassFilter()
        return band_pass_filter.time_filter( series, fps, low_pulse_bpm, high_pulse_bpm)
