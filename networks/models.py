from django.db import models

from instruments.models import AD_Sensor
# Create your models here.

# 台网名
class Network(models.Model):
    Net_type = (
        (1, 'Adapt '),
        (2, 'SeisComp'),
        (3, 'TDE324')
    )
    Code = models.CharField(verbose_name="台网代码",max_length=2)
    Name = models.CharField(verbose_name="台网名称",max_length=80)
    IDataDir = models.CharField(verbose_name='数据目录', default='', blank=True, max_length=200)  # 设备参数文件
    IOutDir = models.CharField(verbose_name= '产出目录', default='', blank=True, max_length=200)   # 设备参数文件
    INetMode = models.IntegerField(verbose_name="台网模式",  choices=Net_type,    default=1)

    def __str__(self):
        return self.Name

class Station(models.Model):
    Code = models.CharField(verbose_name="台站代码",max_length=5)   #代码应具有唯一性
    Name = models.CharField(verbose_name="台站名称",max_length=80)
    fJin = models.FloatField(verbose_name="经度",default=111.11)  #度
    fWei = models.FloatField(verbose_name="经度",default=22.22)   #度
    fHeigth = models.FloatField(verbose_name="高程",default=100)  #米
    fDepth = models.FloatField(verbose_name="安装深度",default=100)  #米
    Network =  models.ForeignKey(Network,verbose_name='台网名称',on_delete=models.CASCADE)       # 生产厂商

    def __str__(self):
        return self.Code

class Sta_ADSensor(models.Model):  # 台站安装的数采，1 对 多 关系， 即1个台站可能安装多个数采
    SeiralNo = models.IntegerField( verbose_name='设备顺序号',  default=0)                       # 用于 设定 Location 00/01/02/03
    Station = models.ForeignKey(Station,verbose_name="台站名称",on_delete=models.CASCADE)        # 台站
    ADSensor = models.ForeignKey(AD_Sensor,verbose_name="数采",on_delete=models.CASCADE) # 数采

    def __str__(self):
        return self.Station.Network.Code \
                + '.' + self.Station.Code \
                + '_' + self.ADSensor.ADInfo.DigitizerRate.DigitizerGain.Digitizer.Name \
                + '_' + self.ADSensor.ADInfo.DigitizerRate.DigitizerGain.Gain \
                + '_' + self.ADSensor.ADInfo.DigitizerRate.Rate \
                + '_' + self.ADSensor.ADInfo.Filter \
                + '_' + self.ADSensor.SensorInfo1.Sensor.Name \
                + '_' + self.ADSensor.SensorInfo1.IFreqInfo + '_' + self.ADSensor.SensorInfo1.ISensitivityInfo

class Channel(models.Model):            #  根据 Sta_Digitizer， Digitizer_Sensor 确定 Channel
    CHNo = models.IntegerField( verbose_name='通道顺序号',  default=0)
    Sta_ADSensor = models.ForeignKey(Sta_ADSensor,verbose_name="台站-数采-传感器",on_delete=models.CASCADE,default=None) # 台站-数采-传感器
    Code_Loc = models.CharField(verbose_name="位置代码",max_length=2)
    Code_CH = models.CharField(verbose_name="通道代码",max_length=3)
    Start_Time = models.DateField(verbose_name="开始运转时间",blank=True)     # 开始运转时间，包括设置好参数的时间
    End_Time = models.DateField(verbose_name="停止运转时间",blank=True)

    def __str__(self):
        return self.Sta_ADSensor.Station.Network.Code \
            + '.' + self.Sta_ADSensor.Station.Code \
            + '.' + self.Code_Loc + '.' + self.Code_CH \
            + '_' + self.Sta_ADSensor.ADSensor.ADInfo.DigitizerRate.DigitizerGain.Digitizer.Name \
            + '_' + self.Sta_ADSensor.ADSensor.ADInfo.DigitizerRate.DigitizerGain.Gain \
            + '_' + self.Sta_ADSensor.ADSensor.ADInfo.DigitizerRate.Rate \
            + '_' + self.Sta_ADSensor.ADSensor.ADInfo.Filter \
            + '_' + self.Sta_ADSensor.ADSensor.SensorInfo1.Sensor.Name \
            + '_' + self.Sta_ADSensor.ADSensor.SensorInfo1.IFreqInfo  \
            + '_' + self.Sta_ADSensor.ADSensor.SensorInfo1.ISensitivityInfo

class Day_data(models.Model):            #  日数据，目前包括 运行率数据
    ch = models.ForeignKey(Channel,verbose_name='日数据',on_delete=models.CASCADE)
    date = models.DateField(verbose_name="数据时间")
    runrate = models.FloatField(verbose_name="运行率",default=1.0)
