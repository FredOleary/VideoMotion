import matplotlib.pyplot as plt


class MotionCharts:
    """Charts showing results of motion analysis of video """
    def __init__(self):
        print("MotionCharts:__init__ ")
        self.charts = None

    def initialize_charts(self):
        self.charts = {"X": self.create_time_chart('X'),
                       "Y": self.create_time_chart('Y'),
                       "W": self.create_time_chart('W')
                       # "H": self.create_time_chart('H')
                       }

    def initialize_time_test_chart(self, test):
        self.charts = {test: self.create_time_chart(test)}

    @staticmethod
    def create_time_chart(dimension):
        """Shows three stacked charts. The top chart shows raw motion vs time.
        The middle chart shows filtered motion vs time. The bottom chart is an FFT of the filtered motion"""
        fig, ax = plt.subplots(3, 1)
        fig.suptitle(dimension + " Dimension " + dimension, fontsize=14)
        ax[0].set_xlabel('Time')
        ax[0].set_ylabel('Amplitude - Unfiltered ' + dimension)

        ax[1].set_xlabel('Pulse (BMP) N/A')
        ax[1].set_ylabel('Amplitude - filtered ' + dimension)

        ax[2].set_xlabel('Pulse (BMP)')
        ax[2].set_ylabel('|Y(BMP)| ' + dimension)

        return {"fig": fig, "ax": ax}

    def update_time_chart(self, data):
        """Update amplitude vs time and FFT charts"""
        self.charts[data['dimension']]["ax"][0].clear()
        self.charts[data['dimension']]["ax"][1].clear()
        self.charts[data['dimension']]["ax"][2].clear()
        if len(data['x_time']) > 0:
            try:
                self.charts[data['dimension']]["fig"].suptitle(data['dimension'] + " Dimension BPM - " +
                                                               str(round(data['beats_per_minute'], 2)), fontsize=14)

                self.charts[data['dimension']]["ax"][0].plot(data['x_time'], data['y_amplitude'],
                                                             label='Motion change - raw data')
                self.charts[data['dimension']]["ax"][0].plot(data['x_time'], data['y_amplitude_detrended'],
                                                             label='Motion change - detrended',
                                                             color=(0.0, 1.0, 0.0))

                self.charts[data['dimension']]["ax"][0].legend(loc='best')

                self.charts[data['dimension']]["ax"][1].plot(data['x_time'], data['y_amplitude_filtered'],
                                                             color=(1.0, 0.0, 0.0), label='Motion change - filtered')
                if 'peaks_positive' in data and data['peaks_positive'] is not None:
                    self.charts[data['dimension']]["ax"][1].plot(data['x_time'][data['peaks_positive']],
                                                                 data['y_amplitude_filtered'][data['peaks_positive']],
                                                                 'ro', ms=3, label='positive peaks',
                                                                 color=(0.0, 0.0, 1.0))
                self.charts[data['dimension']]["ax"][1].legend(loc='best')

                if 'x_frequency' in data and data['x_frequency'] is not None:
                    chart_bar_width = (data['x_frequency'][len(data['x_frequency']) - 1] / (
                                len(data['x_frequency']) * 2))

                    self.charts[data['dimension']]["ax"][2].bar(data['x_frequency'], data['y_frequency'],
                                                                color=(1.0, 0.0, 0.0), width=chart_bar_width,
                                                                label='harmonics, Filtered data')
                    self.charts[data['dimension']]["ax"][2].legend(loc='best')

            except IndexError:
                print("charting error " + data['dimension'])
        else:
            self.charts[data['dimension']]["fig"].suptitle(data['dimension'] + " Dimension BPM - Not available"
                                                           , fontsize=14)

        plt.ion()
        plt.pause(0.00001)
        plt.show()

    def initialize_fft_test_chart(self, test):
        self.charts = {test: self.create_fft_chart(test)}

    @staticmethod
    def create_fft_chart(dimension):
        fig, ax = plt.subplots(2, 1)
        fig.suptitle(dimension + " Dimension " + dimension, fontsize=14)
        ax[0].set_xlabel('Time')
        ax[0].set_ylabel('Amplitude ' + dimension)

        ax[1].set_xlabel('Pulse (BMP)')
        ax[1].set_ylabel('|Y(BMP)| ' + dimension)
        return {"fig": fig, "ax": ax}

    def update_fft_chart(self, data):
        self.charts[data['dimension']]["ax"][0].clear()
        self.charts[data['dimension']]["ax"][1].clear()
        self.charts[data['dimension']]["fig"].suptitle("FFT for " + data['dimension'], fontsize=14)
        self.charts[data['dimension']]["ax"][0].plot(data['x_time'], data['y_amplitude'])

        chart_bar_width = (data['x_frequency'][len(data['x_frequency']) - 1] / (len(data['x_frequency']) * 2)) * 60

        self.charts[data['dimension']]["ax"][1].bar(data['x_frequency']*60, data['y_frequency'],
                                                    color=(1.0, 0.0, 0.0), width=chart_bar_width)
        plt.ion()
        plt.pause(0.00001)
        plt.show()


