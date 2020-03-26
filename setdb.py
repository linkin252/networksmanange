# coding=utf-8
import datetime
import sqlite3

from trunk import calibrate

class Network:
    def __init__(self, NetCode, NetName, fSrcDir, sDenDir, nNetMode):
        self.conn = sqlite3.connect(SQL_PATH)
        self.c = self.conn.cursor()
        self.netCode = NetCode
        self.netName = NetName
        self.fSrcDir = fSrcDir
        self.sDenDir = sDenDir
        self.nNetMode = nNetMode

    def get_or_create_Network(self):
        try:
            sql = 'SELECT id from networks_network where ' \
                  'Code="%s" and Name="%s" and IDataDir="%s" and IOutDir="%s" and INetMode=%d'\
                  % (self.netCode, self.netName, self.fSrcDir, self.sDenDir, self.nNetMode)
            net = self.selCmd(sql)
            return net
        except:
            self.create()
            net = self.get_or_create_Network()
            return net

    def create(self):
        sql = "INSERT INTO networks_network (Code, Name, IDataDir, IOutDir, INetMode) " \
              "VALUES ('%s', '%s', '%s', '%s', %d)"\
              % (self.netCode, self.netName, self.fSrcDir, self.sDenDir, self.nNetMode)
        print(sql)
        self.c.execute(sql)
        self.conn.commit()

    def selCmd(self, sql):
        cursor = self.c.execute(sql)
        for row in cursor:
            ret = row[0]
            return ret


class Station:
    def __init__(self, net, StaCode, StaName):
        self.conn = sqlite3.connect(SQL_PATH)
        self.c = self.conn.cursor()
        self.net = net
        self.staCode = StaCode
        self.staName = StaName

    def get_or_create_Station(self):
        try:
            sql = 'SELECT id from networks_station where StaCode="%s" and StaName="%s" and Network_id="%d"'\
                  % (self.staCode, self.staName, self.net)
            sta = self.selCmd(sql)
        except:
            self.create()
            sta = self.get_or_create_Station()
        return sta

    def create(self, fJin=111.11, fWei=22.22, fHeigth=100., fDepth=100.):
        sql = "INSERT INTO networks_station (Code, Name, Network_id, fJin, fWei, fHeigth, fDepth)" \
              "VALUES ('%s', '%s', '%d', '%f', '%f', '%f', '%f')"\
              % (self.staCode, self.staName, self.net, fJin, fWei, fHeigth, fDepth)
        self.c.execute(sql)
        self.conn.commit()

    def selCmd(self, sql):
        cursor = self.c.execute(sql)
        for row in cursor:
            ret = row[0]
            return ret

class DeleteSql:
    def __init__(self):
        self.conn = sqlite3.connect(SQL_PATH)
        self.c = self.conn.cursor()

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


class SelectAllTable:
    def __init__(self):
        self.conn = sqlite3.connect(SQL_PATH)
        self.c = self.conn.cursor()
        sql = 'SELECT name from sqlite_master where type = "table" order by name'
        self.c.execute(sql)
        print(self.c.fetchall())


