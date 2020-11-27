# -*- coding: utf-8 -*-
import configparser
import os
import re
import platform
import struct
import sys, getopt

import math
import numpy as np
import obspy
from obspy import read
import datetime
from array import array
from matplotlib.font_manager import FontProperties  # 字体管理器
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams["legend.loc"] = 'best'

SEN_TYPE = ''
#mpl.rcParams['axes.unicode_minus']=False #用来正常显示负号
#mpl.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
#plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签

if platform.system() == 'Windows':
    PLATFORM = 'Windows'
    SQL_PATH = 'D:/django/trunk/db.sqlite3'
    MON_PATH = 'D:/django/trunk/params/monitor.ini'
    PI_PATH = 'D:/django/trunk/params/pi.ini'
    RES_PATH = 'D:/django/trunk/params/response.ini'
    CAL_PATH = 'D:\\LK\\86.40新镜像程序\\源数据\\cal'
    EVENT_PATH = 'D:\\LK\\86.40新镜像程序\\源数据\\event'
elif platform.system() == 'Linux':
    PLATFORM = 'Linux'
    SQL_PATH = '/home/usrdata/usb/django/taide/db.sqlite3'
    MON_PATH = '/home/usrdata/pi/tde/params/monitor.ini'
    PI_PATH = '/home/usrdata/pi/tde/params/pi.ini'
    RES_PATH = '/home/usrdata/pi/tde/params/response.ini'
    CAL_PATH = '/home/usrdata/usb/log/cal'
    EVENT_PATH = '/home/usrdata/usb/log/event'

def setFont():
    if PLATFORM == "Windows":
        font = FontProperties(fname=r"c:\\windows\\fonts\\simhei.ttf",size=9)
        fontTitle = FontProperties(fname=r"c:\\windows\\fonts\\simhei.ttf",size=12)
    else:
        font = FontProperties(fname=r"/usr/share/fonts/SIMHEI.TTF", size=9)
        fontTitle = FontProperties(fname=r"/usr/share/fonts/SIMHEI.TTF", size=12)
    return (font,fontTitle)

def get_median(data):
    data.sort()
    half = len(data) // 2
    return (data[half] + data[~half]) / 2


def split21space(line):
    line = re.sub(r"[\/\\\:\*\|\t\,\n\r]", ' ',line).strip()
    line = re.sub(' +', ' ', line)
    return line

#  parserPar --  解析参数文件
def parserPar(parfile):
    fTBlank = array('f',range(0))
    fTWork  = array('f',range(0))
    fGain = array('f',range(0))
    fFreq = array('f',range(0))
    SinOrPulse = 'ERR'

    cal_num = 1
    try:
        nId = -1
        f = open(parfile, 'rt')
        l0 = f.readline()
        line = f.readline()
        lines = f.readlines()
        f.close()

        nId = 0
        l0 = split21space(l0).lower()
        sRandom_Sec = '0.'

        #print(l0)
        if (l0[0]=='p'):   # pulse
            SinOrPulse = 'pulse'
        elif (l0[0]=='s'): # sin
            SinOrPulse = 'sin'
        elif (l0[0]=='r'): #random
            SinOrPulse = 'random'
            l0 = split21space(l0)
            (sMode, sRandom_Sec) = l0.split(' ')

        line = split21space(line)
        lenline = len(line.split(' '))
        if lenline > 5:
            global SEN_TYPE
            (sNetMode, sCalMode, cal_input, ad_stvt, sCalNum, SEN_TYPE) = line.split(' ')
        else:
            (sNetMode, sCalMode, cal_input, ad_stvt, sCalNum) = line.split(' ')
        cal_num = int(sCalNum)
        cal_stvt = array('f',range(cal_num))
        #cal_stvt = float(cal_stvt)
        cal_input = float(cal_input)
        ad_stvt = float(ad_stvt)
        fRandom_Sec = float(sRandom_Sec)

        print('Cal Mode=%s Mode.' % SinOrPulse)
        if (sNetMode.lower()[0] == 'a'):
            nNetMode = 'A'
            print('Sensor Mode: Accelerometer.')
        else:
            nNetMode = 'V'
            print('Sensor Mode: Seismometer.')
        if (sCalMode.lower()[0] == 'v'):
            nCalMode = 'V'
            print('Input mode: Voltage Mode.')
        else:
            nCalMode = 'A'
            print('Input mode: Current Mode.')
        print('Cal Input=%f%s.  Digitizer Sensitivity=%fCt/V, channel Num=%d'
              % (cal_input, nCalMode, ad_stvt, len(cal_stvt)))

        nId = 1
        nReadId = 0
        for line in lines:
            line = split21space(line)
            if (nReadId<cal_num):
                cal_stvt[nReadId] = float(line)
            elif (SinOrPulse=='sin'):
                num = line.count(' ')
                if (num!=3):
                    print('Line:%d read error!' % nId+1)
                    nId += 1
                    continue
                (fTb,fF,fTw,fG) = line.split(' ')
                fTBlank.append(float(fTb))
                fTWork.append(float(fTw))
                fGain.append(float(fG))
                fFreq.append(1./float(fF))
                #print(fTBlank[nId-1],fTWork[nId-1],fGain[nId-1],fFreq[nId-1])
            nReadId += 1
            nId+=1

        for i in range(len(cal_stvt)):
            print("Cal_Sensitivity[%d] = %f m/s**2/%s" % (i, cal_stvt[i], nCalMode))

    except Exception as e:
        print("Read Par File Error,Line:%d,Err:%s" % (nId+1,e))
        if (nId<2+cal_num):
            fStart = array('f',range(0))
            fEnd = array('f', range(0))
            fTm0 = array('f', range(0))
            return(SinOrPulse,'ERR',"ERR",cal_stvt,cal_input,ad_stvt,fTm0,fStart,fEnd,fGain,fFreq,fRandom_Sec)

    if (SinOrPulse=='sin'):
        nLen = len(fFreq)
        fStart = array('f',range(nLen))
        fEnd = array('f',range(nLen))
        fTm0 = array('f',range(nLen))
        fTm0[0] = fTBlank[0]
        for i in range(1,nLen):
            fTm0[i] = fTm0[i-1] + fTWork[i-1] + fTBlank[i]
        for i in range(0,nLen):
            fT0 = fTm0[i]
            fPd2 = 0.5/fFreq[i]
            if (fTWork[i]<=5):
                fBk = 1
            elif (fTWork[i]<=10):
                fBk = 3
            elif (fTWork[i]<=30):
                fBk = 5
            elif (fTWork[i]<=60):
                fBk = 5
            elif (fTWork[i]<=120):
                fBk = 5
            elif (fTWork[i]<=300):
                fBk = 5
            else:
                fBk = 5
            if (fPd2*2>1.):
                if (fBk<=fPd2+0.1):
                    fBk = fPd2
                elif (fBk<=fPd2*2+0.1):
                    fBk = fPd2 * 2
                elif (fBk<=fPd2*3+0.1):
                    fBk = fPd2 * 3
                elif (fBk<=fPd2*4+0.1):
                    fBk = fPd2 * 4
                elif (fBk<=fPd2*5+0.1):
                    fBk = fPd2 * 5
                elif (fBk<=fPd2*5+0.1):
                    fBk = fPd2 * 5
                elif (fBk<=fPd2*6+0.1):
                    fBk = fPd2 * 6
                elif (fBk<=fPd2*7+0.1):
                    fBk = fPd2 * 7
                elif (fBk<=fPd2*8+0.1):
                    fBk = fPd2 * 8
                elif (fBk<=fPd2*9+0.1):
                    fBk = fPd2 * 9
                elif (fBk<=fPd2*10+0.1):
                    fBk = fPd2 * 10

            fStart[i] = fT0 + fBk
            fEnd[i] = fT0 + fTWork[i] - fBk

            #print(fTBlank[i],fTWork[i],fStart[i],fEnd[i],fGain[i],fFreq[i])
    else:
        fStart = array('f',range(0))
        fEnd = array('f', range(0))
        fTm0 = array('f', range(0))

    return (SinOrPulse,nNetMode,nCalMode,cal_stvt,cal_input,ad_stvt,fTm0,fStart,fEnd,fGain,fFreq,fRandom_Sec)

def getFE(fSrc,nMaxId):
    nLen = len(fSrc)
    nHLen = nLen // 2
    # 1.1 FFT 取模并并归一化
    fSrc_f = np.fft.fft(fSrc)
    fAngle = np.angle(fSrc_f[nMaxId])
    fSrc_a = np.abs(fSrc_f) / nHLen
    # 1.2 数据取半波并将零点归零
    fSrc_ha = fSrc_a[range(nHLen)]
    fSrc_ha[0] = 0
    fSrc_ha[1] = 0
    #1.3 获取最大值幅值的频率，得到主频，并检验主频是否是输入点
    maxSrcId = np.argmax(fSrc_ha)
    ndoCt = 0
    while (np.abs(nMaxId-maxSrcId)>3 and ndoCt<nHLen):
        maxSrcId = np.argmax(fSrc_ha)
        fSrc_ha[maxSrcId] = 0
        ndoCt += 1
    #print(maxSrcId, nMaxId, ndoCt)
    #1.4 获取主频旁瓣和三次谐波的能量加和
    fSrc_e = 0.
    for k in range(1,4):
        nBegId = maxSrcId*k - 3
        if (nBegId>=nHLen):
            break
        if (nBegId<0):
            nBegId = 0
        nEndId = maxSrcId*k + 4
        if (nEndId > nHLen):
            nEndId = nHLen
        for i in range(nBegId, nEndId):
            fSrc_e += (fSrc_ha[i] * fSrc_ha[i])
    fSrc_e = math.sqrt(fSrc_e)
    #if (maxSrcId*3<nHLen):
    #    print(fSrc_e,fSrc_ha[maxSrcId],fSrc_ha[maxSrcId*2],fSrc_ha[maxSrcId*3])
    #else:
    #    print(fSrc_e, fSrc_ha[maxSrcId])

    #1.4 返回主频能量值
    return (fSrc_e,fAngle)

def getFE2(fSrc,nMaxId):
    nLen = len(fSrc)
    nHLen = nLen // 2
    # 1.1 FFT 取模并并归一化
    fSrc_f = np.fft.fft(fSrc)
    fSrc_a = np.abs(fSrc_f) / nHLen
    # 1.2 数据取半波并将零点归零
    fSrc_ha = fSrc_a[range(nHLen)]
    fSrc_ha[0] = 0
    #1.2 获取最大值幅值的频率，得到主频，并检验主频是否是输入点
    maxSrcId = np.argmax(fSrc_ha)
    while (np.abs(nMaxId-maxSrcId)>3):
        maxSrcId = np.argmax(fSrc_ha)
        print(maxSrcId,nMaxId)
        fSrc_ha[maxSrcId] = 0
    #1.3 获取主频旁瓣和三次谐波的能量加和
    fSrc_e = 0.
    for i in range(nHLen):
        fSrc_e +=  (fSrc_ha[i] * fSrc_ha[i])
    fSrc_e = math.sqrt(fSrc_e)

    if (maxSrcId*3<nHLen):
        print(fSrc_e,fSrc_ha[maxSrcId],fSrc_ha[maxSrcId*2],fSrc_ha[maxSrcId*3])
    else:
        print(fSrc_e, fSrc_ha[maxSrcId])
    #1.4 返回主频总能量值
    return (fSrc_e)

