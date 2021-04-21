# This is a sample Python script.
import matplotlib
import pandas as _pd
import numpy as _np
import datetime

import coordinate
import matplotlib.pyplot as _plt

import math
import matplotlib as _mptl
from bokeh.plotting import figure, output_file, show


# -2095994.5592   4805173.1241   3620879.5075
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def _azel(x_rec, y_rec, z_rec, x_sat, y_sat, z_sat, distance):
    lat_rec, lon_rec, h_rec = coordinate.cart2ell(x_rec, y_rec, z_rec)
    east, north, up = coordinate.ell2topo(lat_rec, lon_rec, h_rec)
    unit_p = _np.matrix([(x_sat - x_rec) / distance,
                         (y_sat - y_rec) / distance,
                         (z_sat - z_rec) / distance])
    elevation = []
    azimuth = []
    for i in range(len(_np.transpose(unit_p))):
        elevation.append((_np.arcsin(_np.matmul(_np.transpose(unit_p[:, i]), up))))
        azimuth.append(
            _np.arctan2(_np.matmul(_np.transpose(unit_p[:, i]), east), _np.matmul(_np.transpose(unit_p[:, i]), north)))
        elevation[i] = elevation[i].item()
        azimuth[i] = azimuth[i].item()

    elevation = _np.degrees(elevation)
    azimuth = _np.degrees(azimuth)
    zenith = _np.degrees(_np.pi / 2) - elevation
    return (azimuth, elevation, zenith)


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


def readsatfile():
    approx_position = [-2095994.5592, 4805173.1241, 3620879.5075]
    SVlist = []
    # Xs = []
    # Ys = []
    # Zs = []
    pos = []
    epochList = []
    with open("satall.pos", 'r') as f:
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
        # Xs.append(float(line[3]))
        # Ys.append(float(line[4]))
        # Zs.append(float(line[5]))
        pos.append([float(line[3]), float(line[4]), float(line[5]), epoch])
    # print(epochList[23])
    # dataframe
    # , 'Epoch', 'Azimuth', 'Elevation', 'Zenith'
    header = ['X', 'Y', 'Z', 'Epoch']
    gnss = _pd.DataFrame(pos, index=SVlist, columns=header)
    gnss.index.name = 'SV'
    gnss.set_index('Epoch', append=True, inplace=True)
    gnss = gnss.reorder_levels(["SV", "Epoch"])

    gnss["Distance"] = coordinate._distance_euclidean(approx_position[0], approx_position[1], approx_position[2],
                                                      gnss.X, gnss.Y, gnss.Z)
    gnss['Azimuth'], gnss['Elevation'], gnss['Zenith'] = _azel(approx_position[0], approx_position[1],
                                                               approx_position[2], gnss.X, gnss.Y, gnss.Z,
                                                               gnss.Distance)
    gnss['svx'] = _np.radians(gnss.Azimuth.values)
    return gnss


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


def skyplot(gnss):
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
        raise Warning("Satellite(s) that you have entered not in NAV file Program Stopped")
    fig = _plt.figure('Skyplot')
    figName = 'Skyplot'
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)

    # colors = [_plt.cm.tab10(i / float(len(SVList) - 1)) for i in range(len(SVList))]
    #
    colors = ["red", "darkorange", "orange", "yellow", "forestgreen", "lime", "aqua", "dodgerblue", "midnightblue", "b",
              "darkviolet", "fuchsia", "hotpink"]
    #cm = _plt.cm.get_cmap('prism')
    i = 0
    for sv in SVList:
        try:
            if str(sv[0]) == 'G':
                skyplot = ax.scatter(gnss.loc[sv].svx, gnss.loc[sv].Zenith, s=4.2, color=colors[i], alpha=0.25,
                                     linewidths=1, vmax=1)
                ax.text(gnss.loc[sv].svx[int(len(gnss.loc[sv].svx) / 12)],
                        gnss.loc[sv].Zenith[int(len(gnss.loc[sv].Zenith) / 12)], sv, fontsize=12, color=colors[i],
                        weight="bold")
                i = i + 1
        except:
            print("error in " + str(sv))
    # Axes properties
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_rmax(90.0)
    ax.set_yticks(range(0, 90, 15))
    ylabels = ["90°", "75°", "60°", "45°", "30°", "15°"]
    # map(str, range(90, 0, -20))
    ax.set_yticklabels(ylabels)
    _plt.show()
    _plt.title(figName)
    _plt.rcParams['savefig.dpi'] = 500  # 图片像素
    _plt.rcParams['figure.dpi'] = 500  # 分辨率
    fig.savefig("SkyplotC_sea.png", transparent=True)


