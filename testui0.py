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
import untitled0
from PyQt5 import QtCore, QtGui,QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import requests
from scipy.fftpack import fft, fftshift, ifft
from scipy.fftpack import fftfreq

dir_name=""

#创建一个matplotlib图形绘制类
class MyFigure(FigureCanvas):
    def __init__(self,width=5, height=4, dpi=100):
        #第一步：创建一个创建Figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        #第二步：在父类中激活Figure窗口
        super(MyFigure,self).__init__(self.fig) #此句必不可少，否则不能显示图形
        #第三步：创建一个子图，用于绘制图形用，111表示子图编号，如matlab的subplot(1,1,1)
        self.axe=self.fig.add_subplot





class MainWin(QMainWindow):
    def __init__(self, parent=None):
        super(QtWidgets.QMainWindow, self).__init__(parent)
        self.ui = untitled0.Ui_mainWindow()
        self.ui.setupUi(self)

        self.F0 = MyFigure(width=3, height=2, dpi=100)
        for i in range(1,11):
            self.F0.axe(10,1,i)
        self.gridlayout = QGridLayout(self.ui.groupBox)  # 继承容器groupBox
        self.gridlayout.addWidget(self.F0, 0, 1)


    def plottingEMG(self,emgdata):

        self.F = MyFigure(width=3, height=2, dpi=100)
        for i in range(1,11):
            self.F.axe(10,1,i).plot(emgdata["X [s]"], 1000 * emgdata["Avanti sensor %d: EMG %d [V]" % (i, i)])
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
        else:
            print("未选择")
            self.delImage()

    def showplot(self,filename):
        global dir_name
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
        dir_name = filename[:dirpos + 1]
        raw.to_csv(dir_name + "csvtemp.csv")

        print("show over")

def main():
    myapp = QApplication(sys.argv)
    myDlg = MainWin()
    myDlg.show()
    sys.exit(myapp.exec_())

if __name__=='__main__':
    main()
    print("2")