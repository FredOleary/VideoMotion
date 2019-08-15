from scipy.signal import butter, lfilter
import scipy.io

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y


def run():
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.signal import freqz

    # Sample rate and desired cutoff frequencies (in Hz).
    fs = 12.0 # assuming 30 fps
    lowcut = 60.0/60    #60bpm
    highcut = 100/60    #100bpm

    # Plot the frequency response for a few different orders.
    plt.figure(1)
    plt.clf()
    for order in [3, 6, 9]:
        b, a = butter_bandpass(lowcut, highcut, fs, order=order)
        w, h = freqz(b, a, worN=2000)
        plt.plot((fs * 0.5 / np.pi) * w, abs(h), label="order = %d" % order)

    plt.plot([0, 0.5 * fs], [np.sqrt(0.5), np.sqrt(0.5)],
             '--', label='sqrt(0.5)')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Gain')
    plt.grid(True)
    plt.legend(loc='best')

    #Load sample signal
    data_set = scipy.io.loadmat('Pulse_X')
    t = data_set['x'][0]
    x = data_set['y'][0]

    f0 = 70.0/60

    T = t[t.size-1]
    a = 0.02

    plt.figure(2)
    plt.clf()
    plt.plot(t, x, label='Noisy signal')

    y = butter_bandpass_filter(x, lowcut, highcut, fs, order=6)

    #find peaks
    peaks_positive, _ = scipy.signal.find_peaks(y, height=.5, threshold=None)

    time_intervals = np.average(np.diff(peaks_positive))
    per_beat_in_seconds = time_intervals * t[1]-t[0]

    beats_per_minute = 1/per_beat_in_seconds *60
    print("beats_per_minute: ", str(beats_per_minute))
    plt.plot(t, y, label='Filtered signal (%g Hz)' % f0)

    plt.plot(t[peaks_positive], y[peaks_positive], 'ro', ms=3, label='positive peaks + (' + str(round(beats_per_minute,2)) + ') BPM')

    plt.xlabel('time (seconds)')
    plt.hlines([-a, a], 0, T, linestyles='--')
    plt.grid(True)
    plt.axis('tight')
    plt.legend(loc='upper left')

    plt.show()


run()