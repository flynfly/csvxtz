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


def signal_filter(signal, sampling_rate=1000, lowcut=None, highcut=None, method='', order=2, window_size='default',
                  powerline=50, show=False, f0=50, Q=45):
    """

    Parameters
    ----------
    signal : Union[list, np.array, pd]
        单通道信号
    sampling_rate : int
        采样率
    lowcut : float
        Lower cutoff frequency in Hz. The default is ``None``.
    highcut : float
        Upper cutoff frequency in Hz. The default is ``None``.
    method : str
        option ['butterworth', 'fir']
    order : int
        default order 2
    window_size : int
        Only used if ``method`` is ``"savgol"``. The length of the filter window (i.e. the number of
        coefficients). Must be an odd integer. If default, will be set to the sampling rate
        divided by 10 (101 if the sampling rate is 1000 Hz).
    powerline : int
        工频干扰
        only used if methond = 'powerline'
    show :  bool
        plot filtered data

    f0 : int
        only work when method = 'iirnotch'

    Q : int
        quality factor

    Returns
    -------
    filtered : float32

    Examples
    -------
        TODO ：添加使用example

    """
    method = method.lower()  # 将 method str 转成小写

    if method in ['powerline']:
        filtered = _signal_filter_powerline(signal, sampling_rate, powerline)

    else:
        if method in ['butter', 'butterworth']:
            filtered = _signal_filter_butterworth(signal, sampling_rate, lowcut, highcut, order)
        elif method in ['butter_ba', 'butterworth_ba']:
            filtered = _signal_filter_butterworth_ba(signal, sampling_rate, lowcut, highcut, order)
        elif method in ['fir']:
            filtered = _signal_filter_fir(signal, sampling_rate, lowcut, highcut, window_size='default')
        elif method in ['iirnotch']:
            filtered = _signal_filter_iirnotch(signal, sampling_rate, f0, Q)

        else:
            raise ValueError(
                "ERROR: signal_filter():'method' should be one of 'butterworth',"
                "'butterworth_ba', 'fir' or 'powerline'"
            )

    if show is True:
        if signal.shape[0] > 2000:
            signal_len = 2000
        else:
            signal_len = signal.shape[0]

        fig, axes = plt.subplots(signal.shape[1], 1)
        for i in range(0, signal.shape[1]):
            axes[i].plot(signal[0:signal_len, i], color='lightgrey')
            axes[i].plot(filtered[0:signal_len, i], color='blue', alpha=0.9)
            axes[i].set_title("EMG Channel {}".format(i + 1))
        plt.show(block=True)
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

def _signal_filter_iirnotch(signal, sampling_rate, f0, Q=45, frequency_response=False):
    """
    second order narrow bandwitch notch filter

    Parameters
    ----------
    signal : float 64
    sampling_rate : int
    f0 : int
        remove freq 待去除的频率
    Q : int
        quality,

    Returns
    -------
    filtered : float 64
        notch filtered data

    """
    w0 = f0 / (sampling_rate / 2)  # normalized sampling frequency
    b, a = iirnotch(w0, Q, sampling_rate)

    if frequency_response is True:
        _signal_filter_freqz(b, a)
        # os.system("pause")

    filtered = filtfilt(b, a, signal, axis=-1)

    return filtered


# =============================================================================
# Butterworth
# =============================================================================

def _signal_filter_butterworth(signal, sampling_rate, lowcut, highcut, order=4):
    """ 默认 4阶 butterworth 滤波 """
    freqs, filter_type = _signal_filter_sanitize(lowcut, highcut, sampling_rate, normalize=False)
    sos = scipy.signal.butter(order, freqs, btype=filter_type, output='sos', fs=sampling_rate)
    filtered = scipy.signal.sosfiltfilt(sos, signal, padtype=None) # TODO : change padtype
    return filtered


def _signal_filter_butterworth_ba(signal, sampling_rate, lowcut, highcut, order):
    """ 通过 b a 计算 butterworth 滤波 参数 """
    freqs, filter_type = _signal_filter_sanitize(lowcut, highcut, sampling_rate, normalize=False)
    b, a = scipy.signal.butter(order, freqs, btype=filter_type, output='ba', fs=sampling_rate)
    filtered = filtfilt(b, a, signal, method='gust', axis=1)
    return filtered


# =============================================================================
# fir filter
# =============================================================================

def _signal_filter_fir(signal, sampling_rate, lowcut, highcut, window_size='default'):
    """ Filter a signal using a FIR filter. """

    try:
        import mne
    except ImportError:
        raise ImportError(
            "Package error: signal_filter(): the 'mne' module is required for this method to run. ",
            "Please install it first (`pip install mne`).",
        )

    if isinstance(window_size, str):
        window_size = "auto"

    if signal.dtype != np.float64:
        signal = signal.astype(np.float64)

    # mne requires input data shape (n_chans, n_times)
    if signal.shape[0] > 256:
        signal = np.transpose(signal)

    filtered = mne.filter.filter_data(
        signal,
        sfreq=sampling_rate,
        l_freq=lowcut,
        h_freq=highcut,
        method="fir",
        fir_window="hamming",
        filter_length=window_size,
        l_trans_bandwidth="auto",
        h_trans_bandwidth="auto",
        phase="zero-double",
        fir_design="firwin",
        pad="reflect_limited",
        verbose=False,
    )

    filtered = np.transpose(filtered)
    print("filtered data shape: {}".format(filtered.shape))

    return filtered


# =============================================================================
# Utility
# =============================================================================

def _signal_filter_sanitize(lowcut=None, highcut=None, sampling_rate=1000, normalize=False):
    # 检查 lowcut 和 highcut 是否满足奈奎斯特定律
    if lowcut is not None and highcut is not None:
        if sampling_rate < 2 * np.nanmax(np.array([lowcut, highcut], dtype=np.float64)):
            raise ValueError(
                "Digital filter critical frequencies "
                "must be 0 < Wn < fs/2 (fs={} -> fs/2={})".format(sampling_rate, sampling_rate / 2)
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


def _signal_filter_freqz(b, a=1, worN=512, whole=False, plot=None, fs=6.283185307179586, include_nyquist=False):
    """ show filter frequency response """

    w, h = freqz(b, a, worN, fs=fs)
    fig, ax1 = plt.subplots()
    ax1.set_title('Digital filter frequency response')
    ax1.plot(w, 20 * np.log10(abs(h)), 'b')
    ax1.set_ylabel('Amplitude [dB]', color='b')
    ax1.set_xlabel('Frequency [rad/sample]')
    ax2 = ax1.twinx()
    angles = np.unwrap(np.angle(h))
    ax2.plot(w, angles, 'g')
    ax2.set_ylabel('Angle (radians)', color='g')
    ax2.grid(True)
    ax2.axis('tight')

    plt.show(block=True)


# if __name__ == '__main__':
#     from data.load_emg_data import load_emg_data
#
#     data = load_emg_data('emg')
#     filtered = signal_filter(data, sampling_rate=1000, lowcut=20, highcut=350, method='butter', order=4,
#                              powerline=50, show=True, f0=50, Q=45)

