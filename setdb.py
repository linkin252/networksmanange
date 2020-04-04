# coding=utf-8

import warnings
warnings.filterwarnings("ignore")

import datetime
import os
import platform
import sqlite3


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
    def getField(self, field, name):
        sql = 'SELECT %s from instruments_instruments_base where Name="%s"' % (field, name)
        ret = self.selCmd(sql)
        return ret


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
    def __init__(self, Name='TDV-60B', Freq='', Sensitivity=''):
        super().__init__()
        self.Name = Name
        self.Freq = Freq
        self.Sensitivity = Sensitivity

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

    def getField(self, field, name):  # 获取仪器类型
        try:
            sql = 'SELECT %s from instruments_sensor_info where id="%d"' % (field, name)
            ret = self.selCmd(sql)
        except TypeError:
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


class ZeroPoles(SetDB):
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


def countDay_1OfYear(now):
    dayCount = now - datetime.date(now.year - 1, 12, 31)  # 减去上一年最后一天
    if dayCount.days == 1:
        dayCount = countDay_1OfYear(datetime.date(now.year - 1, 12, 31))
    elif dayCount.days == 365 or dayCount.days == 366:
        return dayCount
    else:
        return dayCount.days - 1
    return dayCount.days


def updateSql():
    table_list = ('networks_network', 'networks_station', 'networks_sta_adsensor',
                  'networks_channel', 'networks_day_data', 'instruments_ad_sensor')
    for table in table_list:
        DeleteSql().updateid(table)


def addNetDemo(fSrcDir, static_path, flag=True):
    STATIC_PATH = static_path
    sDenDir = 'networks'
    fDenDir = os.path.join(STATIC_PATH, sDenDir)
    mkfile(fDenDir, 0)
    all_files = []
    all_paths = []
    all_files, all_paths = show_path(fSrcDir, all_files, all_paths)
    for i in range(0, len(all_files)):
        file = all_files[i]
        path = all_paths[i]
        if file.count('.') >= 6:
            dayCount = countDay_1OfYear(datetime.date.today())
            (NetCode, StaCode, LocCode, ChCode, DataCode, nYear, nDay) = file.split('.')
            if (len(NetCode) <= 2 and len(StaCode) <= 5 and len(LocCode) <= 2 and len(ChCode) <= 3 and DataCode == 'D'
                    and len(nYear) <= 4 and len(nDay) <= 3 and int(nDay) == dayCount):  # and int(nDay) == dayCount
                # net = Network(NetCode, NetCode, fSrcDir, sDenDir, 3).get_or_create_Network()
                # sta = Station(net, StaCode, StaCode).get_or_create_Station()
                cDigitizerInfo = DigitizerInfo('TDE-324', '10Vpp', '100Hz', 'Linear')
                (bRet, AD, gain, rate, filter) = cDigitizerInfo.getDigitizerInfo()
                if not bRet:
                    print('Digitizer not found!')
                    continue
                cSensorInfo = SensorInfo('TDA-33M')
                (bRet, sensor, sensorinfo) = cSensorInfo.getSensorInfo()
                if not bRet:
                    print('Sensor not found!')
                    continue
                # adsensor = ADSensor(filter, sensorinfo).get_ADSensor()
                # sta_adsensor = Sta_ADSensor(sta, adsensor).get_or_create_Sta_ADSensor()
                ch = Channel(1, LocCode, ChCode).get_or_create_CH()

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

                from obspy import read
                # from obspy.io.xseed import Parser
                from obspy.signal import PPSD
                from obspy.imaging.cm import pqlx

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
                st.plot(size=(800, 600), tick_format='%I:%M:%p', type="dayplot", interval=30,
                        right_vertical_labels=True,
                        vertical_scaling_range=st[0].data.std() * 20, one_tick_per_line=True,
                        color=["r", "b", "g"], show_y_UTC_label=True,
                        title=ChName, time_offset=8,
                        outfile=outfile1)
                st2 = st.copy()

                st.filter("lowpass", freq=0.2, corners=2)
                st.plot(size=(800, 600), tick_format='%I:%M:%p', type="dayplot", interval=30,
                        right_vertical_labels=True,
                        vertical_scaling_range=st[0].data.std() * 20, one_tick_per_line=True,
                        color=["r", "b", "g"], show_y_UTC_label=True,
                        title=ChName + '.low_pass 0.2Hz', time_offset=8,
                        outfile=outfile2)

                st2.filter("highpass", freq=0.2)
                st2.plot(size=(800, 600), tick_format='%I:%M:%p', type="dayplot", interval=30,
                         right_vertical_labels=True,
                         vertical_scaling_range=st2[0].data.std() * 20, one_tick_per_line=True,
                         color=["r", "b", "g"], show_y_UTC_label=True,
                         # events={"min_magnitude": 5},
                         title=ChName + '.high_pass 0.2Hz', time_offset=8,
                         outfile=outfile3)

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
                st = read(path)
                # print(st)
                ppsd = PPSD(st[0].stats, paz)
                ppsd.add(st)
                # print(ppsd.times_data)
                # print('len=',len(ppsd.times_data),ppsd.times_data[0][0],ppsd.times_data[0][1])
                if flag:
                    ppsd.plot(outfile4, xaxis_frequency=True, cmap=pqlx)
                    ppsd.plot_spectrogram(filename=outfile5, cmap='CMRmap_r')
                    if cSensorInfo.getField('IMainType', sensor) < 2000:
                        outfile6 = fDenDir + '/' + ChName + '.1-2s.sp.png'
                        ppsd.plot_temporal(1.414, filename=outfile6)
                    elif 2000 <= cSensorInfo.getField('IMainType', sensor) < 3000:  # 加速度模式)
                        outfile6 = fDenDir + '/' + ChName + '.1-2Hz.sp.png'
                        ppsd.plot_temporal(.707, filename=outfile6)
                fBlankTime = 0.
                for i in range(1, len(ppsd.times_data)):  # 1个整时间段说明未丢数
                    dt = (ppsd.times_data[i][0] - ppsd.times_data[i - 1][1])
                    if dt < 0:
                        print(dt, ppsd.times_data[i][0], ppsd.times_data[i - 1][1])
                    else:
                        fBlankTime += dt
                runrate = 1.0 - fBlankTime / 86400.
                date = datetime.date(ppsd.times_data[0][0].year, ppsd.times_data[0][0].month, ppsd.times_data[0][0].day)
                DayData(ch, date, runrate).set_or_create_Day_data()
        else:
            print(file, "Name is error.")


