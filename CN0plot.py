import matplotlib
import pandas as _pd
import numpy as _np
import datetime

import coordinate
import matplotlib.pyplot as _plt

import math
import matplotlib as _mptl
from bokeh.plotting import figure, output_file, show


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


def plotAverageCN0_EL(avefilename):
    SV = []
    EL = []
    CN0 = []
    CN0L5 = []
    Info = []
    with open(avefilename, 'r') as f:
        lists = f.readlines()
    for list in lists:
        line = list.split()
        SV.append(line[0])
        EL.append(int(line[1]))
        CN0.append(float(line[2]))
        CN0L5.append(float(line[3]))
        Info.append([int(line[1]), float(line[2]), float(line[3])])
    header = ['EL', 'CN0', 'CN0L5']
    data = _pd.DataFrame(Info, index=SV, columns=header)
    data.index.name = 'SV'

    print('finish found dataframe')
    # plot
    fig, ax = _plt.subplots()  # 创建一个figure
    SVList = data.index.get_level_values('SV').unique()
    # SVList=['G01','G08','G11','G17','G18','G28']#'G06','G03','G19',,'G30','G07'
    Gsvlist=['G01','G11','G30']
    Csvlist=['C01','C08','C26']
    for sv in Gsvlist:
        if str(sv[0]) == 'G':
            ax.plot(data.loc[str(sv)].EL, data.loc[str(sv)].CN0, '--o', markersize=3.5, label=str(sv)+' L1')
            ax.plot(data.loc[str(sv)].EL, data.loc[str(sv)].CN0L5, '--o', markersize=3.5, label=str(sv) + ' L5')

    ax.legend(loc='lower center', ncol=4)
    fig.suptitle('EL CN0')
    ax.set_xticks(range(0, 100, 10))
    ax.set_yticks(range(10, 55, 5))
    # ax.set_yticks(range(10, 60, 10))
    ax.set_xlabel('EL')
    ax.set_ylabel('CN0')

    xlabels = ["0", "10", "20", "30", "40", "50", "60", "70", "80", "90"]
    # ylabels = ["10", "20", "30",  "40", "50"]
    ylabels = ["10", "15", "20", "25", "30", "35", "40", "45", "50"]
    ax.set_xticklabels(xlabels)
    ax.set_yticklabels(ylabels)
    ax.grid(ls='--')
    _plt.rcParams['savefig.dpi'] = 500  # 图片像素
    _plt.rcParams['figure.dpi'] = 500  # 分辨率
    _plt.show()


def readqualityfile(filename):
    SVlist = []
    Systemlist = []
    AZ = []
    EL = []
    ZE = []
    SNR = []
    SNRL5 = []
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
        # 存取系统的名称
        prn = getprn(int(line[2]))
        # if prn[0]=='G':
        #     Systemlist.append('G')
        # elif prn[0]=='C':
        #     Systemlist.append('C')
        # elif prn[0]=='R':
        #     Systemlist.append('R')
        # elif prn[0]=='E':
        #     Systemlist.append('E')
        AZ.append(float(line[3]))
        EL.append(float(line[4]))
        ZE.append(_np.degrees(_np.pi / 2) - float(line[4]))
        SNR.append(int(line[5]) / 1000.0)
        SNRL5.append(int(line[6]) / 1000.0)
        Info.append(
            [float(line[3]), float(line[4]), _np.degrees(_np.pi / 2) - float(line[4]), int(line[5]) / 1000.0,
             int(line[6]) / 1000.0, epoch, prn[0], prn])
    header = ['Azimuth', 'Elevation', 'Zenith', 'SNR', 'SNRL5', 'Epoch', 'System', 'sv']
    gnss = _pd.DataFrame(Info, index=SVlist, columns=header)
    gnss.index.name = 'SV'
    gnss.set_index('Epoch', append=True, inplace=True)
    gnss = gnss.reorder_levels(["SV", "Epoch"])
    gnss['epoch'] = epochList
    gnss['svx'] = _np.radians(gnss.Azimuth.values)
    return gnss


