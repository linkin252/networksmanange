# -*- coding: utf-8 -*-
import numpy as np
# import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

from matplotlib.font_manager import FontProperties  # 字体管理器

import obspy
from obspy.io.xseed.parser import Parser
from obspy import read_inventory
from obspy.signal.invsim import paz_to_freq_resp


def plot_Freq_Amp_Phase(pltfile, paz, sName, type):
    poles = paz['poles']
    zeros = paz['zeros']
    scale_fac = paz['gain'] * paz['seismometer_gain']

    if (1000 <= type and type < 2000):
        h, f = paz_to_freq_resp(poles, zeros, scale_fac, 0.005, 65536 * 8, freq=True)
    elif (2000 <= type):
        h, f = paz_to_freq_resp(poles, zeros, scale_fac, 0.001, 65536 * 8, freq=True)
    else:
        h, f = paz_to_freq_resp(poles, zeros, scale_fac, 0.001, 65536 * 8, freq=True)

    font = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=12)
    fontTitle = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=18)
    plt.figure(figsize=(16, 12))
    # plt.xlim(0.001,  100)
    plt.subplot(211)
    plt.grid(linestyle=':')
    plt.loglog(f, abs(h))
    plt.xlabel('频率[Hz]', fontproperties=font)
    if 1000 <= type < 2000:
        plt.ylabel('增益[V/(m/s)]', fontproperties=font)
    elif 2000 <= type:
        plt.ylabel('增益[V/(m/s**2)]', fontproperties=font)
    else:
        plt.ylabel('增益', fontproperties=font)
    plt.subplot(212)
    plt.grid(linestyle=':')
    phase = np.unwrap(np.angle(h))
    fTt = 0
    for p0 in phase:
        fTt += p0
    fAver = fTt / len(phase)
    if (fAver <= -np.pi):
        phase += 2 * np.pi
    elif (fAver > np.pi):
        phase -= 2 * np.pi

    import datetime
    timestr = datetime.datetime.now().strftime('%Y-%m-%d')
    timestr = "Created by 泰德, " + timestr
    x0 = '                                                                   频率[Hz]                                         ' + timestr

    plt.semilogx(f, phase)
    # plt.xlabel('频率[Hz]',fontproperties=font)
    plt.xlabel(x0, fontproperties=font)
    plt.ylabel('相位[rad]', fontproperties=font)
    # ticks and tick labels at multiples of pi
    plt.yticks(
        [-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi],
        [r'$-\pi$', r'$-\frac{\pi}{2}$', '$0$', r'$\frac{\pi}{2}$', r'$\pi$'])
    plt.ylim(-0.2 - np.pi, np.pi + 0.2)
    # title, centered above both subplots
    if (1000 <= type and type < 2000):
        plt.suptitle('%s 地震计幅频相频响应' % (sName), fontproperties=fontTitle)
    elif (2000 <= type):
        plt.suptitle('%s 加速度计幅频相频响应' % (sName), fontproperties=fontTitle)
    else:
        plt.suptitle('仪器 %s 幅频相频响应' % (sName), fontproperties=fontTitle)

    # import datetime
    # timestr = datetime.datetime.now().strftime('%Y-%m-%d')
    # timestr = "Created by TAIDE, " + timestr
    # plt.text(10.6,-4.2,timestr,fontsize=12)

    # make more room in between subplots for the ylabel of right plot
    plt.subplots_adjust(wspace=0.1)
    plt.savefig(pltfile)
    plt.close('all')


# def (Ymax,Ymin,Tmax,Tmin,Tzero) = plot_Seep_Response(pltfile, paz):
def plot_Seep_Response(pltfile, paz, sName, type):
    poles = paz['poles']
    zeros = paz['zeros']
    scale_fac = paz['gain'] * paz['seismometer_gain']
    from scipy import signal
    system = (zeros, poles, scale_fac)
    t, y = signal.step(system, N=10000)
    fStep = t[len(t) - 1] / len(y)
    y[0] = 0

    if (1000 <= type and type < 2000):
        for i in range(1, len(y)):
            y[i] = y[i - 1] + y[i] * fStep * 0.001  # 输出太大，按 0.001m/s**2 响应计算

    Ymax = max(y)
    Ymin = min(y)
    Tmax = Tmin = Tzero = 0
    index = 0
    for index in range(2, len(y)):
        if (y[index] >= Ymax and Tmax == 0):
            Tmax = index * fStep
        if (y[index] <= Ymin and Tmin == 0):
            Tmin = index * fStep
        if (y[index] * y[index - 1] <= 0 and Tzero == 0):
            Tzero = index * fStep
    if (1000 <= type and type < 2000):
        sInfo = '%s 地震计阶跃理论响应(等效激励=1mm/s**2)\n T=%.3fs:Vmax=%.3fV,  T=%.3fs:V=0,  T=%.3fs:Vmin=%.3fV' \
                % (sName, Tmax, Ymax, Tzero, Tmin, Ymin)
    elif (2000 <= type):
        sInfo = '%s 加速度计阶跃理论响应(等效激励=1m/s**2)' % (sName)
    else:
        sInfo = '仪器 %s 阶跃理论响应' % (sName)

    font = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=12)
    fontTitle = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=18)
    plt.figure(figsize=(16, 12))
    plt.grid(linestyle=':')

    import datetime
    timestr = datetime.datetime.now().strftime('%Y-%m-%d')
    timestr = "Created by 泰德, " + timestr
    x0 = '                                                                    时间(s)                                          ' + timestr
    plt.xlabel(x0, fontproperties=font)
    plt.ylabel('幅度(V)', fontproperties=font)
    plt.suptitle(sInfo, fontproperties=fontTitle)
    plt.plot(t, y)

    # plt.text(1400,200,timestr,fontsize=12,xycoords='•axes pixels')
    # dict0 = dict[width:0,headwidth:0,headlength:0,shrink:0,facecolor:'white']
    # plt.annotate(s=timestr, xy=(1400,200), xytext=(0, 0),xycoords='•axes pixels',arrowprops=dict0)

    plt.savefig(pltfile)
    plt.close('all')
    return (Ymax, Ymin, Tmax, Tmin, Tzero)


