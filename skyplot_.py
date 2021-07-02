# -*- coding: utf-8 -*-
# @prohject : 'main.py'
# @Time    : 2021/6/28 12:10
# @Author  : Butterflying
# @Email   : 2668609932@qq.com
# @File    : skyplot_.py
# code is far away from bugs with the god animal protecting
import pandas as _pd
import numpy as _np
import datetime

import coordinate
import matplotlib.pyplot as _plt

import math
def getprn(num):
    if 0 < num < 10:
        return "G0" + str(num)
    if 32 >= num >= 10:
        return 'G' + str(num)
    if 27 >= num - 32 > 0:
        num = num - 32
        if 0 < num < 10:
            return "R0" + str(num)
        else:
            return 'R' + str(num)
    if 32 + 27 < num <= 32 + 27 + 36:
        num = num - 32 - 27
        if 0 < num < 10:
            return "E0" + str(num)
        else:
            return 'E' + str(num)
    if 32 + 27 + 36 < num <= 32 + 27 + 36 + 10:
        num = num - 32 - 27 - 36
        if 0 < num < 10:
            return "Q0" + str(num)
        else:
            return 'Q' + str(num)
    if 32 + 27 + 36 + 10 < num <= 32 + 27 + 36 + 10 + 63:
        num = num - 32 - 27 - 36 - 10
        if 0 < num < 10:
            return "C0" + str(num)
        else:
            return 'C' + str(num)
def skyplot_all(gnss):
    SVList = gnss.index.get_level_values('SV').unique()
    for sv in SVList:
        try:
            if sv[0] not in {'G', 'R', 'C', 'E'} or sv[1:].isdigit() == False or len(sv) != 3 or sv is None:
                raise Warning(
                    "Invalid format: Please enter satellite(s) that you want to plot proper format. Exp. SVlist= ['G01', 'G02', 'G11',....] Program Stopped")
            elif sv not in SVList:
                # SVList.remove(sv)
                print('{} satellite not in sat file'.format(sv))
        except:
            # SVList.remove(sv)
            print(sv)
    if len(SVList) == 0:
        raise Warning("Satellite(s) that you have entered not ")
    fig = _plt.figure('Skyplot')
    figName = 'Skyplot'
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)

    # colors = [_plt.cm.tab10(i / float(len(SVList) - 1)) for i in range(len(SVList))]
    #
    colors = ["red", "darkorange", "orange", "gold", "forestgreen", "lime", "aqua", "dodgerblue", "midnightblue", "b",
              "darkviolet", "fuchsia", "hotpink","violet","turquoise","m","cornflowerblue","slateblue","salmon","tomato",
              "chartreuse","fuchsia","orchid","c","coral"]

    i = 0
    print(len(SVList))
    for sv in SVList:
        try:
            if str(sv[0]) == 'E':
                skyplot = ax.scatter(gnss.loc[sv].svx, gnss.loc[sv].Zenith, s=4.2,
                                     color='r',
                                     alpha=0.25,
                                     linewidths=1, vmax=1)
                ax.text(gnss.loc[sv].svx[int(len(gnss.loc[sv].svx) / 20)],
                        gnss.loc[sv].Zenith[int(len(gnss.loc[sv].Zenith) / 20)], sv, fontsize=15,
                        color='r',
                        weight="bold")
                i = i + 1
            if str(sv[0]) == 'G':
                skyplot = ax.scatter(gnss.loc[sv].svx, gnss.loc[sv].Zenith, s=4.2,
                                     color='b',
                                     alpha=0.25,
                                     linewidths=1, vmax=1)
                ax.text(gnss.loc[sv].svx[int(len(gnss.loc[sv].svx) / 20)],
                        gnss.loc[sv].Zenith[int(len(gnss.loc[sv].Zenith) / 20)], sv, fontsize=15,
                        color='b',
                        weight="bold")
                i = i + 1
            if str(sv[0]) == 'R':
                skyplot = ax.scatter(gnss.loc[sv].svx, gnss.loc[sv].Zenith, s=4.2,
                                     color='g',
                                     alpha=0.25,
                                     linewidths=1, vmax=1)
                ax.text(gnss.loc[sv].svx[int(len(gnss.loc[sv].svx) / 20)],
                        gnss.loc[sv].Zenith[int(len(gnss.loc[sv].Zenith) / 20)], sv, fontsize=15,
                        color='g',
                        weight="bold")
                i = i + 1
            if str(sv[0]) == 'C':
                skyplot = ax.scatter(gnss.loc[sv].svx, gnss.loc[sv].Zenith, s=4.2,
                                     color='c',
                                     alpha=0.25,
                                     linewidths=1, vmax=1)
                ax.text(gnss.loc[sv].svx[int(len(gnss.loc[sv].svx) / 20)],
                        gnss.loc[sv].Zenith[int(len(gnss.loc[sv].Zenith) / 20)], sv, fontsize=15,
                        color='c',
                        weight="bold")
                i = i + 1

        except:
            print("error in " + str(sv))
    # Axes properties
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_rmax(90.0)
    ax.set_yticks(range(0, 90, 15))
    ylabels = [" ", "75°", "60°", "45°", "30°", "15°"]
    # map(str, range(90, 0, -20))
    ax.set_yticklabels(ylabels)
    _plt.show()
    _plt.title(figName)
    _plt.rcParams['savefig.dpi'] = 500  # 图片像素
    _plt.rcParams['figure.dpi'] = 500  # 分辨率
    # fig.savefig("SkyplotC_sea.png", transparent=True)
def readqualityfile(filename):
    SVlist = []
    AZ = []
    EL = []
    ZE = []
    SNR = []
    Info = []

    epochList = []
    with open(filename, 'r') as f:
        lists = f.readlines()
    for list in lists:
        line = list.split()
        epoch_year, epoch_month, epoch_day = line[0].split('/')
        epoch_hour, epoch_minute, epoch_second = line[1].split(':')
        epoch = datetime.datetime(year=int(epoch_year),
                                  month=int(epoch_month),
                                  day=int(epoch_day),
                                  hour=int(epoch_hour),
                                  minute=int(epoch_minute),
                                  second=int(float(epoch_second)))
        # print(line)
        epochList.append(epoch)
        SVlist.append(getprn(int(line[2])))
        AZ.append(float(line[3]))
        EL.append(float(line[4]))
        ZE.append(_np.degrees(_np.pi / 2) - float(line[4]))
        SNR.append(int(line[5]) / 1000.0)
        Info.append(
            [float(line[3]), float(line[4]), _np.degrees(_np.pi / 2) - float(line[4]), int(line[5]) / 1000.0, epoch])
    header = ['Azimuth', 'Elevation', 'Zenith', 'SNR', 'Epoch']
    gnss = _pd.DataFrame(Info, index=SVlist, columns=header)
    gnss.index.name = 'SV'
    gnss.set_index('Epoch', append=True, inplace=True)
    gnss = gnss.reorder_levels(["SV", "Epoch"])
    gnss['epoch']=epochList
    gnss['svx'] = _np.radians(gnss.Azimuth.values)
    return gnss
if __name__ == '__main__':
    # Use a breakpoint in the code line below to debug your script.
    # print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    gnss = readqualityfile("sea_MI81_quality.txt")
    skyplot_all(gnss)