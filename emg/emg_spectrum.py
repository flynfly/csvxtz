# coding=utf-8
"""

Author:Jayleen
Date:2023/3/27 16:48
Desc:
"""
import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import welch, periodogram
from statsmodels.regression import yule_walker
from statsmodels.regression.linear_model import burg

from signal.signal_utils import signal_window_overlap


def emg_spectrum(epoch, sampling_rate, p, method, ar_method="burg",
                 window_length=0.256, window_overlap=0.5, show=True):
    N, step = signal_window_overlap(window_length=window_length,
                                    window_overlap=window_overlap,
                                    sampling_rate=sampling_rate)

    if method in ["AR", "ar"]:
        result = _emg_spectrum_ar_psd(epoch, p, ar_method=ar_method)
    elif method in ["MA", "ma"]:
        result = _emg_spectrum_ma_psd(epoch, p)
    elif method in ["ARMA", "ARMA"]:
        result = _emg_spectrum_arma_psd(epoch, p)
    elif method in ["welch"]:
        result = emg_classic_psd(epoch, sampling_rate, psd_method='welch', N=N, step=step)
    elif method in ["periodogram"]:
        result = emg_classic_psd(epoch, sampling_rate, psd_method='periodogram', N=N, step=step)
    else:
        raise TypeError("method' should be one of the 'ARMA','AR','welch',...")

    if show is True:
        _emg_spectrum_plot(result, method)

    return result


def _emg_spectrum_ar_psd(epoch, p, ar_method):
    """
    AR模型估计PSD
    """
    if ar_method in ["yule","yule_walker"]:
        rho, sigma2 = yule_walker(epoch, order=p, method="adjusted", df=None, inv=False,
                              demean=True)
    elif ar_method in ["burg","Burg"]:
        rho,sigma2 = burg(epoch,p,demean=True)

    # 计算 freqs
    freqs, _ = welch(epoch, fs=1000, window='hann', nperseg=256, noverlap=128, return_onesided=True, axis=0)

    # 根据AR参数计算PSD
    ar_psd = _ar_psd(freqs, rho, sigma2)

    return ar_psd


def _emg_spectrum_ma_psd(epoch,p):
    pass

def _emg_spectrum_arma_psd(epoch,p):
    pass


def _ar_psd(freqs, ar_params, sigma2):
    """
    根据计算的AR系数估计PSD
    """
    p = len(ar_params)
    a = np.r_[1, -ar_params]  # 转换 AR 参数
    freqs_2d = freqs[:, np.newaxis]  # 将频率向量转换为 2D 数组，以便进行外积运算
    # w = 2 * np.pi * freqs_2d / 1000
    # 根据公式实现基于自回归的功率谱
    denominator = np.abs(1 + np.sum(a * np.exp(-1j * 2 * np.pi * freqs_2d * np.arange(p + 1)), axis=1)) ** 2
    return sigma2 / denominator


def emg_classic_psd(epoch, sampling_rate, psd_method, N, step):
    """
    选择经典谱估计方法
    """
    f, Pxx = None, None

    if psd_method in ["welch", "pwelch"]:
        f, Pxx = welch(epoch, fs=sampling_rate, window='hann', nperseg=N, noverlap=step, axis=0)
    elif psd_method in ["periodogram"]:
        f, Pxx = periodogram(epoch, fs=sampling_rate, window='boxcar', nfft=None, detrend='constant',
                             return_onesided=True, scaling='density', axis=-1)
    elif psd_method in ["AR", "ar"]:
        pass
    else:
        raise TypeError('Unknown value for choosing classic psd approximation method')

    # 调整了scipy的输出，与 matlab pwelch结果保持一致
    Pxx_adjust = Pxx * 256 * np.sum(np.hanning(256) ** 2) / 1000

    return f, Pxx_adjust


def _emg_spectrum_plot(epoch, method):
    pass


if __name__ == '__main__':
    from data.load_emg_data import load_emg_data
    from signal.signal_utils import signal_epoch

    data = load_emg_data()
    data = data * 10e3  # un

    epoch = signal_epoch(data[:,0], 0, data.shape[0])
    result = emg_spectrum(epoch, sampling_rate=2000, p=10, method="periodogram", ar_method="burg",
                 window_length=0.256, window_overlap=0.5, show=True)
    plt.plot(result)