def getFE3(fSrc,nMaxId):
    nLen = len(fSrc)
    #1.3 获取主频旁瓣和三次谐波的能量加和
    fSrc_e = 0.
    for i in range(nLen):
        fSrc_e +=  (fSrc[i] * fSrc[i])
    fSrc_e = math.sqrt(fSrc_e)
    #1.4 返回主频总能量值
    return (fSrc_e,0)

def getFE4(fSrc):
    nLen = len(fSrc)
    nHLen = nLen // 2
    # 1.1 FFT 取模并并归一化
    fSrc_f = np.fft.fft(fSrc)
    fSrc_a = np.abs(fSrc_f) / nHLen    # 对应频点的能量
    fAngle = np.angle(fSrc_f)
    return(fSrc_a,fAngle)

def doCalSin(st0,figfile,outfile,
             nNetMode, nCalMode, cal_stvt, cal_input, ad_stvt, fTm0, fStart, fEnd, fGain, fFreq,
             nTxtMode=0,language='chinese',nSaveMode=0,pdf=None):
    sps = st0.stats.sampling_rate
    nSPS = int(sps + 0.5)
    npts = st0.stats.npts
    t_start = st0.stats.starttime.datetime
    print("sps=%f, ntps=%d \n" % (sps,npts))
    data = st0.data
    #  设置相对应的时间数组，用于画图
    time = np.zeros(npts)
    time[0] = 0
    for i in range(1, npts):
        time[i] = i / sps
    sName = st0.stats.network+ '.'+ st0.stats.station + '.'+ st0.stats.location + '.' + st0.stats.channel
    t_new = t_start.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
    sTime = t_new.strftime('%Y-%m-%d %H:%M:%S')

    (font, fontTitle) = setFont()
    plt.grid(linestyle=':')
    # 检测数据是否在范围内，不在的话就不处理
    nLen = len(fFreq)
    if (fEnd[nLen - 1] > npts / sps):
        plt.figure(figsize=(12, 9))
        if (language == 'english'):
            sInfo = u'%s %s %sseismometer sin File size eroor，simulation wrong\n ' % (sTime, sName, SEN_TYPE)
            sLabels = u'source data'
        else:
            sInfo = u'%s %s %s地震计正弦数据长度不够，不能仿真\n ' % (sTime, sName, SEN_TYPE)
            sLabels = u'原始数据'
        print("file %s data length Error. need length = %fs, file length=%fs" % (sName, fEnd[nLen - 1], npts / sps))
        plt.suptitle(sInfo, fontproperties=fontTitle)
        plt.plot(time, data, c='blue', label=sLabels)
        plt.legend(prop=font)

        if (nSaveMode == 0):
            pdf.savefig()
        else:
            plt.savefig(figfile)
        plt.close('all')
        cal_freq = array('f', range(0))
        cal_gain = array('f', range(0))
        return (cal_freq, cal_gain)

    # 将所有数据转化为标准电压值，包括基准信号
    fVOut = np.zeros(npts)
    for i in range(npts):
        fVOut[i] = data[i] / ad_stvt;  # 将数据输出单位从 Ct 转化为电压值

    # 计算标定产生的电压值
    cal_v = array('f', range(nLen))
    cal_a = array('f', range(nLen))
    cal_in = array('f', range(nLen))
    cal_gain = array('f', range(nLen))
    for k in range(nLen):
        nEnd = int(fEnd[k] * nSPS)
        nStart = int(fStart[k] * nSPS)
        nFFTT0 = nEnd - nStart
        fSrc = np.zeros(nFFTT0)
        fRef = np.zeros(nFFTT0)

        for j in range(nStart, nEnd):
            fSrc[j - nStart] = fVOut[j]  # * win[j-nStart]
            if (fFreq[k]<(sps/2.-0.01)):
                fRef[j - nStart] = -math.sin(2 * math.pi * fFreq[k] * (j / sps - fTm0[k]))
            else:
                fRef[j - nStart] = -math.sin(2 * math.pi * (j / sps - fTm0[k]))  # * win[j-nStart]
        # print('k1=%d,aver1=%f,aver2=%f' % (k,aver1,aver2))
        fSrc = fSrc - np.mean(fSrc)
        fRef = fRef - np.mean(fRef)

        if (fFreq[k] * 2<(sps-0.01)):      # 信号频点在带外则计算单点频
            (fSrc_e,fSrc_a) = getFE(fSrc, int(fFreq[k] * nFFTT0 / nSPS + 0.5))
            (fRef_e,fRef_a) = getFE(fRef, int(fFreq[k] * nFFTT0 / nSPS + 0.5))
        else:   # 信号频点在带外则计算总能力
            (fSrc_e,fSrc_a) = getFE3(fSrc, int(fFreq[k] * nFFTT0 / nSPS + 0.5))
            (fRef_e,fRef_a) = getFE3(fRef, int(fFreq[k] * nFFTT0 / nSPS + 0.5))
        cal_v_temp = fSrc_e / (fRef_e+1e-10)  # 标定输出，V
        #cal_v[k] = fSrc_e / (fRef_e + 1e-10)  # 标定输出，V
        cal_a[k] = fSrc_a - fRef_a

        #修正了相位后再做一次计算
        for j in range(nStart, nEnd):
            if (fFreq[k]<(sps/2.-0.01)):
                fRef[j - nStart] = -math.sin(cal_a[k] + 2 * math.pi * fFreq[k] * (j / sps - fTm0[k]))
                #fRef[j - nStart] = -math.sin(2 * math.pi * fFreq[k] * (j / sps - fTm0[k]))
            else:
                fRef[j - nStart] = -math.sin(2 * math.pi * (j / sps - fTm0[k]))  # * win[j-nStart]
        fRef = fRef - np.mean(fRef)
        win = np.kaiser(nFFTT0, 5)
        for j in range(0, nEnd - nStart):
            fSrc[j] = fSrc[j]  * win[j]
            fRef[j] = fRef[j]  * win[j]
        # plt.plot(fSrc)
        # plt.plot(fRef)
        # plt.show()
        if (fFreq[k] * 2<(sps-0.01)):      # 信号频点在带外则计算单点频
            (fSrc_e,fSrc_a) = getFE(fSrc, int(fFreq[k] * nFFTT0 / nSPS + 0.5))
            (fRef_e,fRef_a) = getFE(fRef, int(fFreq[k] * nFFTT0 / nSPS + 0.5))
        else:   # 信号频点在带外则计算总能力
            (fSrc_e,fSrc_a) = getFE3(fSrc, int(fFreq[k] * nFFTT0 / nSPS + 0.5))
            (fRef_e,fRef_a) = getFE3(fRef, int(fFreq[k] * nFFTT0 / nSPS + 0.5))
        cal_v[k] = fSrc_e / (fRef_e+1e-10)  # 标定输出，V
        #print('1st.=%f, 2nd.=%f, ratio=%f' % (cal_v_temp,cal_v[k],cal_v[k]/cal_v_temp))

        # 1.标定灵敏度*标定电流=m/s**2/A * A=m/s**2
        if (nNetMode == 'V'):
            # 2.1  v=∫a*sin(w*t) dt = ∫a*sin(2*pi*f*t) dt = a*cos(2*pi*f*t)/(2*pi*f)
            cal_in[k] = cal_stvt * cal_input * fGain[k] / (2 * math.pi * fFreq[k])  # 单位：m/s
        else:
            # 2.1  a*sin(w*t)
            cal_in[k] = cal_stvt * cal_input * fGain[k]  # 单位：m/s**2
        cal_gain[k] = cal_v[k] / cal_in[k]

    # for k in range(nLen):
    #    if (nNetMode=='V'):
    #        print('Freq=%fHz, vout=%fV, Calin=%fm/s, gain=%fV/(m/s)' % (fFreq[k],cal_v[k],cal_in[k],cal_gain[k]))
    #    else:
    #        print('Freq=%fHz, vout=%fV, Calin=%fm/s**2, gain=%fV/(m/s**2)' % (fFreq[k],cal_v[k],cal_in[k],cal_gain[k]))

    # 开始画图
    plt.figure(figsize=(12, 16))
    if (language == 'english'):
        sLabels0 = u'source data'
        sLabels1 = u'Simu. Data'
        if (nNetMode == 'V'):
            sInfo = u'%s %s %sseismometer sin response diagram\n' \
                    'Cal. Input=%.5f%s, Cal. Sensitivity=%em/s**2/%s，Digitizer Sensitivity=%.1fCt/V' \
                    % (sTime, sName, SEN_TYPE, cal_input, nCalMode, cal_stvt, nCalMode, ad_stvt)
        else:
            sInfo = u'%s %s %saccelerometer sin response diagram\n' \
                    'Cal. Input=%.5f%s, Cal. Sensitivity=%em/s**2/%s，Digitizer Sensitivity=%.1fCt/V' \
                    % (sTime, sName, SEN_TYPE, cal_input, nCalMode, cal_stvt, nCalMode, ad_stvt)
    else:
        sLabels0 = u'原始数据'
        sLabels1 = u'仿真数据'
        if (nNetMode == 'V'):
            sInfo = u'%s %s %s地震计正弦标定响应\n' \
                    '标定输入=%.5f%s, 标定灵敏度=%em/s**2/%s，数采灵敏度=%.1fCt/V' \
                    % (sTime, sName, SEN_TYPE, cal_input, nCalMode, cal_stvt, nCalMode, ad_stvt)
        else:
            sInfo = u'%s %s %s加速度计正弦标定响应\n' \
                    '标定输入=%.5f%s, 标定灵敏度=%em/s**2/%s，数采灵敏度=%.1fCt/V' \
                    % (sTime, sName, SEN_TYPE, cal_input, nCalMode, cal_stvt, nCalMode, ad_stvt)
    sInfo1 = "\n\n" + sInfo
    plt.suptitle(sInfo1, fontproperties=fontTitle)

    ax = plt.subplot(211)
    plt.grid(linestyle='-', which="major")
    plt.grid(linestyle=':', which="minor")
    timestr = datetime.datetime.now().strftime('%Y-%m-%d')
    if (language == 'english'):
        timestr = "Created by TAIDE, " + timestr
    else:
        timestr = "Created by 泰德, " + timestr

    if (language == 'english'):
        ax.set_title("Amplitude - Frequency Response Diagram", fontproperties=fontTitle)
        x0 = '                                                                   Freq[Hz]                                         ' + timestr
        plt.xlabel(x0, fontproperties=font)
        if (nNetMode == 'V'):
            plt.ylabel('Gain[V/(m/s)]', fontproperties=font)
        else:
            plt.ylabel('Gain[V/(m/s**2)]', fontproperties=font)
    else:
        ax.set_title("幅频特性", fontproperties=fontTitle)
        x0 = '                                                                   频率[Hz]                                         ' + timestr
        plt.xlabel(x0, fontproperties=font)
        if (nNetMode == 'V'):
            plt.ylabel('增益[V/(m/s)]', fontproperties=font)
        else:
            plt.ylabel('增益[V/(m/s**2)]', fontproperties=font)
    plt.loglog(fFreq, cal_gain, c='blue', label=sLabels0, marker='.')
    #plt.semilogx(fFreq, cal_gain, c='blue', label=sLabels0, marker='.')

    plt.legend(prop=font)

    ax = plt.subplot(212)
    plt.grid(linestyle=':')
    if (language == 'english'):
        ax.set_title("Simulation Data", fontproperties=fontTitle)
        x0 = '                                                                   Time[s]                                         ' + timestr
        plt.xlabel(x0, fontproperties=font)
        plt.ylabel('Signal[Ct]', fontproperties=font)
    else:
        ax.set_title("仿真计算结果", fontproperties=fontTitle)
        x0 = '                                                                   时间[s]                                         ' + timestr
        plt.xlabel(x0, fontproperties=font)
        plt.ylabel('信号[Ct]', fontproperties=font)
    plt.plot(time, data, c='blue', label=sLabels0)

    # 校验结果并输出文本文件
    fErr = np.zeros(nLen)
    for k in range(nLen):
        nEnd = int(fEnd[k] * nSPS)
        nStart = int(fStart[k] * nSPS)
        nCalCt = nEnd - nStart
        fCal = np.zeros(nCalCt)
        fT0 = np.zeros(nCalCt)
        fTSrc = np.zeros(nCalCt)

        fAver = 0.
        for j in range(nCalCt):
            fAver += float(data[int(fStart[k]*sps)+j])
        fAver /= nCalCt

        gain = cal_in[k] * cal_gain[k] * ad_stvt
        for j in range(nCalCt):
            fT0[j] = fStart[k] + j / sps
            if (fFreq[k]<(sps/2.-0.01)):
                fCal[j] = fAver - math.sin(cal_a[k] +
                    2 * math.pi * fFreq[k] * (j / sps + (fStart[k] - fTm0[k]))) * gain
            else:
                fCal[j] = fAver - math.sin(
                    2 * math.pi            * (j / sps + (fStart[k] - fTm0[k]))) * gain
            fTSrc[j] = data[int(fStart[k] * sps) + j]
        if (k == 0):
            plt.plot(fT0, fCal, ls = '-', lw= .6 , c='red', label=sLabels1)
            plt.legend(prop=font)
        else:
            plt.plot(fT0, fCal, ls = '-', lw= .6 , c='red')

        fCal -= np.mean(fCal)
        fTSrc -= np.mean(fTSrc)
        fSrc_e = 0
        fCal_e = 0
        for j in range(nCalCt):
            fCal_e += fCal[j] * fCal[j]
            fSrc_e += fTSrc[j] * fTSrc[j]
        fCal_e = math.sqrt(fCal_e)
        fSrc_e = math.sqrt(fSrc_e)
        fErr[k] = np.abs(fCal_e - fSrc_e) / fSrc_e
        # fMaxCal = np.max(fCal)
        # fMinCal = np.min(fCal)
        # fMaxSrc = np.max(fTSrc)
        # fMinSrc = np.min(fTSrc)
        # print (fSrc_e/fCal_e,fCal_e,fSrc_e,fMaxCal,fMinCal,fMaxSrc,fMinSrc)

    if (nSaveMode==0):
        pdf.savefig()
    else:
        plt.savefig(figfile)
    plt.close('all')

    if (nTxtMode==0):
        f = open(outfile, "wt")
    else:
        f = open(outfile, "at")
        f.write("\n\n")

    f.write("%s\n" % sInfo);
    print(sInfo)
    if (nNetMode == 'V'):
        f.write('频率  增益  phase  fErr\nHz  V/(m/s)  °  %%\n')
        print('频率  增益  phase  fErr\nHz  V/(m/s)  °  %%\n')
    else:
        f.write('频率  增益  phase  fErr\nHz  V/(m/s**2)  °  %%\n')
        print('频率  增益  phase  fErr\nHz  V/(m/s**2)  °  %%\n')
    for k in range(nLen):
        if (nNetMode == 'V'):
            sInfo = '%f  %f   %f  %f' % (fFreq[k], cal_gain[k], cal_a[k]*180/math.pi,fErr[k] * 100.)
            f.write('%s\n' % sInfo)
            print(sInfo)
        else:
            sInfo = '%f  %f   %f  %f' % (fFreq[k], cal_gain[k], cal_a[k]*180/math.pi,fErr[k] * 100.)
            f.write('%s\n' % sInfo)
            print(sInfo)
    f.close()
    return ( fFreq, cal_gain)