def plotEL_CN0_PRN(prn):
    gnss = readqualityfile("sea_MI8_quality_L1L5_changeGALcode.txt")

    gnss['Time'] = gnss['epoch'].dt.hour * 60 * 60 + gnss['epoch'].dt.minute * 60 + gnss['epoch'].dt.second
    # gnss['Seconds'] = _pd.to_timedelta(gnss['epoch']).apply(lambda x: x.total_seconds())
    print("finish import gnss Dataframe")
    fig, ax = _plt.subplots(figsize=(6, 3))  # 创建一个figure

    # ax.set_title('Time-Elevation-C/N0 Plot',fontsize=11)
    ax.scatter(gnss.loc[prn].Time, gnss.loc[prn].SNR, c='blue', marker='_', s=4, linewidths=2.0, vmin=20, vmax=50,
               label='L1')
    # GPS卫星有些有L1和L5波段
    ax.scatter(gnss.loc[prn].Time, gnss.loc[prn].SNRL5, c='green', marker='_', s=3, linewidths=1.5, vmin=20, vmax=50,
               label='L5')
    # _plt.legend(loc='lower center', ncol=2, fontsize=12, frameon=False)  # 去掉图例边框

    ax.set_yticks(_np.arange(30, 51, 5))  # 设置左边纵坐标刻度
    ax.set_ylabel('CN0 Value(dBHz)', fontsize=14, color='blue')  # 设置左边纵坐标标签
    ax.tick_params(axis='y', width=3, colors='blue')
    _plt.ylim((25, 50))

    ax2 = ax.twinx()
    ax2.plot(gnss.loc[prn].Time, gnss.loc[prn].Elevation, c='red', linewidth=2.0)
    ax2.set_yticks(_np.arange(10, 91, 10))  # 设置左边纵坐标刻度
    ax2.set_ylabel('Elevation(°)', fontsize=14, color='red')  # 设置左边纵坐标标签
    ax2.tick_params(axis='y', width=3, colors='red')
    _plt.ylim((10, 90))

    ax.tick_params(axis='x', labelsize=11)
    ax.tick_params(axis='y', labelsize=12)
    ax2.tick_params(axis='y', labelsize=12)
    # xticks=['0','','2400','']
    ax.set_xticks(_np.arange(0, 14500, 1800))
    # ax.set_xlabel("Time", fontsize=10)
    ax2.set_xticks(_np.arange(0, 14500, 1800))
    # ax2.set_xlabel("Time", fontsize=10)
    ax.grid(ls='--')
    _plt.xlim((0, 14400))
    # ax.set_xlabel('Numbers of epoch with 1s sample interval', fontsize=12)
    _plt.text(500, 70, prn, fontsize=16, weight='bold',
              # style='italic'
              )

    # _plt.rcParams['savefig.dpi'] = 500  # 图片像素
    # _plt.rcParams['figure.dpi'] = 500  # 分辨率
    # _plt.rcParams['figure.figsize'] = (10.0, 4.0)
    _plt.show()


def getAverageCN0(gnss):
    SVList = gnss.index.get_level_values('SV').unique()
    Epochlist = gnss.index.get_level_values('Epoch').unique()
    fo = open("AverageCN0MI81_L1L5.txt", mode='w+')
    for sv in SVList:
        # sv = 'G04'
        el_list = gnss.loc[sv].Elevation
        maxvalue = math.ceil(max(el_list))
        minvalue = 1
        for i in range(minvalue, maxvalue + 1):
            el = gnss.loc[sv][round(gnss.loc[sv].Elevation) == i]
            try:
                snr_avg = sum(el.SNR) / len(el.SNR)
                tete = el.SNRL5
                snrL5_avg = sum(el.SNRL5) / len(el.SNRL5)
                fo.write(sv + "  " + str(i) + "  " + str(snr_avg) + "  " + str(snrL5_avg) + "\n")
                print(sv + "L5 average CN0 in ELevation " + str(i) + '° is ' + str(snrL5_avg))
            except:
                continue
    fo.close()


