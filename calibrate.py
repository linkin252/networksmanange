# -*- coding: utf-8 -*-
import os
import platform

import math
import obspy
import datetime
from array import array
from matplotlib.font_manager import FontProperties #字体管理器
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.rcParams['axes.unicode_minus']=False #用来正常显示负号
mpl.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签

import numpy as np

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
def CalAccPulse(filename,outname,fCalIn=1.0,fCalStvt=1.0,fADStvt=1.0,CalMode='V'):
    st = obspy.read(filename)
    sps = st[0].stats.sampling_rate
    npts = st[0].stats.npts
    t_start = st[0].stats.starttime.datetime

    #print("File=%s, sps=%f, ntps=%d \n" % (filename,sps,npts))
    data = st[0].data.copy()
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
    data = st[0].data
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

    sName = filename.split('\\')[-1]
    t_new = t_start.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
    sTime = t_new.strftime('%Y-%m-%d %H:%M:%S')
    #sT0 = t_start.strftime('%Y-%m-%d %H:%M:%S')
    #print("UTC time=%s, Local time=%s"%(sT0,sTime))
    if (CalMode=='V'):
        sInfo = u'%s %s 加速度计阶跃响应仿真结果\n' \
                'Cal+ 灵敏度=%.2f V/(m/s**2)，Cal- 灵敏度=%.2f V/(m/s**2)\n' \
                '标定脉冲输入=%.6fV, 标定灵敏度%fm/s**2/V，数采灵敏度%.1fCt/V' \
                % (sTime, sName, fMaxStvt,fMinStvt,fCalIn,fCalStvt,fADStvt)
    else:
        sInfo = u'%s %s 加速度计阶跃响应仿真结果\n' \
                'Cal+ 灵敏度=%.4f V/(m/s**2)，Cal- 灵敏度=%.4f V/(m/s**2)\n' \
                '标定脉冲输入=%.6fA, 标定灵敏度%fm/s**2/A，数采灵敏度%.1fCt/V' \
                % (sTime, sName, fMaxStvt,fMinStvt,fCalIn,fCalStvt,fADStvt)
    #font = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=12)
    #fontTitle = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=18)
    #font = FontProperties(fname=r"c:\windows\fonts\simhei.ttf", size=12)
    #fontTitle = FontProperties(fname=r"c:\windows\fonts\simhei.ttf", size=18)
    sys = platform.system()
    if sys == "Windows":
        font = FontProperties(size=12)
        fontTitle = FontProperties(size=18)
    else:
        font = FontProperties(fname=r"/usr/share/fonts/SIMHEI.TTF", size=12)
        fontTitle = FontProperties(fname=r"/usr/share/fonts/SIMHEI.TTF", size=18)

    plt.figure(figsize=(16, 12))
    plt.grid(linestyle=':')
    timestr = datetime.datetime.now().strftime('%Y-%m-%d')
    timestr = "Created by 泰德, " + timestr
    x0 = '                                                                    时间(s)                                          ' + timestr
    plt.xlabel(x0, fontproperties=font)
    plt.ylabel('幅度(Ct)', fontproperties=font)
    plt.suptitle(sInfo, fontproperties=fontTitle)
    plt.plot(time,  data,    c='blue',  label='原始数据')
    plt.plot(tMax.tolist(),ySimuMax.tolist(), ls='--', c='red',   label='Cal+ 仿真数据')  # 对拟合之后的数据数组画图
    plt.plot(tMin.tolist(),ySimuMin.tolist(), ls='--', c='pink',  label='Cal- 仿真数据')  # 对拟合之后的数据数组画图
    plt.legend(prop=font)
    plt.savefig(outname)
    plt.close('all')

    return(t_start,abs(fMaxStvt),abs(fMinStvt))

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

