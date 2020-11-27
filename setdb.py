# coding=utf-8
import configparser
import re
import time
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

from obspy import read
from obspy.signal import PPSD
from obspy.imaging.cm import pqlx

import datetime
import os
import sys, getopt
import platform
import sqlite3

MON_CHN = {}
MON_KEYS_CI = ('MONITOR1', 'MONITOR2', 'MONITOR3', 'MONITOR4', 'MONITOR5',
            'MONITOR6', 'MONITOR7')
MON_DIST_CI = {'MONITOR1': ('UD1零位', 0.001, '幅值(V)'), 'MONITOR2': ('NS1零位', 0.001, '幅值(V)'),
            'MONITOR3': ('EW1零位', 0.001, '幅值(V)'), 'MONITOR4': ('供电电压', 0.001, '电压(V)'),
            'MONITOR5': ('供电电流', 0.00001, '电流(A)'), 'MONITOR6': ('主板温度', 0.01, '温度(°C)'),
            'MONITOR7': ('CPU温度', 0.01, '温度(°C)')}
MON_KEYS_FI = ('MONITOR1', 'MONITOR2', 'MONITOR3', 'MONITOR4', 'MONITOR5',
            'MONITOR6', 'MONITOR7', 'MONITOR8', 'MONITOR9', 'MONITOR10')
MON_DIST_FI = {'MONITOR1': ('UD1零位', 0.001, '幅值(V)'), 'MONITOR2': ('NS1零位', 0.001, '幅值(V)'),
            'MONITOR3': ('EW1零位', 0.001, '幅值(V)'), 'MONITOR4': ('UD2零位', 0.001, '幅值(V)'),
            'MONITOR5': ('NS2零位', 0.001, '幅值(V)'), 'MONITOR6': ('EW2零位', 0.001, '幅值(V)'),
            'MONITOR7': ('供电电压', 0.001, '电压(V)'), 'MONITOR8': ('供电电流', 0.00001, '电流(A)'),
            'MONITOR9': ('主板温度', 0.01, '温度(°C)'), 'MONITOR10': ('CPU温度', 0.01, '温度(°C)')}
DAS_2020_LIST = ('TDE-626CI-2', 'TDE-626FI-2')  # 新版324-2020数采
MONITOR2_LIST = ('TDPP-800', )  # 电源控制器2020

if platform.system() == 'Windows':
    PLATFORM = 'Windows'
    SQL_PATH = 'D:/django/trunk/db.sqlite3'
    MON_PATH = 'D:/django/trunk/params/monitor.ini'
    PI_PATH = 'D:/django/trunk/params/pi.ini'
    RES_PATH = 'D:/django/trunk/params/response.ini'
    cf = configparser.ConfigParser()
    cf.read(PI_PATH)
    if cf.getint('PI_PAR', 'CHN_NUM') == 3:
        AD_TYPE = 0
    else:
        AD_TYPE = 1
    STA_TYPE = cf.get('PI_PAR', 'STA_TYPE')
    sys.path.append('D:/django/trunk/')
elif platform.system() == 'Linux':
    PLATFORM = 'Linux'
    SQL_PATH = '/home/usrdata/usb/django/taide/db.sqlite3'
    MON_PATH = '/home/usrdata/pi/tde/params/monitor.ini'
    PI_PATH = '/home/usrdata/pi/tde/params/pi.ini'
    RES_PATH = '/home/usrdata/pi/tde/params/response.ini'
    cf = configparser.ConfigParser()
    cf.read(PI_PATH)
    if cf.getint('PI_PAR', 'CHN_NUM') == 3:
        AD_TYPE = 0
    else:
        AD_TYPE = 1
    STA_TYPE = cf.get('PI_PAR', 'STA_TYPE')
    sys.path.append('/home/usb/django/taide/')


class SetDB:
    def __init__(self):
        self.conn = sqlite3.connect(SQL_PATH)
        self.c = self.conn.cursor()

    def selCmd(self, sql):
        cursor = self.c.execute(sql)
        for row in cursor:
            ret = row[0]
            return ret


class Instruments_base(SetDB):
    def __init__(self):
        super().__init__()
        self.table = 'instruments_instruments_base'

    def getField(self, field, name):
        sql = 'SELECT %s from instruments_instruments_base where Name="%s"' % (field, name)
        ret = self.selCmd(sql)
        return ret

    def getid(self, field):
        sql = f'SELECT id from {self.table} where Name="{field}"'
        ret = self.selCmd(sql)
        return ret

    def delInst(self, Name):
        instruments_base_ptr_id = self.getid(Name)
        sensorinfo = SensorInfo()
        sensor_info_id = sensorinfo.getid(instruments_base_ptr_id)
        sql = f'DELETE FROM instruments_zeropole where sensor_info_id="{sensor_info_id}"'
        self.c.execute(sql)
        sql = f'DELETE FROM instruments_sensor_info where id="{sensor_info_id}"'
        self.c.execute(sql)
        sql = f'DELETE FROM instruments_sensor_base where instruments_base_ptr_id="{instruments_base_ptr_id}"'
        self.c.execute(sql)
        sql = f'DELETE FROM {self.table} where id="{instruments_base_ptr_id}"'
        self.c.execute(sql)
        self.conn.commit()



class Chg626(Instruments_base):
    def __init__(self):
        super().__init__()
        self.list = {7: 5368709.12, 10: 5368709.12, 8: 2684354.56, 11: 2684354.56, 9: 1342177.28, 12: 1342177.28}

    def isExists626(self):
        id = self.getField('id', 'TDE-626')
        if id is not None:
            print('TDE626ID:', id)
            sql = 'UPDATE instruments_instruments_base set Name="TDE-324-2020" where id="%d"' % id
            self.c.execute(sql)
            self.upd_sensitivity()
            self.conn.commit()
            self.create_png()
        else:
            print('TDE-324-2020 is exists')

    def upd_sensitivity(self):
        for id in range(7, 13):
            sql = 'UPDATE instruments_digitizer_filter set sensitivity=%f where DigitizerRate_id=%d' \
                  % (self.list[id], id)
            self.c.execute(sql)

    def create_png(self):
        sName = '泰德 TDE-324'
        for id in range(85, 97):
            sql = 'SELECT IParUrl FROM instruments_digitizer_filter where id=%d' % id
            parurl = self.selCmd(sql)
            if PLATFORM == 'Windows':
                dir = os.path.join('D:/django/trunk/static', parurl)
                (sample_rate, sensitivity) = self.parser_digitizer_resp(dir, sName)
            else:
                dir = '/home/usb/django/taide/static/' + parurl.replace('\\', '/')
                (sample_rate, sensitivity) = self.parser_digitizer_resp(dir, sName)
            print(dir)
            print(sample_rate, sensitivity)

    def plot_Digitizer_Freq_Amp(self, pltfile, sName, sample_rate, sensitivity, h, f):
        (font, fontTitle) = setFont()
        plt.figure(figsize=(16, 12))
        plt.grid(linestyle=':')
        plt.semilogy(f, abs(h))

        import datetime
        timestr = datetime.datetime.now().strftime('%Y-%m-%d')
        timestr = "Created by 泰德, " + timestr
        x0 = '                                                                   频率[Hz]                                         ' + timestr
        plt.xlabel(x0, fontproperties=font)
        plt.ylabel('增益[Ct/V]', fontproperties=font)
        plt.title('%s 理论幅频响应\n (采样速率：%sSPS，归一化增益：%sCt/V)\n' % (sName, sample_rate, sensitivity),
                  fontproperties=fontTitle)
        plt.savefig(pltfile)
        plt.close('all')

    def parser_digitizer_resp(self, dir, sName):
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
        self.plot_Digitizer_Freq_Amp(dir + '.freq_amp.png', sName, sample_rate, sensitivity, response, freqs)
        return (sample_rate, sensitivity)


class Company(SetDB):
    def __init__(self, Name, ChnName=''):
        self.Name = Name
        self.ChnName = ChnName
        super().__init__()

    def get_company(self):
        sql = 'SELECT id from instruments_company where Name="%s"' % self.Name
        Name = self.selCmd(sql)
        return Name

    def set_company(self):
        sql = 'INSERT INTO instruments_company (Name,ChnName,CIcon,CWeb,CInfo,CNational_id) VALUES ' \
              f'("{self.Name}", "{self.ChnName}", "company\\{self.Name}\\{self.Name}_icon.png", ' \
              f'"http://www.{self.Name}.cn", "company\\{self.Name}\\{self.Name}_info.txt", 1)'
        print(sql)
        self.c.execute(sql)
        self.conn.commit()