class DigitizerInfo:
    def __init__(self, Name='TDE-324', Gain='', Rate='', Filter=''):
        self.conn = sqlite3.connect(SQL_PATH)
        self.c = self.conn.cursor()
        self.Name = Name
        self.Gain = Gain
        self.Rate = Rate
        self.Filter = Filter

    def getDigitizerInfo(self):
        AD = None
        gain = None
        rate = None
        filter = None
        try:
            sql = 'SELECT Name from instruments_instruments_base where Name="%s"' % self.Name
            AD = self.selCmd(sql)
        except:
            return (False, AD, gain, rate, filter)

        sql = 'SELECT id from instruments_instruments_base where Name="%s"' % self.Name
        AD_id = self.selCmd(sql)
        if self.Gain == '':
            try:
                sql = 'SELECT Gain from instruments_digitizer_gain where Digitizer_id="%d"' % AD_id
                gain = self.selCmd(sql)
            except:
                return (False, AD, gain, rate, filter)
        else:
            try:
                sql = 'SELECT Gain from instruments_digitizer_gain where Digitizer_id="%d" and Gain="%s"' % (AD_id, self.Gain)
                gain = self.selCmd(sql)
            except:
                return (False, AD, gain, rate, filter)

        sql = 'SELECT id from instruments_digitizer_gain where Gain="%s"' % self.Gain
        Gain_id = self.selCmd(sql)
        if self.Rate == '':
            try:
                sql = 'SELECT Rate from instruments_digitizer_rate where DigitizerGain_id="%d"' % Gain_id
                rate = self.selCmd(sql)
            except:
                return (False, AD, gain, rate, filter)
        else:
            try:
                sql = 'SELECT Rate from instruments_digitizer_rate where DigitizerGain_id="%d" and Rate="%s"' % (Gain_id, self.Rate)
                rate = self.selCmd(sql)
            except:
                return (False, AD, gain, rate, filter)

        sql = 'SELECT id from instruments_digitizer_rate where Rate="%s"' % self.Rate
        Rate_id = self.selCmd(sql)
        if self.Filter == '':
            try:
                sql = 'SELECT id from instruments_digitizer_filter where DigitizerRate_id="%d"' % Rate_id
                filter = self.selCmd(sql)
            except:
                return (False, AD, gain, rate, filter)
        else:
            try:
                sql = 'SELECT id from instruments_digitizer_filter where DigitizerRate_id="%d" and Filter="%s"' % (Rate_id, self.Filter)
                filter = self.selCmd(sql)
            except:
                return (False, AD, gain, rate, filter)
        return (True, AD, gain, rate, filter)

    def selCmd(self, sql):
        cursor = self.c.execute(sql)
        for row in cursor:
            ret = row[0]
            return ret


class SensorInfo:
    def __init__(self, Name='TDV-60B', Freq='', Sensitivity=''):
        self.conn = sqlite3.connect(SQL_PATH)
        self.c = self.conn.cursor()
        self.Name = Name
        self.Freq = Freq
        self.Sensitivity = Sensitivity

    def getSensorInfo(self):
        sensor = None
        sensorinfo = None
        try:
            sql = 'SELECT Name from instruments_instruments_base where Name="%s"' % self.Name
            sensor = self.selCmd(sql)
        except:
            return(False, sensor, sensorinfo)
        sql = 'SELECT id from instruments_instruments_base where Name="%s"' % self.Name
        sensor_id = self.selCmd(sql)
        if self.Freq == '' and self.Sensitivity == '':
            try:
                sql = 'SELECT id from instruments_sensor_info where Sensor_id="%d"' % sensor_id
                sensorinfo = self.selCmd(sql)
            except:
                return (False, sensor, sensorinfo)
        else:
            try:
                sql = 'SELECT id from instruments_sensor_info where Sensor_id="%d" and ISensitivity="%s" and ' \
                      'IFreqInfo="%s"' % (sensor_id, self.Sensitivity, self.Freq)
                sensorinfo = self.selCmd(sql)
            except:
                return(False, sensor, sensorinfo)
        return(True, sensor, sensorinfo)

    def selCmd(self, sql):
        cursor = self.c.execute(sql)
        for row in cursor:
            ret = row[0]
            return ret

class ADSensor:
    def __init__(self, filter, sensorinfo1, sensorinfo2=None, sensorinfo3=None, sensorinfo4=None):
        self.conn = sqlite3.connect(SQL_PATH)
        self.c = self.conn.cursor()
        self.filter = filter
        self.sensorinfo1 = sensorinfo1
        if sensorinfo4 == None:
            self.sensorinfo4 = sensorinfo1
        if sensorinfo3 == None:
            self.sensorinfo3 = sensorinfo1
        if sensorinfo2 == None:
            self.sensorinfo2 = sensorinfo1

    def get_ADSensor(self):
        try:
            sql = 'SELECT id from instruments_ad_sensor where ADInfo_id="%d" and Sensorinfo1_id="%d" and ' \
                  'Sensorinfo2_id="%d" and ' \
                  'Sensorinfo3_id="%d" and ' \
                  'Sensorinfo4_id="%d"' % (self.filter, self.sensorinfo1,
                                           self.sensorinfo2, self.sensorinfo3, self.sensorinfo4)
            adsensor = self.selCmd(sql)
        except:
            sql = 'INSERT INTO instruments_ad_sensor (type, ADInfo, SensorInfo1,  SensorInfo2, SensorInfo3, SensorInfo4)' \
                  ' VALUES (1, %d, %d, %d, %d, %d)' % (self.filter, self.sensorinfo1, self.sensorinfo2, self.sensorinfo3, self.sensorinfo4)
            self.c.execute(sql)
            self.conn.commit()
            adsensor = self.get_ADSensor()
        return adsensor

    def selCmd(self, sql):
        cursor = self.c.execute(sql)
        for row in cursor:
            ret = row[0]
            return ret


