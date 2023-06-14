# coding=utf-8
"""

Author:Jayleen
Date:2023/3/15 15:07
Desc: EMG 频域分析
"""
import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from statsmodels.regression import yule_walker
from statsmodels.tsa.ar_model import AutoReg
from tabulate import tabulate

from emg.emg_spectrum import emg_classic_psd
from Mysignal.signal_utils import signal_window_overlap, _signal_plot_line
from scipy.signal import welch

matplotlib.use('TkAgg')


def emg_frequency(epoch,
                  method,
                  window_length=0.1,
                  window_overlap=0.,
                  psd_method="welch",
                  sampling_rate=2000,
                  cutoff=75,
                  binsize=10,
                  p=10,
                  show=False):
    N, step = signal_window_overlap(window_length=window_length,
                                    window_overlap=window_overlap,
                                    sampling_rate=sampling_rate)

    if method in ["MDF", "mdf"]:
        result = _emg_frequency_mdf(epoch, sampling_rate, N, step, psd_method, method, show)
    elif method in ["MNF", "mnf"]:
        result = _emg_frequency_mnf(epoch, sampling_rate, N, step, psd_method, method, show)
    elif method in ["HLR", "hlr"]:
        result = _emg_frequency_hlr(epoch, sampling_rate, N, step, cutoff, psd_method, method, show)
    elif method in ["PF", "pf"]:
        result = _emg_frequency_pf(epoch, sampling_rate, N, step, psd_method, method, show)
    elif method in ["BE", "be"]:
        result = _emg_frequency_BE(epoch, sampling_rate, N, step, psd_method, binsize, show)

    else:
        raise TypeError(
            " signal_filter(): 'method' should be one of the 'MDF','MNF',,..."
        )

    return result


def _emg_frequency_mdf(epoch, sampling_rate, N, step, psd_method="welch", method="MDF", show=True):
    """
    Median frequency
    计算中值频率
    """
    f, psd = emg_classic_psd(epoch, sampling_rate, psd_method, N, step)

    # 累加psd
    cumulative_power = np.cumsum(psd, axis=0)
    # 每个通道的中值频率
    half_power = np.sum(psd, axis=0) / 2
    # 搜索每个通道大于half_power的点返回index
    median_frequency_idx = np.argmax(cumulative_power >= half_power, axis=0)
    mdf = f[median_frequency_idx]

    if show is True:
        _signal_plot_line(f, psd, mdf, method)

    _emg_print_result(mdf)

    return mdf


def _emg_frequency_mnf(epoch, sampling_rate, N, step, psd_method="welch", method="MNF", show=True):
    """
    Mean frequency, central frequency
    计算平均功率，中心频率
    """
    f, psd = emg_classic_psd(epoch, sampling_rate, psd_method, N, step)

    # 广播机制进行计算
    mnf = np.sum(f[:, None] * psd, axis=0) / np.sum(psd, axis=0)

    if show is True:
        _signal_plot_line(f, psd, mnf, method)

    _emg_print_result(mnf)

    return mnf


def _emg_frequency_hlr(epoch, sampling_rate, N, step, cutoff, psd_method, method="HLR", show=True):
    """
    计算高频/低频成分的比值
    """
    f, psd = emg_classic_psd(epoch, sampling_rate, psd_method, N, step)

    cutoff_idx = np.argmax(f >= cutoff)

    hf = np.sum(psd[:cutoff_idx], axis=0)
    lf = np.sum(psd[cutoff_idx:], axis=0)

    hlr = hf / lf

    cutoff_arr = np.ones(epoch.shape[1]) * cutoff

    if show is True:
        _signal_plot_line(f, psd, cutoff_arr, method)

    _emg_print_result(hlr)

    return hlr


def _emg_frequency_pf(epoch, sampling_rate, N, step, psd_method, method="PF", show=True):
    """
    Peak Frequency 峰值频率
    功率谱密度中具有最大功率的频率，反映了信号中最显著的频率成分
    """
    f, psd = emg_classic_psd(epoch, sampling_rate, psd_method, N, step)

    pf_idx = np.argmax(f[:, None] * psd, axis=0)

    pf = f[pf_idx]
    _emg_print_result(pf)

    if show is True:
        _signal_plot_line(f, psd, pf, method)

    return pf


def _emg_frequency_BE(epoch, sampling_rate, N, step, psd_method, binsize, show):
    """
    Band Energy， 频带能量
    默认以10Hz为区间，计算一个区间内的功率, 绘制直方图
    """
    f, psd = welch(epoch, fs=sampling_rate, window='hann', nperseg=N, noverlap=step, axis=0)

    # 计算频带能量
    bin_edges = np.arange(0, np.max(f) + binsize, binsize)
    be = []
    for i in range(psd.shape[1]):
        # 频带能量（功率）等于将一个区间范围内psd求和
        be_channel, hist = np.histogram(f, bins=bin_edges, weights=psd[:, i])
        be.append(be_channel)

    be = np.array(be)

    if show is True:
        _emg_plot_hist(be, bin_edges)

    return be


# =============================================================================
# Utility
# =============================================================================


def _emg_print_result(values):
    """
    按通道打印相应频率点
    """
    data = values.flatten()
    headers = [f"Chan {i + 1}" for i in range(len(data))]
    print(tabulate([data], headers=headers, tablefmt="grid"))


def _emg_plot_hist(be, bin_edges):
    """
    绘制频带能量直方图
    """
    num_channels = be.shape[0]
    fig, axes = plt.subplots(num_channels, 1, figsize=(4, 1.5 * num_channels))

    freq_limit = 300
    bin_mask = bin_edges[:-1] < freq_limit

    for i, ax in enumerate(axes):
        ax.bar(bin_edges[:-1][bin_mask], be[i][bin_mask], width=np.diff(bin_edges)[bin_mask], edgecolor="black",
               align="edge")
        # ax.set_xlabel("Frequency (Hz)")
        # ax.set_ylabel("Band Energy")
        # ax.set_title(f"Channel {i + 1}")

    fig.suptitle("Band Energy")
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    from data.load_emg_data import load_emg_data
    from Mysignal.signal_utils import signal_epoch

    # data = load_emg_data() * 10e3
    # data = signal_epoch(data[:, 0], 0, data.shape[0])

    f1,f2,f3 = 150,200,250
    fs = 2000
    siglen = fs*1
    t = np.linspace(0,1,fs)
    x1 = np.sin(2*np.pi*f1*t)
    x2 = np.sin(2*np.pi*f2*t)
    x3 = np.sin(2*np.pi*f3*t)
    x = x1+x2+x3
    x = np.atleast_2d(x).reshape(-1, 1)
    # 默认窗大小为256，重叠0.5
    result = emg_frequency(x, method="mdf", window_length=0.256, window_overlap=0.5, cutoff=100, psd_method="welch",
                           sampling_rate=fs, show=True)