class Network(SetDB):
    def __init__(self, NetCode, NetName, fSrcDir, sDenDir, nNetMode):
        super().__init__()
        self.netCode = NetCode
        self.netName = NetName
        self.fSrcDir = fSrcDir
        self.sDenDir = sDenDir
        self.nNetMode = nNetMode

    def get_or_create_Network(self):
        sql = 'SELECT id from networks_network where Code="%s"' % self.netCode
        net = self.selCmd(sql)
        if net is None:
            self.create()
            net = self.get_or_create_Network()
        return net

    def create(self):
        sql = "INSERT INTO networks_network (Code, Name, IDataDir, IOutDir, INetMode) " \
              "VALUES ('%s', '%s', '%s', '%s', %d)" \
              % (self.netCode, self.netName, self.fSrcDir, self.sDenDir, self.nNetMode)
        self.c.execute(sql)
        self.conn.commit()


class Station(SetDB):
    def __init__(self, net, StaCode, StaName):
        super().__init__()
        self.net = net
        self.staCode = StaCode
        self.staName = StaName

    def get_or_create_Station(self):
        sql = 'SELECT id from networks_station where Code="%s" and Name="%s" and Network_id="%d"' \
              % (self.staCode, self.staName, self.net)
        sta = self.selCmd(sql)
        if sta is None:
            self.create()
            sta = self.get_or_create_Station()
        return sta

    def create(self, fJin=111.11, fWei=22.22, fHeigth=100., fDepth=100.):
        sql = "INSERT INTO networks_station (Code, Name, Network_id, fJin, fWei, fHeigth, fDepth)" \
              "VALUES ('%s', '%s', '%d', '%f', '%f', '%f', '%f')" \
              % (self.staCode, self.staName, self.net, fJin, fWei, fHeigth, fDepth)
        self.c.execute(sql)
        self.conn.commit()


class DeleteSql(SetDB):
    def delTable(self, table):
        sql = 'DROP TABLE %s' % table
        print(sql)
        self.c.execute(sql)
        self.conn.commit()

    def delAllField(self, table):  # 删除表中全部数据
        sql = 'DELETE from %s' % table
        print(sql)
        self.c.execute(sql)
        self.conn.commit()

    def updateid(self, table):  # 更新id从1开始
        self.delAllField(table)
        sql = 'UPDATE sqlite_sequence set seq=0 where name="%s"' % table
        print(sql)
        self.c.execute(sql)
        self.conn.commit()


class SelectAllTable(SetDB):
    def __init__(self):
        super().__init__()
        sql = 'SELECT name from sqlite_master where type = "table" order by name'
        self.c.execute(sql)
        print(self.c.fetchall())


class DigitizerInfo(Instruments_base):
    def __init__(self, Name='TDE-324', Gain='', Rate='', Filter=''):
        super().__init__()
        self.Name = Name
        self.Gain = Gain
        self.Rate = Rate
        self.Filter = Filter

    def getDigitizerInfo(self):
        AD = None
        gain = None
        rate = None
        filter = None
        sql = 'SELECT Name from instruments_instruments_base where Name="%s"' % self.Name
        AD = self.selCmd(sql)
        if AD is None:
            return False, AD, gain, rate, filter

        sql = 'SELECT id from instruments_instruments_base where Name="%s"' % self.Name
        AD_id = self.selCmd(sql)
        if self.Gain == '':
            sql = 'SELECT Gain from instruments_digitizer_gain where Digitizer_id="%d"' % AD_id
            self.Gain = gain = self.selCmd(sql)
            if gain is None:
                return False, AD, gain, rate, filter
        else:
            sql = 'SELECT Gain from instruments_digitizer_gain where Digitizer_id="%d" and Gain="%s"' % (
                AD_id, self.Gain)
            gain = self.selCmd(sql)
            if gain is None:
                return False, AD, gain, rate, filter

        sql = 'SELECT id from instruments_digitizer_gain where Gain="%s"' % self.Gain
        Gain_id = self.selCmd(sql)
        if self.Rate == '':
            sql = 'SELECT Rate from instruments_digitizer_rate where DigitizerGain_id="%d"' % Gain_id
            self.Rate = rate = self.selCmd(sql)
            if rate is None:
                return False, AD, gain, rate, filter
        else:
            sql = 'SELECT Rate from instruments_digitizer_rate where DigitizerGain_id="%d" and Rate="%s"' \
                  % (Gain_id, self.Rate)
            rate = self.selCmd(sql)
            if rate is None:
                return False, AD, gain, rate, filter

        sql = 'SELECT id from instruments_digitizer_rate where Rate="%s"' % self.Rate
        Rate_id = self.selCmd(sql)
        if self.Filter == '':
            sql = 'SELECT id from instruments_digitizer_filter where DigitizerRate_id="%d"' % Rate_id
            self.Filter = filter = self.selCmd(sql)
            if filter is None:
                return False, AD, gain, rate, filter
        else:
            sql = 'SELECT id from instruments_digitizer_filter where DigitizerRate_id="%d" and Filter="%s"' \
                  % (Rate_id, self.Filter)
            filter = self.selCmd(sql)
            if filter is None:
                return False, AD, gain, rate, filter
        return True, AD, gain, rate, filter

    def getField(self, field, name):
        try:
            sql = 'SELECT %s from instruments_digitizer_filter where id="%d"' % (field, name)
            ret = self.selCmd(sql)
        except TypeError:
            ret = super().getField(field, name)
        return ret


class SensorInfo(Instruments_base):
    def __init__(self, Name='TDV-60B', Freq='', Sensitivity='', resp=None):
        super().__init__()
        if resp is None:
            resp = {}
        self.table = 'instruments_sensor_info'
        self.Name = Name
        self.Freq = Freq
        self.Sensitivity = Sensitivity
        self.resp = resp

    def getSensorInfo(self):
        sensor = None
        sensorinfo = None
        sql = 'SELECT Name from instruments_instruments_base where Name="%s"' % self.Name
        sensor = self.selCmd(sql)
        if sensor is None:
            return False, sensor, sensorinfo
        sql = 'SELECT id from instruments_instruments_base where Name="%s"' % self.Name
        sensor_id = self.selCmd(sql)
        if self.Freq == '' and self.Sensitivity == '':
            sql = 'SELECT id from instruments_sensor_info where Sensor_id="%d"' % sensor_id
            sensorinfo = self.selCmd(sql)
            if sensorinfo is None:
                return False, sensor, sensorinfo
        else:
            sql = 'SELECT id from instruments_sensor_info where Sensor_id="%d" and ISensitivity="%s" and ' \
                  'IFreqInfo="%s"' % (sensor_id, self.Sensitivity, self.Freq)
            sensorinfo = self.selCmd(sql)
            if sensorinfo is None:
                return False, sensor, sensorinfo
        return True, sensor, sensorinfo

    def setSensorInfo(self):
        ICompany_id = Company(self.resp['company']).get_company()

        sql = 'INSERT INTO instruments_instruments_base ' \
              '(Name, IMainType, IDBOK, IDir, MainChannel, AuxChannel, ICompany_id) ' \
              f'VALUES ("{self.Name}", {self.resp["mode"]}, 1, "instruments\sensor\\{self.resp["company"]}\\{self.Name}", ' \
              f'3, 3, {ICompany_id})'
        self.c.execute(sql)
        self.conn.commit()

        sensor_id = Instruments_base().getid(self.Name)
        sql = f'INSERT INTO instruments_sensor_base (instruments_base_ptr_id) VALUES ({sensor_id})'
        self.c.execute(sql)
        self.conn.commit()

        selunit = lambda x: 'V/M/S' if x == 1000 else 'V/M/S**2'
        sql = f'INSERT INTO {self.table} ' \
              '(ISensitivityInfo, IParUrl, IFreqInfo, IGainNormalization, IGain, ZeroNum, PoleNum, Sensor_id) ' \
              f'VALUES ("{self.resp["gain0"]}{selunit(self.resp["mode"])}", ' \
              f'"instruments\sensor\\{self.resp["company"]}\\{self.Name}\\{self.Name}", ' \
              f'"{self.resp["freq"]}Hz", {self.resp["gainno0"]}, {self.resp["gain0"]}, {self.resp["zerono0"]}, ' \
              f'{self.resp["poleno0"]}, {sensor_id})'
        self.c.execute(sql)
        self.conn.commit()

        sensor_info_id = self.getid(sensor_id)
        if self.resp["zerono0"]:
            gp = self.resp["zerogp0"]
            for i in range(0, len(gp), 2):
                sql = 'INSERT INTO instruments_zeropole (nZPMode, fReal, fImag, sComplex, sensor_info_id) ' \
                      f'VALUES ({0}, {gp[i]}, {gp[i+1]}, "{gp[i]}+{gp[i+1]}j", {sensor_info_id})'
                self.c.execute(sql)
        if self.resp["poleno0"]:
            gp = self.resp["polegp0"]
            for i in range(0, len(gp), 2):
                sql = 'INSERT INTO instruments_zeropole (nZPMode, fReal, fImag, sComplex, sensor_info_id) ' \
                      f'VALUES ({1}, {gp[i]}, {gp[i+1]}, "{gp[i]}+{gp[i+1]}j", {sensor_info_id})'
                self.c.execute(sql)
        self.conn.commit()

    def delSensorInfo(self):
        pass

    def getid(self, field):
        sql = f'SELECT id from {self.table} where Sensor_id="{field}"'
        ret = self.selCmd(sql)
        return ret

    def getField(self, field, name):  # 获取仪器类型
        try:
            sql = f'SELECT {field} from {self.table} where id="{name}"'
            ret = self.selCmd(sql)
        except:
            ret = super().getField(field, self.Name)
        return ret