class Sta_ADSensor:
    def __init__(self, sta, ADSensor):
        self.conn = sqlite3.connect(SQL_PATH)
        self.c = self.conn.cursor()
        self.sta = sta
        self.ADSensor = ADSensor

    def get_or_create_Sta_ADSensor(self):
        try:
            sql = 'SELECT id from ADSensor_id="%d" and Station_id="%d"' % (self.ADSensor, self.sta)
            sta_adsensor_id = self.selCmd(sql)
        except:
            sql = 'INSERT INTO networks_sta_adsensor (SeiralNo, ADSensor_id, Station_id) ' \
                  'VALUES (%d, %d, %d)' % (0, self.ADSensor, self.sta)
            self.c.execute(sql)
            self.conn.commit()
            sta_adsensor_id = self.get_or_create_Sta_ADSensor()
        return sta_adsensor_id

    def selCmd(self, sql):
        cursor = self.c.execute(sql)
        for row in cursor:
            ret = row[0]
            return ret


class Channel:
    def __init__(self, StaADSensor, LocCode, ChCode):
        self.conn = sqlite3.connect(SQL_PATH)
        self.c = self.conn.cursor()
        self.sta_adsensor = StaADSensor
        self.locCode = LocCode
        self.chCode = ChCode

    def get_or_create_CH(self):
        try:
            sql = 'SELECT id from networks_channel where ' \
                  'Sta_ADSensor_id="%d" and Code_Loc="%s" and Code_CH="%s"'\
                  % (self.sta_adsensor, self.locCode, self.chCode)
            ch_id = self.selCmd(sql)
        except:
            starttime = datetime.date.today()
            endtime = datetime.date(2099, 1, 1)
            sql = 'INSERT INTO networks_channel (CHNo, Code_Loc, Code_CH, Start_Time, End_Time, Sta_ADSensor_id) ' \
                  'VALUES (%d, %s, %s, %s, %s, %d)'\
                  % (0, self.locCode, self.chCode, starttime, endtime, self.sta_adsensor)
            self.c.execute(sql)
            self.conn.commit()
            ch_id = self.get_or_create_CH()
        return ch_id

    def selCmd(self, sql):
        cursor = self.c.execute(sql)
        for row in cursor:
            ret = row[0]
            return ret

def main():
    # table_list = ('networks_network', 'networks_station', 'networks_sta_adsensor', 'networks_channel', 'networks_day_data')
    # for table in table_list:
    #     DeleteSql().updateid(table)
    net = Network('TE', 'TE', 'D:/DJANGO', 'D/DJANGO', 3).get_or_create_Network()
    print(net, type(net))
    # sta = Station(net, 'T2867', 'T2867').get_or_create_Station()
    # (bRet, AD, gain, rate, filter) = DigitizerInfo('TDE-324', '10Vpp', '100Hz', 'Linear').getDigitizerInfo()
    # if not bRet:
    #     return
    # (bRet, sensor, sensorinfo) = SensorInfo('TMA-33').getSensorInfo()
    # if not bRet:
    #     return
    # adsensor = ADSensor(filter, sensorinfo).get_ADSensor()
    # sta_adsensor = Sta_ADSensor(sta, adsensor).get_or_create_Sta_ADSensor()
    # ch = Channel(sta_adsensor, '00', 'BHE').get_or_create_CH()
    # print(adsensor)



if __name__ == "__main__":
    SQL_PATH = 'D:/django/trunk/db.sqlite3'
    main()