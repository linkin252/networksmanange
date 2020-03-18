# Create your views here.
# encoding = utf-8

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import National,Company,Sensor_base,Sensor_info,Zero,Pole,Digitizer_base,Digitizer_filter,AD_Sensor

class IndexView(generic.ListView):
    template_name = 'instruments/index.html'
    context_object_name = 'National_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return National.objects.order_by('id')

class NationalView(generic.ListView):
    template_name = 'instruments/national.html'
    context_object_name = 'National_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return National.objects.order_by('id')

class CompanyView(generic.ListView):
    template_name = 'instruments/company.html'
    context_object_name = 'Company_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Company.objects.order_by('id')

# 以下类或方法均调用 instruments.html 页面
class SensorView(generic.ListView):
    template_name = 'instruments/instruments.html'
    context_object_name = 'Sensor_list'

    def get_queryset(self):
        return Sensor_base.objects.order_by('id')

def SensorSelCompany(request, pk):
    company_sel = get_object_or_404(Company, pk=pk)
    Sensor_list = Sensor_base.objects.filter(ICompany=company_sel).order_by('id')
    context = {'Sensor_list': Sensor_list,'company_sel':company_sel}
    return render(request, 'instruments/instruments.html', context)

def SensorSelNational(request, pk):
    national_sel = get_object_or_404(National, pk=pk)
    Company_list = Company.objects.filter(CNational=national_sel).order_by('id')
    Sensor_list = []
    for company in Company_list:
        Sensor_part = Sensor_base.objects.filter(ICompany=company).order_by('id')
        for sensor in Sensor_part:
            Sensor_list.append(sensor)
    context = {'Sensor_list': Sensor_list,'national_sel':national_sel}
    return render(request, 'instruments/instruments.html', context)

class DigitizerView(generic.ListView):
    template_name = 'instruments/instruments.html'
    context_object_name = 'Digitizer_list'

    def get_queryset(self):
        return Digitizer_base.objects.order_by('id')

def DigitizerSelCompany(request, pk):
    company_sel = get_object_or_404(Company, pk=pk)
    Digitizer_list = Digitizer_base.objects.filter(ICompany=company_sel).order_by('id')
    context = {'Digitizer_list': Digitizer_list,'company_sel':company_sel}
    return render(request, 'instruments/instruments.html', context)

def DigitizerSelNational(request, pk):
    national_sel = get_object_or_404(National, pk=pk)
    Company_list = Company.objects.filter(CNational=national_sel).order_by('id')
    Digitizer_list = []
    for company in Company_list:
        Digitizer_part = Digitizer_base.objects.filter(ICompany=company).order_by('id')
        for digitizer in Digitizer_part:
            Digitizer_list.append(digitizer)
    context = {'Digitizer_list': Digitizer_list,'national_sel':national_sel}
    return render(request, 'instruments/instruments.html', context)

def InstrumentAll(request):
    Digitizer_list = Digitizer_base.objects.order_by('id')
    Sensor_list = Sensor_base.objects.order_by('id')
    context = {'Digitizer_list':Digitizer_list,"Sensor_list":Sensor_list}
    return render(request, 'instruments/instruments.html', context)

def InstrumentSelCompany(request, pk):
    company_sel = get_object_or_404(Company, pk=pk)
    Sensor_list = Sensor_base.objects.filter(ICompany=company_sel).order_by('id')
    Digitizer_list = Digitizer_base.objects.filter(ICompany=company_sel).order_by('id')
    context = {'Sensor_list': Sensor_list,'Digitizer_list': Digitizer_list,'company_sel':company_sel}
    return render(request, 'instruments/instruments.html', context)

def InstrumentSelNational(request, pk):
    national_sel = get_object_or_404(National, pk=pk)
    Company_list = Company.objects.filter(CNational=national_sel).order_by('id')
    Sensor_list = []
    Digitizer_list = []
    for company in Company_list:
        Digitizer_part = Digitizer_base.objects.filter(ICompany=company).order_by('id')
        for digitizer in Digitizer_part:
            Digitizer_list.append(digitizer)
        Sensor_part = Sensor_base.objects.filter(ICompany=company).order_by('id')
        for sensor in Sensor_part:
            Sensor_list.append(sensor)

    context = {'Sensor_list': Sensor_list,'Digitizer_list': Digitizer_list,'national_sel':national_sel}
    return render(request, 'instruments/instruments.html', context)