def parser_sensor_resp(dir, sName, type):
    par = Parser(dir + '.resp')
    par.write_xseed(dir + '.xml')
    par.write_seed(dir + '.dataless')

    channel = par.blockettes[52][0].channel_identifier
    paz = par.get_paz(channel)
    if (len(paz['zeros']) <= len(paz['poles'])):
        plot_Freq_Amp_Phase(dir + '.freq_amp_phase.png', paz, sName, type)
        (Ymax, Ymin, Tmax, Tmin, Tzero) = plot_Seep_Response(dir + '.impulse.png', paz, sName, type)
        return (paz, Ymax, Ymin, Tmax, Tmin, Tzero)
    else:
        print(
            "sName Error! , zeros number is larger than poles, Can't Calculate Response and Bode Diagram, Check it!!!")
        return (paz, 0, 0, 0, 0, 0)


def plot_Digitizer_Freq_Amp(pltfile, sName, sample_rate, sensitivity, h, f):
    font = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=12)
    fontTitle = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=18)
    plt.figure(figsize=(16, 12))
    plt.grid(linestyle=':')
    plt.semilogy(f, abs(h))

    import datetime
    timestr = datetime.datetime.now().strftime('%Y-%m-%d')
    timestr = "Created by 泰德, " + timestr
    x0 = '                                                                   频率[Hz]                                         ' + timestr
    plt.xlabel(x0, fontproperties=font)
    plt.ylabel('增益[Ct/V]', fontproperties=font)
    plt.title('%s 理论幅频响应\n (采样速率：%sSPS，归一化增益：%sCt/V)\n' % (sName, sample_rate, sensitivity), fontproperties=fontTitle)
    plt.savefig(pltfile)
    plt.close('all')


def parser_digitizer_resp(dir, sName):
    filename = dir + '.resp'
    par = Parser(filename)
    par.write_xseed(dir + '.xml')
    par.write_seed(dir + '.dataless')

    channel = par.blockettes[52][0].channel_identifier
    sample_rate = par.blockettes[52][0].sample_rate
    paz = par.get_paz(channel)
    sensitivity = paz['digitizer_gain']
    if (sample_rate < 1):
        sample_rate = 1

    inv = read_inventory(filename, "RESP")
    resp = inv[0][0][0].response
    # print(resp)
    response, freqs = resp.get_evalresp_response(1. / (sample_rate * 2.), 65536 * 16, output="VEL")
    plot_Digitizer_Freq_Amp(dir + '.freq_amp.png', sName, sample_rate, sensitivity, response, freqs)
    return (sample_rate, sensitivity)


"""
dir = 'D:\\django\\taide\\static\\instruments\\digitizer\\taide\\TDE-324\\taide_TDE-324_10Vpp_100Hz_Linear'
sName = "泰德 TDE324CI"
(sample_rate,sensitivity) = parser_digitizer_resp(dir,sName)
print(sample_rate,sensitivity)

dir = 'D:\\django\\taide\\static\\instruments\\digitizer\\taide\\TDE-324\\taide_TDE-324___-10V_100Hz_Linear'
sName = "泰德 TDE324CI"
(sample_rate,sensitivity) = parser_digitizer_resp(dir,sName)
print(sample_rate,sensitivity)

#dir= "D:\\django\\taide\\static\\resource\\IRIS\\dataloggers\\taide.old\\RESP.XX.GD001..HHZ.TDE324.1.40.200.LP"
dir = 'D:\\django\\taide\\static\\instruments\\digitizer\\taide\\TDE-324\\taide_TDE-324___-10V_100Hz_Linear.resp'
#dir ='D:\\django\\taide\\static\\instruments\\digitizer\\geotech\\SMART24\\geotech_SMART24_40_Vpp_1_200_Hz_200_Hz_Linear'
sName = "泰德 TDE324CI"
(sample_rate,sensitivity) = parser_digitizer_resp(dir,sName)
print(sample_rate,sensitivity)
"""
