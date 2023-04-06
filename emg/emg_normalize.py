# coding=utf-8
"""

Author:Jayleen
Date:2023/3/16 11:01
Desc: 幅度和时间标准化
"""
import numpy as np
from Mysignal.signal_utils import signal_epoch, signal_processed_plot, signal_window_overlap


def emg_normalized(epoch,
                   method="mvc",
                   window_length=0.1,
                   window_overlap=0.,
                   sampling_rate=1000,
                   zero_pad=False,
                   show=False):
    """

    Parameters
    ----------
    Mysignal : float32
        input multichannel Mysignal
    left  : int
        left index
    right : int
        right index
    method : str
        ["MVC","mvc","RVC","rvc","mv","PV"]
    window_length : float
        length of window
    window_overlap : float

    sampling_rate : int
    zero_pad : bool
    show : bool

    Returns
    -------
    normalized : float
        return normalized data
    """
    normalized = None

    N, step = signal_window_overlap(window_length=window_length,
                                    window_overlap=window_overlap,
                                    sampling_rate=sampling_rate)
    if method in ["MVC", "mvc", "mv"]:
        normalized = _emg_normalized_mvc(epoch)
    elif method in ["AVG", "avg", "mean"]:
        normalized = _emg_normalized_avg(epoch)
    # elif method in ["PV"]:
    #     normalized = _emg_normalized_pv(epoch, N, step)

    if show is True:
        signal_processed_plot(epoch)

    return normalized


# =============================================================================
# Normalization
# =============================================================================

def _emg_normalized_mvc(epoch):
    """
    对多通道 EMG 信号进行 MVC 标准化。
    前提 是输入信号是 "等长收缩信号段"取包络, 且计算多段数据的最大值求平均。
    """
    # Find the maximum value for each channel
    mvc = np.amax(epoch, axis=0)

    # Normalize the epoch by the maximum value
    normalized = epoch / mvc

    return normalized


def _emg_normalized_avg(epoch):
    """
    对多通道 EMG 信号进行平均值归一化
    """
    # Find the maximum value for each channel
    mean = np.mean(epoch, axis=0)

    #
    if np.all(np.equal(np.round(mean), 0)):
        print("The average of each channel of input Mysignal equals ZERO")
        normalized = epoch
    else:
        # Normalize the epoch by the maximum value
        normalized = epoch / mean

    return normalized


if __name__ == '__main__':
    from data.load_emg_data import load_emg_data

    import time

    data = load_emg_data()
    data = data * 10e3  # unit mV

    start = time.time()
    data = signal_epoch(data, left=0, right=data.shape[0])
    normalized = emg_normalized(data[:, :], method="avg",
                                window_length=0.5, window_overlap=0.1, show=False)

    end = time.time()

    print(end - start)
    print(normalized.shape)