class ADSensor(SetDB):
    def __init__(self, filter, sensorinfo1, sensorinfo2=None, sensorinfo3=None, sensorinfo4=None):
        super().__init__()
        self.filter = filter
        self.sensorinfo1 = sensorinfo1
        if sensorinfo4 == None:
            self.sensorinfo4 = sensorinfo1
        if sensorinfo3 == None:
            self.sensorinfo3 = sensorinfo1
        if sensorinfo2 == None:
            self.sensorinfo2 = sensorinfo1

    def get_ADSensor(self):
        sql = 'SELECT id from instruments_ad_sensor where ADInfo_id="%d" and Sensorinfo1_id="%d" and ' \
              'Sensorinfo2_id="%d" and ' \
              'Sensorinfo3_id="%d" and ' \
              'Sensorinfo4_id="%d"' % (self.filter, self.sensorinfo1,
                                       self.sensorinfo2, self.sensorinfo3, self.sensorinfo4)
        adsensor = self.selCmd(sql)
        if adsensor is None:
            sql = 'INSERT INTO instruments_ad_sensor ' \
                  '(type, ADInfo_id, SensorInfo1_id,  SensorInfo2_id, SensorInfo3_id, SensorInfo4_id)' \
                  ' VALUES (1, %d, %d, %d, %d, %d)' \
                  % (self.filter, self.sensorinfo1, self.sensorinfo2, self.sensorinfo3, self.sensorinfo4)
            self.c.execute(sql)
            self.conn.commit()
            adsensor = self.get_ADSensor()
        return adsensor


class Sta_ADSensor(SetDB):
    def __init__(self, sta, ADSensor):
        super().__init__()
        self.sta = sta
        self.ADSensor = ADSensor

    def get_or_create_Sta_ADSensor(self):
        sql = 'SELECT id from networks_sta_adsensor where ADSensor_id="%d" and Station_id="%d"' \
              % (self.ADSensor, self.sta)
        sta_adsensor_id = self.selCmd(sql)
        if sta_adsensor_id is None:
            sql = 'INSERT INTO networks_sta_adsensor (SeiralNo, ADSensor_id, Station_id) ' \
                  'VALUES (%d, %d, %d)' % (0, self.ADSensor, self.sta)
            self.c.execute(sql)
            self.conn.commit()
            sta_adsensor_id = self.get_or_create_Sta_ADSensor()
        return sta_adsensor_id


class Channel(SetDB):
    def __init__(self, StaADSensor, LocCode, ChCode):
        super().__init__()
        self.sta_adsensor = StaADSensor
        self.locCode = LocCode
        self.chCode = ChCode

    def get_or_create_CH(self):
        sql = 'SELECT id from networks_channel where ' \
              'Code_Loc="%s" and Code_CH="%s" and Sta_ADSensor_id="%d"' \
              % (self.locCode, self.chCode, self.sta_adsensor)
        ch_id = self.selCmd(sql)
        if ch_id is None:
            ch_id = 1
            # starttime = datetime.date.today()
            # endtime = datetime.date(2099, 1, 1)
            # sql = 'INSERT INTO networks_channel (CHNo, Code_Loc, Code_CH, Start_Time, End_Time, Sta_ADSensor_id) ' \
            #       'VALUES ("%d", "%s", "%s", "%s", "%s", "%d")' \
            #       % (0, self.locCode, self.chCode, starttime, endtime, self.sta_adsensor)
            # self.c.execute(sql)
            # self.conn.commit()
            # ch_id = self.get_or_create_CH()
        return ch_id


class DayData(SetDB):
    def __init__(self, ch, date, runrate):
        super().__init__()
        self.ch = ch
        self.date = date
        self.rundate = runrate

    def set_or_create_Day_data(self):
        sql = 'SELECT id from networks_day_data where ch_id="%d" and date="%s"' % (self.ch, self.date)
        data_id = self.selCmd(sql)
        if data_id is None:
            sql = 'INSERT INTO networks_day_data (ch_id, date, runrate) VALUES ("%d", "%s", "%f")' \
                  % (self.ch, self.date, self.rundate)
            self.c.execute(sql)
            self.conn.commit()
            data_id = self.set_or_create_Day_data()
            return data_id
        sql = 'UPDATE networks_day_data SET runrate="%f" where id="%d"' % (self.rundate, data_id)
        self.c.execute(sql)
        self.conn.commit()
        return data_id


class ZeroPoles(SensorInfo):
    pass


class Zeros(ZeroPoles):
    def __init__(self, sensorinfo):
        super().__init__()
        self.sensorinfo = sensorinfo

    def getZero(self):
        sql = 'SELECT fReal, fImag from instruments_zeropole where nZPMode=0 and sensor_info_id="%d"' % self.sensorinfo
        zero_list = self.selCmd(sql)
        return zero_list

    def selCmd(self, sql):
        zero_list = []
        cursor = self.c.execute(sql)
        for row in cursor:
            zero_list.append(complex(row[0], row[1]))
        return zero_list


class Poles(ZeroPoles):
    def __init__(self, sensorinfo):
        super().__init__()
        self.sensorinfo = sensorinfo

    def getPole(self):
        sql = 'SELECT fReal, fImag from instruments_zeropole where nZPMode=1 and sensor_info_id="%d"' % self.sensorinfo
        pole_list = self.selCmd(sql)
        return pole_list

    def selCmd(self, sql):
        pole_list = []
        cursor = self.c.execute(sql)
        for row in cursor:
            pole_list.append(complex(row[0], row[1]))
        return pole_list


class selopt:
    def __init__(self, daycount=0):
        monMatch(MON_PATH)
        if PLATFORM == 'Windows':
            if STA_TYPE in MONITOR2_LIST:
                static_path = 'D:\\LK\\TDPP\\产出数据'
                srcdir = 'D:\\LK\\TDPP\\源数据'
            else:
                static_path = 'D:\\LK\\86.40新镜像程序\\产出数据'
                srcdir = 'D:\\LK\\86.40新镜像程序\\源数据'
        else:
            static_path = '/home/usrdata/usb/django/taide/static'
            srcdir = '/home/usrdata/usb'
        self.produce = Produce(srcdir, static_path, daycount=daycount)
        self.pro_flag = True
        if not os.path.exists(srcdir):
            self.pro_flag = False

    def opts_(self, opt):
        if self.pro_flag:
            if STA_TYPE in DAS_2020_LIST:
                if opt == 'all':
                    self.produce.addData()
                    self.produce.addMonData()
                elif opt == 'data':
                    self.produce.addData()
                elif opt == 'mondata':
                    self.produce.addMonData()
                elif opt == 'qdata':
                    self.produce.addData(1)
            elif STA_TYPE in MONITOR2_LIST:
                self.produce.tdppdata()

        else:
            print('Resource File not found!')


