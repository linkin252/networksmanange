# Create your models here.
# encoding = utf-8
from django.db import models

"""
Filter_type = (
        1,      #  'FIR & IIR',
        2,      #  'FIR only',
        3,      #  'IIR only',
    )
DB_type = (
    1,  # 已有型号
    2,  # 正在定型
    3,  # 通过定型
)
Signal_type = (
    0,  # 00***        暂时未知主类型的仪器
    1000,  # 01*** - 99***  传感器类型，如：
    #         1000  ---- 地震计，
    #         2000  ---- 加速度计，
    #         ******
    #   1** - 9**  -- 安装类型，
    #              100  --  地表安装
    #              200  --  结构建筑物安装，
    #              300  --  浅井型
    #              400  --  井下型
    #              500  --  深井型
    # 1000 -- 标准 三分向速度型地震计，101-199 为子类型，
    #          1010 -- 无源地震计或检波器
    #          1011 -- 无源检波器  2Hz 以上，不含2Hz
    #          1012 -- 无源短周期地震计    10s - 2Hz
    #          1013 -- 无源宽频带地震计    10s以上
    #          1014 -- 无源甚宽带......    2Hz 以上
    #          1020 -- 线圈换能地震计
    #          1030 -- XYZ电容换能地震计，
    #          1040 -- UVW电容换能地震计，
    #          1050 -- 其他类型加速度计，如化学摆
    2000,  # 2000 -- 标准 三分向加速度型地震计，201-299 为子类型，
    # 例如：
    #          2010 -- 无源加速度计
    #          2020 -- 机械式力平衡式加速度计
    #          2030 -- MEMS力平衡式加速度计
    #          2040 -- 强震烈度仪
    #          2050 -- 石英加速度计（西安、日本系列）
    #          2060 -- 其他类型加速度计
    3000  # 3000 -- 位移传感器
    # 例如：
    #          3010 -- 无源加速度计
    #          2020 -- 机械式力平衡式加速度计
    #          2030 -- MEMS力平衡式加速度计
    #          2040 -- 强震烈度仪
    #          2050 -- 石英加速度计（西安、日本系列）
    #          2060 -- 其他类型加速度计
)
"""


# 国家名
class National(models.Model):
    Name = models.CharField(verbose_name="英文名", max_length=80)
    ChnName = models.CharField(verbose_name="中文名", max_length=80, null=True, blank=True)
    Icon32 = models.URLField(verbose_name="32*32图片链接", null=True, blank=True)
    Icon64 = models.URLField(verbose_name="64*64图片链接", null=True, blank=True)
    Icon128 = models.URLField(verbose_name="128*128图片链接", null=True, blank=True)

    def __str__(self):
        return self.Name


# 仪器生产厂商
class Company(models.Model):
    Name = models.CharField(verbose_name='英文名', max_length=80)
    ChnName = models.CharField(verbose_name='中文名', max_length=80, null=True, blank=True)
    CNational = models.ForeignKey(National, verbose_name='国别', on_delete=models.CASCADE)
    CIcon = models.URLField(verbose_name='图标', null=True, blank=True)
    CWeb = models.URLField(verbose_name='网站', null=True, blank=True)
    # CBitmap = models.URLField(verbose_name='图片',null=True,blank=True)
    CInfo = models.URLField(verbose_name='信息', null=True, blank=True)

    def __str__(self):
        return self.Name