def getAverageCN0(gnss):
    SVList = gnss.index.get_level_values('SV').unique()
    Epochlist = gnss.index.get_level_values('Epoch').unique()
    fo = open("AverageCN0MI82.txt", mode='w+')
    for sv in SVList:
        # sv = 'G04'
        el_list = gnss.loc[sv].Elevation
        maxvalue = math.ceil(max(el_list))
        minvalue = 1
        for i in range(minvalue,maxvalue+1):
            el = gnss.loc[sv][round(gnss.loc[sv].Elevation) == i]
            try:
                snr_avg = sum(el.SNR) / len(el.SNR)
                fo.write(sv + "  " + str(i) + "  " + str(snr_avg) + "\n")
                print(sv + " average CN0 in ELevation " + str(i) + '° is ' + str(snr_avg))
            except:
                continue
    fo.close()


def plotAverageCN0_EL(avefilename):
    SV = []
    EL = []
    CN0 = []
    Info = []
    with open(avefilename, 'r') as f:
        lists = f.readlines()
    for list in lists:
        line = list.split()
        SV.append(line[0])
        EL.append(int(line[1]))
        CN0.append(float(line[2]))
        Info.append([int(line[1]), float(line[2])])
    header = ['EL', 'CN0']
    data = _pd.DataFrame(Info, index=SV, columns=header)
    data.index.name = 'SV'

    print('finish found dataframe')
    # plot
    fig, ax = _plt.subplots()  # 创建一个figure
    SVList = data.index.get_level_values('SV').unique()
    #SVList=['G01','G08','G11','G17','G18','G28']#'G06','G03','G19',,'G30','G07'
    for sv in SVList:
        if str(sv[0]) == 'G':
            ax.plot(data.loc[str(sv)].EL, data.loc[str(sv)].CN0, '--o', markersize=3.5, label=str(sv))

    ax.legend(loc='lower center', ncol=4)
    fig.suptitle('EL CN0')
    ax.set_xticks(range(0, 100, 10))
    ax.set_yticks(range(10,55, 5))
    #ax.set_yticks(range(10, 60, 10))
    ax.set_xlabel('EL')
    ax.set_ylabel('CN0')

    xlabels = ["0", "10", "20", "30", "40", "50", "60", "70", "80","90"]
    #ylabels = ["10", "20", "30",  "40", "50"]
    ylabels = ["10","15","20", "25", "30", "35", "40", "45", "50"]
    ax.set_xticklabels(xlabels)
    ax.set_yticklabels(ylabels)
    ax.grid(ls='--')
    _plt.rcParams['savefig.dpi'] = 500  # 图片像素
    _plt.rcParams['figure.dpi'] = 500  # 分辨率
    _plt.show()


def getGNSSDataframe():
    # Use a breakpoint in the code line below to debug your script.
    # print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

    gnss = readqualityfile("sea_MI81_quality.txt")
    # skyplot(gnss)
    #getAverageCN0(gnss)
    print("finish import gnss Dataframe")