def mkfile(path, mode):
    if not os.path.exists(path):
        if mode == 0:
            os.makedirs(path)
        elif mode == 1:
            f = open(path, 'wt')
            f.close()
        return False
    return True


def show_path(path, all_files, all_paths):
    files = os.listdir(path)
    for file in files:
        if os.path.isfile(os.path.join(path, file)):
            all_files.append(file)
            all_paths.append(os.path.join(path, file))
        elif os.path.isdir(os.path.join(path, file)):
            all_files, all_paths = show_path(os.path.join(path, file), all_files, all_paths)
    return all_files, all_paths


def yes_count(now):
    """
    判断昨天日期天数
    @param now: 今天日期
    @return: 昨天日期的天数
    """
    dayCount = now - datetime.date(now.year - 1, 12, 31)  # 减去上一年最后一天
    if dayCount.days == 1:
        dayCount = yes_count(datetime.date(now.year - 1, 12, 31))
    elif dayCount.days == 365 or dayCount.days == 366:
        return dayCount
    else:
        return dayCount.days - 1
    return dayCount.days


def updateSql():
    """
    清空本地台站数据库数据
    """
    table_list = ('networks_network', 'networks_station', 'networks_sta_adsensor',
                  'networks_channel', 'networks_day_data', 'instruments_ad_sensor')
    for table in table_list:
        DeleteSql().updateid(table)

def clearSql():
    """
    清空本地台站数据库数据
    """
    table_list = ('networks_day_data', )
    for table in table_list:
        DeleteSql().updateid(table)


def chnMatch(path, chn_list):
    """
    匹配通道名和通道摆类型
    @param path: pi.ini路径
    @param chn_list: 匹配列表
    @return:匹配列表
    """
    cf = configparser.ConfigParser()
    cf.read(path)
    chn_num = cf.getint('PI_PAR', 'CHN_NUM')
    chn = [['CHN0_CODE', 'CHN0_TYPE'], ['CHN1_CODE', 'CHN1_TYPE'], ['CHN2_CODE', 'CHN2_TYPE'],
           ['CHN3_CODE', 'CHN3_TYPE'], ['CHN4_CODE', 'CHN4_TYPE'], ['CHN5_CODE', 'CHN5_TYPE']]
    if chn_num == 3:
        for i in range(0, 3):
            if cf.getint('PI_PAR', chn[i][1]) == 1:
                chn[i].append('V')
            elif cf.getint('PI_PAR', chn[i][1]) == 2:
                chn[i].append('A')
            else:
                chn[i].append('A')
            chn_list.append([cf.get('PI_PAR', chn[i][0]), chn[i][2]])
    elif chn_num == 6:
        for i in range(0, 6):
            if cf.getint('PI_PAR', chn[i][1]) == 1:
                chn[i].append('V')
            elif cf.getint('PI_PAR', chn[i][1]) == 2:
                chn[i].append('A')
            else:
                chn[i].append('A')
            chn_list.append([cf.get('PI_PAR', chn[i][0]), chn[i][2]])
    else:
        for i in range(chn_num):
            chn_list.append([cf.get('PI_PAR', f'CHN{i}_CODE'), 'A'])
    return chn_list


def senMatch(path, chn_list):
    """
    添加电压/电流标定，标定灵敏度
    @param path: response.ini路径
    @param chn_list: 匹配列表
    @return: 匹配列表
    """
    f = open(path, 'r')
    for readline in f.readlines():
        if 'SENSOR0_TYPE' in readline:
            for i in range(0, 3):
                chn_list[i].append(re.split("=|,|\n", readline)[2])
        if 'SENSOR1_TYPE' in readline and len(chn_list) > 3:
            for i in range(3, 6):
                chn_list[i].append(re.split("=|,|\n", readline)[2])
    return chn_list


# 修改数据库626为324-2020
def isnewSql():
    # from obspy.io.xseed.parser import Parser
    # from obspy import read_inventory
    chg626 = Chg626()
    chg626.create_png()


def monMatch(path):
    cf = configparser.ConfigParser()
    cf.read(PI_PATH)
    sta_type = cf.get('PI_PAR', 'STA_TYPE')
    mon_dist = {}
    if sta_type in {'TDE-624FI', 'TDE-626FI-2'}:
        MON_KEYS = MON_KEYS_FI
        MON_DIST = MON_DIST_FI
    else:
        MON_KEYS = MON_KEYS_CI
        MON_DIST = MON_DIST_CI
    for mon in MON_KEYS:
        mon_dist.setdefault(mon, '')
    if os.path.exists(path):
        f = open(path, 'r')
        for readline in f.readlines():
            if readline.split('=')[0] in MON_KEYS:
                chName = re.split("=|,|\s", readline)
                mon_dist[readline.split('=')[0]] = chName[-2]
    for key in MON_KEYS:
        MON_CHN.setdefault(mon_dist[key], MON_DIST[key])


def stamp2time(stamp):
    da = time.localtime(stamp)
    da = time.strftime('%H:%M:%S', da)
    return da


def setFont():
    sys = platform.system()
    if sys == "Windows":
        font = FontProperties(fname=r"c:\\windows\\fonts\\simhei.ttf", size=9)
        fontTitle = FontProperties(fname=r"c:\\windows\\fonts\\simhei.ttf", size=12)
    else:
        font = FontProperties(fname=r"/usr/share/fonts/SIMHEI.TTF", size=9)
        fontTitle = FontProperties(fname=r"/usr/share/fonts/SIMHEI.TTF", size=12)
    return font, fontTitle


#  统一采样率和标识符
def mulRate(st):
    tr_id = []
    for i in range(len(st)):
        if st[i].id not in tr_id:
            tr_id.append(st[i].id)

    tr = []
    for i in range(len(st)):
        if st[i].stats.sampling_rate not in tr:
            tr.append(float(st[i].stats.sampling_rate))
    if len(tr) == 1 and len(tr_id) == 1:
        return st
    elif len(tr) != 1:
        max_sam = 0
        max_time = 0
        for i in range(len(tr)):
            st2 = st.select(sampling_rate=tr[i])
            times = st2[0].stats.endtime.timestamp - st2[0].stats.starttime.timestamp
            if times > max_time:
                max_time = times
                max_sam = tr[i]
        st2 = st.copy()
        st2.interpolate(sampling_rate=max_sam)
        print("change traces to same sampling rate:%d from %s" % (max_sam, tr))
        return st2
    elif len(tr_id) != 1:
        max_id = 0
        max_time = 0
        for i in range(len(tr_id)):
            st2 = st.select(id=tr_id[i])
            times = st2[0].stats.endtime.timestamp - st2[0].stats.starttime.timestamp
            if times > max_time:
                max_time = times
                max_id = tr_id[i]
        st2 = st.select(id=max_id)
        print("change traces to same id:%s from %s" % (max_id, tr_id))
        return st2
    else:
        return st