# 仪器类型
class Instruments_base(models.Model):
    DB_type = (
        (1, ''),  # 已有型号
        (2, '正在定型'),  # 正在定型
        (3, '通过定型')  # 通过定型
    )
    Signal_type = (
        (0, ''),  # 00***        暂时未知主类型的仪器
        (1000, '地震计'),  # 01*** - 99***  传感器类型，如：
        (1001, '检波器'),  # 2Hz,    G
        (1002, '短周期地震计'),  # <20s,   S
        (1003, '宽频带地震计'),  # <120s,  B
        (1004, '甚宽带地震计'),  # <360s   B
        (1005, '超宽带地震计'),  # 360s 以上 B
        # E Extremely Short Period ≥ 80 to < 250 < 10 sec
        # S Short Period ≥ 10 to < 80 < 10 sec
        # H High Broad Band ≥ 80 to < 250 ≥ 10 sec
        # B Broad Band ≥ 10 to < 80 ≥ 10 sec
        # M Mid Period > 1 to < 10
        # L Long Period ≈ 1
        # V Very Long Period ≈ 0.1
        # U Ultra Long Period ≈ 0.01
        #         1000  ---- 地震计，
        #         2000  ---- 加速度计，
        #         ******
        #   1** - 9**  -- 安装类型，
        #              100  --  地表安装
        #              200  --  结构建筑物安装，
        #              300  --  浅井型
        #              400  --  井下型
        #              500  --  深井型
        # 1000 -- 标准 三分向速度型地震计，101-199 为子类型，
        #          1010 -- 无源地震计或检波器
        #          1011 -- 无源检波器  2Hz 以上，不含2Hz
        #          1012 -- 无源短周期地震计    20s - 2Hz
        #          1013 -- 无源宽频带地震计    20s-120s以上
        #          1014 -- 无源甚宽带......    120s 以上
        #          1014 -- 无源甚宽带......    120s 以上

        #          1020 -- 线圈换能地震计
        #          1030 -- XYZ电容换能地震计，
        #          1040 -- UVW电容换能地震计，
        #          1050 -- 其他类型加速度计，如化学摆
        (2000, '加速度计'),  # 2000 -- 标准 三分向加速度型地震计，201-299 为子类型，
        # 例如：
        #          2010 -- 无源加速度计
        #          2020 -- 机械式力平衡式加速度计
        #          2030 -- MEMS力平衡式加速度计
        #          2040 -- 强震烈度仪
        #          2050 -- 石英加速度计（西安、日本系列）
        #          2060 -- 其他类型加速度计
        (3000, '位移传感器'),  # 3000 -- 位移传感器
        # 例如：
        #          3010 -- 无源加速度计
        #          2020 -- 机械式力平衡式加速度计
        #          2030 -- MEMS力平衡式加速度计
        #          2040 -- 强震烈度仪
        #          2050 -- 石英加速度计（西安、日本系列）
        #          2060 -- 其他类型加速度计
        (4000, '位移传感器'),  # 3000 -- 数据采集器
    )
    Name = models.CharField(verbose_name='仪器型号', max_length=160)
    ICompany = models.ForeignKey(Company, verbose_name='生产厂商', on_delete=models.CASCADE)  # 生产厂商
    IMainType = models.IntegerField(verbose_name='仪器类型', choices=Signal_type, default=0)
    IDBOK = models.IntegerField(verbose_name='定型信息', choices=DB_type, default=1)  # 默认所有仪器均未定型
    IDir = models.CharField(verbose_name='仪器目录', null=True, blank=True, max_length=160)
    MainChannel = models.IntegerField(verbose_name='主通道数', default=3)
    AuxChannel = models.IntegerField(verbose_name='辅助通道数', default=3)

    # IComments  = models.CharField(         verbose_name='注释',    null=True,blank=True,max_length=80)
    # IInfoUrl = models.URLField(null=True,blank=True)                           # 仪器介绍 Url，内置 PDF 文件
    # ISpecf  = models.CharField(max_length=10000,null=True,blank=True)          # 仪器参数，可解析
    # ITtMainChannels = models.IntegerField(default=3)        # 仪器主通道数
    # ITtAuxChannels = models.IntegerField(default=3)         # 仪器辅助通道数
    # IBitmap = models.ImageField()           # 仪器照片

    def __str__(self):
        return self.Name


# 数采基本参数
class Digitizer_base(Instruments_base):
    # Instruments_Name()
    # MainADBits = models.IntegerField(default=24)                # 主通道AD位数
    # MainADRate = models.CharField(max_length=200,null=True,blank=True)      # 主通道AD采样速率，以字符串保存，然后通过解析获取其采样率
    # MainGain = models.CharField(max_length=200,null=True,blank=True)        # 主通道AD增益，以字符串保存，然后通过解析获取其采样率
    # MainFilter = models.IntegerField(default=1)
    # AuxADBits = models.IntegerField(default=16)                 # 辅助通道AD 位数
    # MainSensitivity = models.FloatField(default=8.3886e5)       # 主通道标准灵敏度 Count/V，Main Gain = 1
    # AuxSensitivity = models.FloatField(default=3276.75)         # 辅助通道 Count/V
    pass


class Digitizer_gain(models.Model):
    Digitizer = models.ForeignKey(Digitizer_base, verbose_name='采集器型号', on_delete=models.CASCADE)  # 仪器型号
    Gain = models.CharField(verbose_name='增益参数', default='', blank=True, max_length=200)


class Digitizer_rate(models.Model):
    DigitizerGain = models.ForeignKey(Digitizer_gain, verbose_name='增益参数', on_delete=models.CASCADE)  # 仪器型号
    Rate = models.CharField(verbose_name='速率参数', default='', blank=True, max_length=200)