def Net2dbDemo():
    # updateSql()  # 删除旧数据并更新数据库
    if PLATFORM == 'Windows':
        static_path = os.path.join(os.path.dirname(__file__), 'static')
        if os.path.exists('D:\\LK\\86.40新镜像程序\\TD.STA40'):
            addNetDemo('D:\\LK\\86.40新镜像程序\\TD.STA40', static_path)
        elif os.path.exists("E:\\86.40新镜像程序\\源数据\\ATSY"):
            addNetDemo("E:\\86.40新镜像程序\\源数据\\ATSY", static_path)
        else:
            print('Resource File not found!')
    elif PLATFORM == 'Linux':
        static_path = '/home/usrdata/usb/django/taide/static'
        addNetDemo('/home/usrdata/usb/data', static_path)
        addNetDemo('/home/usrdata/usb/mondata', static_path, False)


def main():
    if not os.path.exists(SQL_PATH) and PLATFORM == 'Linux':
        mkfile(os.path.dirname(SQL_PATH), 0)
        os.system('sudo cp /home/usrdata/pi/tde/params/db.sqlite3 %s' % os.path.dirname(SQL_PATH))
    Net2dbDemo()


if __name__ == "__main__":
    if platform.system() == 'Windows':
        PLATFORM = 'Windows'
        SQL_PATH = 'D:/django/trunk/db.sqlite3'
    elif platform.system() == 'Linux':
        PLATFORM = 'Linux'
        SQL_PATH = '/home/usrdata/usb/django/taide/db.sqlite3'
    main()