def plotEL_CN0_PRN(prn):

    gnss = readqualityfile("sea_MI81_quality.txt")

    gnss['Time'] = gnss['epoch'].dt.hour*60*60+gnss['epoch'].dt.minute*60+gnss['epoch'].dt.second
    #gnss['Seconds'] = _pd.to_timedelta(gnss['epoch']).apply(lambda x: x.total_seconds())
    print("finish import gnss Dataframe")
    fig,ax = _plt.subplots(figsize=(6,3))  # 创建一个figure

    #ax.set_title('Time-Elevation-C/N0 Plot',fontsize=11)
    ax.scatter(gnss.loc[prn].Time,gnss.loc[prn].SNR,c='blue',marker='_',s=4,linewidths=2.0,vmin=20,vmax=50)

    ax.set_yticks(_np.arange(30, 51, 5))  # 设置左边纵坐标刻度
    ax.set_ylabel('CN0 Value', fontsize=10,color='blue')  # 设置左边纵坐标标签
    ax.tick_params(axis='y', width=2, colors='blue')
    _plt.ylim((25,50))

    ax2=ax.twinx()
    ax2.plot(gnss.loc[prn].Time,gnss.loc[prn].Elevation,c='red',linewidth=2.0)
    ax2.set_yticks(_np.arange(10, 91, 10))  # 设置左边纵坐标刻度
    ax2.set_ylabel('Elevation', fontsize=10,color='red')  # 设置左边纵坐标标签
    ax2.tick_params(axis='y', width=2, colors='red')
    _plt.ylim((10, 90))

    ax.tick_params(axis='x',labelsize=8)
    ax.set_xticks(_np.arange(0,14500,1200))
    #ax.set_xlabel("Time", fontsize=10)
    ax2.set_xticks(_np.arange(0, 14500, 1200))
    #ax2.set_xlabel("Time", fontsize=10)
    ax.grid(ls='--')
    _plt.xlim((0,14400))

    _plt.text(500,30,prn,fontsize=12,weight='bold',style='italic')

    # _plt.rcParams['savefig.dpi'] = 500  # 图片像素
    # _plt.rcParams['figure.dpi'] = 500  # 分辨率
    # _plt.rcParams['figure.figsize'] = (10.0, 4.0)
    _plt.show()


def plot_PRNNUMBER():
    gnss = readqualityfile("sea_MI81_quality.txt")
    gnss['Time'] = gnss['epoch'].dt.hour * 60 * 60 + gnss['epoch'].dt.minute * 60 + gnss['epoch'].dt.second
    print("finish import gnss Dataframe")

    # open dataframe
    header = ['Gnum', 'Rnum', 'Enum', 'Cnum', 'Time']
    Info=[]
    time=range(1,14401,1)

    for i in range(1,14401):
        epochdata=gnss.loc[gnss['Time']==i]
        SVList = epochdata.index.get_level_values('SV').unique()
        Gnum,Rnum,Enum,Cnum=0,0,0,0
        for sv in SVList:
            if str(sv).startswith('G'):
                Gnum=Gnum+1
            elif str(sv).startswith('R'):
                Rnum=Rnum+1
            elif str(sv).startswith('E'):
                Enum=Enum+1
            elif str(sv).startswith('C'):
                Cnum=Cnum+1
        Info.append([Gnum,Rnum,Enum,Cnum,i])
    prnnumberdata = _pd.DataFrame(Info, index=time, columns=header)

    ##############plot prn number ###############
    fig,ax = _plt.subplots(figsize=(7,3.5))  # 创建一个figure
    ax.set_yticks(_np.arange(0, 17, 2))  # 设置左边纵坐标刻度
    ax.set_ylabel('Number of satellites', fontsize=10)  # 设置左边纵坐标标签
    _plt.ylim((0, 16))
    ax.tick_params(axis='x',labelsize=8)
    ax.set_xticks(_np.arange(0,14500,1200))
    ax.grid(ls='--')
    _plt.xlim((0, 14400))

    ax.plot(time, prnnumberdata['Gnum'], '--o',c='steelblue', linewidth=0.3,markersize=1.0, label='GPS')
    ax.plot(time, prnnumberdata['Rnum'], '--o',c='greenyellow', linewidth=0.3,markersize=1.0, label='GLONASS')
    ax.plot(time, prnnumberdata['Cnum'], '--o', c='darkorange', linewidth=0.3, markersize=1.2, label='BDS')
    ax.plot(time, prnnumberdata['Enum'],'--o', c='dimgrey', linewidth=0.3,markersize=1.0, label='Galileo')
    _plt.legend(loc='upper center', ncol=4,fontsize=10,frameon=False)#去掉图例边框
    _plt.show()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #print_hi('PyCharm')
    #getGNSSDataframe()
    #plotAverageCN0_EL("AverageCN0MI82.txt")
    #plotEL_CN0_PRN('G01')
    # plotEL_CN0_PRN('C13')
    # plotEL_CN0_PRN('C26')
    plot_PRNNUMBER()