class Digitizer_filter(models.Model):
    DigitizerRate = models.ForeignKey(Digitizer_rate, verbose_name='速率参数', on_delete=models.CASCADE)  # 仪器型号
    Filter = models.CharField(verbose_name='滤波参数', default='', blank=True, max_length=200)
    IParUrl = models.CharField(verbose_name='参数目录', default='', blank=True, max_length=200)  # 设备参数文件
    rate = models.FloatField(verbose_name='采样速率', default=100.)
    sensitivity = models.FloatField(verbose_name='灵敏度', default=100.)


# 传感器基本参数
class Sensor_base(Instruments_base):
    # InfoNum = models.IntegerField(     verbose_name='不同配置参数数量',default=0,blank=True)
    # Instruments_Name()
    # MainLowFreq = models.FloatField(default=0.008333)  # 主通道低频频带
    # MainHighFreq = models.FloatField(default=50)  # 主通道高频频带
    # def __init__(self):
    #    Instruments_base.__init__(self)
    # MainType = models.IntegerField(choices=Instruments_base.Signal_type)     # = 1 Velocity , = 2 accelerometer
    pass


class Sensor_info(models.Model):
    Sensor = models.ForeignKey(Sensor_base, verbose_name='传感器型号', on_delete=models.CASCADE)  # 仪器型号
    ISensitivityInfo = models.CharField(verbose_name='灵敏度信息', default='', blank=True, max_length=80)
    IParUrl = models.CharField(verbose_name='仪器参数', default='', blank=True, max_length=200)  # 设备参数文件
    IFreqInfo = models.CharField(verbose_name='频带信息', default='', blank=True, max_length=80)
    IGainNormalization = models.FloatField(verbose_name='归一化增益', default=1.0)
    IGain = models.FloatField(verbose_name='传感器增益', default=2000.0)
    ZeroNum = models.IntegerField(verbose_name='零点数量', default=0)  # 零点数量
    PoleNum = models.IntegerField(verbose_name='极点数量', default=0)  # 极点数量
    # IFreqNormalization = models.FloatField(verbose_name='归一化频率',default=1.0)


# 零极点信息
class ZeroPole(models.Model):
    ZP_type = (
        (0, '零点'),  #
        (1, '极点')  #
    )
    nZPMode = models.IntegerField(verbose_name='零极点类型', choices=ZP_type, default=0)
    fReal = models.FloatField(verbose_name='实部', default=1.0)
    fImag = models.FloatField(verbose_name='虚部', default=1.0)
    sComplex = models.CharField(verbose_name='复数显示', default="0+0j", max_length=80)
    sensor_info = models.ForeignKey(Sensor_info, verbose_name='仪器信息', on_delete=models.CASCADE)  # 仪器信息


class Zero(ZeroPole):
    pass


class Pole(ZeroPole):
    pass


# 一体化传感器 = Sensor + digitizer
class Graph_base(Digitizer_base):
    MainLowFreq = models.FloatField(default=0.008333)  # 主通道低频频带
    MainHighFreq = models.FloatField(default=50)  # 主通道高频频带

    def __init__(self):
        Digitizer_base.__init__(self)
        MainSensitivity = models.FloatField(2000. * 8.3886e5)  # 主通道标准灵敏度  2000/m/s or 2.5V/g
        # AuxSensitivity =  models.FloatField(10000. * 3276.75)  # 辅助通道 Count/V
        # AuxType = models.IntegerField(default=2)  # = 0 Displace, = 1 Velocity , = 2 accelerometer, = 3 NULL
        # AuxLowFreq = models.FloatField(default=0.)  # 辅助通道低频频带
        # AuxHighFreq = models.FloatField(default=50.)  # 辅助通道高频频带
        # MainType = models.IntegerField(default=1)           # = 0 Displace, = 1 Velocity , = 2 accelerometer