def get_median(data):
    data.sort()
    half = len(data) // 2
    return (data[half] + data[~half]) / 2

# 构造特征函数
def Initddt2(dt,npts):
    ddt2 = [0.] * npts
    for i in range(1, npts - 1):
        ddt2[i] = float(dt[i]) * float(dt[i]) - float(dt[i - 1]) * float(dt[i + 1])
        ddt2[i] = ddt2[i]*ddt2[i]  #math.pow(ddt2[i],2)
    ddt2[0] = ddt2[1]
    ddt2[i-1] = ddt2[i-2]
    return ddt2

#ARAIC 找到新的最佳位置（P波初动 & S波初动）
def  ARAIC(outname,dt,npts,nMaxIndex,nPreCt=300,nAftCt=300):
    ddt2 = Initddt2(dt,npts)
    ddt3 = [0.] * npts
    for i in range(nMaxIndex-nPreCt+1,nMaxIndex+nAftCt-1):
        sigma1 = sigma2 = 0
        nCt1=nCt2 = 0
        for j in range(nMaxIndex-nPreCt,i):
            sigma1 = sigma1 + ddt2[j]
            nCt1 += 1
        sigma1 /= nCt1
        for j in range(i,nMaxIndex+nAftCt):
            sigma2 = sigma2 + ddt2[j]
            nCt2 += 1
        sigma2 /= nCt2
        ddt3[i] = (i-nMaxIndex+nPreCt) * math.log10(sigma1) + (nMaxIndex+nPreCt-i) * math.log10(sigma2)

    fMin = 1e100
    nNewIndex = nMaxIndex
    for i in range(nMaxIndex-nPreCt+1,nMaxIndex+nAftCt-1):
        if (ddt3[i]<fMin):
            nNewIndex = i;
            fMin = ddt3[i];

    #f = open(outname,'wt')
    #for i in range(nMaxIndex-nPreCt+1,nMaxIndex+nAftCt-1):
    #    f.write("dt[%d]=%f, ddt3[%d]=%f \n" % (i,dt[i],i,ddt3[i]))
    #f.close()

    return nNewIndex;

#ARAIC 找到新的最佳位置（P波初动 & S波初动）
def  ARAIC2(dt,npts,nStartCt,nEndCt):
    ddt2 = Initddt2(dt,npts)
    ddt3 = [0.] * npts
    for i in range(nStartCt+10,nEndCt-10):
        sigma1 = sigma2 = 0
        nCt1=nCt2 = 0
        for j in range(nStartCt,i):
            sigma1 = sigma1 + ddt2[j]
            nCt1 += 1
        sigma1 /= nCt1
        for j in range(i,nEndCt):
            sigma2 = sigma2 + ddt2[j]
            nCt2 += 1
        sigma2 /= nCt2
        ddt3[i] = (i-nStartCt) * math.log10(sigma1) + (nEndCt-i) * math.log10(sigma2)

    fMin = 1e100
    nNewIndex = nStartCt
    for i in range(nStartCt+30,nEndCt-30):
        if (ddt3[i]<fMin):
            nNewIndex = i;
            fMin = ddt3[i];

    #outname2 =  "d:\\ab2.txt"
    #f = open(outname2,'at')
    #for i in range(nStartCt+1,nEndCt-1):
    #    f.write("dt[%d]=%f, ddt3[%d]=%f \n" % (i,dt[i],i,ddt3[i]))
    #f.close()
    return nNewIndex;

#=================================================================
# CalSensitivity 标定等效加速度值，国际标准单位： m/s^2   ，不论加速度计还是速度计
#=================================================================
def CalAccPulse(st0,outname,fCalIn=1.0,fCalStvt=1.0,fADStvt=1.0,CalMode='V',language='chinese',nSaveMode=0,pdf=None):
    sps = st0.stats.sampling_rate
    nSPS = int(sps + 0.5)
    npts = st0.stats.npts
    t_start = st0.stats.starttime.datetime
    # print("File=%s, sps=%f, ntps=%d \n" % (filename,sps,npts))
    data = st0.data.copy()

    fMid=get_median(data)
    fMax = max(data)
    fMin = min(data)
    fMaxLevel = (fMid + fMax)*0.5
    fMinLevel = (fMid + fMin)*0.5

    nMaxCt =nMinCt = 0
    for i in range(0,npts):
        if (data[i]>fMaxLevel):
            nMaxCt += 1
        if (data[i]<fMinLevel):
            nMinCt += 1
    fMaxList = [0.]*nMaxCt
    fMinList = [0.]*nMinCt
    nMaxId = nMinId = 0
    for i in range(0,npts):
        if (data[i]>fMaxLevel):
            fMaxList[nMaxId] = data[i]
            nMaxId += 1
        if (data[i]<fMinLevel):
            fMinList[nMinId] = data[i]
            nMinId += 1
    fMaxMedian = get_median(fMaxList)
    fMinMedian = get_median(fMinList)

    data = st0.data
    time = np.zeros(npts)
    ySimuMax = array('f',range(0))
    tMax = array('f',range(0))
    ySimuMin = array('f',range(0))
    tMin = array('f',range(0))

    for i in range(npts):
        time[i] = i/sps
        if (data[i]>fMaxLevel):
            ySimuMax.append(fMaxMedian)
            tMax.append(time[i])
        if (data[i]<fMinLevel):
            ySimuMin.append(fMinMedian)
            tMin.append(time[i])

    nBeg = nEnd = 0
    if (tMax[len(tMax)-1]<tMin[0]):     #  先高后底
        nBeg = int(tMax[len(tMax)-1] * nSPS + 0.5)
        nEnd = int(tMin[0] * nSPS + 0.5)
    elif (tMin[len(tMin)-1]<tMax[0]):   #  先底后高
        nBeg = int(tMin[len(tMin)-1] * nSPS + 0.5)
        nEnd = int(tMax[0] * nSPS + 0.5)
    if (nEnd>nBeg):
        yMean = [0.] * (nEnd-nBeg)
        for i in range(nEnd-nBeg):
            #print(yMean[i],data[nBeg+i])
            yMean[i] = data[nBeg+i]
        fMid = get_median(yMean)

    fMaxStvt = (fMaxMedian-fMid)/(fCalIn*fCalStvt*fADStvt)
    fMinStvt = (fMinMedian-fMid)/(fCalIn*fCalStvt*fADStvt)
    fAverStvt = (abs(fMaxStvt) + abs(fMinStvt))/2
    print("MaxStvt=%f,MinStvt=%f" % (fMaxStvt,fMinStvt))

    sName = st0.stats.network+ '.'+ st0.stats.station + '.'+ st0.stats.location + '.' + st0.stats.channel
    t_new = t_start.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
    sTime = t_new.strftime('%Y-%m-%d %H:%M:%S')
    #sT0 = t_start.strftime('%Y-%m-%d %H:%M:%S')
    #print("UTC time=%s, Local time=%s"%(sT0,sTime))
    x0 = ''

    if (language == 'english'):
        sInfo = u'%s %s %saccelerometer pulse response simulation\n' \
                    'Cal. Input=%.5f%s, Cal. Sensitivity=%em/s**2/%s，Digitizer Sensitivity=%.1fCt/V\n' \
                    'Cal+ Sensitivity=%.2f V/(m/s**2)，Cal- Sensitivity=%.2f V/(m/s**2), ' \
                    'Average Sensitivity=%.4f V/(m/s**2)' \
                % (sTime, sName, SEN_TYPE, fCalIn, CalMode, fCalStvt, CalMode, fADStvt, fMaxStvt, fMinStvt, fAverStvt)
        sLabels0 = u'source data'
        sLabels1 = 'Cal+ Simu. Data'
        sLabels2 = 'Cal- Simu. Data'
        timestr = datetime.datetime.now().strftime('%Y-%m-%d')
        timestr = "Created by TAIDE, " + timestr
        x0 = '                                                                    Time(s)                                          ' + timestr
        y0 = 'Amplitude(Ct)'
    else:
        sInfo = u'%s %s %s加速度计阶跃响应仿真结果\n' \
                    '标定脉冲输入=%.5f%s, 标定灵敏度=%em/s**2/%s，数采灵敏度=%.1fCt/V\n' \
                    'Cal+ 灵敏度=%.4f V/(m/s**2)，Cal- 灵敏度=%.4f V/(m/s**2)，平均灵敏度=%.4f V/(m/s**2)' \
                    % (sTime, sName,SEN_TYPE,fCalIn,CalMode,fCalStvt,CalMode,fADStvt, fMaxStvt,fMinStvt, fAverStvt)
        sLabels0 = u'原始数据'
        sLabels1 = 'Cal+ 仿真数据'
        sLabels2 = 'Cal- 仿真数据'
        timestr = datetime.datetime.now().strftime('%Y-%m-%d')
        timestr = "Created by 泰德, " + timestr
        x0 = '                                                                    时间(s)                                          ' + timestr
        y0 = '幅度(Ct)'

    (font,fontTitle) = setFont()
    plt.figure(figsize=(12, 9))
    plt.grid(linestyle=':')
    plt.xlabel(x0, fontproperties=font)
    plt.ylabel(y0, fontproperties=font)
    plt.suptitle(sInfo, fontproperties=fontTitle)
    plt.plot(time,  data,    c='blue',  label=sLabels0)
    plt.plot(tMax.tolist(),ySimuMax.tolist(), ls='--', c='red',   label=sLabels1)  # 对拟合之后的数据数组画图
    plt.plot(tMin.tolist(),ySimuMin.tolist(), ls='--', c='pink',  label=sLabels2)  # 对拟合之后的数据数组画图
    plt.legend(prop=font)
    if (nSaveMode==0):
        pdf.savefig()
    else:
        plt.savefig(outname)
    plt.close('all')

    return(sInfo,t_start,abs(fMaxStvt),abs(fMinStvt))

