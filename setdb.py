# coding=utf-8

import sqlite3

from trunk import calibrate

class Network:
    def __init__(self):
        try:
            self.conn = sqlite3.connect(SQL_PATH)
        except Exception as ex:
            print(ex)
        else:
            self.c = self.conn.cursor()

    def get(self, field, value):
        val = ''
        sql = "SELECT %s from networks_network" % field
        cursor = self.c.execute(sql)
        for row in cursor:
            if row[0] == value:
                val = row[0]
                break
        self.conn.close()
        return val

    def getId(self, field_res, value):
        netId = 0
        sql = 'SELECT id from networks_network where %s="%s"' % (field_res, value)
        cursor = self.c.execute(sql)
        for row in cursor:
            netId = row[0]
            break
        self.conn.close()
        return netId

    def create(self, NetCode, NetName, fSrcDir, sDenDir, nNetMode):
        sql = "INSERT INTO networks_network (Code, Name, IDataDir, IOutDir, INetMode) " \
              "VALUES ('%s', '%s', '%s', '%s', %d)" % (NetCode, NetName, fSrcDir, sDenDir, nNetMode)
        self.c.execute(sql)
        self.conn.commit()
        net = self.get('Name', NetName)
        return net


class Station:
    def __init__(self):
        self.conn = sqlite3.connect(SQL_PATH)
        self.c = self.conn.cursor()

    def get(self, field1, value1, field2, value2):
        val = ''
        sql = "SELECT %s, %s from networks_station" % (field1, field2)
        cursor = self.c.execute(sql)
        for row in cursor:
            if row[0] == value1 and row[1] == value2:
                val = row[0]
        self.conn.close()
        return val

    def create(self, StaCode, StaName, net, fJin=111.11, fWei=22.22, fHeigth=100, fDepth=100):
        netId = Network().getId('Name', net)
        sql = "INSERT INTO networks_station (Code, Name, Network_id, fJin, fWei, fHeigth, fDepth)" \
              "VALUES ('%s', '%s', '%d', '%d', '%d', '%d', '%d')" % (StaCode, StaName, netId, fJin, fWei, fHeigth, fDepth)
        self.c.execute(sql)
        self.conn.commit()
        sta = self.get('Code', StaCode, 'Network_id', netId)
        return sta


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


class SelectAll:
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
                sql = 'SELECT Filter from instruments_digitizer_filter where DigitizerRate_id="%d"' % Rate_id
                filter = self.selCmd(sql)
            except:
                return (False, AD, gain, rate, filter)
        else:
            try:
                sql = 'SELECT Filter from instruments_digitizer_filter where DigitizerRate_id="%d" and Filter="%s"' % (Rate_id, self.Filter)
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


def main():
    # net = Network().create('TE', 'TE', 'D:/DJANGO', 'D/DJANGO', 3)
    # sta = Station().create('T2867', 'T2867', 'TE')
    (bRet, AD, gain, rate, filter) = DigitizerInfo('TDE-324', '10Vpp', '100Hz', 'Linear').getDigitizerInfo()
    print(bRet, AD, gain, rate, filter)
    # table_list = ('networks_network', 'networks_station', 'networks_sta_adsensor', 'networks_channel', 'networks_day_data')
    # for table in table_list:
    #     DeleteSql().updateid(table)


if __name__ == "__main__":
    SQL_PATH = 'D:/django/trunk/db.sqlite3'
    main()