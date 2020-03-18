#networks/urls.py

from django.urls import path
from . import views

app_name = 'networks'
urlpatterns = [
    # index.html
    path('',          views.IndexView.as_view(),       name='Index'),         # ex: /networks/
    # network.html
    path('network/',   views.NetworkView.as_view(),     name='network'),       # ex: /networks/network
    # station.html
    path('station/',   views.StationView.as_view(),     name='station'),       # ex: /networks/station
    # adsensor.html
    path('adsensor/',  views.AdsensorView.as_view(),    name='adsensor'),      # ex: /networks/adsensor
    # channel.html
    path('channel/',   views.ChannelView.as_view(),     name='channel'),       # ex: /networks/channel
    path('channel_detail/<int:pk>',       views.ChannelDetails,    name='channel_detail'),
    # data.html
    path('day_data/',      views.DayDataView.as_view(),     name='day_data'),                     # ex: /networks/data
    path('day_data_sel_date/<int:pk>',    views.DayDataSelDate,    name='day_data_sel_date'),     # ex: /networks/data
    path('day_data_sel_network/<int:pk>', views.DayDataSelNetwork, name='day_data_sel_network'),  # ex: /networks/data
    path('day_data_sel_station/<int:pk>', views.DayDataSelStation, name='day_data_sel_station'),  # ex: /networks/data
    path('day_data_sel_channel/<int:pk>', views.DayDataSelChannel, name='day_data_sel_channel'),  # ex: /networks/data
    path('day_data_detail/<int:pk>',      views.DayDataDetails,    name='day_data_detail'),
]


