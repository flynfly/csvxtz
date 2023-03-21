# coding=utf-8
"""

Author:Jayleen
Date:2023/3/7 17:53
Desc: 肌电时域分析模块
"""
import numpy as np

from signal.signal_utils import signal_window_overlap, signal_processed_plot


def emg_amplitude(signal,
                  method,
                  window_length=0.1,
                  window_overlap=None,
                  sampling_rate=1000,
                  show=False):

    """
    Calculate the amplitude of multichannel EMG signals using the specified method.

    Parameters
    ----------
    signal : ndarray
        Multi-channel EMG signals as a 2D array (time x channels).
    method : str
        The method to compute the amplitude, options include 'RMS', 'MAV', etc.
    window_length : float, optional
        The length of the sliding window for calculating amplitude, default is 0.1.
        E.g. The length of window is 0.1 * 1000 Hz = 100 ms
    window_overlap : float, optional
        The overlap between sliding windows as a fraction, default is None (no overlap).
    sampling_rate : int, optional
        The sampling rate of the EMG signals in Hz, default is 1000 Hz.
    show : bool, optional
        If True, plot the resulting amplitude values, default is False (no plot).

    Returns
    -------
    amplitude : ndarray
        The computed amplitude of the EMG signals using the specified method.

    """

    N, step = signal_window_overlap(window_length=window_length,
                                    window_overlap=window_overlap,
                                    sampling_rate=sampling_rate)

    if method in ["RootMeanSquare", "RMS", "rms"]:
        result = _emg_amplitude_rms(signal, N, step)
    elif method in ["MeanAbsoluteValue", "MAV", "mav"]:
        result = _emg_amplitude_mav(signal, N, step)
    elif method in ["MovingAverage", "MV", "mv"]:
        result = _emg_amplitude_mv(signal, N, step)
    elif method in ["IEMG", "iemg"]:
        result = _emg_amplitude_iemg(signal, N)
    elif method in ["MAVS", "mavs"]:
        result = _emg_amplitude_mavs(signal, N, step)
    elif method in ["SSI", "ssi"]:
        result = _emg_amplitude_ssi(signal, N)
    elif method in ["ZC", "zc", "zcr"]:
        result = _emg_amplitude_zc(signal, N, step)

    elif method in ["VAR", "var"]:
        result = _emg_amplitude_var(signal, N, step)
    elif method in ["STD", "std"]:
        result = _emg_amplitude_std(signal, N, step)


    else:
        raise TypeError(
            " signal_filter(): 'method' should be one of the 'RMS','MAV',..."
        )

    if show is True:
        signal_processed_plot(result)

    return result


# =============================================================================
# Amplitude Calculation Scripts
# =============================================================================

def _emg_amplitude_rms(signal, N, step):
    """
    Root Mean Square
    """
    # Create a sliding window view of the epoch
    sliding_view = np.lib.stride_tricks.sliding_window_view(signal, window_shape=(N, 1), axis=(0, 1))[::step]

    # Calculate the square, mean, and square root for each window
    square = sliding_view ** 2
    mean = np.mean(square, axis=2)  # 对每个滑动窗求平均
    rms = np.sqrt(mean).reshape(-1, signal.shape[1])

    return rms


def _emg_amplitude_mav(signal, N, step):
    """
    Mean absolute value, 平均绝对值
    """
    sliding_view = np.lib.stride_tricks.sliding_window_view(signal, window_shape=(N, 1), axis=(0, 1))[::step]

    mav = np.mean(np.abs(sliding_view), axis=2)

    return mav


def _emg_amplitude_mv(signal, N, step):
    """
    Moving Average, 移动平均值
    """
    sliding_view = np.lib.stride_tricks.sliding_window_view(signal, window_shape=(N, 1), axis=(0, 1))[::step]
    mv = np.mean(sliding_view, axis=2).reshape(-1, signal.shape[1])

    return mv


def _emg_amplitude_mavs(signal, N, step):
    """
    mean absolute value slope (MAVS)

    ..math::
    M A V S_{i}=M A V_{i+1}-M A V
    """

    pass


def _emg_amplitude_ssi(signal, N):
    """
    Simple square integral, 简单平方积分
    """
    sliding_view = np.lib.stride_tricks.sliding_window_view(signal, window_shape=(N, 1), axis=(0, 1))[::N]
    square = sliding_view ** 2
    ssi = np.sum(square, axis=2).reshape(-1, signal.shape[1])

    return ssi


def _emg_amplitude_iemg(signal, N):
    """
    Integrate EMG (iEMG) ,default without overlapping window
    """
    # Create a sliding window view of the signal
    sliding_view = np.lib.stride_tricks.sliding_window_view(signal, window_shape=(N, 1), axis=(0, 1))[::N]

    # Calculate the absolute sum (integral) of each window
    iemg = np.sum(np.abs(sliding_view), axis=2).reshape(-1, signal.shape[1])

    return iemg


def _emg_amplitude_zc(signal, N, step):
    """
    Zero Crossing Rate (ZCR) 过零率
    """
    # Create a sliding window view
    sliding_view = np.lib.stride_tricks.sliding_window_view(signal, window_shape=(N, 1), axis=(0, 1))[::step]

    # Calculate the zero-crossing rate for each window
    zc = np.greater(np.multiply(sliding_view[:-1], sliding_view[1:]), 0).astype(int)
    zcr = (np.sum(zc, axis=2) / (N - 1)).reshape(-1, signal.shape[1])

    return zcr

# =============================================================================
# Sstatistics
# =============================================================================

def _emg_amplitude_std(signal, N, step=None):
    """
    standard deviation, 窗口默认不重叠
    """
    if step is None:
        step = N
    # Create a sliding window view of the signal
    sliding_view = np.lib.stride_tricks.sliding_window_view(signal, window_shape=(N, 1), axis=(0, 1))[::step]

    std = np.std(sliding_view, axis=2, ddof=1).reshape(-1, signal.shape[1])  # unbiased standard deviation

    return std


def _emg_amplitude_var(signal, N, step=None):
    """
    Unbiased Variance, 窗口默认不重叠
    """
    if step is None:
        step = N
    # Create a sliding window view of the signal
    sliding_view = np.lib.stride_tricks.sliding_window_view(signal, window_shape=(N, 1), axis=(0, 1))[::step]

    var = np.var(sliding_view, axis=2, ddof=1).reshape(-1, signal.shape[1])  # unbiased variance

    return var


if __name__ == '__main__':
    # 测试

    from data.load_emg_data import load_emg_data
    from signal.signal_utils import signal_epoch
    import time

    data = load_emg_data()
    data = data * 10e3  # unit mV

    start = time.time()

    epoch = signal_epoch(data, 0, data.shape[0])
    result = emg_amplitude(data, method="zc",
                           window_length=0.05, window_overlap=0.1,show=False)
    end = time.time()
    print(end - start)
    print(result.shape)
