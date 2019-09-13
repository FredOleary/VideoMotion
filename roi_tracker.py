import numpy as np
from bandpass_filter import BandPassFilter
from fft_filter import FFTFilter
from scipy import signal


class ROITracker:
    """ROITracker maintains raw and processed data for the dimension of interest """
    def __init__(self, name):
        self.name = name
        self.time_series = None
        self.raw_amplitude_series = list()      # Raw data collected from video frames
        self.de_trended_series = None           # de-trended data
        self.filtered_amplitude_series = None   # time filtered
        self.peaks_positive_amplitude = None    # positive peaks.
        self.fft_amplitude_series = None        # fft amplitude, from fft on time filtered data
        self.fft_frequency_series = None        # fft harmonics
        self.bpm_peaks = None
        self.bpm_fft = None
        self.base_value = None

    def initialize(self, initial_value):
        self.base_value = initial_value

    def add_value(self, value):
        self.raw_amplitude_series.append(value - self.base_value)

    def create_time_series(self, fps):
        sample_interval = 1.0 / fps
        video_length = len(self.raw_amplitude_series) * sample_interval
        self.time_series = np.arange(0, video_length, sample_interval)
#        self.time_series = self.time_series[range(len(self.raw_amplitude_series))]

    def de_trend_series(self):
        self.de_trended_series = signal.detrend(self.raw_amplitude_series)

    def time_filter(self, fps, low_pulse_bpm, high_pulse_bpm):
        band_pass_filter = BandPassFilter()
        series = self.de_trended_series if self.de_trended_series is not None else self.raw_amplitude_series
        self.filtered_amplitude_series = band_pass_filter.time_filter2(series,  fps, low_pulse_bpm, high_pulse_bpm)

    def calculate_positive_peaks(self):
        peaks_positive, _ = signal.find_peaks(self.filtered_amplitude_series, height=.2, threshold=None)
        if len(peaks_positive) > 1:
            # time_intervals = np.average(np.diff(peaks_positive))
            # per_beat_in_seconds = time_intervals * x_time[1] - x_time[0]
            # beats_per_minute = 1 / per_beat_in_seconds * 60
            self.peaks_positive_amplitude = peaks_positive;
        else:
            self.peaks_positive_amplitude = None

    def calculate_bpm_from_peaks_positive(self):
        if self.peaks_positive_amplitude is not None:
            time_intervals = np.average(np.diff(self.peaks_positive_amplitude))
            per_beat_in_seconds = time_intervals * self.time_series[1] - self.time_series[0]
            self.bpm_peaks = 1 / per_beat_in_seconds * 60

    def calculate_bpm_from_fft(self):
        if self.fft_amplitude_series is not None:
            freqArray = np.where(self.fft_amplitude_series == np.amax(self.fft_amplitude_series))
            if len(freqArray) > 0:
                self.bpm_fft = (self.fft_frequency_series[freqArray[0]] * 60)[0]

    def fft_filter(self, fps, low_pulse_bpm, high_pulse_bpm):
        """Note this requires that the raw data is previously filtered"""
        fft_filter = FFTFilter()
        self.fft_frequency_series, self.fft_amplitude_series = \
            fft_filter.fft_filter2(self.filtered_amplitude_series, fps, low_pulse_bpm, high_pulse_bpm)