def get_cal_resp(fA0,fFreq,fFactor):
    omiga = fFreq * 2 * math.pi
    a = -fFactor * omiga
    b = math.sqrt(1-fFactor*fFactor) * omiga
    poles = [complex(a,b),complex(a,-b)]
    zeros = [complex(0,0),complex(0,0)]
    scale_fac = fA0
    from scipy import signal
    system = (zeros,poles,scale_fac)
    t, y = signal.step(system,N=10000)
    fStep = t[len(t)-1] / len(y)
    y[0] = 0
    for i in range(1, len(y)):
        y[i] = y[i - 1] + y[i] * fStep
    return(t,y)

def GetMaxId(fLSRatio,nBeg,nEnd):
    nMaxSec = 0
    fMax = -1e20
    for i in range(nBeg, nEnd):
        if (fMax<fLSRatio[i]):
            nMaxSec = i;
            fMax = fLSRatio[i]
    return nMaxSec

def CalRMS(data,nBeg,nEnd):
    fRms = 0.
    fAver = 0.
    for i in range(nBeg,nEnd):
        fAver += data[i]
    fAver /= (nEnd-nBeg)
    for i in range(nBeg,nEnd):
        fRms += (data[i]-fAver) * (data[i]-fAver)
    fRms = math.sqrt(fRms)
    fRms /= (nEnd-nBeg)
    return fRms

def CalRMS2(data,nBeg,nEnd):
    fRms = 0.
    for i in range(nBeg,nEnd):
        fRms += abs(data[i]-data[nBeg])
    fRms /= (nEnd-nBeg)
    return fRms

def LSTrig(data,Id,sps=100):
    fRmsBef = CalRMS(data,(Id-5)*sps,Id*sps)
    fRmsAft = CalRMS(data,Id*sps,(Id+5)*sps)
    return (fRmsAft/(fRmsBef+1e-6))

#ARAIC 找到新的最佳位置（P波初动 & S波初动）
def  ARAIC3(dt,npts,nMaxIndex,nPreCt=300,nAftCt=300):
    #ddt2 = Initddt2(dt,npts)
    ddt3 = np.zeros(npts)
    fRmsBef = np.zeros(npts)
    fRmsAft = np.zeros(npts)
    for i in range(nMaxIndex-nPreCt+100,nMaxIndex+nAftCt-100):
        fRmsBef[i] = CalRMS(dt,i-100,i)
        fRmsAft[i] = CalRMS2(dt,i,i+100)
        ddt3[i] = fRmsAft[i]/(fRmsBef[i]+1e-6)
    fMax = -1e100
    nNewIndex = nMaxIndex
    for i in range(nMaxIndex-nPreCt+100,nMaxIndex+nAftCt-100):
        if (ddt3[i]>fMax):
            nNewIndex = i;
            fMax = ddt3[i];

    #f = open(outname,'wt')
    #for i in range(nMaxIndex-nPreCt+100,nMaxIndex+nAftCt-100):
    #    f.write("dt[%d]=%f, ddt3[%d]=%f, %f, %f \n" % (i,dt[i],i,ddt3[i],fRmsBef[i],fRmsAft[i]))
    #f.close()

    return nNewIndex;