class Produce:
    def __init__(self, fSrcDir, static_path, daycount=0):
        self.STATIC_PATH = static_path
        self.sDenDir = 'networks'
        self.fDenDir = os.path.join(self.STATIC_PATH, self.sDenDir)
        self.fSrcDir = fSrcDir
        self.DATA_PATH = os.path.join(fSrcDir, 'data')
        self.MON_PATH = os.path.join(fSrcDir, 'mondata')
        mkfile(self.fDenDir, 0)
        self.chn_list = []
        self.sensortype = 'TMA-33'
        (self.font, self.fontTitle) = setFont()
        if daycount != 0:
            self.dayCount = daycount
        else:
            self.dayCount = yes_count(datetime.date.today())
        if PLATFORM == 'Windows':
            self.chn_list = chnMatch(PI_PATH, self.chn_list)
            self.chn_list = senMatch(RES_PATH, self.chn_list)
        else:
            if os.path.exists('/home/pi/tde/params/pi.ini'):
                self.chn_list = chnMatch('/home/pi/tde/params/pi.ini', self.chn_list)
            if os.path.exists('/home/pi/tde/params/response.ini'):
                self.chn_list = senMatch('/home/pi/tde/params/response.ini', self.chn_list)
            else:
                print('params files is not exists!')

    def addData(self, mod=11):
        all_files = []
        all_paths = []
        all_files, all_paths = show_path(self.DATA_PATH, all_files, all_paths)
        for I in range(0, len(all_files)):
            file = all_files[I]
            path = all_paths[I]
            if file.count('.') == 6:
                (NetCode, StaCode, LocCode, ChCode, DataCode, nYear, nDay) = file.split('.')
                if (int(nDay) == self.dayCount and len(NetCode) <= 2 and len(StaCode) <= 5 and len(LocCode) <= 2 and len(
                        ChCode) <= 3 and DataCode == 'D'
                        and len(nYear) <= 4 and len(nDay) <= 3):
                    # net = Network(NetCode, NetCode, fSrcDir, sDenDir, 3).get_or_create_Network()
                    # sta = Station(net, StaCode, StaCode).get_or_create_Station()
                    cDigitizerInfo = DigitizerInfo('TDE-324', '10Vpp', '100Hz', 'Linear')
                    (bRet, AD, gain, rate, filter) = cDigitizerInfo.getDigitizerInfo()
                    if not bRet:
                        print('Digitizer not found!')
                        continue

                    sDenDir2 = self.sDenDir + '/' + NetCode
                    fDenDir = os.path.join(self.STATIC_PATH, sDenDir2)
                    mkfile(fDenDir, 0)

                    sDenDir2 = sDenDir2 + '/' + StaCode
                    fDenDir = os.path.join(self.STATIC_PATH, sDenDir2)
                    mkfile(fDenDir, 0)

                    sDenDir2 = sDenDir2 + '/' + nYear
                    fDenDir = os.path.join(self.STATIC_PATH, sDenDir2)
                    mkfile(fDenDir, 0)

                    sDenDir2 = sDenDir2 + '/' + nDay
                    fDenDir = os.path.join(self.STATIC_PATH, sDenDir2)
                    mkfile(fDenDir, 0)

                    try:
                        st = read(path)
                    except Exception as ex:
                        print('%s数据读取错误\n' % file, ex)
                        continue
                    ChName = NetCode + '.' + StaCode + '.' + LocCode + '.' + ChCode + '.' + nYear + '.' + nDay
                    outfile1 = fDenDir + '/' + ChName + '.day_wave.png'
                    outfile2 = fDenDir + '/' + ChName + '.day_wave.low_pass_0.2Hz.png'
                    outfile3 = fDenDir + '/' + ChName + '.day_wave.high_pass_0.2Hz.png'
                    outfile4 = fDenDir + '/' + ChName + '.ppsd.png'
                    outfile5 = fDenDir + '/' + ChName + '.spectrogram.png'

                    print(NetCode, StaCode, LocCode, ChCode, DataCode, nYear, nDay)
                    st = mulRate(st)
                    if 11 & mod >> 1:
                        try:
                            st.plot(size=(1600, 1200), tick_format='%I:%M:%p', type="dayplot", interval=30,
                                    right_vertical_labels=True,
                                    vertical_scaling_range=st[0].data.std() * 40, one_tick_per_line=True,
                                    color=["r", "b", "g"], show_y_UTC_label=True,
                                    title=ChName, time_offset=8,
                                    outfile=outfile1)
                            st2 = st.copy()
                            st.filter("lowpass", freq=0.2, corners=2)
                            st.plot(size=(1600, 1200), tick_format='%I:%M:%p', type="dayplot", interval=30,
                                    right_vertical_labels=True,
                                    vertical_scaling_range=st[0].data.std() * 40, one_tick_per_line=True,
                                    color=["r", "b", "g"], show_y_UTC_label=True,
                                    title=ChName + '.low_pass 0.2Hz', time_offset=8,
                                    outfile=outfile2)

                            st2.filter("highpass", freq=0.2)
                            st2.plot(size=(1600, 1200), tick_format='%I:%M:%p', type="dayplot", interval=30,
                                     right_vertical_labels=True,
                                     vertical_scaling_range=st2[0].data.std() * 40, one_tick_per_line=True,
                                     color=["r", "b", "g"], show_y_UTC_label=True,
                                     # events={"min_magnitude": 5},
                                     title=ChName + '.high_pass 0.2Hz', time_offset=8,
                                     outfile=outfile3)
                        except Exception as ex:
                            print('主通道产出图失败\n', ex)
                    if 11 & mod:
                        for chn in self.chn_list:
                            if ChCode == chn[0] and len(chn) >= 3:
                                sensortype = chn[2]
                            else:
                                sensortype = 'TMA-33'
                        cSensorInfo = SensorInfo(sensortype)
                        (bRet, sensor, sensorinfo) = cSensorInfo.getSensorInfo()
                        if not bRet:
                            print('Sensor not found! use TMA-33')
                            cSensorInfo = SensorInfo('TMA-33')
                            (bRet, sensor, sensorinfo) = cSensorInfo.getSensorInfo()
                        # adsensor = ADSensor(filter, sensorinfo).get_ADSensor()
                        # sta_adsensor = Sta_ADSensor(sta, adsensor).get_or_create_Sta_ADSensor()
                        ch = Channel(1, LocCode, ChCode).get_or_create_CH()
                        print(ChCode, sensortype)

                        paz = {}
                        paz['zeros'] = []
                        paz['zeros'] = Zeros(sensorinfo).getZero()
                        paz['poles'] = []
                        paz['poles'] = Poles(sensorinfo).getPole()
                        if 2000 <= cSensorInfo.getField('IMainType', sensor) <= 3000:
                            paz['zeros'].append(complex(0., 0))
                        paz['gain'] = cSensorInfo.getField('IGainNormalization', sensorinfo)
                        paz['sensitivity'] = cSensorInfo.getField('IGain', sensorinfo) \
                                             * cDigitizerInfo.getField('sensitivity', filter)
                        # print(paz)
                        # print('len=',len(ppsd.times_data),ppsd.times_data[0][0],ppsd.times_data[0][1])
                        st = read(path)
                        ppsd = PPSD(st[0].stats, paz)
                        ppsd.add(st)
                        try:
                            ppsd.plot(outfile4, xaxis_frequency=True, cmap=pqlx)
                            ppsd.plot_spectrogram(filename=outfile5, cmap='CMRmap_r')
                            if cSensorInfo.getField('IMainType', sensor) < 2000:
                                outfile6 = fDenDir + '/' + ChName + '.1-2s.sp.png'
                                ppsd.plot_temporal(1.414, filename=outfile6)
                            elif 2000 <= cSensorInfo.getField('IMainType', sensor) < 3000:  # 加速度模式)
                                outfile6 = fDenDir + '/' + ChName + '.1-2Hz.sp.png'
                                ppsd.plot_temporal(.707, filename=outfile6)
                        except Exception as ex:
                            print('质量产出图失败\n', ex)
                        fBlankTime = 0.
                        # for I in range(1, len(ppsd.times_data)):  # 1个整时间段说明未丢数
                        #     dt = (ppsd.times_data[I][0] - ppsd.times_data[I - 1][1])
                        #     if dt < 0:
                        #         print(dt, ppsd.times_data[I][0], ppsd.times_data[I - 1][1])
                        #     else:
                        #         fBlankTime += dt
                        for i in range(1, len(st)):
                            dt = st[i].stats.starttime - st[i - 1].stats.endtime
                            if dt < 0:
                                print(st[i].stats.starttime, st[i - 1].stats.endtime)
                            else:
                                fBlankTime += dt
                        runrate = 1.0 - fBlankTime / 86400.
                        date = datetime.date(st[0].stats.starttime.year, st[0].stats.starttime.month,
                                             st[0].stats.starttime.day)
                        DayData(ch, date, runrate).set_or_create_Day_data()

    def addMonData(self):
        all_files = []
        all_paths = []
        all_files, all_paths = show_path(self.MON_PATH, all_files, all_paths)
        for I in range(0, len(all_files)):
            file = all_files[I]
            path = all_paths[I]
            if file.count('.') == 6:
                (NetCode, StaCode, LocCode, ChCode, DataCode, nYear, nDay) = file.split('.')
                if (int(nDay) == self.dayCount and len(NetCode) <= 2 and len(StaCode) <= 5 and len(LocCode) <= 2 and len(
                        ChCode) <= 3 and DataCode == 'D'
                        and len(nYear) <= 4 and len(nDay) <= 3):

                    sDenDir2 = self.sDenDir + '/' + NetCode
                    fDenDir = os.path.join(self.STATIC_PATH, sDenDir2)
                    mkfile(fDenDir, 0)

                    sDenDir2 = sDenDir2 + '/' + StaCode
                    fDenDir = os.path.join(self.STATIC_PATH, sDenDir2)
                    mkfile(fDenDir, 0)

                    sDenDir2 = sDenDir2 + '/' + nYear
                    fDenDir = os.path.join(self.STATIC_PATH, sDenDir2)
                    mkfile(fDenDir, 0)

                    sDenDir2 = sDenDir2 + '/' + nDay
                    fDenDir = os.path.join(self.STATIC_PATH, sDenDir2)
                    mkfile(fDenDir, 0)

                    try:
                        st = read(path)
                    except Exception as ex:
                        print('%s数据读取错误\n' % file, ex)
                        continue
                    ChName = NetCode + '.' + StaCode + '.' + LocCode + '.' + ChCode + '.' + nYear + '.' + nDay
                    outfile1 = fDenDir + '/' + ChName + '.day_wave.png'

                    print(NetCode, StaCode, LocCode, ChCode, DataCode, nYear, nDay)
                    try:
                        sTime = st[0].stats.starttime
                        nSample = st[0].stats.sampling_rate

                        f = lambda tick: sTime.timestamp + tick
                        xtick = np.arange(3600 * 24 + 1, step=14400)
                        xtk = []
                        xtk_list = []
                        mon_name = MON_CHN[ChCode][0]
                        mon_weight = MON_CHN[ChCode][1]
                        mon_units = MON_CHN[ChCode][2]
                        if re.search(r"[°CAV]+", MON_CHN[ChCode][2]).group():
                            mon_unit = re.search(r"[°CAV]+", MON_CHN[ChCode][2]).group()  # °C
                        else:
                            mon_unit = ''  # °C
                        max_data = max(st.max()) * mon_weight
                        min_data = min([min(tr) for tr in st]) * mon_weight
                        avg_data = (max_data + min_data) / 2
                        daystr = datetime.datetime.now().strftime('%Y-%m-%d')
                        timestr = "Created by 泰德, " + daystr
                        for i, x in enumerate(xtick):
                            xtk.append(x)
                            xtk_list.append(stamp2time(f(x)))
                        plt.figure(figsize=(8, 6))
                        plt.grid(linestyle=':')
                        for st0 in st:
                            mon_data = st0.data * mon_weight
                            ssTime = (st0.stats.starttime - sTime) * nSample
                            eeTime = (st0.stats.endtime - sTime) * nSample + 1
                            nTime = np.arange(ssTime, eeTime)
                            plt.plot(nTime, mon_data, c='blue')
                            # if (plt.axis()[-1] - plt.axis()[-2]) <= 1:
                            #     plt.ylim(ymin=(plt.axis()[-2]-0.5), ymax=(plt.axis()[-1]+0.5))
                            # if 1< (plt.axis()[-1] - plt.axis()[-2]) <= 10:
                            #     plt.ylim(ymin=(plt.axis()[-2]-10), ymax=(plt.axis()[-1]+10))
                        plt.xticks(xtk, xtk_list, fontproperties=self.font)
                        x0 = '                                                       时间                         ' + timestr
                        plt.xlabel(x0, fontproperties=self.font)
                        plt.ylabel(mon_units, fontproperties=self.font)
                        titles = '%s %s %s\n最小值:%.4f%s, 最大值:%.4f%s, 平均值:%.4f%s' % \
                                 (daystr, ChName, mon_name, min_data, mon_unit, max_data, mon_unit, avg_data, mon_unit)
                        plt.suptitle(titles, fontproperties=self.fontTitle)
                        plt.savefig(outfile1)
                        plt.close('all')
                    except Exception as ex:
                        print('辅助通道产出图失败\n', ex)
            else:
                pass

    def tdppdata(self):
        all_files = []
        all_paths = []
        all_files, all_paths = show_path(self.DATA_PATH, all_files, all_paths)
        for I in range(0, len(all_files)):
            file = all_files[I]
            path = all_paths[I]
            if file.count('.') == 6:
                (NetCode, StaCode, LocCode, ChCode, DataCode, nYear, nDay) = file.split('.')
                if (int(nDay) == self.dayCount and len(NetCode) <= 2 and len(StaCode) <= 5 and len(
                        LocCode) <= 2 and len(
                        ChCode) <= 3 and DataCode == 'D'
                        and len(nYear) <= 4 and len(nDay) <= 3):

                    sDenDir2 = self.sDenDir + '/' + NetCode
                    fDenDir = os.path.join(self.STATIC_PATH, sDenDir2)
                    mkfile(fDenDir, 0)

                    sDenDir2 = sDenDir2 + '/' + StaCode
                    fDenDir = os.path.join(self.STATIC_PATH, sDenDir2)
                    mkfile(fDenDir, 0)

                    sDenDir2 = sDenDir2 + '/' + nYear
                    fDenDir = os.path.join(self.STATIC_PATH, sDenDir2)
                    mkfile(fDenDir, 0)

                    sDenDir2 = sDenDir2 + '/' + nDay
                    fDenDir = os.path.join(self.STATIC_PATH, sDenDir2)
                    mkfile(fDenDir, 0)

                    try:
                        st = read(path)
                    except Exception as ex:
                        print('%s数据读取错误\n' % file, ex)
                        continue
                    ChName = NetCode + '.' + StaCode + '.' + LocCode + '.' + ChCode + '.' + nYear + '.' + nDay
                    outfile1 = fDenDir + '/' + ChName + '.day_wave.png'

                    print(NetCode, StaCode, LocCode, ChCode, DataCode, nYear, nDay)
                    st = mulRate(st)
                    try:
                        # st.plot(size=(960, 800), tick_format='%I:%M:%p', type="dayplot", interval=30,
                        #         right_vertical_labels=True,
                        #         vertical_scaling_range=st[0].data.std() * 20, one_tick_per_line=True,
                        #         color=["r", "b", "g"], show_y_UTC_label=True,
                        #         title=ChName, time_offset=8,
                        #         outfile=outfile1)
                        sTime = st[0].stats.starttime
                        nSample = st[0].stats.sampling_rate
                        f = lambda tick: sTime.timestamp + tick
                        xtick = np.arange(3600 * 24 + 1, step=14400)
                        xtk = []
                        xtk_list = []
                        daystr = datetime.datetime.now().strftime('%Y-%m-%d')
                        timestr = "Created by 泰德, " + daystr
                        titles = ChName
                        for i, x in enumerate(xtick):
                            xtk.append(x)
                            xtk_list.append(stamp2time(f(x)))
                        plt.figure(figsize=(12, 3.5))
                        plt.grid(linestyle=':')
                        for st0 in st:
                            mon_data = st0.data
                            ssTime = (st0.stats.starttime - sTime) * nSample
                            eeTime = (st0.stats.endtime - sTime) * nSample + 1
                            nTime = np.arange(ssTime, eeTime)
                            plt.plot(nTime, mon_data, c='blue')
                        #     x.extend(nTime)
                        #     y.extend(mon_data)
                        # plt.plot(x, y, c='blue')
                        plt.xticks(xtk, xtk_list, fontproperties=self.font)
                        x0 = ' '*75 + '时间' + ' '*40 + timestr
                        plt.xlabel(x0, fontproperties=self.font)
                        plt.ylabel('幅值（Ct）', fontproperties=self.font)
                        plt.suptitle(titles, fontproperties=self.fontTitle)
                        plt.savefig(outfile1)
                        plt.close('all')
                    except Exception as ex:
                        print('tdpp产出图失败\n', ex)


