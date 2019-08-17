import time
from bandpass_filter import BandPassFilter
from fft_filter import FFTFilter


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

    def add_no_motion(self):
        try:
            if self.base_x is not None:
                if len(self.x) == 0:
                    self.x.append(0)
                    self.y.append(0)
                    self.w.append(0)
                    self.h.append(0)
                else:
                    self.x.append(self.x[len(self.x)-1])
                    self.y.append(self.y[len(self.y)-1])
                    self.w.append(self.w[len(self.w)-1])
                    self.h.append(self.h[len(self.h)-1])


        except IndexError:
            print("foo")
    def fft_filter_motion(self, dimension, fps, low_pulse_bpm, high_pulse_bpm):
        if dimension == 'X':
            series = self.x
        elif dimension == 'Y':
            series = self.y
        elif dimension == 'W':
            series = self.w
        else:
            series = self.h
        fft_filter = FFTFilter()
        return fft_filter.fft_filter(series, fps, dimension, low_pulse_bpm, high_pulse_bpm)

    @staticmethod
    def fft_filter_series(series, fps, dimension, low_pulse_bpm, high_pulse_bpm):
        fft_filter = FFTFilter()
        return fft_filter.fft_filter(series, fps, dimension, low_pulse_bpm, high_pulse_bpm)

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

        return band_pass_filter.time_filter(series, fps, low_pulse_bpm, high_pulse_bpm)

    @staticmethod
    def time_filter_series(series, fps, low_pulse_bpm, high_pulse_bpm):
        band_pass_filter = BandPassFilter()
        return band_pass_filter.time_filter(series, fps, low_pulse_bpm, high_pulse_bpm)
