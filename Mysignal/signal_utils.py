# coding=utf-8
"""

Author:Jayleen
Date:2023/3/20 15:21
Desc:
"""
import numpy as np
from matplotlib import pyplot as plt


# =============================================================================
# Utility
# =============================================================================

def signal_epoch(signal, left, right):
    """
    extract emg epoch
    """
    signal = np.atleast_2d(signal).reshape(-1, 1) if (signal.ndim == 1) else np.atleast_2d(signal)

    return signal[left:right, :]


def signal_processed_plot(signal):
    """
    plot processed data
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
        ax.set_title("EMG Channel {}".format(i + 1))

    plt.tight_layout()
    plt.show()


def signal_window_overlap(window_length=0.25, window_overlap=None, sampling_rate=1000):
    """
    计算窗长，步长
    """
    N = int(window_length * sampling_rate)

    if window_overlap is None:
        step = N
    else:
        step = int(N - window_overlap * N)

    return N, step
