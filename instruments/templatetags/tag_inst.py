from django import template
from django.utils.safestring import mark_safe
from instruments.models import National, Company, Sensor_base, Sensor_info, Digitizer_base,Zero,Pole,\
    Digitizer_gain, Digitizer_rate, Digitizer_filter,AD_Sensor

register = template.Library()  # register的名字是固定的,不可改变

@register.filter
def getZero_list(sensorInfo):
    zero_list = Zero.objects.filter(sensor_info=sensorInfo).order_by('id')
    return zero_list

@register.filter
def getPole_list(sensorInfo):
    pole_list = Pole.objects.filter(sensor_info=sensorInfo).order_by('id')
    return pole_list

@register.filter
def getSensorInfo_list(sensor):
    sensor_info_list = Sensor_info.objects.filter(Sensor=sensor).order_by('id')
    return sensor_info_list

@register.filter
def getSensorInfo_Ct(sensor):
    sensor_info_list = Sensor_info.objects.filter(Sensor=sensor).order_by('id')
    return (len(sensor_info_list))

@register.filter
def getSensor_list(company):
    sensor_list = Sensor_base.objects.filter(ICompany=company).order_by('id')
    return sensor_list

@register.filter
def getSensor_Ct(company):
    sensor_list = Sensor_base.objects.filter(ICompany=company).order_by('id')
    return (len(sensor_list))

@register.filter
def getCompany_list(national):
    company_list = Company.objects.filter(CNational=national).order_by('id')
    return company_list

@register.filter
def getCompany_Ct(national):
    company_list = Company.objects.filter(CNational=national).order_by('id')
    return (len(company_list))

@register.filter
def getGain_list(digitizer):
    gain_list = Digitizer_gain.objects.filter(Digitizer=digitizer)
    return gain_list

@register.filter
def getRate_list(gain):
    rate_list = Digitizer_rate.objects.filter(DigitizerGain=gain)
    return rate_list

@register.filter
def getFilter_list(rate):
    filter_list = Digitizer_filter.objects.filter(DigitizerRate=rate)
    return filter_list

@register.filter
def getSystemSensitivityString(ADSensor):
    fAD = ADSensor.ADInfo.sensitivity
    fSensor = ADSensor.SensorInfo1.IGain
    fRet = fSensor * fAD
    if (ADSensor.SensorInfo1.Sensor.IMainType < 2000):
        sRet = "%.1f Ct/(m/s)" % fRet
    elif (2000 <= ADSensor.SensorInfo1.Sensor.IMainType and ADSensor.SensorInfo1.Sensor.IMainType < 3000):  # 加速度模式)
        sRet = "%.1f Ct/(m/s**2)" % fRet
    return sRet
