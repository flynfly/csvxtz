# coding=utf-8
"""

Author:Jayleen
Date:2023/3/8 9:34
Desc: signal filter
"""
import matplotlib
import numpy as np
import scipy
from matplotlib import pyplot as plt

matplotlib.use('TKAgg')
from scipy.signal import filtfilt, iirnotch, freqz


def signal_filter(signal, sampling_rate=1000, lowcut=None, highcut=None, method='',
                  order=2, numtaps=81, window_type='hamming',show=False, f0=50, Q=45, freqz=False):
    """
    Filter the input signal using the specified method and parameters.

    Parameters
    ----------
    signal : ndarray
        Input signal to be filtered.
    sampling_rate : int, optional
        The sampling rate of the signal in Hz, default is 1000 Hz.
    lowcut : float, optional
        The lower cutoff frequency for the filter, default is None (no lowcut).
    highcut : float, optional
        The higher cutoff frequency for the filter, default is None (no highcut).
    method : str, optional
        The filtering method to use, options include 'iir', 'fir', 'iirnotch', etc., default is an empty string.
    order : int, optional
        The order of the filter, default is 2.
    numtaps : int, optional
        The number of filter taps for FIR filters, default is 81.
    window_type : str, optional
        The type of window to use for FIR filters, default is 'hamming'.
    show : bool, optional
        If True, plot the filtered signal, default is False (no plot).
    f0 : int, optional
        The frequency for the notch filter, default is 50 Hz.
    Q : int, optional
        The quality factor for the notch filter, default is 45.
    freqz : bool, optional
        If True, plot the frequency response and phase response, default is False (no plot).

    Returns
    -------
    filtered : ndarray
        The filtered signal using the specified method and parameters.
    """
    method = method.lower()  # 将 method str 转成小写

    if method in ['butter', 'butterworth']:
        filtered = _signal_filter_butterworth(signal, sampling_rate, lowcut, highcut, order,freqz)
    elif method in ['butter_ba', 'butterworth_ba']:
        filtered = _signal_filter_butterworth_ba(signal, sampling_rate, lowcut, highcut, order, freqz)
    elif method in ['fir']:
        filtered = _signal_filter_fir(signal, sampling_rate, lowcut, highcut, numtaps, window_type,freqz=False)
    elif method in ['iirnotch']:
        filtered = _signal_filter_iirnotch(signal, sampling_rate, f0, Q, freqz)

    else:
        raise ValueError(
            "ERROR: signal_filter():'method' should be one of 'butterworth',"
            "'butterworth_ba', 'fir' or 'powerline'"
        )

    if show is True:
        _signal_filtered_plot(signal, filtered)

    return filtered


# =============================================================================
# Powerline
# =============================================================================

def _signal_filter_powerline(signal, sampling_rate, powerline=50):
    """ remove powerline 去除 50Hz 工频干扰 """
    # TODO : 检查滤波效果
    if sampling_rate >= 100:
        b = np.ones(int(sampling_rate / powerline))
    else:
        b = np.ones(2)

    a = [len(b)]
    filtered = filtfilt(b, a, signal, method="gust")
    return filtered


# =============================================================================
# iirnotch
# =============================================================================

def _signal_filter_iirnotch(signal, sampling_rate, f0, Q, freqz=False):
    """
    Apply a second-order narrow bandwidth notch filter to the input signal.

    Parameters
    ----------
    signal : ndarray
        Input signal to be filtered, with dtype float64.
    sampling_rate : int
        The sampling rate of the signal in Hz.
    f0 : int
        The frequency to be removed (notch frequency) from the signal.
    Q : int
        The quality factor of the notch filter, representing the bandwidth.
        45/55/65 recommended

    Returns
    -------
    filtered : ndarray
        The signal after applying the notch filter.

    Optional
    --------
    freqz : bool, default=False
        If True, plot the frequency response of the filter.
    """
    w0 = f0 / (sampling_rate / 2)  # normalized sampling frequency
    b, a = iirnotch(w0, Q, sampling_rate)

    if freqz is True:
        _signal_filter_freqz(b, a)

    filtered = filtfilt(b, a, signal, axis=-1)

    return filtered


# =============================================================================
# IIR Filter : Butterworth
# =============================================================================

def _signal_filter_butterworth(signal, sampling_rate, lowcut, highcut, order=4,freqz=False):
    """ 默认 4阶 butterworth 滤波 """
    freqs, filter_type = _signal_filter_sanitize(lowcut, highcut, sampling_rate, normalize=False)
    sos = scipy.signal.butter(order, freqs, btype=filter_type, output='sos', fs=sampling_rate)

    if freqz is True:
        _signal_filter_freqz(b_fir=sos)

    filtered = scipy.signal.sosfiltfilt(sos, signal, padtype=None)  # TODO : change padtype
    return filtered