class AD_Sensor(models.Model):
    ADInfo = models.ForeignKey(Digitizer_filter, verbose_name='数采名称', on_delete=models.CASCADE, default=None)  # 仪器信息
    SensorInfo1 = models.ForeignKey(Sensor_info, verbose_name='传感器1', related_name='Sensor_info1',
                                    on_delete=models.CASCADE, blank=True, default=None)  # 地震计1类型
    SensorInfo2 = models.ForeignKey(Sensor_info, verbose_name='传感器2', related_name='Sensor_info2',
                                    on_delete=models.CASCADE, blank=True, default=None)  # 地震计2类型
    SensorInfo3 = models.ForeignKey(Sensor_info, verbose_name='传感器3', related_name='Sensor_info3',
                                    on_delete=models.CASCADE, blank=True, default=None)  # 地震计3类型
    SensorInfo4 = models.ForeignKey(Sensor_info, verbose_name='传感器4', related_name='Sensor_info4',
                                    on_delete=models.CASCADE, blank=True, default=None)  # 地震计4类型
    type = models.IntegerField(verbose_name='组合类型', default=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        return

'''
        sInfo = ''
        if (self.SensorInfo1 != None):
            sInfo = sInfo + self.ADInfo.DigitizerRate.DigitizerGain.Digitizer.Name \
                    + ' ' + self.ADInfo.DigitizerRate.DigitizerGain.Gain + ' ' + self.ADInfo.DigitizerRate.Rate + ' ' + self.ADInfo.Filter \
                    + '_' + self.SensorInfo1.Sensor.Name + ' ' + self.SensorInfo1.IFreqInfo + ' ' + self.SensorInfo1.ISensitivityInfo
        if (self.SensorInfo2 != self.SensorInfo1 and self.SensorInfo2 != None):
            sInfo = sInfo + '_' + self.SensorInfo2.Sensor.Name + ' ' + self.SensorInfo2.IFreqInfo + ' ' + self.SensorInfo2.ISensitivityInfo
        if (self.SensorInfo3 != self.SensorInfo1 and self.SensorInfo3 != None):
            sInfo = sInfo + '_' + self.SensorInfo3.Sensor.Name + ' ' + self.SensorInfo3.IFreqInfo + ' ' + self.SensorInfo3.ISensitivityInfo
        if (self.SensorInfo4 != self.SensorInfo1 and self.SensorInfo4 != None):
            sInfo = sInfo + '_' + self.SensorInfo4.Sensor.Name + ' ' + self.SensorInfo4.IFreqInfo + ' ' + self.SensorInfo4.ISensitivityInfo


    # =1 常规 3通道地震计加3通道数采模式
    # =2 常规 3通道地震计、3通道加速度计加6通道数采模式，Sensor2 有效
class Seismometer3_base(Sensor_base):

    def __init__(self):
        Sensor_base.__init__(self)
        MainType = models.IntegerField(1)            # = 1 Velocity , = 2 accelerometer
        MainSensitivity = models.FloatField(2000.)   # 主通道标准灵敏度  2000/m/s or 2.5V/g
        ITtMainChannels = models.IntegerField(3)     # 仪器主通道数

class Electmagnetic_Seismometer_base(Seismometer3_base):
    pass

class Feedback_Seismometer_base(Seismometer3_base):
    pass

class Banlance_Seismometer_base(Feedback_Seismometer_base):
    AuxType = models.IntegerField(default=2,
                                  choices=Sensor_base.Signal_type)  # = 0 Displace, = 1 Velocity , = 2 accelerometer, = 3 NULL
    AuxSensitivity = models.FloatField(default=10000.)  # 辅助通道 Count/V
    AuxLowFreq = models.FloatField(default=0.)  # 辅助通道低频频带
    AuxHighFreq = models.FloatField(default=50.)  # 辅助通道高频频带
    def __init__(self):
        Feedback_Seismometer_base(self)
        ITtAuxChannels = models.IntegerField(default=3)        # 仪器主通道数

class Accelerometer_base(Sensor_base):
    def __init__(self):
        Sensor_base.__init__(self)
        ITtMainChannels = models.IntegerField(3)  # 仪器主通道数
        MainType = models.IntegerField(2)         # = 1 Velocity , = 2 accelerometer

class Digitizer_3ch_base(Digitizer_base):
    def __init__(self):
        Digitizer_base.__init__(self)
        ITtMainChannels = models.IntegerField(3)        # 仪器主通道数
        ITtAuxChannels = models.IntegerField(3)         # 仪器辅助通道数

class Digitizer_6ch_base(Digitizer_base):
    def __init__(self):
        Digitizer_base.__init__(self)
        ITtMainChannels = models.IntegerField(6)        # 仪器主通道数
        ITtAuxChannels = models.IntegerField(6)         # 仪器辅助通道数

class TDE324CIO_base(Digitizer_3ch_base):
    pass

class TDE324FIO_base(Digitizer_6ch_base):
    pass

class TDE324CIN_base(Digitizer_3ch_base):
    pass

class TDE324FIN_base(Digitizer_6ch_base):
    pass
'''