# coding=utf-8

import sqlite3

from trunk import calibrate

class Network:
    def __init__(self):
        try:
            self.conn = sqlite3.connect(SQL_PATH)
        except Exception as ex:
            print('sql not connect')
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

    def getId(self, field, value):
        netId = 0
        sql = "SELECT id, %s from networks_network" % field
        cursor = self.c.execute(sql)
        for row in cursor:
            if row[1] == field:
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
        netId = Network().getId('Name',net)
        sql = "INSERT INTO networks_station (Code, Name, Network_id, fJin, fWei, fHeigth, fDepth)" \
              "VALUES ('%s', '%s', '%d', '%d', '%d', '%d', '%d')" % (StaCode, StaName, netId, fJin, fWei, fHeigth, fDepth)
        self.c.execute(sql)
        self.conn.commit()
        sta = self.get('Code', StaCode, 'Network_id', netId)
        return sta


class DigitizerInfo:
    def __init__(self, Name, Gain, Rate, Filter):
        self.conn = sqlite3.connect(SQL_PATH)
        self.c = self.conn.cursor()


def main():
    # net = Network().create('TE', 'TE', 'D:/DJANGO', 'D/DJANGO', 3)
    sta = Station().create('T2867', 'T2867', 'TE')


if __name__ == "__main__":
    SQL_PATH = 'D:/django/trunk/db.sqlite3'
    main()