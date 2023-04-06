import tkinter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
from tkinter import *
import tkinter.filedialog
from scipy.fftpack import fft, fftshift, ifft
from scipy.fftpack import fftfreq

root = Tk()
root.geometry("500x500")
L0 = Label(root, text='\n')
L0.pack()
dirname=""






samp_freq = 1259.259  # 采样率

def plottingEMG(emgdata):
    plt.ion()
    plt.figure()

    for i in range(1,11):

        plt.subplot(10,1,i)
        plt.plot(emgdata["X [s]"], 1000 * emgdata["Avanti sensor %d: EMG %d [V]"%(i,i)])

    plt.ioff()
    plt.show()



def selectAndShow():
    global dirname
    filename= tkinter.filedialog.askopenfilename()
    if filename != '':
        L0.config(text="选择的数据文件：" + filename);
    else:
        L0.config(text="未选择任何文件");

    raw= pd.read_csv(filename, encoding="unicode_escape", header=494)[["X [s]",
               "Avanti sensor 1: EMG 1 [V]", "Avanti sensor 2: EMG 2 [V]",
               "Avanti sensor 3: EMG 3 [V]", "Avanti sensor 4: EMG 4 [V]",
               "Avanti sensor 5: EMG 5 [V]", "Avanti sensor 6: EMG 6 [V]",
               "Avanti sensor 7: EMG 7 [V]", "Avanti sensor 8: EMG 8 [V]",
               "Avanti sensor 9: EMG 9 [V]", "Avanti sensor 10: EMG 10 [V]"]]
    plottingEMG(raw)

    dirpos=filename.rfind('/')
    dirname=filename[:dirpos+1]
    raw.to_csv(dirname+"csvtemp.csv")

    bandBTN.config(state=tkinter.NORMAL)
    fftBTN.config(state=tkinter.NORMAL)


def filting_notch(raw):
# 陷波
    notch_freq = 50.0  # 工频
    quality_factor = 30.0  # Quality factor

    # Design a notch filter using Mysignal.iirnotch
    b_notch, a_notch = signal.iirnotch(notch_freq, quality_factor, samp_freq)
    for i in range(1,11):
        raw["Avanti sensor %d: EMG %d [V]"%(i,i)]=signal.filtfilt(b_notch, a_notch, raw["Avanti sensor %d: EMG %d [V]"%(i,i)])


def bandpassfiltAndShow():
    # 带通滤波
    # 10-400Hz
    raw = pd.read_csv(dirname+"csvtemp.csv", encoding="unicode_escape", header=0)
    f1=int(band1TXT.get())
    f2=int(band2TXT.get())
    w1=2*f1/samp_freq
    w2=2*f2/samp_freq
    b, a = signal.butter(8, [w1,w2], 'bandpass')    #配置滤波器 8 表示滤波器的阶数
    for i in range(1,10):
        raw["Avanti sensor %d: EMG %d [V]"%(i,i)] = signal.filtfilt(b, a, raw["Avanti sensor %d: EMG %d [V]"%(i,i)])

    plottingEMG(raw)

def fft_data():
    fft_num=int(fftTXT.get())
    data=pd.read_csv(dirname+"csvtemp.csv")
    npdata=data.to_numpy()
    plt.figure()
    
    ss=np.zeros((fft_num,10))
    for i in range(1,11):
        ss[:,i-1] = fft( npdata[:,i],fft_num)
        ss[:,i-1] = np.abs(ss[:,i-1])
        plt.subplot(10, 1, i)
        plt.plot(20*np.log10(ss[:fft_num//2,i-1]))
    plt.show()
    pd.DataFrame(ss).to_csv(dirname+"fftdata.csv")


btn = Button(root, text="选择数据并做图", command=selectAndShow)
btn.pack()

L1 = Label(root, text="\n\n带通范围（Hz）：")
L1.pack( )
band1TXT = Entry(root, bd =5)
band1TXT.pack()
band2TXT = Entry(root, bd =5)
band2TXT.pack()
bandBTN = Button(root, state=tkinter.DISABLED,text="带通滤波并做图", command=bandpassfiltAndShow)
bandBTN.pack()

L2 = Label(root, text="\n\n设置FFT点数")
L2.pack()
fftTXT = Entry(root)
fftTXT.pack()
fftBTN = Button(root, state=tkinter.DISABLED,text="求FFT", command=fft_data)
fftBTN.pack()

powerBTN = Button(root,text="求功率谱", command=fft_data)
powerBTN.pack()
corpowerBTN = Button(root, text="求相关功率谱", command=fft_data)
corpowerBTN.pack()

root.mainloop()