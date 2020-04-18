# coding=utf-8

import os, sys
import django
import platform

if platform.platform() == 'Windows':
    sys.path.append('D:/django/trunk')
else:
    sys.path.append('/home/usb/django/taide')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taide.settings")  # NoQA
django.setup()  # NoQA

import net2db
from networks.models import Network, Station, Sta_ADSensor, Channel, Day_data


def delDayDataByNet(network):
    num = 0
    for day_data in Day_data.objects.order_by('id'):
        if day_data.ch.Sta_ADSensor.Station.Network.__str__() == network:
            Day_data.objects.filter(id=day_data.id).delete()
            num += 1
    print('删除了%s台网中的%d个日数据' % (network, num))


def delChnByNet(network):
    num = 0
    for channel in Channel.objects.order_by('id'):
        if channel.Sta_ADSensor.Station.Network.__str__() == network:
            Channel.objects.filter(id=channel.id).delete()
            num += 1
    print('删除了%s台网中的%d个分向' % (network, num))


def delStaAdSenByNet(network):
    num = 0
    for sta_adsensor in Sta_ADSensor.objects.order_by('id'):
        if sta_adsensor.Station.Network == network:
            Sta_ADSensor.objects.filter(id=sta_adsensor.id).delete()
            num += 1
    print('删除了%s台网中的%d个台站仪器组' % (network, num))


def delStaByNet(network):
    num = 0
    for sta in Station.objects.order_by('id'):
        if sta.Network.__str__() == network:
            Station.objects.filter(id=sta.id).delete()
            num += 1
    print('删除了%s台网中的%d个台站' % (network, num))


def delNetByNet(network):
    num = 0
    for net in Network.objects.order_by('id'):
        if net.__str__() == network:
            Network.objects.filter(id=net.id).delete()
            num += 1
    print('删除了%s台网中的%d个台网' % (network, num))


def delByNet(network):
    delDayDataByNet(network)
    delChnByNet(network)
    delStaAdSenByNet(network)
    delStaByNet(network)
    delNetByNet(network)


def delChnByIsExits():
    num = 0
    chn_list = []
    for chn in Channel.objects.order_by('id'):
        chn_list.append(chn.id)
    for day_data in Day_data.objects.order_by('id'):
        if day_data.ch_id not in chn_list:
            Day_data.objects.filter(id=day_data.id).delete()
            num += 1
    print('删除了%d个通道分向' % num)


def delStaBySta(station):
    num = 0
    for sta in Station.objects.order_by('id'):
        if sta.Code == station:
            Station.objects.filter(id=sta.id).delete()
            num += 1
    print('删除了%s台站中的%d个台站' % (station, num))


def delStaAdSenBySta(station):
    num = 0
    for sta_adsensor in Sta_ADSensor.objects.order_by('id'):
        if sta_adsensor.Station.Code == station:
            Sta_ADSensor.objects.filter(id=sta_adsensor.id).delete()
            num += 1
    print('删除了%s台站中的%d个台站仪器组' % (station, num))


def delChnBySta(station):
    num = 0
    for chn in Channel.objects.order_by('id'):
        if chn.Sta_ADSensor.Station.Code == station:
            Channel.objects.filter(id=chn.id).delete()
            num += 1
    print('删除了%s台站中的%d个通道分向' % (station,num))


def delDayDataBySta(station):
    num = 0
    for day_data in Day_data.objects.order_by('id'):
        if day_data.ch.Sta_ADSensor.Station.Code == station:
            Day_data.objects.filter(id=day_data.id).delete()
            num += 1
    print('删除了%s台站中的%d个日数据' % (station,num))


def delBySta(station):
    delDayDataBySta(station)
    delChnBySta(station)
    delStaAdSenBySta(station)
    delStaBySta(station)


def getDayData():
    sensorinfo = 'TDA-33M'
    net2db.Net2dbDemo(sensorinfo)


def main():
    getDayData()
    # delByNet('TE')
    # delChnByIsExits()
    # delBySta('T2867')


if __name__ == "__main__":
    main()
