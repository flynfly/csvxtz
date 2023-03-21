# coding:utf-8
#by：谢天哲
import shutil
import os
import numpy as np
import pandas as pd
import matplotlib
import scipy.io

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import sys
from UI import appliedUI,paraDialog

from PyQt5 import QtCore, QtGui,QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from scipy.fftpack import fft
from scipy import signal

from signal import signal_filter

matplotlib.use("Qt5Agg")  # 声明使用QT5

#创建一个matplotlib图形绘制类
class MyFigure(FigureCanvas):
    def __init__(self,width=10, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        super(MyFigure,self).__init__(self.fig)
        self.axe=self.fig.add_subplot
        # self.fig.tight_layout()


class Dialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = paraDialog.Ui_Dialog()
        self.ui.setupUi(self)

    def accept(self):
        # 在这里添加你的对话框的行为
        super().accept()


class MainWin(QMainWindow):
    dir_name = ""
    samp_freq = 1259.259  # 采样率
    fft_num=0
    channels=10
    flag=''
    
    def __init__(self, parent=None):
        super(QtWidgets.QMainWindow, self).__init__(parent)
        self.ui = appliedUI.Ui_mainWindow()
        self.ui.setupUi(self)

        self.ui.menu_savefile.setEnabled(0)
        self.ui.pushButton.setEnabled(0)

        self.F0 = MyFigure(width=6, height=4, dpi=100)

        for i in range(1,self.channels+1):
            self.F0.axe(self.channels,1,i).set_title("channel %d"%i)
            # self.F0.fig.tight_layout()
        self.gridlayout = QGridLayout(self.ui.groupBox)  # 继承容器groupBox
        self.gridlayout.addWidget(self.F0, 0, 1)


    def plottingEMG(self,npdata):
        self.F = MyFigure(width=3, height=2, dpi=100)
        for i in range(1,self.channels+1):
            self.F.axe(self.channels, 1, i).set_title("channel %d" % i)
            self.F.axe(self.channels, 1, i).plot(np.arange(npdata.shape[0]), 1000 * npdata[:,i-1])
            # self.F.axe(10,1,i).plot(tempcsv["X [s]"], 1000 * tempcsv["Avanti sensor %d: EMG %d [V]" % (i, i)])
            # self.F.fig.tight_layout()
        self.gridlayout.addWidget(self.F, 0, 1)
        np.save(self.dir_name +'temp/'+ 'nptemp.npy', npdata)
        self.ui.menu_savefile.setEnabled(1)
        self.ui.pushButton.setEnabled(1)

    def delImage(self):
        self.gridlayout.addWidget(self.F0, 0, 1)

    def savedata(self):
        filename,_ = QFileDialog.getSaveFileName(self,'save file',directory=self.dir_name+'data/'+'*.npy',filter='(*.npy)')
        if filename and filename.endswith('.npy'):
            shutil.copy(self.dir_name+'temp/nptemp.npy', filename)
        else:
            print('未保存')

    def data2show(self,file_name):
        print("选择的数据文件：" + file_name)
        if file_name.endswith('.csv'):
            rawcsv = pd.read_csv(file_name, encoding="unicode_escape", header=494)
            # 选择第0个column和以“[V]”结尾的column
            # rawcsv = rawcsv.loc[:, rawcsv.columns.str.endswith('[V]') | (rawcsv.columns == rawcsv.columns[0])]
            rawcsv = rawcsv.loc[:, rawcsv.columns.str.endswith('[V]')]
            npdata = rawcsv.to_numpy()
            self.showplot(file_name, npdata)
        elif file_name.endswith('.npy'):
            npdata = np.load(file_name)
            self.showplot(file_name, npdata)
        elif file_name.endswith('.mat'):
            matdata = scipy.io.loadmat(file_name)
            npdata = matdata['emg']
            self.showplot(file_name, npdata)
        else:
            print("other format")

    def openfile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", self.dir_name+'data/'
                                                   ,"All Data (*.npy *.csv *.mat);;npy Data (*.npy);;csv Data (*.csv);;mat Data (*.mat)"
                                                   , options=options)
        if file_name:
            self.data2show(file_name)
        else:
            print("未选择")
            self.delImage()



    def showplot(self,filename,npdata):

        self.channels = npdata.shape[1]

        self.plottingEMG(npdata)
        self.flag = 'csv2np'
        print("show over")

        dirpos = filename.rfind('/data')
        self.dir_name = filename[:dirpos + 1]

        p = filename.rfind('/')
        self.ui.listWidget.addItem(filename[p + 1:])


    def bandpassfiltAndShow(self):#带通滤波
        items1 = ('50', '100', '200')
        items2 = ('200', '500', '1000')
        item1, ok1 = QInputDialog.getItem(self, "滤波参数", '截止频率1', items1, 0, False)
        item2, ok2 = QInputDialog.getItem(self, "滤波参数", '截止频率2', items2, 0, False)
        if ok1 and ok2 and item1 and item2:
            f1 = int(item1)
            f2 = int(item2)
        data=np.load(self.dir_name + 'temp/nptemp.npy')
        w1 = 2 * f1 / self.samp_freq
        w2 = 2 * f2 / self.samp_freq
        b, a = signal.butter(8, [w1, w2], 'bandpass')  # 配置滤波器,8 表示滤波器的阶数
        for i in range(1, self.channels):
            data[:,i] = signal.filtfilt(b, a,data[:,i])
        self.plottingEMG(data)
        self.flag='bandfilt'

    def multifilt(self):
        data=np.load(self.dir_name + 'temp/nptemp.npy')
        self.dialog = Dialog()
        items1 = ('50', '100', '200')
        self.dialog.ui.comboBox.addItems(['butterworth', 'fir'])
        self.dialog.ui.lineEdit_1.setText("1000")
        self.dialog.ui.label_1.setText("滤波类型")
        self.dialog.ui.label_2.setText("采样率")
        self.dialog.ui.label_3.setText("下截止频率")
        self.dialog.ui.label_4.setText("上截止频率")
        self.plottingEMG(data)
        if self.dialog.exec_():
            method=self.dialog.ui.comboBox.currentText()
            self.samp_freq=int(self.dialog.ui.lineEdit_1.text())
            low = float(self.dialog.ui.lineEdit_2.text())
            high = float(self.dialog.ui.lineEdit_3.text())
            filted=signal_filter.signal_filter(data,self.samp_freq,low,high,method)
            self.plottingEMG(filted)


    def dirrect_power(self):
        ss0 = pd.read_csv(self.dir_name +'temp/'+ "fftdata.csv")
        ss = ss0.to_numpy()

        ps = np.zeros((self.fft_num, self.channels))
        self.F = MyFigure(width=3, height=2, dpi=100)
        for i in range(1, self.channels+1):
            ps[:, i - 1] = ss[:, i] ** 2 / self.fft_num
            self.F.axe(self.channels, 1, i).set_title("channel %d" % i)
            self.F.axe(self.channels, 1, i).plot(20 * np.log10(ps[:self.fft_num // 2, i - 1]))

        self.gridlayout.addWidget(self.F, 0, 1)

    def cor_power(self):
        data = pd.read_csv(self.dir_name + "csvtemp.csv")
        npdata = data.to_numpy()

        cor_x=cor_X=ps_cor = np.zeros((self.fft_num, self.channels))
        self.F = MyFigure(width=3, height=2, dpi=100)
        for i in range(1, self.channels+1):
            cor_x[:, i - 1] = np.correlate(npdata[:, i + 1], npdata[:, i + 1], 'same')
            cor_X[:, i - 1] = fft(cor_x[:, i - 1], self.fft_num)
            ps_cor[:, i - 1] = np.abs(cor_X[:, i - 1])
            ps_cor[:, i - 1] = ps_cor[:, i - 1] / np.max(ps_cor[:, i - 1])
            self.F.axe(self.channels, 1, i).set_title("channel %d" % i)
            self.F.axe(self.channels, 1, i).plot(20 * np.log10(ps_cor[:self.fft_num // 2],i-1))
        self.gridlayout.addWidget(self.F, 0, 1)

    def cut_data(self):
        low_0=min(self.ui.horizontalSlider.value(),self.ui.horizontalSlider_2.value())
        hign_99=max(self.ui.horizontalSlider.value(),self.ui.horizontalSlider_2.value())
        raw = np.load(self.dir_name + 'temp/nptemp.npy')
        total_size=raw.shape[0]
        cut=raw[int(total_size*low_0/99):int(total_size*hign_99/99),:]
        # np.save('cuttemp.npy',cut)
        self.plottingEMG(cut)
        self.flag='cut'
        print('总点数：'+str(total_size)+'\n'+'裁剪后起始点：'+str(int(total_size*low_0/99)))
        print("cut done")
        

    def fft_data(self):
        items = ('200', '500', '1000')
        item, ok = QInputDialog.getItem(self, "FFT参数", '点数', items, 0, False)
        if ok and item:
            self.fft_num=int(item)

        npdata = np.load(self.dir_name +'temp/'+ "nptemp.npy")

        ss = np.zeros((self.fft_num, self.channels))
        self.F = MyFigure(width=3, height=2, dpi=100)
        for i in range(1, self.channels+1):
            ss[:, i - 1] = fft(npdata[:, i-1], self.fft_num)
            ss[:, i - 1] = np.abs(ss[:, i - 1])
            self.F.axe(self.channels, 1, i).set_title("channel %d" % i)
            self.F.axe(self.channels, 1, i).plot(20 * np.log10(ss[:self.fft_num // 2, i - 1]))

        self.gridlayout.addWidget(self.F, 0, 1)
        self.ui.menu_savefile.setEnabled(0)

    def on_listWidgetItemDoubleClicked(self, item):
        print("Double clicked item:", item.text())
        self.data2show(self.dir_name+'data/'+item.text())

def main():
    myapp = QApplication(sys.argv)
    myDlg = MainWin()
    myDlg.show()
    sys.exit(myapp.exec_())

if __name__=='__main__':
    main()

