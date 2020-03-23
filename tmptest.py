# coding = utf-0

import os
import configparser
import re
import struct


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


def addCalInput(chn_list):
    f = open('D:/django/trunk/da.par', 'rb')
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
        if nCommRate == 0:  # 26位
            if nGain_CI == iGain[0]:
                ad_ctvt_ci = 1677721.6/iGain[1]
            if nGain_FI == iGain[0]:
                ad_ctvt_fi = 1677721.6/iGain[1]
        elif nCommRate == 1:  # 24位
            if nGain_CI == iGain[0]:
                ad_ctvt_ci = 419430.4/iGain[1]
            if nGain_FI == iGain[0]:
                ad_ctvt_fi = 419430.4/iGain[1]
    for i in range(len(chn_list)):
        if i < 3:
            chn_list[i].append(ad_ctvt_ci)
        if i >= 3:
            chn_list[i].append(ad_ctvt_fi)


chn_list = []
chnMatch('pi.ini', chn_list)
senMatch('response.ini', chn_list)
addCalInput(chn_list)
getCiPar('ci.par', chn_list)
print(chn_list)


