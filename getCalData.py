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
import datetime
from array import array
from matplotlib.font_manager import FontProperties #字体管理器
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams["legend.loc"]='best'

#mpl.rcParams['axes.unicode_minus']=False #用来正常显示负号
#mpl.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
#plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签

def setFont():
    sys = platform.system()
    if sys == "Windows":
        font = FontProperties(fname=r"c:\\windows\\fonts\\simhei.ttf",size=12)
        fontTitle = FontProperties(fname=r"c:\\windows\\fonts\\simhei.ttf",size=18)
    else:
        font = FontProperties(fname=r"/usr/share/fonts/SIMHEI.TTF", size=12)
        fontTitle = FontProperties(fname=r"/usr/share/fonts/SIMHEI.TTF", size=18)
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

    try:
        nId = -1
        f = open(parfile, 'rt')
        l0 = f.readline()
        line = f.readline()
        lines = f.readlines()
        f.close()

        nId = 0
        l0 = split21space(l0).lower()
        print(l0)
        if (l0[0]=='p'):   # pulse
            SinOrPulse = 'pulse'
        else: # sin
            SinOrPulse = 'sin'
        line = split21space(line)
        (sNetMode, sCalMode,  cal_input, ad_stvt , sCalNum) =  line.split(' ')
        cal_num = int(sCalNum)
        cal_stvt = array('f',range(cal_num))
        #cal_stvt = float(cal_stvt)
        cal_input = float(cal_input)
        ad_stvt = float(ad_stvt)
        print('mode=%s' % SinOrPulse)
        if (sNetMode.lower()[0] == 'a'):
            nNetMode = 'A'
            print('sensor mode: accelerometer')
        else:
            nNetMode = 'V'
            print('sensor mode: seismometer')
        if (sCalMode.lower()[0] == 'v'):
            nCalMode = 'V'
            print('Calibration mode: Voltage Mode')
        else:
            nCalMode = 'A'
            print('Calibration mode: Current Mode')
        print('Cal Input=%f%s.  Digitizer Sensitivity=%fCt/V, channel Num=%d'
              % (cal_input, nCalMode, ad_stvt, len(cal_stvt)))

        nId = 1
        nReadId = 0
        for line in lines:
            line = split21space(line)
            if (nReadId<cal_num):
                cal_stvt[nReadId] = float(line)
            elif (SinOrPulse=='sin'):
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
        fStart = array('f',range(0))
        fEnd = array('f', range(0))
        fTm0 = array('f', range(0))
        print("Read Par File Error,Line:%d,Err:%s" % (nId+1,e))
        return(SinOrPulse,'ERR',"ERR",cal_stvt,cal_input,ad_stvt,fTm0,fStart,fEnd,fGain,fFreq)

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
            if (fTWork[i]<=5):
                fStart[i] = fT0
                fEnd[i] = fT0 + fTWork[i]
            elif (fTWork[i]<=10):
                fStart[i] = fT0 + 1.5
                fEnd[i] = fT0 + fTWork[i] - 1.5
            elif (fTWork[i]<=30):
                fStart[i] = fT0 + 3
                fEnd[i] = fT0 + fTWork[i] - 3
            elif (fTWork[i]<=60):
                fStart[i] = fT0 + 5
                fEnd[i] = fT0 + fTWork[i] - 5
            else:
                fStart[i] = fT0 + 10
                fEnd[i] = fT0 + fTWork[i] - 10
            #print(fTBlank[i],fTWork[i],fStart[i],fEnd[i],fGain[i],fFreq[i])
    else:
        fStart = array('f',range(0))
        fEnd = array('f', range(0))
        fTm0 = array('f', range(0))

    return (SinOrPulse,nNetMode,nCalMode,cal_stvt,cal_input,ad_stvt,fTm0,fStart,fEnd,fGain,fFreq)

def getFE(fSrc,nMaxId):
    nLen = len(fSrc)
    nHLen = nLen // 2
    # 1.1 FFT 取模并并归一化
    fSrc_f = np.fft.fft(fSrc)
    fSrc_a = np.abs(fSrc_f) / nHLen
    # 1.2 数据取半波并将零点归零
    fSrc_ha = fSrc_a[range(nHLen)]
    fSrc_ha[0] = 0
    #1.3 获取最大值幅值的频率，得到主频，并检验主频是否是输入点
    maxSrcId = np.argmax(fSrc_ha)
    while (np.abs(nMaxId-maxSrcId)>3):
        maxSrcId = np.argmax(fSrc_ha)
        # print(maxSrcId,nMaxId)
        fSrc_ha[maxSrcId] = 0
        if maxSrcId == 0:
            print('maxSrcId = %d,exit loop' % maxSrcId)
            break
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
    return (fSrc_e)

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
    return (fSrc_e)