# 直方图绘制
def gethistplot():
    gnss = readqualityfile("sea_MI8_quality_L1L5_changeGALcode.txt")

    gnss['Time'] = gnss['epoch'].dt.hour * 60 * 60 + gnss['epoch'].dt.minute * 60 + gnss['epoch'].dt.second
    print("finish import gnss Dataframe")
    # fig = _plt.figure()
    # ax1 = fig.add_subplot(1, 3, 1)
    # ax2 = fig.add_subplot(1, 3, 2)
    # ax3 = fig.add_subplot(1, 3, 3)
    fig,(ax1,ax2,ax3)=_plt.subplots(1,3,sharey=True)
    Gcn0L1 = gnss.loc[gnss['System'] == 'G']['SNR']
    p = gnss.loc[gnss['System'] == 'G']
    Gcn0L5 = p.loc[gnss['SNRL5'] > 0]['SNRL5']
    Ecn0e1 = gnss.loc[gnss['System'] == 'E']['SNR']

    Rcn0R1 = gnss.loc[gnss['System'] == 'R']['SNR']
    Ccn0C2 = gnss.loc[gnss['System'] == 'C']['SNR']

    geoc01 = gnss.loc[gnss['sv'] == 'C01']['SNR']
    geoc03 = gnss.loc[gnss['sv'] == 'C03']['SNR']
    geoc04 = gnss.loc[gnss['sv'] == 'C04']['SNR']
    geo = geoc01.append([geoc03, geoc04])
    igsoc08 = gnss.loc[gnss['sv'] == 'C08']['SNR']
    igsoc10 = gnss.loc[gnss['sv'] == 'C10']['SNR']
    igso = igsoc08.append(igsoc10)

    meoc12 = gnss.loc[gnss['sv'] == 'C12']['SNR']
    meoc13 = gnss.loc[gnss['sv'] == 'C13']['SNR']
    meoc26 = gnss.loc[gnss['sv'] == 'C26']['SNR']
    meoc29 = gnss.loc[gnss['sv'] == 'C29']['SNR']
    meo = meoc12.append([meoc13, meoc26, meoc29])
    _plt.xlim([20,60])
    _plt.xticks([20,30,40,50,60])
    #xlabels=['','[20-30]','[30-40]','[40-50]','[50-60]']

    #_plt.set_xtickLabels([])
    ax1.hist([Gcn0L1, Gcn0L5], bins=[20, 30, 40, 50, 60], density=True, histtype='bar', rwidth=0.8,color=['red','blue'],label=['GPS L1','GPS L5'])
    ax1.legend(loc='best')
    #ax1.set_xlabel("(a) GPS")
    #ax1.set_xticklabels(xlabels)
    #ax2.hist([Rcn0R1, Ecn0e1], bins=[20, 30, 40, 50, 60], density=True, histtype='bar', rwidth=0.8,color=['red','blue'],label=['GLNASS','Galileo E1'])
    ax2.hist(Rcn0R1, bins=[20, 30, 40, 50, 60], density=True, histtype='bar', rwidth=0.7,color='red',label='GLONASS')

    ax2.legend(loc='best')
    #ax2.set_xlabel("(b) GLONASS")

    ax3.hist([geo, igso, meo], bins=[20, 30, 40, 50, 60], density=True, histtype='bar', rwidth=0.9,color=['red','blue','green'],label=['GEO','IGSO','MEO'])
    ax3.legend(loc='best')
    #ax3.set_xlabel("(c) BDS")
    # _plt.hist(Gcn0L5, bins=[0, 20, 30, 40, 50, 60], density=True, histtype='bar', rwidth=0.8)
    ax1.set_ylabel('Frequency')
    ax1.set_xlabel('CN0 value(dBHZ)')
    ax2.set_xlabel('CN0 value(dBHZ)')
    ax3.set_xlabel('CN0 value(dBHZ)')
    _plt.show()


if __name__ == '__main__':
    # gnss=readqualityfile("sea_MI8_quality_L1L5.txt")
    # getAverageCN0(gnss)

    plotAverageCN0_EL("AverageCN0MI81_L1L5.txt")

    # plotEL_CN0_PRN('C01')#GEO
    # plotEL_CN0_PRN('C08')#IGSO
    # plotEL_CN0_PRN('C26')#MEO
    # plotEL_CN0_PRN('C10')#IGSO
    # plotEL_CN0_PRN('E01')
    # plotEL_CN0_PRN('C29')  # IGSO

    # plotEL_CN0_PRN('R24')#xuanze
    # plotEL_CN0_PRN('R14')#xuanze
    # plotEL_CN0_PRN('R13')  # xuanze

    # plotEL_CN0_PRN('G01')
    # plotEL_CN0_PRN('G08')
    # plotEL_CN0_PRN('G11')
    # plotEL_CN0_PRN('G30')

    # plot 直方图
    #gethistplot()