def _signal_filter_butterworth_ba(signal, sampling_rate, lowcut, highcut, order, freqz=False):
    """ 通过 b a 计算 butterworth 滤波参数进行滤波 """
    freqs, filter_type = _signal_filter_sanitize(lowcut, highcut, sampling_rate, normalize=False)
    b, a = scipy.signal.butter(order, freqs, btype=filter_type, output='ba', fs=sampling_rate)

    if freqz is True:
        _signal_filter_freqz(b, a)

    filtered = filtfilt(b, a, signal, method='gust', axis=1)
    return filtered


# =============================================================================
# Fir Filter
# =============================================================================

def _signal_filter_fir(signal, sampling_rate, lowcut, highcut, numtaps, window_type='hamming', freqz=False):
    """ Filter a signal using a FIR filter. """

    freqs, filter_type = _signal_filter_sanitize(lowcut, highcut, sampling_rate, normalize=False)

    cutoff = freqs / (sampling_rate / 2)
    taps = scipy.signal.firwin(numtaps, cutoff=cutoff, window=window_type, pass_zero=False)

    if freqz is True:
        _signal_filter_freqz(b_fir=taps)

    filtered = scipy.signal.filtfilt(taps, a=1, x=signal, method='gust')

    return filtered


# =============================================================================
# Utility
# =============================================================================

def _signal_filter_sanitize(lowcut=None, highcut=None, sampling_rate=1000, normalize=False):
    nyq = sampling_rate / 2
    # 检查 lowcut 和 highcut 是否满足奈奎斯特定律, 且转化为归一化频率
    if lowcut is not None and highcut is not None:
        if sampling_rate < 2 * np.nanmax(np.array([lowcut, highcut], dtype=np.float64)):
            raise ValueError(
                "Digital filter critical frequencies "
                "must be 0 < Wn < fs/2 (fs={} -> fs/2={})".format(sampling_rate, nyq)
            )

    # 用 None 替代 lowcut 和 highcut
    if lowcut is not None and lowcut == 0:
        lowcut = None
    if highcut is not None and highcut == 0:
        highcut = None

    # 返回 bandstop bandpass lowpass highpass
    if lowcut is not None and highcut is not None:
        if lowcut > highcut:  # TODO: 为什么是大于
            filter_type = "bandstop"
        else:
            filter_type = "bandpass"
            freqs = np.sort([lowcut, highcut])

    elif lowcut is None and highcut > 0:
        # 低于截止频率的通过
        filter_type = "lowpass"
        freqs = [highcut]
    elif highcut is None and lowcut > 0:
        # 高于截止频率的通过
        filter_type = "highpass"
        freqs = [lowcut]

    return freqs, filter_type


def _signal_filter_freqz(b_iir=None, a_iir=None, b_fir=None, worN=512, fs=6.283185307179586):
    """ Show IIR and FIR filter frequency responses """

    fig, ax1 = plt.subplots(2, 1,figsize=(8, 6))
    fig.tight_layout()
    plt.suptitle('Digital filter frequency response')

    if b_iir is not None and a_iir is not None:
        # Compute frequency responses
        w_iir, h_iir = freqz(b_iir, a_iir, worN, fs=fs)
        # Plot IIR filter response
        ax1[0].plot(w_iir, 20 * np.log10(np.maximum(abs(h_iir), 1e-10)), 'b', label='IIR Filter')
        ax1[1].plot(w_iir, np.unwrap(np.angle(h_iir)) * 180 / np.pi, color='green')

    elif b_iir is not None:

        w_fir, h_fir = freqz(b_fir, worN, fs=fs)
        # Plot FIR filter response
        ax1[0].plot(w_fir, 20 * np.log10(np.maximum(abs(h_fir), 1e-10)), 'b', label='IIR Filter')
        ax1[0].plot(w_fir, 20 * np.log10(abs(h_fir)), 'b', label='IIR Filter')
        ax1[1].plot(w_fir, np.unwrap(np.angle(h_fir)) * 180 / np.pi, color='green')

    ax1[0].grid(True)
    ax1[0].set_title("Frequency Response")
    ax1[0].set_ylabel("Amplitude (dB)", color='blue')
    ax1[1].set_title("Angle Response")
    ax1[1].set_ylabel("Angle (degrees)", color='green')
    ax1[1].set_xlabel("Frequency (Hz)")
    ax1[1].grid(True)
    plt.show(block=True)


def _signal_filtered_plot(signal, filtered):
    """
    plot filtered data
    """
    if signal.shape[0] > 10000:
        signal_len = 10000
    else:
        signal_len = signal.shape[0]

    signal = np.atleast_2d(signal)
    num_channels = signal.shape[1]

    fig, axes = plt.subplots(num_channels, 1, figsize=(18, 6 * num_channels), sharex=True)

    if num_channels == 1:
        axes = [axes]

    for i, ax in enumerate(axes):
        ax.plot(signal[0:signal_len, i], color='b')
        ax.plot(filtered[0:signal_len, i], color='red', alpha=0.9)
        ax.set_title("EMG Channel {}".format(i + 1))

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    from data.load_emg_data import load_emg_data

    data = load_emg_data('emg')

    filtered = signal_filter(data, sampling_rate=1000, lowcut=2, highcut=250, method='butter_ba', order=4,
                             show=False, freqz=True)
