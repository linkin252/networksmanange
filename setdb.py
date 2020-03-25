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

    def getId(self, field_des, field_res, value):
        netId = 0
        if type(value) == 'int':
            sql = "SELECT %s from networks_network where %s = %d" % (field_des, field_res, value)
        else:
            sql = "SELECT %s from networks_network where %s = %s" % (field_des, field_res, value)
        cursor = self.c.execute(sql)
        netId = cursor[0][0]
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

    def delAllField(self, table):
        sql = 'DELETE from %s' % table
        print(sql)
        self.c.execute(sql)
        self.conn.commit()


    def updateid(self, table):
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
    def __init__(self, Name, Gain, Rate, Filter):
        self.conn = sqlite3.connect(SQL_PATH)
        self.c = self.conn.cursor()


def main():
    net = Network().create('TE', 'TE', 'D:/DJANGO', 'D/DJANGO', 3)
    # sta = Station().create('T2867', 'T2867', 'TE')
    # table_list = ('networks_network', 'networks_station', 'networks_sta_adsensor', 'networks_channel', 'networks_day_data')
    # for table in table_list:
    #     DeleteSql().updateid(table)


if __name__ == "__main__":
    SQL_PATH = 'D:/django/trunk/db.sqlite3'
    main()