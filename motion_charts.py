import matplotlib.pyplot as plt


class MotionCharts:
    def __init__(self):
        print("MotionCharts:__init__ ")
        self.charts = None

    def initialize_charts(self):
        self.charts = {"X": self.create_time_chart('X'),
                       "Y": self.create_time_chart('Y'),
                       "W": self.create_time_chart('W'),
                       "H": self.create_time_chart('H')
                       }

    def initialize_time_test_chart(self, test):
        self.charts = {test: self.create_time_chart(test)}

    def create_time_chart(self, dimension):
        fig, ax = plt.subplots(2, 1)
        fig.suptitle(dimension + " Dimension " + dimension, fontsize=14)
        ax[0].set_xlabel('Time')
        ax[0].set_ylabel('Amplitude - Unfiltered ' + dimension)

        ax[1].set_xlabel('Pulse (BMP) N/A')
        ax[1].set_ylabel('Amplitude - filtered ' + dimension)
        return {"fig":fig, "ax":ax}

    def update_time_chart(self, data):
        self.charts[data['dimension']]["ax"][0].clear()
        self.charts[data['dimension']]["ax"][1].clear()
        if len(data['x_time']) > 0:
            self.charts[data['dimension']]["fig"].suptitle(data['dimension'] + " Dimension BPM - " +
                                                         str(round(data['beats_per_minute'], 2)), fontsize=14)
            self.charts[data['dimension']]["ax"][0].plot(data['x_time'], data['y_amplitude'])
            self.charts[data['dimension']]["ax"][1].plot(data['x_time'], data['y_amplitude_filtered'],
                                                         color=(1.0, 0.0, 0.0))
            self.charts[data['dimension']]["ax"][1].plot(data['x_time'][data['peaks_positive']],
                                                          data['y_amplitude_filtered'][data['peaks_positive']],
                                                         'ro', ms = 3, label = 'positive peaks',
                                                         color = (0.0, 0.0, 1.0))
        else:
            self.charts[data['dimension']]["fig"].suptitle(data['dimension'] + " Dimension BPM - Not available"
                                                           , fontsize=14)

        plt.ion()
        plt.pause(0.00001)
        plt.show()


    def initialize_fft_test_chart(self, test):
        self.charts = {test: self.create_fft_chart(test)}

    def create_fft_chart(self, dimension):
        fig, ax = plt.subplots(2, 1)
        fig.suptitle(dimension + " Dimension " + dimension, fontsize=14)
        ax[0].set_xlabel('Time')
        ax[0].set_ylabel('Amplitude ' + dimension)

        ax[1].set_xlabel('Pulse (BMP)')
        ax[1].set_ylabel('|Y(BMP)| ' + dimension)
        return {"fig":fig, "ax":ax}

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


    # @staticmethod
    # def show_fft_and_time(beats_per_minute, x_time, y_amplitude, y_amplitude_filtered,
    #                       peaks_positive, x_frequency, y_frequency, dimension):
    #     fig, ax = plt.subplots(3, 1)
    #     if len(x_time) > 0:
    #         fig.suptitle(dimension + " Dimension BPM " + str(round(beats_per_minute, 2)), fontsize=14)
    #         ax[0].plot(x_time, y_amplitude)
    #         ax[0].set_xlabel('Time')
    #         ax[0].set_ylabel('Amplitude - Unfiltered')
    #
    #         ax[1].plot(x_time, y_amplitude_filtered, color=(1.0, 0.0, 0.0))
    #         ax[1].plot(x_time[peaks_positive], y_amplitude_filtered[peaks_positive], 'ro', ms=3, label='positive peaks',
    #                    color=(0.0, 0.0, 1.0))
    #         ax[1].set_ylabel('Amplitude - filtered')
    #
    #         chart_bar_width = (x_frequency[len(x_frequency) - 1] / (len(x_frequency) * 2)) * 60
    #         ax[2].bar(x_frequency * 60, y_frequency, color=(1.0, 0.0, 0.0), width=chart_bar_width)
    #         ax[2].set_xlabel('Pulse (BMP)')
    #         ax[2].set_ylabel('|Y(BMP)|')
    #     else:
    #         fig.suptitle(dimension + " Dimension - No data available", fontsize=14)
