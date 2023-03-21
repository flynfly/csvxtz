# coding=utf-8
"""

Author:Jayleen
Date:2023/3/7 16:48
Desc: 加载 NinaPro DB2 数据集
"""

import os.path
from pprint import pprint
from scipy.io import loadmat
# from signal import signal_filter


def load_emg_data(
        datatype='emg'):
    """
    EMG signal from NinaPro dataset DB2

    Parameters
    ----------
    datatype : str
        default EMG

    Returns
    -------
    data : float32
        return 12-channels EMG data

    """
    datatype = datatype.lower()

    PROJECT_ROOT = os.path.dirname(os.path.realpath((__file__)))  # acquire project root
    data_path = os.path.join(PROJECT_ROOT, "S1_E3_A1.mat")
    data = loadmat(data_path)
    data = data[datatype]
    # TODO: using pd.DataFrame

    print("Loading data ...")
    print("data shape : {}".format(data.shape))
    # pprint(data)
    return data


if __name__ == '__main__':
    load_emg_data('emg')
    # data = np.load(r"E:\Users\dell\PycharmProjects\EMGLibrary\data\nptemp.npy")
    # savemat("../data/emg_test.mat", {"emg":data})