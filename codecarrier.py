import matplotlib
import pandas as _pd
import numpy as _np
import datetime


import matplotlib.pyplot as _plt

import math

def readfile(filename):
    with open(filename, 'r') as f:
        lists = f.readlines()
    epochList = []
    TDCC=[]
    Info=[]
    time=[]#second
    for list in lists:
        line = list.split()
        epoch_year, epoch_month, epoch_day = (line[0]),(line[1]),(line[2])
        epoch_hour, epoch_minute, epoch_second = (line[3]),(line[4]),(line[5])
        epoch = datetime.datetime(year=int(epoch_year),
                                  month=int(epoch_month),
                                  day=int(epoch_day),
                                  hour=int(epoch_hour),
                                  minute=int(epoch_minute),
                                  second=int(epoch_second))
        epochList.append(epoch)
        TDCC.append(float(line[7]))
        Info.append([float(line[7]),epoch])
    header = ['TDCC', 'Epoch']
    gnss = _pd.DataFrame(Info, index=epochList, columns=header)
    gnss['Time'] = gnss['Epoch'].dt.hour * 60 * 60 + gnss['Epoch'].dt.minute * 60 + gnss['Epoch'].dt.second
    print("gnss dataframe finished")
    return gnss

def readGfile(filename):
    with open(filename, 'r') as f:
        lists = f.readlines()
    epochList = []
    TDCC_C1C=[]
    TDCC_C5Q = []
    Info=[]
    time=[]#second
    for list in lists:
        line = list.split()
        epoch_year, epoch_month, epoch_day = (line[0]),(line[1]),(line[2])
        epoch_hour, epoch_minute, epoch_second = (line[3]),(line[4]),(line[5])
        epoch = datetime.datetime(year=int(epoch_year),
                                  month=int(epoch_month),
                                  day=int(epoch_day),
                                  hour=int(epoch_hour),
                                  minute=int(epoch_minute),
                                  second=int(epoch_second))
        epochList.append(epoch)
        TDCC_C1C.append(float(line[11]))
        TDCC_C5Q.append(float(line[12]))
        Info.append([float(line[11]),float(line[12]),epoch])
    header = ['TDCC_C1C','TDCC_C5Q' ,'Epoch']
    gnss = _pd.DataFrame(Info, index=epochList, columns=header)
    gnss['Time'] = gnss['Epoch'].dt.hour * 60 * 60 + gnss['Epoch'].dt.minute * 60 + gnss['Epoch'].dt.second
    print("gnss dataframe finished")
    return gnss

def plottdcc(gnss):
    ##############plot  ###############
    fig, ax = _plt.subplots(figsize=(7, 3.5))  # 创建一个figure
    ax.set_yticks(_np.arange(-20, 21, 5))  # 设置左边纵坐标刻度
    ax.set_ylabel('TD-CC', fontsize=10)  # 设置左边纵坐标标签
    _plt.ylim((-20, 20))
    ax.tick_params(axis='x', labelsize=8)
    ax.set_xticks(_np.arange(0, 14500, 1200))
    ax.grid(ls='--')
    _plt.xlim((0, 14400))
    #ax.plot(gnss['Time'], gnss['TDCC'], '--o',c='steelblue', linewidth=0.3,markersize=1.0, label='C01')
    ax.scatter(gnss['Time'], gnss['TDCC'], c='deepskyblue', marker='+', s=10, linewidths=2.0)
    _plt.show()


if __name__ == '__main__':
    gnss=readfile("ANDROID_C8.qua")
    plottdcc(gnss)