import unittest
import matplotlib.pyplot as plt
import numpy as np
from motion_processor import MotionProcessor
from motion_capture import MotionCapture

class TestFilters(unittest.TestCase):

    def test_time_filter(self):
        config = {"low_pulse_bpm":30, "high_pulse_bpm":150}
        mc = MotionCapture(config)
        mp = MotionProcessor()
        fps = 12.0  # frames/second (sample rate)
        sample_interval = 1.0 / fps  # sampling interval
        length_of_signal_seconds = 15
        x_time = np.arange(0, length_of_signal_seconds, sample_interval)  # time vector 15 seconds

        pulse_rate_seconds = 0.9  # test pulse rate in seconds frequency (.9Hz = 54 bpm)
        # y = np.sin(pulse_rate_seconds * 2.0 * np.pi * x_time)

        # Add some noise at 3 X the pulse rate and 1/3 amplitude, (comment out to remove noise)
        y = np.sin(pulse_rate_seconds * 2.0 * np.pi * x_time) + .3*np.sin(pulse_rate_seconds*3 * 2.0 * np.pi * x_time)

        beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive = mp.time_filter_series(
            y, fps, config["low_pulse_bpm"], config["high_pulse_bpm"])
        mc.show_time_results(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered, peaks_positive, "test")
        self.assertEqual(round(beats_per_minute), 54)
        plt.show()

    def test_fft_filter(self):
        config = {"low_pulse_bpm":30, "high_pulse_bpm":150}
        mc = MotionCapture(config)
        mp = MotionProcessor()
        fps = 30.0  # frames/second (sample rate)
        sample_interval = 1.0 / fps  # sampling interval
        length_of_signal_seconds = 15
        x_time = np.arange(0, length_of_signal_seconds, sample_interval)  # time vector 15 seconds

        pulse_rate_seconds = 1  # test pulse rate in seconds frequency (.9Hz = 54 bpm)
        y = np.sin(pulse_rate_seconds * 2.0 * np.pi * x_time)

        # Add some noise at 3 X the pulse rate and 1/3 amplitude, (comment out to remove noise)
#        y = np.sin(pulse_rate_seconds * 2.0 * np.pi * x_time) + .3*np.sin(pulse_rate_seconds*3 * 2.0 * np.pi * x_time)

        x_time, y_time, x_frequency, y_frequency = mp.fft_filter_series(y, fps, 'test',
                                                                        config["low_pulse_bpm"], config["high_pulse_bpm"])
        mc.show_fft_results(x_time, y_time, x_frequency, y_frequency, 'test')

        for index in range(len(x_frequency)):
            if x_frequency[index] == pulse_rate_seconds:
                self.assertEquals(round(y_frequency[index],1), 0.5 )
            else:
                self.assertEquals(round(y_frequency[index]), 0.0)
        plt.show()


if __name__ == '__main__':
    unittest.main()
