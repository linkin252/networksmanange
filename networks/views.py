from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

import os

# Create your views here.
from .models import Network,Station,Sta_ADSensor,Channel,Day_data
from instruments.models import National,Company,Sensor_base,Sensor_info,Zero,Pole,Digitizer_base,Digitizer_filter,AD_Sensor

class IndexView(generic.ListView):
    template_name = 'networks/index.html'
    context_object_name = 'Network_list'

    def get_queryset(self):
        return Network.objects.order_by('id')

class NetworkView(generic.ListView):
    template_name = 'networks/network.html'
    context_object_name = 'Network_list'

    def get_queryset(self):
        return Network.objects.order_by('id')

class StationView(generic.ListView):
    template_name = 'networks/station.html'
    context_object_name = 'Station_list'

    def get_queryset(self):
        return Station.objects.order_by('id')

class AdsensorView(generic.ListView):
    template_name = 'networks/adsensor.html'
    context_object_name = 'Sta_adsensor_list'

    def get_queryset(self):
        return Sta_ADSensor.objects.order_by('id')

class ChannelView(generic.ListView):
    template_name = 'networks/channel.html'
    context_object_name = 'Channel_list'

    def get_queryset(self):
        return Channel.objects.order_by('id')

class DayDataView(generic.ListView):
    template_name = 'networks/day_data.html'
    context_object_name = 'Day_data_list'

    def get_queryset(self):
        return Day_data.objects.order_by('id')

import datetime
def DayDataSelDate(request, pk):
    year = int(pk/10000)
    month = int((pk%10000)/100)
    day = pk%100
    print(year, month, day)
    SelDay = datetime.date(year, month, day)
    Day_data_list = Day_data.objects.filter(date=SelDay).order_by('id')
    context = {'Day_data_list': Day_data_list,'SelDay':SelDay}
    return render(request, 'networks/day_data.html', context)

def DayDataSelChannel(request, pk):
    channel_sel = get_object_or_404(Channel, pk=pk)
    Day_data_list = Day_data.objects.filter(ch=channel_sel).order_by('id')
    context = {'Day_data_list': Day_data_list,'channel_sel':channel_sel}
    return render(request, 'networks/day_data.html', context)

def DayDataSelStation(request, pk):
    station_sel = get_object_or_404(Station, pk=pk)
    Day_data_list = []
    for dat_data in Day_data.objects.order_by('id'):
        if (dat_data.ch.Sta_ADSensor.Station==station_sel):
            Day_data_list.append(dat_data)
    context = {'Day_data_list': Day_data_list,'station_sel':station_sel}
    return render(request, 'networks/day_data.html', context)

def DayDataSelNetwork(request, pk):
    network_sel = get_object_or_404(Network, pk=pk)
    Day_data_list = []
    for dat_data in Day_data.objects.order_by('id'):
        if (dat_data.ch.Sta_ADSensor.Station.Network==network_sel):
            Day_data_list.append(dat_data)
    context = {'Day_data_list': Day_data_list,'network_sel':network_sel}
    return render(request, 'networks/day_data.html', context)

#from net2db import getStaticStr

def DayDataDetails(request, pk):
    day_data_sel = get_object_or_404(Day_data, pk=pk)
    sYear = day_data_sel.date.strftime('%Y')
    sTDay = day_data_sel.date.strftime('%j')
    sDenDir = 'networks' + '\\' + day_data_sel.ch.Sta_ADSensor.Station.Network.Code \
              + '\\' + day_data_sel.ch.Sta_ADSensor.Station.Code \
              + '\\' + sYear + '\\'+ sTDay \
              + '\\' + day_data_sel.ch.Sta_ADSensor.Station.Network.Code + '.' \
              + day_data_sel.ch.Sta_ADSensor.Station.Code + '.' + day_data_sel.ch.Code_Loc + '.' + day_data_sel.ch.Code_CH + '.' \
              + sYear + '.' + sTDay
    context = {'day_data_sel': day_data_sel,"sDenDir":sDenDir}
    return render(request, 'networks/day_data_detail.html', context)

def ChannelDetails(request, pk):
    channel = get_object_or_404(Channel, pk=pk)

    digitizer_filter = channel.Sta_ADSensor.ADSensor.ADInfo
    digitizer_sel = digitizer_filter.DigitizerRate.DigitizerGain.Digitizer

    sensorInfo = channel.Sta_ADSensor.ADSensor.SensorInfo1
    sensor = sensorInfo.Sensor
    zero_list = Zero.objects.filter(sensor_info=sensorInfo).order_by('id')
    pole_list = Pole.objects.filter(sensor_info=sensorInfo).order_by('id')


    context = {'channel': channel,'digitizer_filter':digitizer_filter,'digitizer_sel':digitizer_sel,
               'sensor':sensor,'sensorInfo':sensorInfo,'zero_list':zero_list,'pole_list':pole_list}

    return render(request, 'networks/channel_detail.html', context)
