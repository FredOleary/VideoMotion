import unittest
import matplotlib.pyplot as plt
import numpy as np
from motion_processor import MotionProcessor
from roi_motion import ROIMotion
from hr_charts import HRCharts


class TestROIMotion(unittest.TestCase):

    def test_roi_motion(self):
        hr_chart = HRCharts()
        hr_chart.add_chart("MotionChart")

        fps = 30.0  # frames/second (sample rate)
        sample_interval = 1.0 / fps  # sampling interval
        length_of_signal_seconds = 10
        pulse_rate_seconds = 1.0

        x_time = np.arange(0, length_of_signal_seconds, sample_interval)

        trend = np.linspace(0, 3, len(x_time))
        y = trend + np.sin(pulse_rate_seconds * 2.0 * np.pi * x_time) + .3 * np.sin(
            pulse_rate_seconds * 3 * 2.0 * np.pi * x_time)

        roi_motion = ROIMotion()

        roi_motion.initialize(y[0])

        for x in range(int(fps * length_of_signal_seconds) - 1):
            roi_motion.update(y[x + 1])

        roi_motion.process(fps, 30, 150)

        roi_motion.calculate_bpm_from_peaks_positive()

        roi_motion.calculate_bpm_from_fft()

        # TODO - Verify results....

        chart_data = {
            "bpm_peaks": roi_motion.bpm_peaks,
            "bpm_fft": roi_motion.bpm_fft,
            "x_time": roi_motion.time_series,
            "y_amplitude": roi_motion.raw_amplitude_series,
            "y_amplitude_detrended": roi_motion.de_trended_series,
            "y_amplitude_filtered": roi_motion.filtered_amplitude_series,
            "peaks_positive": roi_motion.peaks_positive_amplitude,
            "name": 'MotionChart',
            "x_frequency": roi_motion.fft_frequency_series,
            "y_frequency": roi_motion.fft_amplitude_series
        }

        hr_chart.update_chart(chart_data)
        plt.show()
        input("Done - Press Enter/Return to exit")



if __name__ == '__main__':
    unittest.main()