#------------------INPUT------------------------------
#    filename -- SEED 数据或者GSE 等数据文件的路径
#    outname  -- 输出文件名
def CalVelPulse(st0,outname,fCalIn=1.0,fCalStvt=1.0,fADStvt=1.0,CalMode='V',language='chinese',nSaveMode=0,pdf=None):
    #获取 SEED 数据
    sps = st0.stats.sampling_rate
    nSPS = int(sps + 0.5)
    npts = st0.stats.npts
    t_start = st0.stats.starttime.datetime
    # print("File=%s, sps=%f, ntps=%d \n" % (filename,sps,npts))
    data = st0.data
    #  设置相对应的时间数组，用于画图
    time = np.zeros(npts)
    time[0] = 0
    for i in range(1,npts):
        time[i] = i/sps
    sName = st0.stats.network+ '.'+ st0.stats.station + '.'+ st0.stats.location + '.' + st0.stats.channel

    #零、搜索标定数据的起始点和结束点
    nTtSec = npts//nSPS
    fLSRatio = np.zeros(nTtSec)
    for i in range(5, nTtSec-5):
        fLSRatio[i] = LSTrig(data,i,nSPS)

    n1stId = GetMaxId(fLSRatio,5,(nTtSec+5)//2) * nSPS
    n1stId = ARAIC3(data,npts,n1stId,5*nSPS,5*nSPS)-1
    Tmax = st0.stats.starttime + n1stId / sps

    n2ndId = GetMaxId(fLSRatio,(nTtSec+5)//2,nTtSec-5) * nSPS
    n2ndId = ARAIC3(data,npts,n2ndId,5*nSPS,5*nSPS)-1
    Tmin = st0.stats.starttime + n2ndId / sps
    print("%s Cal1 Tm=%s,Ct=%d, Cal2 Tm=%s,Ct=%d" % (sName, Tmax.isoformat(),n1stId,Tmin.isoformat(),n2ndId))

    #outname2 =  "d:\\ab2.txt"
    #f = open(outname2,'wt')
    #for i in range(0,npts):
    #    f.write("data[%d]=%f \n" % (i,data[i]))
    #f.write("\n\n")
    #for i in range(10, nTtSec-10):
    #    f.write("ratio[%d]=%f\n" % (i,fLSRatio[i]))
    #f.write("\n\n")
    #f.write("%s  Max Time %s, Ct=%d,\n" % (filename, Tmax.isoformat(),n1stId))
    #f.write("%s  Min Time %s, Ct=%d,\n" % (filename, Tmin.isoformat(),n2ndId))
    #f.close()

    nBegId = [0] * 2
    nEndId = [0] * 2
    if (n2ndId<n1stId):       #  先高后底
        nBegId[0] = n2ndId
        nBegId[1] = n1stId
    else:
        nBegId[0] = n1stId
        nBegId[1] = n2ndId
    nEndId[0] = nBegId[1]-int(sps)      # (nEegId[1] + nBegId[0]) / 2
    nEndId[1] = npts-int(sps)           # (npts + nBegId[1]) / 2
    #print('search Cal1: Beg=%d,End=%d, Cal2=%d,End=%d' % (nBegId[0],nEndId[0],nBegId[1],nEndId[1]))

    fA0 = np.zeros(2)
    fFreq = np.zeros(2)
    fFactor = np.zeros(2)

    (font,fontTitle) = setFont()

    plt.figure(figsize=(12, 9))
    plt.grid(linestyle=':')
    timestr = datetime.datetime.now().strftime('%Y-%m-%d')
    if (language == 'english'):
        timestr = u"Created by TAIDE, " + timestr
        x0 = '                                                                    Time(s)                                          ' + timestr
        plt.xlabel(x0, fontproperties=font)
        plt.ylabel(u'Amplitude(Ct) ', fontproperties=font)
    else:
        timestr = u"Created by 泰德, " + timestr
        x0 = '                                                                    时间(s)                                          ' + timestr
        plt.xlabel(x0, fontproperties=font)
        plt.ylabel(u'幅度(Ct) ', fontproperties=font)
    t_new = t_start.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
    sTime = t_new.strftime('%Y-%m-%d %H:%M:%S')

    for j in (0,1):
        nLen = nEndId[j] - nBegId[j]
        CalD = np.zeros(nLen)
        Calt = np.zeros(nLen)
        for i in range(0, nLen):
            if (j==0):
                CalD[i] = data[i+nBegId[j]] - data[nBegId[j]]
            else:
                CalD[i] = -data[i+nBegId[j]] + data[nBegId[j]]
            Calt[i] = i/sps
            #if (CalD[i]<=0):
            #    CalD[i] = 1

        # 计算  Y =  A/b * exp(-at)*sin(bt)
        # 一、搜索过零点，找 b
        # 1. 先找搜索起始点和结束点
        nMaxId = 0
        nMinId = 0
        fMax = -1e20
        fMin = 1e20
        for i in range(nSPS//2,nLen-nSPS//2):
            if (fMax<CalD[i]):
                fMax = CalD[i];
                nMaxId = i;
            if (fMin>CalD[i]):
                fMin = CalD[i];
                nMinId = i;
        # 2、找到所有的过零点,取平均值，采用array实现，计算b
        fTm0 = array('f',())
        for i in range(nMaxId,nMinId):
            if (CalD[i]*CalD[i+1] <= 0):      # 找到  sinbt = 0  -> bt = PI -> b=PI/t
                fTm0.append((i + CalD[i]/(CalD[i] - CalD[i+1] + 1e-3))/sps)
                #print(i, CalD[i], CalD[i + 1], CalD[i] * CalD[i + 1], fTm0)
        fb = 0.
        for i in range(0,len(fTm0)):
            fb += fTm0[i]
        fb /= (len(fTm0)+1e-10)
        #print(len(fTm0),fTm0)
        nFit = int(fb * sps)

        if (len(fTm0)==0 or nFit<4):
            if (language=='english'):
                sInfo = u'%s %s seismometer pulse signal is eroor，simulation wrong\n ' % (sTime, sName)
                sLabels = u'source data'
            else:
                sInfo = u'%s %s 地震计阶跃响应数据错误，不能仿真\n '  % (sTime,sName)
                sLabels = u'原始数据'
            plt.suptitle(sInfo, fontproperties=fontTitle)
            plt.plot(time, data, c='blue', label=sLabels)
            plt.legend(prop=font)
            plt.savefig(outname)
            plt.close('all')
            return (t_start, 0,0,0,0,0,0,0,0,0)

        fb = math.pi/fb

        #二、转化为1阶线性拟合，求a，A0/b
        nStart = int(nFit/4)
        nEnd = int(nFit*3/4)
        fX = np.zeros(nEnd-nStart)
        fY = np.zeros(nEnd-nStart)
        for i in range(nStart,nEnd):
            fT = i/sps
            fX[i-nStart] = fT
            fData = CalD[i]/math.sin(fT * fb)
            if fData <= 0:
                fData = 1e-6
            fY[i-nStart] = math.log(fData)
        #print(nStart,nEnd)
        croff = np.polyfit(fX, fY, 1)

        #三、计算A0，a,b
        fA0[j] = math.exp(croff[1]) * fb
        fa = -croff[0]
        fFreq[j] = math.sqrt(fa*fa+fb*fb)/(2*math.pi)
        fFactor[j] = fa/(fFreq[j]*2*math.pi)
        #print(croff,fFreq[j],fFactor[j],fA0[j])
    #四、计算残差
    fErr = np.zeros(2)
    fTt = np.zeros(2)
    (tSimu1,ySimu1) = get_cal_resp(fA0[0],fFreq[0],fFactor[0])
    for i in range(0,len(tSimu1)):
        tSimu1[i] += (nBegId[0]/sps)
        if (n2ndId<n1stId):
            ySimu1[i] = data[nBegId[0]] - ySimu1[i]
        else:
            ySimu1[i] = data[nBegId[0]] + ySimu1[i]
    for i in range(0,len(tSimu1)):
        t0 = tSimu1[i] * sps;
        t1Id = int(t0)
        if (t1Id>=(nEndId[0]-1)):
            break;
        yReal = data[t1Id] + (data[t1Id+1]-data[t1Id]) * (t0-t1Id)
        fErr[0] += (yReal - ySimu1[i])*(yReal - ySimu1[i])
        fTt[0] += ySimu1[i] * ySimu1[i]

    (tSimu2,ySimu2) = get_cal_resp(fA0[1],fFreq[1],fFactor[1])
    for i in range(0,len(tSimu2)):
        tSimu2[i] += (nBegId[1]/sps)
        if (n2ndId<n1stId):
            ySimu2[i] = data[nBegId[1]] + ySimu2[i]
        else:
            ySimu2[i] = data[nBegId[1]] - ySimu2[i]
    for i in range(0,len(tSimu2)):
        t0 = tSimu2[i] * sps;
        t1Id = int(t0)
        if (t1Id>=(nEndId[1]-1)):
            break;
        yReal = data[t1Id] + (data[t1Id + 1] - data[t1Id]) * (t0 - t1Id)
        fErr[1] += (yReal - ySimu2[i]) * (yReal - ySimu2[i])
        fTt[1] += ySimu2[i] * ySimu2[i]
    fT0 = np.zeros(2)
    for i in (0,1):
        fErr[i] /= fTt[i]
        fErr[i] = math.sqrt(fErr[i])
        fA0[i] = fA0[i] / fADStvt / (fCalIn*fCalStvt)
        fT0[i] = 1.0/fFreq[i]
    #五、显示
    #sT0 = t_start.strftime('%Y-%m-%d %H:%M:%S')
    #print("UTC time=%s, Local time=%s"%(sT0,sTime))

    if (language == 'english'):
        sInfo = u'%s %s %sseismometer pulse response simulation\n' \
                'Cal. Input=%.5f%s, Cal. Sensitivity=%em/s**2/%s，Digitizer Sensitivity%.1fCt/V\n'\
                '1st. Sensitivity=%.2f V/(m/s)，period=%.4fs，dump=%.6f，Eesidual error=%.4f%%\n' \
                '2nd. Sensitivity=%.2f V/(m/s)，period=%.4fs，dump=%.6f，Eesidual error=%.4f%% ' \
                % (sTime,sName,SEN_TYPE,
                       fCalIn,CalMode,fCalStvt,CalMode,fADStvt,
                       fA0[0],fT0[0],fFactor[0],fErr[0]*100.,
                       fA0[1],fT0[1],fFactor[1],fErr[1]*100.)
        sLabels0 = u'source data'
        sLabels1 = '1st. Simu. Data'
        sLabels2 = '2nd. Simu. Data'

    else:
        sInfo = u'%s %s %s地震计阶跃响应仿真结果\n' \
                '标定脉冲输入=%.5f%s, 标定灵敏度%em/s**2/%s，数采灵敏度%.1fCt/V\n' \
                '1st. 灵敏度=%.2f V/(m/s)，周期=%.4fs，阻尼=%.6f，残差=%.4f%%\n' \
                '2nd. 灵敏度=%.2f V/(m/s)，周期=%.4fs，阻尼=%.6f，残差=%.4f%%' \
                % (sTime,sName,SEN_TYPE,
                       fCalIn,CalMode,fCalStvt,CalMode,fADStvt,
                       fA0[0],fT0[0],fFactor[0],fErr[0]*100.,
                       fA0[1],fT0[1],fFactor[1],fErr[1]*100.)
        sLabels0 = u'原始数据'
        sLabels1 = u'1st.标定仿真'
        sLabels2 = u'2nd.标定仿真'

    plt.suptitle(sInfo  , fontproperties=fontTitle)
    plt.plot(time,  data,            c='blue',  label=sLabels0)
    plt.plot(tSimu1,ySimu1, ls='--', c='red',   label=sLabels1)  # 对拟合之后的数据数组画图
    plt.plot(tSimu2,ySimu2, ls='--', c='pink',  label=sLabels2)    # 对拟合之后的数据数组画图
    plt.legend(prop =font)
    if (nSaveMode==0):
        pdf.savefig()
    else:
        plt.savefig(outname)
    plt.close('all')
    #六 返回
    print("start time=%s,A0=%f,T0=%f,f0=%f,Err0=%f,A1=%f,T1=%f,f1=%f,Err1=%f" %
          (sTime,fA0[0],fT0[0],fFactor[0],fErr[0],fA0[1],fT0[1],fFactor[1],fErr[1]))
    return (sInfo,t_start,fA0[0],fT0[0],fFactor[0],fErr[0],fA0[1],fT0[1],fFactor[1],fErr[1])

def doCalPulse(st0,figfile,outfile,nNetMode,nCalMode,cal_stvt,pulse_input,ad_stvt,m=0,language='chinese',nSaveMode=0,pdf=None):
    if (nNetMode=='V'):
        (sInfo,cal_time,cal_gain1,cal_freq1,cal_dump1,err1,cal_gain2,cal_freq2,cal_dump2,err2) \
            = CalVelPulse(st0, figfile, pulse_input,cal_stvt,ad_stvt,nCalMode,language,nSaveMode,pdf)
        print(cal_time,cal_gain1,cal_freq1,cal_dump1,err1,cal_gain2,cal_freq2,cal_dump2,err2)
    else:
        (sInfo,cal_time,cal_gain1,cal_gain2) \
            = CalAccPulse(st0, figfile,pulse_input,cal_stvt,ad_stvt,nCalMode,language,nSaveMode,pdf)
        print(cal_time,cal_gain1,cal_gain2)

    if (m==0):
        f = open(outfile, "wt")
    else:
        f = open(outfile, "at")
        f.write("\n")
    f.write("%s\n" % sInfo);
    f.close()

def GetMaxId_Random(fCal):
    fMax = 0;
    nMaxId = 1
    for i in range(len(fCal)):
        if (fMax<fCal[i]):
            nMaxId = i;
            fMax = fCal[i]
    return nMaxId;

def SearchRandomBeg(sps,data):
    nLen = len(data)
    nGrp = int(sps * 0.1)
    if (nGrp<10):
        nGrp = 10
    nCal = nLen
    fBef = np.zeros(nCal)
    fAft = np.zeros(nCal)
    fCal = np.zeros(nCal)

    for i in range(0,nGrp):
        fBef[i] = 1
        fAft[i] = 1
        fCal[i] = 1
    for i in range(nCal,nCal-nGrp):
        fBef[i] = 1
        fAft[i] = 1
        fCal[i] = 1

    for i in range(nGrp,nCal-nGrp):
        fBef[i] = 1e-8
        fAft[i] = 1e-8
        for j in range(0,nGrp):
            fBef[i] += abs(data[i-j] - data[i-j-1]) * (nGrp-j) * (nGrp-j) * (nGrp-j)
            fAft[i] += abs(data[i+j] - data[i+j+1]) * (nGrp-j) * (nGrp-j) * (nGrp-j)
        fCal[i] = fAft[i] / fBef[i];
        #print('Random Point = %d, Time=%fs, data=%f,Bef=%f,Aft=%f,Cal=%f' % (i,1.0*i/sps,data[i],fBef[i],fAft[i],fCal[i]))

    nIndex = GetMaxId_Random(fCal);
    return nIndex

def doCalRandom(fRandom_Sec,st0,figfile,outfile,
            nNetMode,nCalMode,cal_stvt,cal_input,ad_stvt,
                nTxtMode=0,language='chinese',nSaveMode=0,pdf=None):
    sps = st0.stats.sampling_rate
    nSPS = int(sps + 0.5)
    npts = st0.stats.npts
    t_start = st0.stats.starttime.datetime
    print("sps=%f, ntps=%d \n" % (sps,npts))

    fTtSecMin = 20 + fRandom_Sec *1.25
    fCalSecBeg = fRandom_Sec *0.25
    fCalSecEnd = 50 + fRandom_Sec *0.25
    nBegCalId = int(fRandom_Sec *0.25 *sps)
    if (fCalSecEnd>=fTtSecMin):
        fCalSecEnd = fTtSecMin
    # fSearch = np.zeros(50*nSPS)
    # for i in range(0, nSPS*50):
    #     fSearch[i] = st0.data[i + nBegCalId]
    # nBegCalId += SearchRandomBeg(nSPS,fSearch)
    # print('Random Cal. Start Point = %d, Time=%fs' % (nBegCalId,1.0*nBegCalId/sps))
    # dTm = nBegCalId/sps

    sName = st0.stats.network+ '.'+ st0.stats.station + '.'+ st0.stats.location + '.' + st0.stats.channel
    t_start = t_start
    t_new = t_start.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
    sTime = t_new.strftime('%Y-%m-%d %H:%M:%S')

    (font, fontTitle) = setFont()
    plt.grid(linestyle=':')
    # 检测数据是否在范围内，不在的话就不处理
    # npts/sps   数据总时间

    #  设置相对应的时间数组，用于画图
    data = st0.data
    time = np.zeros(npts)
    for i in range(0, npts):
        time[i] = i / sps


    if (npts < nBegCalId+50*nSPS):
        print('Random data length is too short, npts=%d. nBegId=%d, sps=%f' % (npts,nBegCalId,sps))
        plt.figure(figsize=(16, 12))
        if (language == 'english'):
            sInfo = u'%s %s %sseismometer random File size eroor，simulation wrong\n ' % (sTime, sName, SEN_TYPE)
            sLabels0 = u'Source data'
            sLabels1 = u'Random Data'
        else:
            sInfo = u'%s %s %s地震计正弦数据长度不够，不能仿真\n ' % (sTime, sName, SEN_TYPE)
            sLabels0 = u'原始数据'
            sLabels1 = u'标定数据'

        print("file %s data length Error." % (sName))
        plt.suptitle(sInfo, fontproperties=fontTitle)
        plt.plot(time, data, c='blue', label=sLabels0)
        plt.legend(prop=font)

        if (nSaveMode == 0):
            pdf.savefig()
        else:
            plt.savefig(figfile)
        plt.close('all')
        return (0,0)

    fSearch = np.zeros(50*nSPS)
    for i in range(0, nSPS*50):
        fSearch[i] = st0.data[i + nBegCalId]
    nBegCalId += SearchRandomBeg(nSPS,fSearch)
    print('Random Cal. Start Point = %d, Time=%fs' % (nBegCalId,1.0*nBegCalId/sps))
    dTm = nBegCalId/sps

    if (npts < nBegCalId+sps*fRandom_Sec):
        print('Random data length is too short, npts=%d. nBegId=%d, sps=%f,Random Sec=%f' % (npts,nBegCalId,sps,fRandom_Sec))
        plt.figure(figsize=(16, 12))
        if (language == 'english'):
            sInfo = u'%s %s %sseismometer random File size eroor，simulation wrong\n ' % (sTime, sName, SEN_TYPE)
            sLabels0 = u'Source data'
            sLabels1 = u'Random Data'
        else:
            sInfo = u'%s %s %s地震计正弦数据长度不够，不能仿真\n ' % (sTime, sName, SEN_TYPE)
            sLabels0 = u'原始数据'
            sLabels1 = u'标定数据'

        print("file %s data length Error." % (sName))
        plt.suptitle(sInfo, fontproperties=fontTitle)
        plt.plot(time, data, c='blue', label=sLabels0)
        plt.legend(prop=font)

        if (nSaveMode == 0):
            pdf.savefig()
        else:
            plt.savefig(figfile)
        plt.close('all')
        return (0,0)

    nRand = int(fRandom_Sec * sps)
    fSrc = np.zeros(nRand)
    fRef = np.zeros(nRand)
    for i in range(nRand):
        fSrc[i] = st0.data[i+nBegCalId] / ad_stvt  # 将数据输出单位从 Ct 转化为电压值
        fRef[i] = -math.sin(2 * math.pi * (i / sps))  # 参考信号为1H在信号
    fSrc = fSrc - np.mean(fSrc)
    fRef = fRef - np.mean(fRef)

    #win = np.kaiser(nRand, 5)
    for j in range(nRand):
        fSrc[j] = fSrc[j] #* win[j]
        fRef[j] = fRef[j] #* win[j]
    (fSrc_e,fangle_a) = getFE4(fSrc)
    (fRef_e,fRef_a) = getFE(fRef, int(nRand / nSPS + 0.5))

    # 计算谱线并归一化
    #关于输入能量的修正
    #原来的模式为输入单频点能量，现在的模式是输入全频带能量
    #谱线数量为 1228800点，相当于614400条谱线 ，增益为：40.246109，增益为 32.09dB
    #60s 数据，谱线614400条，分布在 DC-1024 Hz 内，折算每Hz有600条谱线，DC-100Hz 内有 60000条谱线能量
    #60s 200Hz 采样，应有 600*200/2=60000条谱线
    #每条谱线能量为 60000/40.246109 = 1490.82 倍
    #1V 信号应该为 3276.8Ct ，但实际系数为 40.246109
    #则输入信号为 40.246109Ct /6553.6 Ct/V= 0.006141 , 有差距
    # 采样速率 为200Hz，而DA的采样速率为 2048Hz，则输出频带宽度为 60/614400 =
    #输入了 60000条谱线能量，实际上200Hz应为 100条谱线，0.012282/60=

    nFreqLine = nRand//2
    fFreqSrc = np.zeros(nFreqLine)
    fGainSrc = np.zeros(nFreqLine)
    fGainSrc[0] = 0
    for j in range(1,nFreqLine):
        fFreqSrc[j] = sps/(2.*nFreqLine) * j
        if (nNetMode == 'V'):
            # 2.1  v=∫a*sin(w*t) dt = ∫a*sin(2*pi*f*t) dt = a*cos(2*pi*f*t)/(2*pi*f)
            cal_in = cal_stvt * cal_input  / (2 * math.pi * fFreqSrc[j])  # 单位：m/s
        else:
            # 2.1  a*sin(w*t)
            cal_in = cal_stvt * cal_input  # 单位：m/s**2
        fFactor = math.sqrt(2)/4/(sps*0.5)
        if (fRandom_Sec==60.):
            cal_in *= fFactor     #  60s  200Hz
        elif (fRandom_Sec == 120.):
            cal_in *= fFactor / math.sqrt(2)      # 60s  200Hz
        elif (fRandom_Sec == 240.):
            cal_in *= fFactor / 2 # 60s  200Hz
        elif (fRandom_Sec == 480.):
            cal_in *= fFactor / (2*math.sqrt(2)) # 60s  200Hz
        elif (fRandom_Sec==960.):  #  谱线偏少，
            cal_in *= fFactor/ 4   #  60s  200Hz
        fGainSrc[j] =  (fSrc_e[j]/fRef_e) / cal_in

    # 谱线整合
    nFreqCollect = sps*10
    fGainInc = math.pow(10,math.log10(sps*0.5/fFreqSrc[1])/nFreqCollect)
    print("Gain=%f" % fGainInc)
    fFreqDen = np.zeros(nFreqLine)
    fGainDen = np.zeros(nFreqLine)
    nCtDen = np.zeros(nFreqLine)

    fFreqDen[0] = fFreqSrc[1]       #    第一个频点
    fGainDen[0] = fGainSrc[1]
    nDen = 0;
    nSrc = 2;
    print(nFreqLine)
    while (nSrc<nFreqLine-1):
        nCt = 0
        if (fFreqDen[nDen]*fGainInc>fFreqSrc[nSrc]):
            nCt = 0;
            nDen += 1;
            fFreqDen[nDen] = fFreqDen[nDen-1]*fGainInc
            fGainDen[nDen] = 0.
            while (fFreqDen[nDen]>=fFreqSrc[nSrc] and nSrc<nFreqLine-1):
                fGainDen[nDen] +=  fGainSrc[nSrc]*fGainSrc[nSrc]
                nCt +=  1
                nSrc += 1
            nCtDen[nDen] = nCt
            fGainDen[nDen] = math.sqrt(fGainDen[nDen]/nCt)
        else:
            nDen += 1
            fFreqDen[nDen] = fFreqSrc[nSrc]
            fGainDen[nDen] = fGainSrc[nSrc]
            nCtDen[nDen] = 1
            nSrc += 1
        # print("nDen=%d,nSrc=%d,fFreqDen[nDen]=%f,fFreqSrc[nSrc]=%f,fGainDen[nDen]=%f,nCt=%d" % (nDen,nSrc,fFreqDen[nDen],fFreqSrc[nSrc],fGainDen[nDen],nCt))

    fFreq = np.zeros(nDen)
    cal_gain = np.zeros(nDen)
    for i in range(nDen):
        fFreq[i] = fFreqDen[i]
        cal_gain[i] = fGainDen[i]

    # 开始画图
    plt.figure(figsize=(16, 24))
    if (language == 'english'):
        sLabels0 = u'Random Cal.'
        sLabels2 = u'Source Data'
        sLabels1 = u'Random Data'
        if (nNetMode == 'V'):
            sInfo = u'%s %s %sseismometer random response diagram\n' \
                    'Cal. Input=%.5f%s, Cal. Sensitivity=%em/s**2/%s，Digitizer Sensitivity=%.1fCt/V' \
                    % (sTime, sName, SEN_TYPE, cal_input, nCalMode, cal_stvt, nCalMode, ad_stvt)
        else:
            sInfo = u'%s %s %saccelerometer random response diagram\n' \
                    'Cal. Input=%.5f%s, Cal. Sensitivity=%em/s**2/%s，Digitizer Sensitivity=%.1fCt/V' \
                    % (sTime, sName, SEN_TYPE, cal_input, nCalMode, cal_stvt, nCalMode, ad_stvt)
    else:
        sLabels0 = u'伪随机标定结果'
        sLabels2 = u'原始数据'
        sLabels1 = u'伪随机序列'
        if (nNetMode == 'V'):
            sInfo = u'%s %s %s地震计伪随机标定响应\n' \
                    '标定输入=%.5f%s, 标定灵敏度=%em/s**2/%s，数采灵敏度=%.1fCt/V' \
                    % (sTime, sName, SEN_TYPE, cal_input, nCalMode, cal_stvt, nCalMode, ad_stvt)
        else:
            sInfo = u'%s %s %s加速度计伪随机标定响应\n' \
                    '标定输入=%.5f%s, 标定灵敏度=%em/s**2/%s，数采灵敏度=%.1fCt/V' \
                    % (sTime, sName, SEN_TYPE, cal_input, nCalMode, cal_stvt, nCalMode, ad_stvt)
    sInfo1 = "\n\n" + sInfo
    plt.suptitle(sInfo1, fontproperties=fontTitle)

    ax = plt.subplot(211)
    plt.grid(linestyle='-', which="major")
    plt.grid(linestyle=':', which="minor")
    timestr = datetime.datetime.now().strftime('%Y-%m-%d')
    if (language == 'english'):
        timestr = "Created by TAIDE, " + timestr
    else:
        timestr = "Created by 泰德, " + timestr

    if (language == 'english'):
        ax.set_title("Amplitude - Frequency Response Diagram", fontproperties=fontTitle)
        x0 = '                                                                   Freq[Hz]                                         ' + timestr
        plt.xlabel(x0, fontproperties=font)
        if (nNetMode == 'V'):
            plt.ylabel('Gain[V/(m/s)]', fontproperties=font)
        else:
            plt.ylabel('Gain[V/(m/s**2)]', fontproperties=font)
    else:
        ax.set_title("幅频特性", fontproperties=fontTitle)
        x0 = '                                                                   频率[Hz]                                         ' + timestr
        plt.xlabel(x0, fontproperties=font)
        if (nNetMode == 'V'):
            plt.ylabel('增益[V/(m/s)]', fontproperties=font)
        else:
            plt.ylabel('增益[V/(m/s**2)]', fontproperties=font)
    plt.loglog(fFreq, cal_gain, c='blue', label=sLabels0)
    #plt.loglog(fFreq, cal_gain, c='blue', label=sLabels0, marker='.')
    #plt.semilogx(fFreq, cal_gain, c='blue', label=sLabels0, marker='.')

    plt.legend(prop=font)

    ax = plt.subplot(212)
    plt.grid(linestyle=':')
    if (language == 'english'):
        ax.set_title("Random Data", fontproperties=fontTitle)
        x0 = '                                                                   Time[s]                                         ' + timestr
        plt.xlabel(x0, fontproperties=font)
        plt.ylabel('Signal[Ct]', fontproperties=font)
    else:
        ax.set_title("伪随机波形", fontproperties=fontTitle)
        x0 = '                                                                   时间[s]                                         ' + timestr
        plt.xlabel(x0, fontproperties=font)
        plt.ylabel('信号[Ct]', fontproperties=font)
    plt.plot(time, data, c='blue', label=sLabels2)

    nRand = int(fRandom_Sec * sps)
    time2 = np.zeros(nRand)
    data2 = np.zeros(nRand)
    for i in range(nRand):
        data2[i] = data[i+nBegCalId]
        time2[i] = time[i+nBegCalId]  # 参考信号为1H在信号
    plt.plot(time2, data2, c='red', label=sLabels1)

    if (nSaveMode==0):
        pdf.savefig()
    else:
        plt.savefig(figfile)
    plt.close('all')

    if (nTxtMode==0):
        f = open(outfile, "wt")
    else:
        f = open(outfile, "at")
        f.write("\n\n")

    f.write("%s\n" % sInfo);
    print(sInfo)
    if (nNetMode == 'V'):
        f.write('频率  增益\nHz  V/(m/s)\n')
        print('频率  增益\nHz  V/(m/s)\n')
    else:
        f.write('频率  增益\nHz  V/(m/s**2)\n')
        print('频率  增益\nHz  V/(m/s**2)\n')
    for k in range(nDen):
        if (nNetMode == 'V'):
            sInfo = '%f  %f' % (fFreq[k], cal_gain[k])
            f.write('%s\n' % sInfo)
            print(sInfo)
        else:
            sInfo = '%f  %f' % (fFreq[k], cal_gain[k])
            f.write('%s\n' % sInfo)
            print(sInfo)
    f.close()
    return ( fFreq, cal_gain)

def getNewName(m,nCh,nSaveMode,filename,figfile_0):
    if (nCh > 1):
        if (nSaveMode == 0):
            figfile = figfile_0
        elif (nSaveMode == 1):
            figfile = filename + "-%d.png" % (m + 1)
        else:
            figfile = figfile_0 + "-%d.png" % (m + 1)
    else:
        figfile = figfile_0
    return figfile

from matplotlib.backends.backend_pdf import PdfPages
def DoAllCal(infile,parfile,figfile_0,outfile,language='chinese'):
    # 解析数据文件
    (SinOrPulse,nNetMode,nCalMode,cal_stvt,cal_input,ad_stvt,fTm0,fStart,fEnd,fGain,fFreq,fRandom_Sec) = parserPar(parfile)
    if (nNetMode=='ERR'):
        print("parserPar Error.")
        cal_freq = array('f', range(0))
        cal_gain = array('f', range(0))
        return False

    (filename, extension) = os.path.splitext(figfile_0)
    print('filename=%s,ext=%s' % (filename, extension))
    if (extension.lower() == '.pdf'):
        nSaveMode = 0
    elif (extension.lower() == '.png'):
        nSaveMode = 1
    else:
        nSaveMode = 2

    st = obspy.read(infile)
    print(st)
    nCh = len(st)
    if (nCh>1):
        st[0] += st[1]

    if (SinOrPulse == 'sin'):              #  正弦标定处理
        if (nSaveMode == 0):  # pdf mode
            with PdfPages(figfile_0) as pdf:
                for m in range(nCh):
                    (fFreq, cal_gain) = doCalSin(st[m],figfile_0,outfile,
                             nNetMode, nCalMode, cal_stvt[m], cal_input, ad_stvt, fTm0, fStart, fEnd, fGain, fFreq,
                             m,language,nSaveMode,pdf)
        else:
            for m in range(nCh):
                figfile = getNewName(m, nCh, nSaveMode, filename, figfile_0)
                ( fFreq, cal_gain) = doCalSin(st[m], figfile, outfile,
                         nNetMode, nCalMode, cal_stvt[m], cal_input, ad_stvt, fTm0, fStart, fEnd, fGain, fFreq,
                         m,language, nSaveMode)
        return True
    elif (SinOrPulse == 'pulse'):       #  脉冲标定处理
        if (nSaveMode == 0):  # pdf mode
            with PdfPages(figfile_0) as pdf:
                for m in range(nCh):
                    doCalPulse(st[m],figfile_0,outfile,
                             nNetMode, nCalMode, cal_stvt[m], cal_input, ad_stvt,
                             m,language,nSaveMode,pdf)
        else:
            for m in range(nCh):
                # figfile = getNewName(m, nCh, nSaveMode, filename, figfile_0)
                figfile = figfile_0
                doCalPulse(st[m], figfile, outfile,
                         nNetMode, nCalMode, cal_stvt[m], cal_input, ad_stvt,
                         m,language, nSaveMode)
        return True
        # do pulse
    elif (SinOrPulse =='random'):       # 伪随机数标定处理
        if (nSaveMode == 0):  # pdf mode
            with PdfPages(figfile_0) as pdf:
                for m in range(nCh):
                    doCalRandom(fRandom_Sec,st[m],figfile_0,outfile,
                             nNetMode, nCalMode, cal_stvt[m], cal_input, ad_stvt,
                             m,language,nSaveMode,pdf)
        else:
            for m in range(nCh):
                figfile = getNewName(m, nCh, nSaveMode, filename, figfile_0)
                # figfile = figfile_0
                doCalRandom(fRandom_Sec,st[m], figfile, outfile,
                         nNetMode, nCalMode, cal_stvt[m], cal_input, ad_stvt,
                         m,language, nSaveMode)
        return True


def show_path(path, all_file, all_path):
    dirlist = os.listdir(path)
    for i in dirlist:
        list = os.path.join(path, i)
        if os.path.isdir(list):
            show_path(list, all_file, all_path)
        elif os.path.isfile(list):
            all_file.append(os.path.dirname(list))
            all_path.append(os.path.abspath(list))
    return all_file, all_path


def newCalFile(ini_path, all_path, inoutfiles):
    maxTime_name = [0]  # 完整的原始数据的最大修改时间和目录名
    min_time = 4102415999  # 2099-12-31 23:59:59  # 更新的原始数据中最小的修改时间
    if not os.path.exists(ini_path):
        open(ini_path, 'w')
    cf = configparser.ConfigParser()
    cf.read(ini_path)
    start_time = cf.getfloat('TIME_START', 'timestamp')  # 起始判断时间
    for file in all_path:
        mTime = os.path.getmtime(file)  # 获取各个文件的修改时间
        if len(file.split('.')) > 3 and mTime >= start_time:
            calName = file.split('.')[-1]
            chnName = file.split('.')[-3]
            if cf.has_option(calName, chnName):
                if cf.getfloat(calName, chnName) == mTime:  # 前10分钟和前20分钟的修改时间一致，说明数据已完整
                    outfile = 'res_' + chnName + '.txt'
                    parfile = 'par_' + chnName + '.txt'
                    inoutfiles.append((file, os.path.join(os.path.dirname(file), outfile),
                                       os.path.join(os.path.dirname(file), parfile), chnName))
                    cf.remove_option(calName, chnName)
                    if calName not in maxTime_name:
                        maxTime_name.append(calName)
                    if mTime >= maxTime_name[0]:
                        maxTime_name[0] = mTime
                    continue
            if not cf.has_section(calName):  # 增加前10分钟获取的新数据的修改时间
                cf.add_section(calName)
                if not cf.has_option(calName, chnName):
                    cf.set(calName, chnName, str(mTime))
            else:
                if not cf.has_option(calName, chnName):
                    cf.set(calName, chnName, str(mTime))
            cf.set(calName, chnName, str(mTime))  # 更新前10分钟更新的数据的修改时间
            if mTime < min_time:  # 获取更新数据的最小修改时间
                min_time = mTime
    if maxTime_name[0] != 0:  # 有产出，无更新
        for cname in maxTime_name[1:]:
            cf.remove_section(cname)
        if min_time == 4102415999:
            cf.set('TIME_START', 'timestamp', str(datetime.datetime.timestamp(datetime.datetime.now())))  # 起始判断时间设为当前时间
    if min_time != 4102415999:  # 有更新，设置起始判断时间为最小更新时间
        cf.set('TIME_START', 'timestamp', str(min_time))
    cf.write(open(ini_path, 'w'))


def newCalPath(path, inoutfiles):
    now = datetime.datetime.now().timestamp()
    for npath in path:
        if (now-10800) < os.path.getmtime(npath) < now:
            dirlist = os.listdir(npath)
            for file in dirlist:
                if len(file.split('.')) > 3:
                    chnName = file.split('.')[-3]
                    if 'Sin_' + chnName + '.png' in dirlist or 'Pulse_' + chnName + '.png' \
                            or 'random_' + chnName + '.png' in dirlist:
                        print('png or pdf already exists')
                        break
                    outfile = 'res_' + chnName + '.txt'
                    parfile = 'par_' + chnName + '.txt'
                    inoutfiles.append((os.path.join(npath, file), os.path.join(npath, outfile),
                                       os.path.join(npath, parfile), chnName))
    return inoutfiles


def getOneCal(file):
    year = file[0:4]
    month = file[4:6]
    language = 'chinese'
    inoutfiles = []
    path = os.path.join(CAL_PATH, year, month, file)
    for file in os.listdir(path):
        if len(file.split('.')) > 3:
            chnName = file.split('.')[-3]
            outfile = 'res_' + chnName + '.txt'
            parfile = 'par_' + chnName + '.txt'
            inoutfiles.append((os.path.join(path, file), os.path.join(path, outfile),
                               os.path.join(path, parfile), chnName))
    if len(inoutfiles) > 0:
        print('\n\n' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
              '-------------------------------------------------------------------')
        for infile, outfile, parfile, chnName in inoutfiles:
            if os.path.exists(parfile):
                figfile = getfigfile(parfile, chnName)
                CalIsOK = DoAllCal(infile, parfile, figfile, outfile, language)
                if (CalIsOK):
                    print('Calibration Calculate OK!')
                else:
                    print('Calibration Calculate Error!')
                    if os.path.exists(figfile):
                        os.remove(figfile)
            else:
                print('Parameter file (%s) not found！' % parfile)


def getOneEvent(file):
    chn_num = pi_par().CHN_NUM
    year = file[0:4]
    month = file[4:6]
    path = os.path.join(EVENT_PATH, year, month, file)
    if not os.path.exists(path):
        print('%s not found!' % path)
        return
    i = 1
    (font, fontTitle) = setFont()
    plt.figure(figsize=(9, 6))
    path_name = file
    tTime = '%s-%s-%s %s:%s:%s' % (file[0:4], file[4:6],
                                   file[6:8], file[8:10],
                                   file[10:12], file[12:14])
    plt.suptitle(tTime)
    data_list = [x for x in os.listdir(path) if x.count('.') >= 5]
    data_list.sort(key=lambda x: x.split('.')[3][-2])
    for chn_data in data_list:
        st = read(os.path.join(path, chn_data))
        sps = st[0].stats.sampling_rate
        npts = st[0].stats.npts
        times = np.zeros(npts)
        for n in range(1, npts):
            times[n] = n / sps
        ax1 = plt.subplot(chn_num, 1, i)
        plt.grid(linestyle=':')
        plt.ylabel(chn_data.split('.')[3] + '  \n(Ct)  ', fontproperties=font, rotation='horizontal',
                   horizontalalignment='center')
        if i < chn_num:
            plt.xticks([])
        else:
            daystr = datetime.datetime.now().strftime('%Y-%m-%d')
            timestr = "Created by 泰德, " + daystr
            x0 = '                                                       时间(s)                      ' + timestr
            plt.xlabel(x0, fontproperties=font)
        plt.plot(times, st[0].data, c='blue')
        i += 1
    outfile = path + '/%s.png' % path_name
    plt.savefig(outfile)
    plt.close('all')
    print('Event:', file)


def newEventFile(event_path):
    chn_num = pi_par().CHN_NUM
    now = datetime.datetime.now().timestamp()
    for epath in event_path:
        if now-10800 < os.path.getmtime(epath) < now:
            path_name = os.path.basename(epath).__str__()
            outfile_base = path_name + '.png'
            if outfile_base in os.listdir(epath):
                continue
            i = 1
            (font, fontTitle) = setFont()
            plt.figure(figsize=(9, 6))
            tTime = '%s-%s-%s %s:%s:%s' % (path_name.split('.')[-1][0:4], path_name.split('.')[-1][4:6],
                                           path_name.split('.')[-1][6:8], path_name.split('.')[-1][8:10],
                                           path_name.split('.')[-1][10:12], path_name.split('.')[-1][12:14])
            plt.suptitle(tTime)
            outfile = epath + '/%s.png' % path_name
            b = [x for x in os.listdir(epath) if x.count('.') >= 5]
            data_list = sorted(b, key=lambda x: x.split('.')[3][-2])
            for chn_data in data_list:
                st = read(os.path.join(epath, chn_data))
                sps = st[0].stats.sampling_rate
                npts = st[0].stats.npts
                times = np.zeros(npts)
                for n in range(1, npts):
                    times[n] = n / sps
                ax1 = plt.subplot(chn_num, 1, i)
                plt.grid(linestyle=':')
                plt.ylabel(chn_data.split('.')[3] + '  \n(Ct)  ', fontproperties=font, rotation='horizontal',
                    horizontalalignment='center')
                if i < chn_num:
                    plt.xticks([])
                else:
                    daystr = datetime.datetime.now().strftime('%Y-%m-%d')
                    timestr = "Created by 泰德, " + daystr
                    x0 = '                                                       时间(s)                      ' + timestr
                    plt.xlabel(x0, fontproperties=font)
                plt.plot(times, st[0].data, c='blue')
                i += 1
            plt.savefig(outfile)
            plt.close('all')
            print('Event:', outfile_base)


def timeInit(ini_path):
    now = datetime.datetime.timestamp(datetime.datetime.now())
    cf = configparser.ConfigParser()
    cf.read(ini_path)
    if not cf.has_section('TIME_START'):
        cf.add_section('TIME_START')
    if not cf.has_option('TIME_START', 'timestamp'):
        cf.set('TIME_START', 'timestamp', str(now - 600))
        cf.write(open(ini_path, 'w'))


# 匹配通道名和通道摆类型
def chnMatch(path, chn_list):
    cf = configparser.ConfigParser()
    cf.read(path)
    chn = [['CHN0_CODE', 'CHN0_TYPE'], ['CHN1_CODE', 'CHN1_TYPE'], ['CHN2_CODE', 'CHN2_TYPE'],
           ['CHN3_CODE', 'CHN3_TYPE'], ['CHN4_CODE', 'CHN4_TYPE'], ['CHN5_CODE', 'CHN5_TYPE']]
    if cf.getint('PI_PAR', 'CHN_NUM') == 3:
        for i in range(0, 3):
            if cf.getint('PI_PAR', chn[i][1]) == 1:
                chn[i].append('V')
            elif cf.getint('PI_PAR', chn[i][1]) == 2:
                chn[i].append('A')
            chn_list.append([cf.get('PI_PAR', chn[i][0]), chn[i][2]])
    elif cf.getint('PI_PAR', 'CHN_NUM') == 6:
        for i in range(0, 6):
            if cf.getint('PI_PAR', chn[i][1]) == 1:
                chn[i].append('V')
            elif cf.getint('PI_PAR', chn[i][1]) == 2:
                chn[i].append('A')
            chn_list.append([cf.get('PI_PAR', chn[i][0]), chn[i][2]])


# 添加电压/电流标定，标定灵敏度
def senMatch(path, chn_list):
    f = open(path, 'r')
    for readline in f.readlines():
        if 'SENSOR0_PULSE' in readline:
            for i in range(0, 3):
                chn_list[i].append(re.split("=|\n", readline)[1])
        if 'SENSOR1_PULSE' in readline and len(chn_list) > 3:
            for i in range(3, 6):
                chn_list[i].append(re.split("=|\n", readline)[1])
        if 'CH0_CA' in readline:
            chn_list[0].append(float(readline.split(',')[1]))
        if 'CH1_CA' in readline:
            chn_list[1].append(float(readline.split(',')[1]))
        if 'CH2_CA' in readline:
            chn_list[2].append(float(readline.split(',')[1]))
        if len(chn_list) > 3:
            if 'CH3_CA' in readline:
                chn_list[3].append(float(readline.split(',')[1]))
            if 'CH4_CA' in readline:
                chn_list[4].append(float(readline.split(',')[1]))
            if 'CH5_CA' in readline:
                chn_list[5].append(float(readline.split(',')[1]))


# 添加标定输入
def addCalInput(path, chn_list):
    f = open(path, 'rb')
    bText1 = f.read(36)
    rText1 = struct.unpack('2H12B4H8B2H', bText1)
    cal_input = rText1[17] / 32768 * 5 - 5
    f.seek(512)
    bText2 = f.read(36)
    rText2 = struct.unpack('2H12B4H8B2H', bText2)
    cal_input2 = rText2[17] / 32768 * 5 - 5
    for i in range(len(chn_list)):
        if i < 3:
            chn_list[i].append(cal_input)
        if i >= 3:
            chn_list[i].append(cal_input2)


# 获取采样位数和AD增益
def getCiPar(path, chn_list):
    ad_ctvt_ci = ad_ctvt_fi = 1677721.6
    Gain_list = ((0, 1), (1, 2), (2, 4), (3, 8), (4, 16), (5, 32), (6, 64))
    f = open(path, 'rb')
    bText = f.read(26)
    rText = struct.unpack('2H8B7s7B', bText)
    # 采样位数
    nCommRate = rText[16] >> 4
    # AD增益
    nGain = rText[17]
    nGain_CI = nGain & 15
    nGain_FI = nGain >> 4
    for iGain in Gain_list:
        if nCommRate == 0:  # 26位
            if nGain_CI == iGain[0]:
                ad_ctvt_ci = 1677721.6 / iGain[1]
            if nGain_FI == iGain[0]:
                ad_ctvt_fi = 1677721.6 / iGain[1]
        elif nCommRate == 1:  # 24位
            if nGain_CI == iGain[0]:
                ad_ctvt_ci = 419430.4 / iGain[1]
            if nGain_FI == iGain[0]:
                ad_ctvt_fi = 419430.4 / iGain[1]
    for i in range(len(chn_list)):
        if i < 3:
            chn_list[i].append(ad_ctvt_ci)
        if i >= 3:
            chn_list[i].append(ad_ctvt_fi)


def getfigfile(parfile, chnName):
    with open(parfile) as f:
        caltype = f.readline().split('\n')[0]
        if ',' in caltype:
            caltype = caltype.split(',')[0]
        f.close()
        figfile = caltype.capitalize() + '_' + chnName + '.png'
        figfile = os.path.join(os.path.dirname(parfile), figfile)
        return figfile


def getchnNum():
    cf = configparser.ConfigParser()
    cf.read(PI_PATH)
    try:
        chnnum = cf.getint('PI_PAR', 'CHN_NUM')
    except:
        chnnum = 6
    return chnnum

class pi_par:
    def __init__(self):
        self.cf = configparser.ConfigParser()
        self.cf.read(PI_PATH)

    @property
    def CHN_NUM(self):
        return self.cf.getint('PI_PAR', 'CHN_NUM')

    @property
    def CHN_CODE(self):
        cCode_list = []
        for i in range(self.CHN_NUM):
            cCode_list.append(self.cf.get('PI_PAR', 'CHN' + str(i) + '_CODE'))
        return cCode_list


def get_event():
    """
    获取事件目录
    """
    event_all_file = []
    event_all_path = []

    event_all_file, event_all_path = show_path(EVENT_PATH, event_all_file, event_all_path)
    new_li = list(set(event_all_file))
    new_li.sort(key=event_all_file.index)
    newEventFile(new_li)

def checkini():
    Enable = 1
    if PLATFORM == 'Windows':
        basedir = 'D:\\django\\trunk'
    else:
        basedir = '/home/usrdata/pi/tde'
    ini_path = basedir + '/params/produce.ini'
    if os.path.exists(ini_path):
        cf = configparser.ConfigParser()
        cf.read(ini_path)
        if cf.has_section('PAR'):
            if cf.has_option('PAR', 'enable'):
                Enable = cf.getint('PAR', 'enable')
    return Enable


def main():
    language = 'chinese'
    cal_all_file = []
    cal_all_path = []
    inoutfiles = []

    show_path(CAL_PATH, cal_all_file, cal_all_path)
    new_li = list(set(cal_all_file))
    new_li.sort(key=cal_all_file.index)
    new_li.sort(key= lambda fn: os.path.getmtime(fn))
    inoutfiles = newCalPath(new_li, inoutfiles)

    if len(inoutfiles) > 0:
        print('\n\n' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
              '-------------------------------------------------------------------')
        for infile, outfile, parfile, chnName in inoutfiles:
            if os.path.exists(parfile):
                figfile = getfigfile(parfile, chnName)
                CalIsOK = DoAllCal(infile, parfile, figfile, outfile, language)
                if (CalIsOK):
                    print('Calibration Calculate OK!')
                else:
                    print('Calibration Calculate Error!')
                    if os.path.exists(figfile):
                        os.remove(figfile)
            else:
                print('Parameter file (%s) not found！' % parfile)


if __name__ == "__main__":
    argv = sys.argv[1:]
    if argv:
        try:
            opts, args = getopt.getopt(argv, "hc:e:")
        except getopt.GetoptError:
            print('python3 getCalData.py -c <cal file> -e <event file>')
            sys.exit(2)
        for opt, arg in opts:
            if opt in ('-h','--help'):
                print('python3 getCalData.py -c <cal file> -e <event file>')
                sys.exit()
            elif opt in ("-c",):
                calfile = arg
                getOneCal(calfile)
            elif opt in ("-e",):
                eventfile = arg
                getOneEvent(eventfile)
        sys.exit()
    else:
        if not checkini():
            # print('Auto production of pictures is prohibited')
            sys.exit(0)
    get_event()
    main()