def doCalSin(st0,figfile,outfile,
             nNetMode, nCalMode, cal_stvt, cal_input, ad_stvt, fTm0, fStart, fEnd, fGain, fFreq,
             nTxtMode=0,language='chinese',nSaveMode=0,pdf=None):
    sps = st0.stats.sampling_rate
    nSPS = int(sps + 0.5)
    npts = st0.stats.npts
    t_start = st0.stats.starttime.datetime
    # print("File=%s, sps=%f, ntps=%d \n" % (filename,sps,npts))
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
        plt.figure(figsize=(16, 12))
        if (language == 'english'):
            sInfo = u'%s %s seismometer pulse signal is eroor，simulation wrong\n ' % (sTime, sName)
            sLabels = u'sorce data'
        else:
            sInfo = u'%s %s 地震计阶跃响应数据错误，不能仿真\n ' % (sTime, sName)
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
    cal_in = array('f', range(nLen))
    cal_gain = array('f', range(nLen))
    for k in range(nLen):
        nEnd = int(fEnd[k] * nSPS)
        nStart = int(fStart[k] * nSPS)
        nFFTT0 = nEnd - nStart
        fSrc = np.zeros(nFFTT0)
        fRef = np.zeros(nFFTT0)

        win = np.kaiser(nFFTT0, 10.0)
        for j in range(nStart, nEnd):
            fSrc[j - nStart] = fVOut[j]  # * win[j-nStart]
            fRef[j - nStart] = math.cos(2 * math.pi * fFreq[k] * (j / sps - fTm0[k]))  # * win[j-nStart]

        aver1 = np.mean(fSrc)
        aver2 = np.mean(fRef)
        # print('k1=%d,aver1=%f,aver2=%f' % (k,aver1,aver2))
        fSrc = fSrc - aver1
        fRef = fRef - aver2

        for j in range(0, nEnd - nStart):
            fSrc[j] = fSrc[j] * win[j]
            fRef[j] = fRef[j] * win[j]

        fSrc_e = getFE(fSrc, int(fFreq[k] * nFFTT0 / nSPS + 0.5))
        fRef_e = getFE(fRef, int(fFreq[k] * nFFTT0 / nSPS + 0.5))
        cal_v[k] = (fSrc_e / fRef_e)  # 标定输出，V
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
    plt.figure(figsize=(16, 24))
    if (language == 'english'):
        sLabels0 = u'sorce data'
        sLabels1 = u'Simu. Data'
        if (nNetMode == 'V'):
            sInfo = u'%s %s seismometer sin response diagram\n' \
                    'Cal. Input=%.5f%s, Cal. Sensitivity=%em/s**2/%s，Digitizer Sensitivity=%.1fCt/V' \
                    % (sTime, sName, cal_input, nCalMode, cal_stvt, nCalMode, ad_stvt)
        else:
            sInfo = u'%s %s accelerometer sin response diagram\n' \
                    'Cal. Input=%.5f%s, Cal. Sensitivity=%em/s**2/%s，Digitizer Sensitivity=%.1fCt/V' \
                    % (sTime, sName, cal_input, nCalMode, cal_stvt, nCalMode, ad_stvt)
    else:
        sLabels0 = u'原始数据'
        sLabels1 = u'仿真数据'
        if (nNetMode == 'V'):
            sInfo = u'%s %s 地震计正弦标定响应\n' \
                    '标定输入=%.5f%s, 标定灵敏度=%em/s**2/%s，数采灵敏度=%.1fCt/V' \
                    % (sTime, sName, cal_input, nCalMode, cal_stvt, nCalMode, ad_stvt)
        else:
            sInfo = u'%s %s 加速度计正弦标定响应\n' \
                    '标定输入=%.5f%s, 标定灵敏度=%em/s**2/%s，数采灵敏度=%.1fCt/V' \
                    % (sTime, sName, cal_input, nCalMode, cal_stvt, nCalMode, ad_stvt)
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
        ax.set_title("幅频相应", fontproperties=fontTitle)
        x0 = '                                                                   频率[Hz]                                         ' + timestr
        plt.xlabel(x0, fontproperties=font)
        if (nNetMode == 'V'):
            plt.ylabel('增益[V/(m/s)]', fontproperties=font)
        else:
            plt.ylabel('增益[V/(m/s**2)]', fontproperties=font)
    plt.loglog(fFreq, cal_gain, c='blue', label=sLabels0, marker='.')
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

        gain = cal_in[k] * cal_gain[k] * ad_stvt
        for j in range(nCalCt):
            fT0[j] = fStart[k] + j / sps
            fCal[j] = data[int((fTm0[k] - 4) * sps)] - math.cos(
                2 * math.pi * fFreq[k] * (j / sps + (fStart[k] - fTm0[k]))) * gain
            fTSrc[j] = data[int(fStart[k] * sps) + j]
        if (k == 0):
            plt.plot(fT0, fCal, c='red', label=sLabels1)
            plt.legend(prop=font)
        else:
            plt.plot(fT0, fCal, c='red')

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
    for k in range(nLen):
        if (nNetMode == 'V'):
            sInfo = 'Freq=%fHz, gain=%fV/(m/s), fErr=%f%%' % (fFreq[k], cal_gain[k], fErr[k] * 100.)
            f.write('%s\n' % sInfo)
            print(sInfo)
        else:
            sInfo = 'Freq=%fHz, gain=%fV/(m/s**2), fErr=%f%%' % (fFreq[k], cal_gain[k], fErr[k] * 100.)
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
    fMaxStvt = (fMaxMedian-fMid)/(fCalIn*fCalStvt*fADStvt)
    fMinStvt = (fMinMedian-fMid)/(fCalIn*fCalStvt*fADStvt)
    print("MaxStvt=%f,MinStvt=%f" % (fMaxStvt,fMinStvt))
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

    sName = st0.stats.network+ '.'+ st0.stats.station + '.'+ st0.stats.location + '.' + st0.stats.channel
    t_new = t_start.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
    sTime = t_new.strftime('%Y-%m-%d %H:%M:%S')
    #sT0 = t_start.strftime('%Y-%m-%d %H:%M:%S')
    #print("UTC time=%s, Local time=%s"%(sT0,sTime))
    x0 = ''

    if (language == 'english'):
        sInfo = u'%s %s accelerometer pulse response simulation\n' \
                    'Cal. Input=%.5f%s, Cal. Sensitivity=%em/s**2/%s，Digitizer Sensitivity=%.1fCt/V\n' \
                    'Cal+ Sensitivity=%.2f V/(m/s**2)，Cal- Sensitivity=%.2f V/(m/s**2)' \
                % (sTime, sName, fCalIn, CalMode, fCalStvt, CalMode, fADStvt, fMaxStvt, fMinStvt)
        sLabels0 = u'sorce data'
        sLabels1 = 'Cal+ Simu. Data'
        sLabels2 = 'Cal- Simu. Data'
        timestr = datetime.datetime.now().strftime('%Y-%m-%d')
        timestr = "Created by TAIDE, " + timestr
        x0 = '                                                                    Time(s)                                          ' + timestr
        y0 = 'Amplitude(Ct)'
    else:
        sInfo = u'%s %s 加速度计阶跃响应仿真结果\n' \
                    '标定脉冲输入=%.5f%s, 标定灵敏度=%em/s**2/%s，数采灵敏度=%.1fCt/V\n' \
                    'Cal+ 灵敏度=%.4f V/(m/s**2)，Cal- 灵敏度=%.4f V/(m/s**2)' \
                    % (sTime, sName,fCalIn,CalMode,fCalStvt,CalMode,fADStvt, fMaxStvt,fMinStvt)
        sLabels0 = u'原始数据'
        sLabels1 = 'Cal+ 仿真数据'
        sLabels2 = 'Cal- 仿真数据'
        timestr = datetime.datetime.now().strftime('%Y-%m-%d')
        timestr = "Created by 泰德, " + timestr
        x0 = '                                                                    时间(s)                                          ' + timestr
        y0 = '幅度(Ct)'

    (font,fontTitle) = setFont()
    plt.figure(figsize=(16, 12))
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

    plt.figure(figsize=(16, 12))
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
                sLabels = u'sorce data'
            else:
                sInfo = u'%s %s 地震计阶跃响应数据错误，不能仿真\n '  % (sTime,sName)
                sLabels = u'原始数据'
            plt.suptitle(sInfo, fontproperties=fontTitle)
            plt.plot(time, data, c='blue', label=sLabels)
            plt.legend(prop=font)
            plt.savefig(outname)
            plt.close('all')
            return (t_start, 0,0,0,0,0,0,0,0, 0)

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
        sInfo = u'%s %s seismometer pulse response simulation\n' \
                'Cal. Input=%.5f%s, Cal. Sensitivity=%em/s**2/%s，Digitizer Sensitivity%.1fCt/V\n'\
                '1st. Sensitivity=%.2f V/(m/s)，period=%.4fs，dump=%.6f，Eesidual error=%.4f%%\n' \
                '2nd. Sensitivity=%.2f V/(m/s)，period=%.4fs，dump=%.6f，Eesidual error=%.4f%% ' \
                % (sTime,sName,
                       fCalIn,CalMode,fCalStvt,CalMode,fADStvt,
                       fA0[0],fT0[0],fFactor[0],fErr[0]*100.,
                       fA0[1],fT0[1],fFactor[1],fErr[1]*100.)
        sLabels0 = u'sorce data'
        sLabels1 = '1st. Simu. Data'
        sLabels2 = '2nd. Simu. Data'

    else:
        sInfo = u'%s %s 地震计阶跃响应仿真结果\n' \
                '标定脉冲输入=%.5f%s, 标定灵敏度%em/s**2/%s，数采灵敏度%.1fCt/V\n' \
                '1st. 灵敏度=%.2f V/(m/s)，周期=%.4fs，阻尼=%.6f，残差=%.4f%%\n' \
                '2nd. 灵敏度=%.2f V/(m/s)，周期=%.4fs，阻尼=%.6f，残差=%.4f%%' \
                % (sTime,sName,
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
        print(st0, figfile, pulse_input,cal_stvt,ad_stvt,nCalMode,language,nSaveMode,pdf)
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
    return (cal_gain1,cal_gain2)

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
    (SinOrPulse,nNetMode,nCalMode,cal_stvt,cal_input,ad_stvt,fTm0,fStart,fEnd,fGain,fFreq) = parserPar(parfile)
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
    nCh = len(st)

    if (SinOrPulse == 'sin'):
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
    else:       #  脉冲标定处理
        if (nSaveMode == 0):  # pdf mode
            with PdfPages(figfile_0) as pdf:
                for m in range(nCh):
                    (cal_gain1,cal_gain2) = doCalPulse(st[m],figfile_0,outfile,
                             nNetMode, nCalMode, cal_stvt[m], cal_input, ad_stvt,
                             m,language,nSaveMode,pdf)
        else:
            for m in range(nCh):
                figfile = getNewName(m, nCh, nSaveMode, filename, figfile_0)
                (cal_gain1,cal_gain2) = doCalPulse(st[m], figfile, outfile,
                         nNetMode, nCalMode, cal_stvt[m], cal_input, ad_stvt,
                         m,language, nSaveMode)
        return True
        # do pulse

    #return (fFreq, cal_gain)


def show_path(path, all_file, all_path):
    dirlist = os.listdir(path)
    for i in dirlist:
        list = os.path.join(path, i)
        if os.path.isdir(list):
            show_path(list, all_file, all_path)
        elif os.path.isfile(list):
            all_file.append(os.path.basename(list))
            all_path.append(os.path.abspath(list))
    return all_file,all_path


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


def timeInit(ini_path):
    now = datetime.datetime.timestamp(datetime.datetime.now())
    cf = configparser.ConfigParser()
    cf.read(ini_path)
    if not cf.has_section('TIME_START'):
        cf.add_section('TIME_START')
    if not cf.has_option('TIME_START', 'timestamp'):
        cf.set('TIME_START', 'timestamp', str(now - 600))
        cf.write(open(ini_path, 'w'))


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


def senMatch(path,chn_list):
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


def addCalInput(path, chn_list):
    f = open(path, 'rb')
    bText1 = f.read(36)
    rText1 = struct.unpack('2H12B4H8B2H', bText1)
    cal_input = rText1[17]/32768*5-5
    f.seek(512)
    bText2 = f.read(36)
    rText2 = struct.unpack('2H12B4H8B2H', bText2)
    cal_input2 = rText2[17]/32768*5-5
    for i in range(len(chn_list)):
        if i < 3:
            chn_list[i].append(cal_input)
        if i >= 3:
            chn_list[i].append(cal_input2)


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
        if nCommRate == 0: #26位
            if nGain_CI == iGain[0]:
                ad_ctvt_ci = 1677721.6/iGain[1]
            if nGain_FI == iGain[0]:
                ad_ctvt_fi = 1677721.6/iGain[1]
        elif nCommRate == 1: #24位
            if nGain_CI == iGain[0]:
                ad_ctvt_ci = 419430.4/iGain[1]
            if nGain_FI == iGain[0]:
                ad_ctvt_fi = 419430.4/iGain[1]
    for i in range(len(chn_list)):
        if i < 3:
            chn_list[i].append(ad_ctvt_ci)
        if i >= 3:
            chn_list[i].append(ad_ctvt_fi)


def getfigfile(parfile, chnName):
    with open(parfile) as f:
        caltype = f.readline().split('\n')[0]
        f.close()
        figfile = caltype.capitalize() + '_' + chnName + '.png'
        figfile = os.path.join(os.path.dirname(parfile), figfile)
        return figfile


def main():
    language = 'chinese'
    all_file = []
    all_path = []
    inoutfiles = []
    cal_path = 'D:/django/trunk/cal_data'
    ini_par = 'caltime.ini'

    sys = platform.system()
    if sys == 'Linux':
        cal_path = '/home/usrdata/usb/log/cal'
        ini_par = '/home/usrdata/pi/tde/params/caltime.ini'

    show_path(cal_path, all_file, all_path)
    timeInit(ini_par)
    newCalFile(ini_par, all_path, inoutfiles)

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
    main()