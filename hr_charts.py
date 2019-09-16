import matplotlib.pyplot as plt
import numpy as np

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

    def update_chart(self, data):
        """Update amplitude vs time and FFT charts"""
        self.chart_dictionary[data['name']]["ax"][0].clear()
        self.chart_dictionary[data['name']]["ax"][1].clear()
        self.chart_dictionary[data['name']]["ax"][2].clear()
        if len(data['x_time']) > 0:
            try:
                bpm_pk = "N/A" if data['bpm_peaks'] is None else str(round(data['bpm_peaks'], 2))
                bpm_fft = "N/A" if data['bpm_fft'] is None else str(round(data['bpm_fft'], 2))

                self.chart_dictionary[data['name']]["fig"].suptitle("{} BPM(pk) {}. BPM(fft) {}".format(
                    data['name'], bpm_pk, bpm_fft), fontsize=14)

                self.chart_dictionary[data['name']]["ax"][0].plot(data['x_time'], data['y_amplitude'],
                                                             label='Motion change - raw data')
                if data['y_amplitude_detrended'] is not None:
                    self.chart_dictionary[data['name']]["ax"][0].plot(data['x_time'], data['y_amplitude_detrended'],
                                                                 label='Motion change - de-trended',
                                                                 color=(0.0, 1.0, 0.0))

                self.chart_dictionary[data['name']]["ax"][0].legend(loc='best')

                self.chart_dictionary[data['name']]["ax"][1].plot(data['x_time'], data['y_amplitude_filtered'],
                                                             color=(1.0, 0.0, 0.0), label='Motion change - filtered')
                if 'peaks_positive' in data and data['peaks_positive'] is not None:
                    self.chart_dictionary[data['name']]["ax"][1].plot(data['x_time'][data['peaks_positive']],
                                                                 data['y_amplitude_filtered'][data['peaks_positive']],
                                                                 'ro', ms=3, label='positive peaks',
                                                                 color=(0.0, 0.0, 1.0))
                self.chart_dictionary[data['name']]["ax"][1].legend(loc='best')

                if 'x_frequency' in data and data['x_frequency'] is not None:
                    chart_bar_width = (data['x_frequency'][len(data['x_frequency']) - 1] / (
                                len(data['x_frequency']) * 2))

                    self.chart_dictionary[data['name']]["ax"][2].bar(data['x_frequency'], data['y_frequency'],
                                                                color=(1.0, 0.0, 0.0), width=chart_bar_width,
                                                                label='harmonics, Filtered data')
                    self.chart_dictionary[data['name']]["ax"][2].legend(loc='best')

            except IndexError:
                print("charting error " + data['name'])
        else:
            self.chart_dictionary[data['name']]["fig"].suptitle(data['name'] + " BPM - Not available"
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

            if 'x_frequency_total' in data and data['x_frequency_total'] is not None:
                chart_bar_width = np.min(np.diff(data['x_frequency_total'])) / 2

                self.chart_dictionary[data['name']]["ax"][1].bar(data['x_frequency_total'], data['y_frequency_total'],
                                                                 color=(1.0, 0.0, 0.0), width=chart_bar_width,
                                                                 label='Total harmonics')
                self.chart_dictionary[data['name']]["ax"][1].legend(loc='best')

        except IndexError:
            print("charting error " + data['name'])

        plt.ion()
        plt.pause(0.00001)
        plt.show()

    # def initialize_fft_test_chart(self, test):
    #     self.charts = {test: self.create_fft_chart(test)}

    # @staticmethod
    # def create_fft_chart(dimension):
    #     fig, ax = plt.subplots(2, 1)
    #     fig.suptitle(dimension + " Dimension " + dimension, fontsize=14)
    #     ax[0].set_xlabel('Time')
    #     ax[0].set_ylabel('Amplitude ' + dimension)
    #
    #     ax[1].set_xlabel('Pulse (BMP)')
    #     ax[1].set_ylabel('|Y(BMP)| ' + dimension)
    #     return {"fig": fig, "ax": ax}

    # def update_fft_chart(self, data):
    #     self.charts[data['name']]["ax"][0].clear()
    #     self.charts[data['name']]["ax"][1].clear()
    #     self.charts[data['name']]["fig"].suptitle("FFT for " + data['name'], fontsize=14)
    #     self.charts[data['name']]["ax"][0].plot(data['x_time'], data['y_amplitude'])
    #
    #     chart_bar_width = (data['x_frequency'][len(data['x_frequency']) - 1] / (len(data['x_frequency']) * 2)) * 60
    #
    #     self.charts[data['name']]["ax"][1].bar(data['x_frequency']*60, data['y_frequency'],
    #                                                 color=(1.0, 0.0, 0.0), width=chart_bar_width)
    #     plt.ion()
    #     plt.pause(0.00001)
    #     plt.show()