class SensorInfoView(generic.ListView):
    template_name = 'instruments/sensor_info.html'
    context_object_name = 'Sensor_info_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Sensor_info.objects.order_by('id')

def index(request):
    return render(request, 'instruments/index.html')

def CompanySelNational(request, pk):
    national_sel = get_object_or_404(National, pk=pk)
    Company_list = Company.objects.filter(CNational=national_sel).order_by('id')
    context = {'Company_list': Company_list,'national_sel':national_sel}
    return render(request, 'instruments/company.html', context)

def SensorInfoAll(request):
    national_list = National.objects.order_by('id')
    context = {'national_list':national_list}
    return render(request, 'instruments/sensor_info.html', context)

def SensorInfoSelNational(request, pk):
    national_sel = get_object_or_404(National, pk=pk)
    context = {'national_sel':national_sel}
    return render(request, 'instruments/sensor_info.html', context)

def SensorInfoSelCompany(request, pk):
    company_sel = get_object_or_404(Company, pk=pk)
    context = {'company_sel':company_sel}
    return render(request, 'instruments/sensor_info.html', context)

def SensorInfoDetails(request, pk):
    sensorInfo = get_object_or_404(Sensor_info, pk=pk)
    sensor = sensorInfo.Sensor
    zero_list = Zero.objects.filter(sensor_info=sensorInfo).order_by('id')
    pole_list = Pole.objects.filter(sensor_info=sensorInfo).order_by('id')
    context = {'sensor':sensor,'sensorInfo':sensorInfo,'zero_list':zero_list,'pole_list':pole_list}
    return render(request, 'instruments/sensor_info_detail.html', context)

def SensorDetails(request, pk):
    sensor = get_object_or_404(Sensor_base, pk=pk)
    sensorInfo_list = Sensor_info.objects.filter(Sensor=sensor).order_by('id')
    context = {'sensor':sensor,  'sensorInfo_list':sensorInfo_list}
    return render(request, 'instruments/sensor_detail.html', context)

def DigitizerInfoView(request):
    digitizer_list = Digitizer_base.objects.order_by('id')
    context = {'digitizer_list':digitizer_list}
    return render(request, 'instruments/digitizer_info.html', context)

def DigitizerInfoSelNational(request, pk):
    national_sel = get_object_or_404(National, pk=pk)
    #digitizer_list = Digitizer_base.objects.filter(ICompany.National_id=national_sel).order_by('id')
    print(national_sel)
    digitizer_list=[]
    for digitizer in  Digitizer_base.objects.order_by('id'):
        print(digitizer.Name,digitizer.ICompany.CNational_id)
        if (digitizer.ICompany.CNational==national_sel):
            digitizer_list.append(digitizer)
    context = {'digitizer_list':digitizer_list}
    return render(request, 'instruments/digitizer_info.html', context)

def DigitizerInfoSelCompany(request, pk):
    company_sel = get_object_or_404(Company, pk=pk)
    digitizer_list = Digitizer_base.objects.filter(ICompany=company_sel).order_by('id')
    context = {'digitizer_list':digitizer_list}
    return render(request, 'instruments/digitizer_info.html', context)

def DigitizerInfoSelDigitizer(request, pk):
    Digitizer_sel = get_object_or_404(Digitizer_base, pk=pk)
    digitizer_list = []
    digitizer_list.append(Digitizer_sel)
    context = {'digitizer_list':digitizer_list}
    return render(request, 'instruments/digitizer_info.html', context)

def DigitizerDetails(request, pk):
    digitizer_sel = get_object_or_404(Digitizer_base, pk=pk)
    context = {'digitizer_sel':digitizer_sel}
    return render(request, 'instruments/digitizer_detail.html', context)

def DigitizerInfoDetails(request, pk):
    digitizer_filter = get_object_or_404(Digitizer_filter, pk=pk)
    digitizer_sel = digitizer_filter.DigitizerRate.DigitizerGain.Digitizer
    context = {'digitizer_filter':digitizer_filter,'digitizer_sel':digitizer_sel}
    return render(request, 'instruments/digitizer_info_detail.html', context)


class ADSensorView(generic.ListView):
    template_name = 'instruments/ad_sensor.html'
    context_object_name = 'ad_sensor_list'

    def get_queryset(self):
        return AD_Sensor.objects.order_by('id')
