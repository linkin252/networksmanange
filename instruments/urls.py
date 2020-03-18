#instruments/urls.py

from django.urls import path
from . import views

app_name = 'instruments'
urlpatterns = [
    # index.html
    path('',           views.IndexView.as_view(),     name='index'),       # ex: /instruments/
    # national.html
    path('national/',  views.NationalView.as_view(),  name='national'),    # ex: /instruments/national
    # company.html
    path('company/',   views.CompanyView.as_view(),   name='company'),     # ex: /instruments/company
    path('company_sel_national/<int:pk>',     views.CompanySelNational,       name='company_sel_national'),
    # instruments.html  digitizer 和 sensor 共用
    path('sensor/',                           views.SensorView.as_view(),     name='sensor'),
    path('sensor_sel_national/<int:pk>',      views.SensorSelNational,        name='sensor_sel_national'),
    path('sensor_sel_company/<int:pk>',       views.SensorSelCompany,         name='sensor_sel_company'),
    path('digitizer/',                        views.DigitizerView.as_view(),  name='digitizer'),
    path('digitizer_sel_national/<int:pk>',   views.DigitizerSelNational,     name='digitizer_sel_national'),
    path('digitizer_sel_company/<int:pk>',    views.DigitizerSelCompany,      name='digitizer_sel_company'),
    path('instrument/',                       views.InstrumentAll,            name='instrument'),
    path('instrument_sel_national/<int:pk>',  views.InstrumentSelNational,    name='instrument_sel_national'),
    path('instrument_sel_company/<int:pk>',   views.InstrumentSelCompany,     name='instrument_sel_company'),
    # sensor_info.html
    path('sensor_info/',                      views.SensorInfoAll,            name='sensor_info'),
    path('sensor_info_sel_national/<int:pk>', views.SensorInfoSelNational,    name='sensor_info_sel_national'),
    path('sensor_info_sel_company/<int:pk>',  views.SensorInfoSelCompany,     name='sensor_info_sel_company'),
    # sensor_detail.html
    path('sensor/<int:pk>',                   views.SensorDetails,            name='sensor_detail'),
    # sensor_info_detail.html
    path('sensor_info/<int:pk>',              views.SensorInfoDetails,        name='sensor_info_detail'),
    # digitizer_info.html
    path('digitizer_info/',                   views.DigitizerInfoView,        name='digitizer_info'),
    path('digitizer_info_sel_national/<int:pk>',views.DigitizerInfoSelNational, name='digitizer_info_sel_national'),
    path('digitizer_info_sel_company/<int:pk>', views.DigitizerInfoSelCompany,  name='digitizer_info_sel_company'),
    path('digitizer_info_sel_digitizer/<int:pk>',views.DigitizerInfoSelDigitizer, name='digitizer_info_sel_digitizer'),
    # digitizer_detail.html
    path('digitizer/<int:pk>',                views.DigitizerDetails,         name='digitizer_detail'),
    # digitizer_info_detail.html
    path('digitizer_info/<int:pk>',           views.DigitizerInfoDetails,     name='digitizer_info_detail'),
    # ad_sensor.html
    path('AD_Sensor/',                        views.ADSensorView.as_view(),   name='ad_sensor'),
]