def CalVelPulse(filename,outname,fCalIn=1.0,fCalStvt=1.0,fADStvt=1.0,CalMode='V'):
    #获取 SEED 数据
    st = obspy.read(filename)
    sps = st[0].stats.sampling_rate
    nSPS = int(sps+0.5)
    npts = st[0].stats.npts
    t_start = st[0].stats.starttime.datetime
    #print("File=%s, sps=%f, ntps=%d \n" % (filename,sps,npts))
    data = st[0].data
    #  设置相对应的时间数组，用于画图
    time = np.zeros(npts)
    time[0] = 0
    for i in range(1,npts):
        time[i] = i/sps
    sName = filename.split('\\')[-1]

    #零、搜索标定数据的起始点和结束点
    nTtSec = npts//nSPS
    fLSRatio = np.zeros(nTtSec)
    for i in range(5, nTtSec-5):
        fLSRatio[i] = LSTrig(data,i,nSPS)

    n1stId = GetMaxId(fLSRatio,5,(nTtSec+5)//2) * nSPS
    n1stId = ARAIC3(data,npts,n1stId,5*nSPS,5*nSPS)-1
    Tmax = st[0].stats.starttime + n1stId / sps

    n2ndId = GetMaxId(fLSRatio,(nTtSec+5)//2,nTtSec-5) * nSPS
    n2ndId = ARAIC3(data,npts,n2ndId,5*nSPS,5*nSPS)-1
    Tmin = st[0].stats.starttime + n2ndId / sps
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

    #font = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=12)
    #fontTitle = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=18)
    #font = FontProperties(fname=r"c:\windows\fonts\simhei.ttf", size=12)
    #fontTitle = FontProperties(fname=r"c:\windows\fonts\simhei.ttf", size=18)
    sys = platform.system()
    if sys == "Windows":
        font = FontProperties(size=12)
        fontTitle = FontProperties(size=18)
    else:
        font = FontProperties(fname=r"/usr/share/fonts/SIMHEI.TTF", size=12)
        fontTitle = FontProperties(fname=r"/usr/share/fonts/SIMHEI.TTF", size=18)
    plt.figure(figsize=(16, 12))
    plt.grid(linestyle=':')
    timestr = datetime.datetime.now().strftime('%Y-%m-%d')
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
        for i in range(0,nLen):
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
        if (len(fTm0)==0):
            sInfo = u'%s %s 地震计阶跃响应数据错误，不能仿真\n '  % (sTime,sName)
            plt.suptitle(sInfo, fontproperties=fontTitle)
            plt.plot(time, data, c='blue', label=u'原始数据')
            plt.legend(prop=font)
            plt.savefig(outname)
            plt.close('all')
            return (t_start, 0,0,0,0,0,0,0,0)

        #print(len(fTm0))
        fb = 0.
        for i in range(0,len(fTm0)):
            fb += fTm0[i]
        fb /= len(fTm0)
        nFit = int(fb * sps)
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
    if (CalMode=='V'):
        sInfo = u'%s %s 地震计阶跃响应仿真结果\n ' \
            '1st. 灵敏度=%.2f V/(m/s)，周期=%.4fs，阻尼=%.6f，残差=%.4f%%\n ' \
            '2nd. 灵敏度=%.2f V/(m/s)，周期=%.4fs，阻尼=%.6f，残差=%.4f%%\n ' \
            '标定脉冲输入=%.5fV, 标定灵敏度%em/s**2/V，数采灵敏度%.1fCt/V' \
            % (sTime,sName, fA0[0],fT0[0],fFactor[0],fErr[0]*100.,
                      fA0[1],fT0[1],fFactor[1],fErr[1]*100.,
               fCalIn,fCalStvt,fADStvt)
    else:
        sInfo = u'%s %s 地震计阶跃响应仿真结果\n ' \
            '1st. 灵敏度=%.2f V/(m/s)，周期=%.4fs，阻尼=%.6f，残差=%.4f%%\n ' \
            '2nd. 灵敏度=%.2f V/(m/s)，周期=%.4fs，阻尼=%.6f，残差=%.4f%%\n ' \
            '标定脉冲输入=%.5fA, 标定灵敏度%em/s**2/A，数采灵敏度%.1fCt/V' \
            % (sTime,sName, fA0[0],fT0[0],fFactor[0],fErr[0]*100.,
                      fA0[1],fT0[1],fFactor[1],fErr[1]*100.,
               fCalIn,fCalStvt,fADStvt)

    plt.suptitle(sInfo  , fontproperties=fontTitle)
    plt.plot(time,  data,            c='blue',  label=u'原始数据')
    plt.plot(tSimu1,ySimu1, ls='--', c='red',   label=u'1st.标定仿真')  # 对拟合之后的数据数组画图
    plt.plot(tSimu2,ySimu2, ls='--', c='pink',  label=u'2nd.标定仿真')    # 对拟合之后的数据数组画图
    plt.legend(prop =font)
    plt.savefig(outname)
    plt.close('all')
    #六 返回
    print("start time=%s,A0=%f,T0=%f,f0=%f,Err0=%f,A1=%f,T1=%f,f1=%f,Err1=%f" %
          (sTime,fA0[0],fT0[0],fFactor[0],fErr[0],fA0[1],fT0[1],fFactor[1],fErr[1]))
    return (t_start,fA0[0],fT0[0],fFactor[0],fErr[0],fA0[1],fT0[1],fFactor[1],fErr[1])

def addCalPulse(infile,outfile,pulse_input,cal_stvt,ad_stvt,nNetMode='V',nCalMode='A'):
    if (nNetMode=='V'):
        (cal_time,cal_gain1,cal_freq1,cal_dump1,err1,cal_gain2,cal_freq2,cal_dump2,err2) \
            = CalVelPulse(infile, outfile, pulse_input,cal_stvt,ad_stvt,nCalMode)
        print(cal_time,cal_gain1,cal_freq1,cal_dump1,err1,cal_gain2,cal_freq2,cal_dump2,err2)
    else:
        (cal_time,cal_gain1,cal_gain2) \
            = CalAccPulse(infile, outfile, pulse_input,cal_stvt,ad_stvt,nCalMode)
        print(cal_time,cal_gain1,cal_gain2)
    return (cal_gain1,cal_gain2)

import sys, getopt
def main(argv):
    infile = 'TD.T2867.40.EIE.D.20190191'
    outfile = 'demo.png'
    nNetMode = 'V'
    nCalMode = 'A'
    cal_stvt = float(10.)     # 10m/s**2/V or 10m/s**2/A
    cal_input = float(0.001)  # 0.001A or 0.001V
    ad_stvt = float(1258290)  # 1258290 Ct/V

    try:
        opts, args = getopt.getopt(argv,"hi:o:s:c:p:a:d:",["ifile=","ofile=","sensor","cal_mode","cal_input","cal_stvt","ad_stvt"])
    except getopt.GetoptError:
        print('python calibrate.py -s <seismometer/accelerometer> -c <Amp/Volt> -a <float cal_stvt> -p <float cal_input) -d <float ad_stvt> -i <inputfile> -o <outputfile>  ')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h','--help'):
            print('calibrate.py -s <seismometer/accelerometer> -c <Amp/Volt> -a <float cal_stvt> -p <float cal_input) -d <float ad_stvt> -i <inputfile> -o <outputfile>  ')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            infile = arg
        elif opt in ("-o", "--ofile"):
            outfile = arg
            filetype = outfile.split('.')[-1]
            if (filetype!='png' and filetype!='pdf'):
                outfile += '.png'
        elif opt in ("-s", '--sensor'):
            if (arg[0]=='a' or arg[0] == 'A'):
                nNetMode = 'A'
        elif opt in ("-c", '--cal_mode'):
            if (arg[0]=='v' or arg[0] == 'V'):
                nCalMode = 'V'
        elif opt in ('-p', '--cal_input'):
            cal_input = float(arg)
        elif opt in ('-a', '--cal_stvt'):
            cal_stvt = float(arg)
        elif opt in ('-d', '--ad_stvt'):
            ad_stvt = float(arg)

    print('input file:  %s' % infile)
    print('output file: %s' % outfile)
    if (nNetMode =='A'):
        print('sensor mode: accelerometer')
    else:
        print('sensor mode: seismometer')
    if (nCalMode=='V'):
        print('Calibration mode: Voltage Mode')
    else:
        print('Calibration mode: Current Mode')
    print('Cal Input=%f%s. Cal Sensitivity=%fm/s**2/%s, Digitizer Sensitivity=%fCt/V' %(cal_input,nCalMode,cal_stvt,nCalMode,ad_stvt))
    (cal_gain1,cal_gain2) = addCalPulse(infile,outfile,cal_input,cal_stvt,ad_stvt,nNetMode,nCalMode)

    if (cal_gain1==0 and cal_gain2==0):
        print('Calibration Calculate Error!')
    else:
        print('Calibration Calculate OK!')

if __name__ == "__main__":
   main(sys.argv[1:])