def addNetDemo(fSrcDir, static_path, daycount=0, mod=11):
    STATIC_PATH = static_path
    sDenDir = 'networks'
    fDenDir = os.path.join(STATIC_PATH, sDenDir)
    mkfile(fDenDir, 0)
    all_files = []
    all_paths = []
    chn_list = []
    sensortype = 'TMA-33'
    if daycount != 0:
        dayCount = daycount
    else:
        dayCount = yes_count(datetime.date.today())
    if os.path.exists(PI_PATH):
        chn_list = chnMatch(PI_PATH, chn_list)
        chn_list = senMatch(RES_PATH, chn_list)
    elif os.path.exists(PI_PATH) and os.path.exists(RES_PATH):
        chn_list = chnMatch(PI_PATH, chn_list)
        chn_list = senMatch(RES_PATH, chn_list)
    else:
        print('params files is not exists!')
        return
    all_files, all_paths = show_path(fSrcDir, all_files, all_paths)
    for I in range(0, len(all_files)):
        file = all_files[I]
        path = all_paths[I]
        if file.count('.') == 6:
            (NetCode, StaCode, LocCode, ChCode, DataCode, nYear, nDay) = file.split('.')
            if (int(nDay) == dayCount and len(NetCode) <= 2 and len(StaCode) <= 5 and len(LocCode) <= 2 and len(
                    ChCode) <= 3 and DataCode == 'D'
                    and len(nYear) <= 4 and len(nDay) <= 3):  # and int(nDay) == dayCount
                # net = Network(NetCode, NetCode, fSrcDir, sDenDir, 3).get_or_create_Network()
                # sta = Station(net, StaCode, StaCode).get_or_create_Station()
                cDigitizerInfo = DigitizerInfo('TDE-324', '10Vpp', '100Hz', 'Linear')
                (bRet, AD, gain, rate, filter) = cDigitizerInfo.getDigitizerInfo()
                if not bRet:
                    print('Digitizer not found!')
                    continue

                sDenDir2 = sDenDir + '/' + NetCode
                fDenDir = os.path.join(STATIC_PATH, sDenDir2)
                mkfile(fDenDir, 0)

                sDenDir2 = sDenDir2 + '/' + StaCode
                fDenDir = os.path.join(STATIC_PATH, sDenDir2)
                mkfile(fDenDir, 0)

                sDenDir2 = sDenDir2 + '/' + nYear
                fDenDir = os.path.join(STATIC_PATH, sDenDir2)
                mkfile(fDenDir, 0)

                sDenDir2 = sDenDir2 + '/' + nDay
                fDenDir = os.path.join(STATIC_PATH, sDenDir2)
                mkfile(fDenDir, 0)

                try:
                    st = read(path)
                except Exception as ex:
                    print('%s数据读取错误\n' % file, ex)
                    continue
                ChName = NetCode + '.' + StaCode + '.' + LocCode + '.' + ChCode + '.' + nYear + '.' + nDay
                outfile1 = fDenDir + '/' + ChName + '.day_wave.png'
                outfile2 = fDenDir + '/' + ChName + '.day_wave.low_pass_0.2Hz.png'
                outfile3 = fDenDir + '/' + ChName + '.day_wave.high_pass_0.2Hz.png'
                outfile4 = fDenDir + '/' + ChName + '.ppsd.png'
                outfile5 = fDenDir + '/' + ChName + '.spectrogram.png'

                print(NetCode, StaCode, LocCode, ChCode, DataCode, nYear, nDay)
                st = mulRate(st)
                if 11&mod >> 1:
                    try:
                        st.plot(size=(1600, 1200), tick_format='%I:%M:%p', type="dayplot", interval=30,
                                right_vertical_labels=True,
                                vertical_scaling_range=st[0].data.std() * 40, one_tick_per_line=True,
                                color=["r", "b", "g"], show_y_UTC_label=True,
                                title=ChName, time_offset=8,
                                outfile=outfile1)
                        st2 = st.copy()
                        st.filter("lowpass", freq=0.2, corners=2)
                        st.plot(size=(1600, 1200), tick_format='%I:%M:%p', type="dayplot", interval=30,
                                right_vertical_labels=True,
                                vertical_scaling_range=st[0].data.std() * 40, one_tick_per_line=True,
                                color=["r", "b", "g"], show_y_UTC_label=True,
                                title=ChName + '.low_pass 0.2Hz', time_offset=8,
                                outfile=outfile2)

                        st2.filter("highpass", freq=0.2)
                        st2.plot(size=(1600, 1200), tick_format='%I:%M:%p', type="dayplot", interval=30,
                                 right_vertical_labels=True,
                                 vertical_scaling_range=st2[0].data.std() * 40, one_tick_per_line=True,
                                 color=["r", "b", "g"], show_y_UTC_label=True,
                                 # events={"min_magnitude": 5},
                                 title=ChName + '.high_pass 0.2Hz', time_offset=8,
                                 outfile=outfile3)
                    except Exception as ex:
                        print('主通道产出图失败\n', ex)
                if 11&mod:
                    for chn in chn_list:
                        if ChCode == chn[0] and len(chn) >= 3:
                            sensortype = chn[2]
                        else:
                            sensortype = 'TMA-33'
                    cSensorInfo = SensorInfo(sensortype)
                    (bRet, sensor, sensorinfo) = cSensorInfo.getSensorInfo()
                    if not bRet:
                        print('Sensor not found! use TMA-33')
                        cSensorInfo = SensorInfo('TMA-33')
                        (bRet, sensor, sensorinfo) = cSensorInfo.getSensorInfo()
                    # adsensor = ADSensor(filter, sensorinfo).get_ADSensor()
                    # sta_adsensor = Sta_ADSensor(sta, adsensor).get_or_create_Sta_ADSensor()
                    ch = Channel(1, LocCode, ChCode).get_or_create_CH()
                    print(ChCode, sensortype)

                    paz = {}
                    paz['zeros'] = []
                    paz['zeros'] = Zeros(sensorinfo).getZero()
                    paz['poles'] = []
                    paz['poles'] = Poles(sensorinfo).getPole()
                    if 2000 <= cSensorInfo.getField('IMainType', sensor) <= 3000:
                        paz['zeros'].append(complex(0., 0))
                    paz['gain'] = cSensorInfo.getField('IGainNormalization', sensorinfo)
                    paz['sensitivity'] = cSensorInfo.getField('IGain', sensorinfo) \
                                         * cDigitizerInfo.getField('sensitivity', filter)
                    # print(paz)
                    # print('len=',len(ppsd.times_data),ppsd.times_data[0][0],ppsd.times_data[0][1])
                    st = read(path)
                    ppsd = PPSD(st[0].stats, paz)
                    ppsd.add(st)
                    try:
                        ppsd.plot(outfile4, xaxis_frequency=True, cmap=pqlx)
                        ppsd.plot_spectrogram(filename=outfile5, cmap='CMRmap_r')
                        if cSensorInfo.getField('IMainType', sensor) < 2000:
                            outfile6 = fDenDir + '/' + ChName + '.1-2s.sp.png'
                            ppsd.plot_temporal(1.414, filename=outfile6)
                        elif 2000 <= cSensorInfo.getField('IMainType', sensor) < 3000:  # 加速度模式)
                            outfile6 = fDenDir + '/' + ChName + '.1-2Hz.sp.png'
                            ppsd.plot_temporal(.707, filename=outfile6)
                    except Exception as ex:
                        print('质量产出图失败\n', ex)
                    fBlankTime = 0.
                    # for I in range(1, len(ppsd.times_data)):  # 1个整时间段说明未丢数
                    #     dt = (ppsd.times_data[I][0] - ppsd.times_data[I - 1][1])
                    #     if dt < 0:
                    #         print(dt, ppsd.times_data[I][0], ppsd.times_data[I - 1][1])
                    #     else:
                    #         fBlankTime += dt
                    for i in range(1, len(st)):
                        dt = st[i].stats.starttime - st[i - 1].stats.endtime
                        if dt < 0:
                            print(st[i].stats.starttime, st[i - 1].stats.endtime)
                        else:
                            fBlankTime += dt
                    runrate = 1.0 - fBlankTime / 86400.
                    date = datetime.date(st[0].stats.starttime.year, st[0].stats.starttime.month, st[0].stats.starttime.day)
                    DayData(ch, date, runrate).set_or_create_Day_data()
        else:
            pass


