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


# =============================================================================
# plot
# =============================================================================

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

    fig, axes = plt.subplots(num_channels, 1, figsize=(12, 3 * num_channels), sharex=True)

    if num_channels == 1:
        axes = [axes]

    for i, ax in enumerate(axes):
        ax.plot(signal[0:signal_len, i], color='b')
        ax.set_title("EMG Channel {}".format(i + 1))

    plt.tight_layout()
    plt.show()


def _signal_plot_line(freqs, psd, values,method):
    """
    绘制功率谱及相应频率线
    """
    signal_len = psd.shape[0]
    num_channels = psd.shape[1]
    fig, axes = plt.subplots(num_channels, 1, figsize=(9, 4 * num_channels), squeeze=False)

    for i, ax in enumerate(axes[:, 0]):
        ax.plot(freqs,10*np.log10(psd[:,i]), color='b')
        ax.axvline(values[i], color='r', linestyle='--', label=f'{method} = {values[i]:.2f}')
        ax.set_ylabel("PSD (dB)",color='b')
        ax.set_xlabel("Frequency (Hz)")
        ax.set_title(f"EMG Channel {i + 1}")
        ax.legend()

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
