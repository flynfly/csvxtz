# coding:utf-8
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
import appliedUI

from PyQt5 import QtCore, QtGui,QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import requests
from scipy.fftpack import fft, fftshift, ifft
from scipy.fftpack import fftfreq
from scipy import signal



#创建一个matplotlib图形绘制类
class MyFigure(FigureCanvas):
    def __init__(self,width=10, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        super(MyFigure,self).__init__(self.fig)
        self.axe=self.fig.add_subplot
        # self.fig.tight_layout()





class MainWin(QMainWindow):
    dir_name = ""
    samp_freq = 1259.259  # 采样率
    fft_num=0
    
    def __init__(self, parent=None):
        super(QtWidgets.QMainWindow, self).__init__(parent)
        self.ui = appliedUI.Ui_mainWindow()
        self.ui.setupUi(self)

        self.F0 = MyFigure(width=6, height=4, dpi=100   )

        for i in range(1,11):
            self.F0.axe(10,1,i).set_title("channel %d"%i)
            # self.F0.fig.tight_layout()
        self.gridlayout = QGridLayout(self.ui.groupBox)  # 继承容器groupBox
        self.gridlayout.addWidget(self.F0, 0, 1)


    def plottingEMG(self,tempcsv):

        self.F = MyFigure(width=3, height=2, dpi=100)
        for i in range(1,11):
            self.F.axe(10, 1, i).set_title("channel %d" % i)
            self.F.axe(10,1,i).plot(tempcsv["X [s]"], 1000 * tempcsv["Avanti sensor %d: EMG %d [V]" % (i, i)])
            # self.F.fig.tight_layout()

        self.gridlayout.addWidget(self.F, 0, 1)

    def delImage(self):
        self.gridlayout.addWidget(self.F0, 0, 1)

    def openfile(self):

        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*);;csv Data (*.csv)", options=options)
        if file_name:
            print("选择的数据文件："+file_name)
            self.showplot(file_name)
            self.ui.listWidget.addItem(file_name)
        else:
            print("未选择")
            self.delImage()

    def showplot(self,filename):
        raw = pd.read_csv(filename, encoding="unicode_escape", header=494)[["X [s]",
                                                                             "Avanti sensor 1: EMG 1 [V]",
                                                                             "Avanti sensor 2: EMG 2 [V]",
                                                                             "Avanti sensor 3: EMG 3 [V]",
                                                                             "Avanti sensor 4: EMG 4 [V]",
                                                                             "Avanti sensor 5: EMG 5 [V]",
                                                                             "Avanti sensor 6: EMG 6 [V]",
                                                                             "Avanti sensor 7: EMG 7 [V]",
                                                                             "Avanti sensor 8: EMG 8 [V]",
                                                                             "Avanti sensor 9: EMG 9 [V]",
                                                                             "Avanti sensor 10: EMG 10 [V]"]]
        self.plottingEMG(raw)

        dirpos = filename.rfind('/')
        self.dir_name = filename[:dirpos + 1]
        raw.to_csv(self.dir_name + "csvtemp.csv")

        print("show over")



    def bandpassfiltAndShow(self):
        items1 = ('20', '50', '100')
        items2 = ('200', '500', '1000')
        item1, ok1 = QInputDialog.getItem(self, "滤波参数", '截止频率1', items1, 0, False)
        item2, ok2 = QInputDialog.getItem(self, "滤波参数", '截止频率2', items2, 0, False)
        if ok1 and ok2 and item1 and item2:
            f1 = int(item1)
            f2 = int(item2)
        raw = pd.read_csv(self.dir_name + "csvtemp.csv", encoding="unicode_escape", header=0)

        w1 = 2 * f1 / self.samp_freq
        w2 = 2 * f2 / self.samp_freq
        b, a = signal.butter(8, [w1, w2], 'bandpass')  # 配置滤波器 8 表示滤波器的阶数
        for i in range(1, 10):
            raw["Avanti sensor %d: EMG %d [V]" % (i, i)] = signal.filtfilt(b, a,
                                                                           raw["Avanti sensor %d: EMG %d [V]" % (i, i)])

        self.plottingEMG(raw)

    def dirrect_power(self):
        ss0 = pd.read_csv(self.dir_name + "fftdata.csv")
        ss = ss0.to_numpy()

        ps = np.zeros((self.fft_num, 10))
        self.F = MyFigure(width=3, height=2, dpi=100)
        for i in range(1, 11):
            ps[:, i - 1] = ss[:, i] ** 2 / self.fft_num
            self.F.axe(10, 1, i).set_title("channel %d" % i)
            self.F.axe(10, 1, i).plot(20 * np.log10(ps[:self.fft_num // 2, i - 1]))

        self.gridlayout.addWidget(self.F, 0, 1)

    def cor_power(self):
        data = pd.read_csv(self.dir_name + "csvtemp.csv")
        npdata = data.to_numpy()

        cor_x=cor_X=ps_cor = np.zeros((self.fft_num, 10))
        self.F = MyFigure(width=3, height=2, dpi=100)
        for i in range(1, 11):
            cor_x[:, i - 1] = np.correlate(npdata[:, i + 1], npdata[:, i + 1], 'same')
            cor_X[:, i - 1] = fft(cor_x[:, i - 1], self.fft_num)
            ps_cor[:, i - 1] = np.abs(cor_X[:, i - 1])
            ps_cor[:, i - 1] = ps_cor[:, i - 1] / np.max(ps_cor[:, i - 1])
            self.F.axe(10, 1, i).set_title("channel %d" % i)
            self.F.axe(10, 1, i).plot(20 * np.log10(ps_cor[:self.fft_num // 2],i-1))
        self.gridlayout.addWidget(self.F, 0, 1)

    def cut_data(self):
        low_0=min(self.ui.horizontalSlider.value(),self.ui.horizontalSlider_2.value())
        hign_99=max(self.ui.horizontalSlider.value(),self.ui.horizontalSlider_2.value())
        raw = pd.read_csv(self.dir_name + "csvtemp.csv")
        total_size=raw.shape[0]
        cut=raw.loc[int(total_size*low_0/99):int(total_size*hign_99/99),:]

        cut.to_csv(self.dir_name + "cuttemp.csv")
        print("done")
        self.plottingEMG(cut)

    def fft_data(self):
        items = ('200', '500', '1000')
        item, ok = QInputDialog.getItem(self, "FFT参数", '点数', items, 0, False)
        if ok and item:
            self.fft_num=int(item)

        data = pd.read_csv(self.dir_name + "csvtemp.csv")
        npdata = data.to_numpy()

        ss = np.zeros((self.fft_num, 10))
        self.F = MyFigure(width=3, height=2, dpi=100)
        for i in range(1, 11):
            ss[:, i - 1] = fft(npdata[:, i+1], self.fft_num)
            ss[:, i - 1] = np.abs(ss[:, i - 1])
            self.F.axe(10, 1, i).set_title("channel %d" % i)
            self.F.axe(10, 1, i).plot(20 * np.log10(ss[:self.fft_num // 2, i - 1]))

        self.gridlayout.addWidget(self.F, 0, 1)
        pd.DataFrame(ss).to_csv(self.dir_name + "fftdata.csv")

    def on_listWidgetItemDoubleClicked(self, item):
        print("Double clicked item:", item.text())
        self.showplot(item.text())

def main():
    myapp = QApplication(sys.argv)
    myDlg = MainWin()
    myDlg.show()
    sys.exit(myapp.exec_())

if __name__=='__main__':
    main()