def addMonData(fSrcDir, static_path, daycount=0):
    STATIC_PATH = static_path
    sDenDir = 'networks'
    fDenDir = os.path.join(STATIC_PATH, sDenDir)
    mkfile(fDenDir, 0)
    all_files = []
    all_paths = []
    (font, fontTitle) = setFont()
    if daycount != 0:
        dayCount = daycount
    else:
        dayCount = yes_count(datetime.date.today())
    all_files, all_paths = show_path(fSrcDir, all_files, all_paths)
    for I in range(0, len(all_files)):
        file = all_files[I]
        path = all_paths[I]
        if file.count('.') == 6:
            (NetCode, StaCode, LocCode, ChCode, DataCode, nYear, nDay) = file.split('.')
            if (int(nDay) == dayCount and len(NetCode) <= 2 and len(StaCode) <= 5 and len(LocCode) <= 2 and len(
                    ChCode) <= 3 and DataCode == 'D'
                    and len(nYear) <= 4 and len(nDay) <= 3):

                sDenDir2 = sDenDir + '/' + NetCode
                fDenDir = os.path.join(STATIC_PATH, sDenDir2)
                mkfile(fDenDir, 0)

                sDenDir2 = sDenDir2 + '/' + StaCode
                fDenDir = os.path.join(STATIC_PATH, sDenDir2)
                mkfile(fDenDir, 0)

                sDenDir2 = sDenDir2 + '/' + nYear
                fDenDir = os.path.join(STATIC_PATH, sDenDir2)
                mkfile(fDenDir, 0)

                sDenDir2 = sDenDir2 + '/' + nDay
                fDenDir = os.path.join(STATIC_PATH, sDenDir2)
                mkfile(fDenDir, 0)

                try:
                    st = read(path)
                except Exception as ex:
                    print('%s数据读取错误\n' % file, ex)
                    continue
                ChName = NetCode + '.' + StaCode + '.' + LocCode + '.' + ChCode + '.' + nYear + '.' + nDay
                outfile1 = fDenDir + '/' + ChName + '.day_wave.png'

                print(NetCode, StaCode, LocCode, ChCode, DataCode, nYear, nDay)
                try:
                    sTime = st[0].stats.starttime
                    nSample = st[0].stats.sampling_rate

                    f = lambda tick: sTime.timestamp + tick
                    xtick = np.arange(3600 * 24 + 1, step=14400)
                    xtk = []
                    xtk_list = []
                    mon_name = MON_CHN[ChCode][0]
                    mon_weight = MON_CHN[ChCode][1]
                    mon_units = MON_CHN[ChCode][2]
                    if re.search(r"[°CAV]+", MON_CHN[ChCode][2]).group():
                        mon_unit = re.search(r"[°CAV]+", MON_CHN[ChCode][2]).group()  # °C
                    else:
                        mon_unit = ''  # °C
                    max_data = max(st.max()) * mon_weight
                    min_data = min([min(tr) for tr in st]) * mon_weight
                    avg_data = (max_data+min_data)/2
                    daystr = datetime.datetime.now().strftime('%Y-%m-%d')
                    timestr = "Created by 泰德, " + daystr
                    for i, x in enumerate(xtick):
                        xtk.append(x)
                        xtk_list.append(stamp2time(f(x)))
                    plt.figure(figsize=(8, 6))
                    plt.grid(linestyle=':')
                    for st0 in st:
                        mon_data = st0.data * mon_weight
                        ssTime = (st0.stats.starttime - sTime) * nSample
                        eeTime = (st0.stats.endtime - sTime) * nSample + 1
                        nTime = np.arange(ssTime, eeTime)
                        plt.plot(nTime, mon_data, c='blue')
                        # if (plt.axis()[-1] - plt.axis()[-2]) <= 1:
                        #     plt.ylim(ymin=(plt.axis()[-2]-0.5), ymax=(plt.axis()[-1]+0.5))
                        # if 1< (plt.axis()[-1] - plt.axis()[-2]) <= 10:
                        #     plt.ylim(ymin=(plt.axis()[-2]-10), ymax=(plt.axis()[-1]+10))
                    plt.xticks(xtk, xtk_list, fontproperties=font)
                    x0 = '                                                       时间                         ' + timestr
                    plt.xlabel(x0, fontproperties=font)
                    plt.ylabel(mon_units, fontproperties=font)
                    titles = '%s %s %s\n最小值:%.4f%s, 最大值:%.4f%s, 平均值:%.4f%s' % \
                             (daystr, ChName, mon_name, min_data, mon_unit, max_data, mon_unit, avg_data, mon_unit)
                    plt.suptitle(titles, fontproperties=fontTitle)
                    plt.savefig(outfile1)
                    plt.close('all')
                except Exception as ex:
                    print('辅助通道产出图失败\n', ex)
        else:
            pass

