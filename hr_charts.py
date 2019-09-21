import matplotlib.pyplot as plt
import numpy as np
from roi_tracker import ROITracker
class HRCharts:
    """Charts showing results of motion analysis of video """
    def __init__(self):
        self.chart_dictionary = {}

    def add_chart(self, name, sub_charts = 3):
        self.chart_dictionary.update({name: self.__create_chart(name, sub_charts)})

    @staticmethod
    def __create_chart(name, sub_charts):
        """Shows three stacked charts. The top chart shows raw motion vs time.
        The middle chart shows filtered motion vs time. The bottom chart is an FFT of the filtered motion"""
        fig, ax = plt.subplots(sub_charts, 1)
        fig.suptitle(name, fontsize=14)
        return {"fig": fig, "ax": ax}

    def update_chart(self, tracker):
        """Update amplitude vs time and FFT charts"""
        self.chart_dictionary[tracker.name]["ax"][0].clear()
        self.chart_dictionary[tracker.name]["ax"][1].clear()
        self.chart_dictionary[tracker.name]["ax"][2].clear()
        if len(tracker.time_period) > 0:
            try:
                bpm_pk = "N/A" if tracker.bpm_pk_pk is None else str(round(tracker.bpm_pk_pk, 2))
                bpm_fft = "N/A" if tracker.bpm_fft is None else str(round(tracker.bpm_fft, 2))

                self.chart_dictionary[tracker.name]["fig"].suptitle("{} BPM(pk-pk) {}. BPM(fft) {}".format(
                    tracker.name, bpm_pk, bpm_fft), fontsize=14)

                self.chart_dictionary[tracker.name]["ax"][0].plot(
                    tracker.time_period,
                    tracker.raw_amplitude,
                    label='Dimension changes - raw data')

                if tracker.de_trended_amplitude is not None:
                    self.chart_dictionary[tracker.name]["ax"][0].plot(
                        tracker.time_period,
                        tracker.de_trended_amplitude,
                        label='Dimension changes - de-trended',
                        color=(0.0, 1.0, 0.0))

                self.chart_dictionary[tracker.name]["ax"][0].legend(loc='best')

                self.chart_dictionary[tracker.name]["ax"][1].plot(
                    tracker.time_period,
                    tracker.filtered_amplitude,
                    color=(1.0, 0.0, 0.0),
                    label='Dimension changes - filtered')

                if tracker.peaks_positive_amplitude is not None:
                    self.chart_dictionary[tracker.name]["ax"][1].plot(
                        tracker.time_period[tracker.peaks_positive_amplitude],
                        tracker.filtered_amplitude[tracker.peaks_positive_amplitude],
                        'ro', ms=3, label='Dimension - positive peaks',
                        color=(0.0, 0.0, 1.0))

                self.chart_dictionary[tracker.name]["ax"][1].legend(loc='best')

                if tracker.fft_frequency is not None:
                    chart_bar_width = (tracker.fft_frequency[len(tracker.fft_frequency) - 1] / (
                                len(tracker.fft_frequency) * 2))

                    self.chart_dictionary[tracker.name]["ax"][2].bar(tracker.fft_frequency, tracker.fft_amplitude,
                                                                color=(1.0, 0.0, 0.0), width=chart_bar_width,
                                                                label='Harmonics, (filtered data)')
                    self.chart_dictionary[tracker.name]["ax"][2].legend(loc='best')

            except IndexError:
                print("charting error " + tracker.name)
        else:
            self.chart_dictionary[tracker.name]["fig"].suptitle(tracker.name + " BPM - Not available"
                                                           , fontsize=14)

        plt.ion()
        plt.pause(0.00001)
        plt.show()

    def update_fft_composite_chart(self, data):
        """Update FFT Composite charts"""
        self.chart_dictionary[data['name']]["ax"][0].clear()
        self.chart_dictionary[data['name']]["ax"][1].clear()
        try:
            bpm_fft = "N/A" if data['bpm_fft'] is None else str(round(data['bpm_fft'], 2))

            self.chart_dictionary[data['name']]["fig"].suptitle("{} BPM(fft) {}".format(
                data['name'], bpm_fft), fontsize=14)

            if ('x_frequency1' in data and data['x_frequency1'] is not None) and \
                    ('x_frequency2' in data and data['x_frequency2'] is not None ):

                chart_bar_width = np.min(np.diff(data['x_frequency1'])) / 3

                self.chart_dictionary[data['name']]["ax"][0].bar(data['x_frequency1']-chart_bar_width, data['y_frequency1'],
                                                            color = (0.0, 0.0, 1.0), width=chart_bar_width,
                                                            label = data['fft_name1'])
                self.chart_dictionary[data['name']]["ax"][0].legend(loc = 'best')

                self.chart_dictionary[data['name']]["ax"][0].bar(data['x_frequency2'], data['y_frequency2'],
                                                                 color = (0.0, 1.0, 0.0), width=chart_bar_width,
                                                                 label = data['fft_name2'])
                self.chart_dictionary[data['name']]["ax"][0].legend(loc = 'best')

            if 'x_frequency_sum_fft' in data and data['x_frequency_sum_fft'] is not None:
                chart_bar_width = np.min(np.diff(data['x_frequency_sum_fft'])) / 2

                self.chart_dictionary[data['name']]["ax"][1].bar(data['x_frequency_sum_fft'], data['y_frequency_sum_fft'],
                                                                 color=(1.0, 0.0, 0.0), width=chart_bar_width,
                                                                 label='Arithmetic sum of harmonics')
                self.chart_dictionary[data['name']]["ax"][1].legend(loc='best')

        except IndexError:
            print("charting error " + data['name'])

        plt.ion()
        plt.pause(0.00001)
        plt.show()

    def update_correlated_composite_chart(self, data):
        """Update FFT Composite charts"""
        self.chart_dictionary[data['name']]["ax"][0].clear()
        self.chart_dictionary[data['name']]["ax"][1].clear()
        try:
            bpm_pk = "N/A" if data['bpm_from_correlated_peaks'] is None else str(round(data['bpm_from_correlated_peaks'], 2))
            bpm_fft = "N/A" if data['bpm_from_correlated_fft'] is None else str(round(data['bpm_from_correlated_fft'], 2))

            self.chart_dictionary[data['name']]["fig"].suptitle("{} BPM(pk-pk) {}. BPM(fft) {}".format(
                data['name'], bpm_pk, bpm_fft), fontsize=14)

            if 'correlated_y1_amplitude' in data and data['correlated_y1_amplitude'] is not None:
                self.chart_dictionary[data['name']]["ax"][0].plot(data['correlated_x_time'],
                                                                  data['correlated_y1_amplitude'],
                                                                  color=(0.0, 1.0, 0.0),
                                                                  label = 'Y1 (filtered')

            if 'correlated_y2_amplitude' in data and data['correlated_y2_amplitude'] is not None:
                self.chart_dictionary[data['name']]["ax"][0].plot(data['correlated_x_time'],
                                                                  data['correlated_y2_amplitude'],
                                                                  color=(0.0, 1.0, 1.0),
                                                                  label = 'Y2 (filtered')

            if 'correlated_amplitude' in data and data['correlated_amplitude'] is not None:
                self.chart_dictionary[data['name']]["ax"][0].plot(data['correlated_x_time'],
                                                                  data['correlated_amplitude'],
                                                                  color=(1.0, 0.0, 0.0),
                                                                  label = 'Sum of correlated series')

            if 'correlated_peaks_positive' in data and data['correlated_peaks_positive'] is not None:
                self.chart_dictionary[data['name']]["ax"][0].\
                    plot(data['correlated_x_time'][data['correlated_peaks_positive']],
                         data['correlated_amplitude'][data['correlated_peaks_positive']],
                         'ro', ms=3, label='positive peaks',
                         color=(0.0, 0.0, 1.0))

                self.chart_dictionary[data['name']]["ax"][0].legend(loc = 'best')

            if 'correlated_fft_frequency' in data and data['correlated_fft_frequency'] is not None:
                chart_bar_width = np.min(np.diff(data['correlated_fft_frequency'])) / 2

                self.chart_dictionary[data['name']]["ax"][1].bar(data['correlated_fft_frequency'],
                                                                 data['correlated_fft_amplitude'],
                                                                 color=(1.0, 0.0, 0.0), width=chart_bar_width,
                                                                 label='Sum of correlated signals - harmonics')
                self.chart_dictionary[data['name']]["ax"][1].legend(loc='best')

        except IndexError:
            print("charting error " + data['name'])

        plt.ion()
        plt.pause(0.00001)
        plt.show()

