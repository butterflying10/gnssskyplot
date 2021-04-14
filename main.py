# This is a sample Python script.
import pandas as _pd
import numpy as _np
import datetime
import coordinate
import matplotlib.pyplot as _plt
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
    if 32 >= num > 10:
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
    cm = _plt.cm.get_cmap('prism')
    i = 0
    for sv in SVList:
        try:
            if str(sv[0]) == 'C':
                skyplot = ax.scatter(gnss.loc[sv].svx, gnss.loc[sv].Zenith, s=4.5, color=colors[i],alpha=0.25,linewidths=1,vmax=1)
                ax.text(gnss.loc[sv].svx[int(len(gnss.loc[sv].svx)/12)],
                        gnss.loc[sv].Zenith[int(len(gnss.loc[sv].Zenith)/12)], sv, fontsize=10, color=colors[i],
                        weight="bold")
                i = i + 1
        except:
            print("error in " + str(sv))
    # Axes properties
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_rmax(90.0)
    ax.set_yticks(range(0, 90, 15))
    ylabels=["90°","75°","60°","45°","30°","15°"]
    #map(str, range(90, 0, -20))
    ax.set_yticklabels(ylabels)
    _plt.show()
    _plt.title(figName)
    _plt.rcParams['savefig.dpi'] = 500  # 图片像素
    _plt.rcParams['figure.dpi'] = 500  # 分辨率
    fig.savefig("SkyplotC.png", transparent=True)
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    # print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    gnss = readsatfile()
    skyplot(gnss)
    pass


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