def Net2dbDemo(opt='all', daycount=0):
    monMatch(MON_PATH)
    if PLATFORM == 'Windows':
        static_path = 'D:\\LK\\86.40新镜像程序\\产出数据'
        srcdir = 'D:\\LK\\86.40新镜像程序\\源数据\\'
        produce = Produce(srcdir, static_path, daycount=daycount)
    else:
        static_path = '/home/usrdata/usb/django/taide/static'
        srcdir = '/home/usrdata/usb/'
        produce = Produce(srcdir, static_path, daycount=daycount)
    if os.path.exists(srcdir):
        if opt == 'all':
            produce.addData()
            produce.addMonData()
        elif opt == 'data':
            produce.addData()
        elif opt == 'mondata':
            produce.addMonData()
        elif opt == 'qdata':
            produce.addData(1)
    else:
        print('Resource File not found!')


def checkini():
    Enable = 1
    if PLATFORM == 'Windows':
        basedir = os.path.dirname(os.path.abspath(__file__))
    else:
        basedir = '/home/usrdata/pi/tde'
    ini_path = basedir + '/params/produce.ini'
    if os.path.exists(ini_path):
        cf = configparser.ConfigParser()
        cf.read(ini_path)
        if cf.has_section('PAR'):
            if cf.has_option('PAR', 'enable'):
                Enable = cf.getint('PAR', 'enable')
        else:
            cf.set('PAR', 'enable', '1')
            with open(ini_path, 'w') as wf:
                cf.write(wf)
    else:
        with open(ini_path, 'w+') as wf:
            cf = configparser.ConfigParser()
            cf.read(ini_path)
            cf.add_section('PAR')
            cf.set('PAR', 'enable', '1')
            cf.write(wf)
    return Enable

def main(argv):
    if not os.path.exists(SQL_PATH) and PLATFORM == 'Linux':
        mkfile(os.path.dirname(SQL_PATH), 0)
        os.system('sudo cp /home/usrdata/pi/tde/params/db.sqlite3 %s' % os.path.dirname(SQL_PATH))
        os.system('sudo chmod 777 %s' % SQL_PATH)
    # isnewSql()  # 更新626为324-2020
    # updateSql()  # 删除旧数据并更新数据库
    option = 'all'
    daycount = 0
    try:
        opts, args = getopt.getopt(argv,"hdmqD:", ['day', 'clearsql'])
    except getopt.GetoptError:
        print('sudo python3 setdb.py -d <data files> -m <mondata files> -D <day>  -q <quality files> --clearsql')
        sys.exit(2)
    if not opts and not checkini():
        # print('Auto production of pictures is prohibited')
        sys.exit(0)
    for opt, arg in opts:
        if opt == '-h':
            print('sudo python3 setdb.py -d <data files> -m <mondata files> -D <day> -q <quality files> --clearsql')
            sys.exit()
        elif opt == '-d':
            option = 'data'
        elif opt == '-m':
            option = 'mondata'
        elif opt in ('-D', '-Day'):
            daycount = int(arg)
        elif opt == '--clearsql':
            clearSql()
            sys.exit(0)
        elif opt == '-q':  # 质量图产出
            option = 'qdata'
    sTime = datetime.datetime.now()
    selopt(daycount).opts_(option)
    eTime = datetime.datetime.now()
    print('用时：%s' % (eTime-sTime))


if __name__ == "__main__":
    main(sys.argv[1:])