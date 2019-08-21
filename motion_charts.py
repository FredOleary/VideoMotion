import matplotlib.pyplot as plt


class MotionCharts:
    def __init__(self):
        print("MotionCharts:__init__ ")
        self.charts = {"X": self.create_chart('X') }

        # self.charts = {"X": self.create_chart('X'),
        #                "Y": self.create_chart('Y'),
        #                "W": self.create_chart('W'),
        #                "H": self.create_chart('H')
        #                }

    def create_chart(self, dimension):
        fig, ax = plt.subplots(2, 1)
        fig.suptitle(dimension + " Dimension BPM N/A", fontsize=14)
        ax[0].set_xlabel('Time')
        ax[0].set_ylabel('Amplitude - Unfiltered ' + dimension)

        ax[1].set_xlabel('Pulse (BMP) N/A')
        ax[1].set_ylabel('Amplitude - filtered ' + dimension)
        return {"fig":fig, "ax":ax}

    def update(self, data):
        self.charts[data['dimension']]["ax"][0].clear()
        self.charts[data['dimension']]["ax"][1].clear()
        self.charts[data['dimension']]["fig"].suptitle(data['dimension'] + " Dimension BPM " +
                                                     str(round(data['beats_per_minute'], 2)), fontsize=14)
        self.charts[data['dimension']]["ax"][0].plot(data['x_time'], data['y_amplitude'])
        self.charts[data['dimension']]["ax"][1].plot(data['x_time'], data['y_amplitude_filtered'],
                                                     color=(1.0, 0.0, 0.0))
        self.charts[data['dimension']]["ax"][1].plot(data['x_time'][data['peaks_positive']],
                                                      data['y_amplitude_filtered'][data['peaks_positive']],
                                                     'ro', ms = 3, label = 'positive peaks',
                                                     color = (0.0, 0.0, 1.0))
        plt.ion()
        plt.pause(0.00001)
        plt.show()

