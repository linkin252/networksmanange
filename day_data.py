import os,sys

import datetime

#mode = 0 ， 存在返回True，如果目录不存在则创建目录，并返回 False
#mode = 1，  存在返回True，如果不存在则创建文件，并返回 False
#mode = 2，  存在返回True，如果不存在则返回 False
def mkfile(path, mode):
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("/")
    # 判断路径是否存在
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        # print('mode=', mode, ',', path, 'is not existed!')
        if (mode == 0):
            # 如果不存在则创建目录
            os.makedirs(path)
            # print('mkdir', path, 'OK.')
        elif (mode == 1):
            # 如果不存在文件则创建文件
            f = open(path, 'wt')
            f.write(path)
            f.close()
        return False
    else:
        return True

def show_files(path, all_files):
    files = os.listdir(path)
    # print(files)
    for file in files:
        # print(file)
        if os.path.isdir(path + '/' + file):
            # print(path + '/' + file)
            show_files(path + '/' + file, all_files)
        elif os.path.isfile(path + '/' + file):
            all_files.append(file)
            #all_files.append(path  + '/' + file)
    return all_files

def show_path(path, all_files,all_paths):
    files = os.listdir(path)
    # print(files)
    for file in files:
        # print(file)
        if os.path.isdir(path + '/' + file):
            # print(path + '/' + file)
            show_path(path + '/' + file, all_files,all_paths)
        elif os.path.isfile(path + '/' + file):
            all_files.append(file)
            all_paths.append(path  + '/' + file)
    return (all_files,all_paths)
#
# def get_or_create_Network(NetCode,NetName,fSrcDir,sDenDir,nNetMode):
#     try:
#         net = Network.objects.get(Code=NetCode)
#     except Network.DoesNotExist:
#         net = Network.objects.create(Code=NetCode, Name=NetName, IDataDir=fSrcDir, IOutDir=sDenDir, INetMode=nNetMode)
#     return net
#
# def get_or_create_Station(net,StaCode,StaName):
#     try:
#         sta = Station.objects.get(Code=StaCode, Network=net)
#     except Station.DoesNotExist:
#         sta = Station.objects.create(Code=StaCode, Name=StaName, Network=net)
#     return sta
#
# def get_DigitizerInfo(Name='TDE-324',Gain='',Rate='',Filter=''):
#     AD = None
#     gain = None
#     rate = None
#     filter = None
#
#     try:
#         AD = Digitizer_base.objects.get(Name=Name)
#     except Digitizer_base.DoesNotExist:
#         bRet = False
#         return (False,AD,gain,rate,filter)
#
#     if Gain=='':
#         try:
#             gain = Digitizer_gain.objects.get(Digitizer=AD, Gain=Gain)
#         except Digitizer_gain.DoesNotExist:
#             bRet = False
#             return (False,AD,gain,rate,filter)
#     else:
#         try:
#             gain = Digitizer_gain.objects.get(Digitizer=AD, Gain=Gain)
#         except Digitizer_gain.DoesNotExist:
#             bRet = False
#             return (False,AD,gain,rate,filter)
#
#     if Rate=='':
#         try:
#             rate = Digitizer_rate.objects.get(DigitizerGain=gain)
#         except Digitizer_rate.DoesNotExist:
#             return (False,AD,gain,rate,filter)
#     else:
#         try:
#             rate = Digitizer_rate.objects.get(DigitizerGain=gain, Rate=Rate)
#         except Digitizer_rate.DoesNotExist:
#             return (False,AD,gain,rate,filter)
#
#     if Filter=='':
#         try:
#             filter = Digitizer_filter.objects.get(DigitizerRate=rate)
#         except Digitizer_filter.DoesNotExist:
#             return (False,AD,gain,rate,filter)
#     else:
#         try:
#             filter = Digitizer_filter.objects.get(DigitizerRate=rate, Filter=Filter)
#         except Digitizer_filter.DoesNotExist:
#             return (False,AD,gain,rate,filter)
#     return (True,AD,gain,rate,filter)
#
# def get_SensorInfo(Name='TDV-60B',Freq='',Sensitivity=''):
#     sensor = None
#     sensorinfo = None
#     try:
#         sensor = Sensor_base.objects.get(Name=Name)
#     except Sensor_base.DoesNotExist:
#         return(False,sensor,sensorinfo)
#     if (Freq=='' and Sensitivity==''):
#         try:
#             sensorinfo = Sensor_info.objects.get(Sensor=sensor)
#         except Sensor_base.DoesNotExist:
#             return(False,sensor,sensorinfo)
#     else:
#         try:
#             sensorinfo = Sensor_info.objects.get(Sensor=sensor,ISensitivityInfo=Sensitivity,IFreqInfo=Freq)
#         except Sensor_base.DoesNotExist:
#             return(False,sensor,sensorinfo)
#     return(True,sensor,sensorinfo)
#
# def get_or_create_ADSensor(filter,sensorinfo1,sensorinfo2=None,sensorinfo3=None,sensorinfo4=None):
#     if (sensorinfo4==None):
#         sensorinfo4 = sensorinfo1
#     if (sensorinfo3==None):
#         sensorinfo3 = sensorinfo1
#     if (sensorinfo2==None):
#         sensorinfo2 = sensorinfo1
#     try:
#         ADSensor = AD_Sensor.objects.get(ADInfo=filter,SensorInfo1=sensorinfo1
#                 ,SensorInfo2=sensorinfo2,SensorInfo3=sensorinfo3,SensorInfo4=sensorinfo4)
#     except:
#         ADSensor = AD_Sensor.objects.create(ADInfo=filter,SensorInfo1=sensorinfo1
#                     ,SensorInfo2=sensorinfo2,SensorInfo3=sensorinfo3,SensorInfo4=sensorinfo4)
#     return ADSensor
#
# def get_or_create_Sta_ADSensor(sta,ADSensor):
#     try:
#         StaAD = Sta_ADSensor.objects.get(Station=sta, ADSensor=ADSensor)
#     except Sta_ADSensor.DoesNotExist:
#         StaAD = Sta_ADSensor.objects.create(Station=sta, ADSensor=ADSensor)
#     return StaAD
#
# def get_or_create_CH(StaADSensor,LocCode, ChCode):
#     try:
#         ch = Channel.objects.get(Sta_ADSensor=StaADSensor, Code_Loc=LocCode, Code_CH=ChCode)
#     except Channel.DoesNotExist:
#         StartTime = datetime.date.today()
#         EndTime = datetime.date(2099, 1, 1)
#         ch = Channel.objects.create(Sta_ADSensor=StaADSensor, Code_Loc=LocCode, Code_CH=ChCode,
#                                     Start_Time=StartTime, End_Time=EndTime)
#     return ch
#
# def set_or_create_Day_data(ch,date,runrate):
#     try:
#         data = Day_data.objects.get(ch=ch,date=date)
#         data.runrate = runrate
#         data.save()
#     except Day_data.DoesNotExist:
#         data = Day_data.objects.create(ch=ch,date=date,runrate=runrate)
#     return data

def addNetDemo(fSrcDir,nNetMode=1):
    # 建立顶层根目录
    STATIC_PATH = os.path.join(os.path.dirname(__file__), 'static')
    sDenDir = 'networks'
    fDenDir = os.path.join(STATIC_PATH, sDenDir)
    mkfile(fDenDir, 0)

    #if nNetMode==1:
    #    sDenDir = 'networks/adapt'
    #elif nNetMode==2:
    #    sDenDir = 'networks/Seiscomp3'
    #elif nNetMode==3:
    #    sDenDir = 'networks/TDE-324CI'
    #fDenDir = os.path.join(STATIC_PATH, sDenDir)
    #mkfile(fDenDir, 0)

    file_list = []
    path_list = []
    (file_list,path_list) = show_path (fSrcDir,file_list,path_list)
    for i in range(len(file_list)):
        file = file_list[i]
        path = path_list[i]

        now = datetime.date.today()
        dayCount = now - datetime.date(now.year - 1, 12, 31)

        num = file.count('.')
        if (num >= 6):
            (NetCode,StaCode,LocCode,ChCode,DataCode,nYear,nDay) = file.split('.')
            # print(NetCode, StaCode, LocCode, ChCode, DataCode, nYear, nDay)
            # print(len(NetCode), len(StaCode), len(LocCode), len(ChCode), len(DataCode), len(nYear), len(nDay))
            if (len(NetCode)<=2 and len(StaCode)<=5 and len(LocCode)<=2 and len(ChCode)<=3 and DataCode=='D'
                    and len(nYear)<=4 and len(nDay)<=3 and int(nDay) == dayCount.days-1):
                # net = get_or_create_Network(NetCode,NetCode,fSrcDir,sDenDir,nNetMode)
                # sta = get_or_create_Station(net,StaCode,StaCode)
                # (bRet,AD,gain,rate,filter) = get_DigitizerInfo('TDE-324','10Vpp','100Hz','Linear')
                # if bRet==False:
                #     continue
                # (bRet,sensor,sensorinfo) = get_SensorInfo('TMA-33')
                # if bRet==False:
                #     continue
                # ADSensor = get_or_create_ADSensor(filter,sensorinfo)
                # StaADSensor = get_or_create_Sta_ADSensor(sta,ADSensor)
                # ch = get_or_create_CH(StaADSensor,LocCode, ChCode)
                # 以上，添加1个台站的逻辑确实很复杂

                sDenDir2 = sDenDir + '/' + NetCode
                fDenDir = os.path.join(STATIC_PATH, sDenDir2)
                mkfile(fDenDir, 0)

                sDenDir2 = sDenDir2 + '/' + StaCode
                fDenDir = os.path.join(STATIC_PATH, sDenDir2)
                mkfile(fDenDir, 0)

                sDenDir2 = sDenDir2 + '/' + nYear
                fDenDir = os.path.join(STATIC_PATH, sDenDir2)
                mkfile(fDenDir, 0)
                sDenDir2 = sDenDir2 + '/' + nDay
                fDenDir = os.path.join(STATIC_PATH, sDenDir2)
                mkfile(fDenDir, 0)

                from obspy import read
                #from obspy.io.xseed import Parser
                from obspy.signal import PPSD
                from obspy.imaging.cm import pqlx

                st = read(path)
                ChName = NetCode + '.' + StaCode + '.' + LocCode + '.' + ChCode + '.' + nYear + '.' + nDay
                outfile1 = fDenDir + '/' + ChName + '.day_wave.png'
                outfile2 = fDenDir + '/' + ChName + '.day_wave.low_pass_0.2Hz.png'
                outfile3 = fDenDir + '/' + ChName + '.day_wave.high_pass_0.2Hz.png'
                outfile4 = fDenDir + '/' + ChName + '.ppsd.png'
                outfile5 = fDenDir + '/' + ChName + '.spectrogram.png'

                print(NetCode, StaCode, LocCode, ChCode, DataCode, nYear, nDay)
                st.plot(size=(1600, 1200), tick_format='%I:%M:%p', type="dayplot", interval=30, right_vertical_labels=True,
                        vertical_scaling_range=st[0].data.std() * 20, one_tick_per_line=True,
                        color=["r", "b", "g"], show_y_UTC_label=True,
                        title=ChName,time_offset=8,
                        outfile=outfile1)
                st2 = st.copy()

                st.filter("lowpass", freq=0.2, corners=2)
                st.plot(size=(1600, 1200), tick_format='%I:%M:%p', type="dayplot", interval=30, right_vertical_labels=True,
                        vertical_scaling_range=st[0].data.std() * 20, one_tick_per_line=True,
                        color=["r", "b", "g"], show_y_UTC_label=True,
                        title=ChName + '.low_pass 0.2Hz',time_offset=8,
                        outfile=outfile2)

                st2.filter("highpass", freq=0.2)
                st2.plot(size=(1600, 1200), tick_format='%I:%M:%p', type="dayplot", interval=30, right_vertical_labels=True,
                         vertical_scaling_range=st2[0].data.std() * 20,one_tick_per_line=True,
                         color=["r", "b", "g"], show_y_UTC_label=True,
                         # events={"min_magnitude": 5},
                         title=ChName+ '.high_pass 0.2Hz', time_offset=8,
                         outfile=outfile3)

                # paz = {}
                # paz['zeros'] = []
                # for zero in Zero.objects.filter(sensor_info=sensorinfo).order_by('id'):
                #     paz['zeros'].append(complex(zero.fReal, zero.fImag))
                # paz['poles'] = []
                # for pole in Pole.objects.filter(sensor_info=sensorinfo).order_by('id'):
                #     paz['poles'].append(complex(pole.fReal, pole.fImag))
                # if (2000<=sensor.IMainType and sensor.IMainType<3000):       # 加速度模式
                #     paz['zeros'].append(complex(0.,0))
                # paz['gain'] = sensorinfo.IGainNormalization
                # paz['sensitivity'] = sensorinfo.IGain * filter.sensitivity
                # #print(paz)
                # st = read(path)
                # #print(st)
                # ppsd = PPSD(st[0].stats, paz)
                # ppsd.add(st)
                # #print(ppsd.times_data)
                # #print('len=',len(ppsd.times_data),ppsd.times_data[0][0],ppsd.times_data[0][1])
                # ppsd.plot(outfile4, xaxis_frequency=True, cmap=pqlx)
                # ppsd.plot_spectrogram(filename=outfile5, cmap='CMRmap_r')
                # if (sensor.IMainType<2000):
                #     outfile6 = fDenDir + '/' + ChName + '.1-2s.sp.png'
                #     ppsd.plot_temporal(1.414, filename=outfile6)
                # elif (2000<=sensor.IMainType and sensor.IMainType<3000):       # 加速度模式)
                #     outfile6 = fDenDir + '/' + ChName + '.1-2Hz.sp.png'
                #     ppsd.plot_temporal(.707, filename=outfile6)
                #
                # fBlankTime = 0.
                # for i in range(1,len(ppsd.times_data)): #  1个整时间段说明未丢数
                #     dt = (ppsd.times_data[i][0] - ppsd.times_data[i-1][1])
                #     if (dt < 0):
                #         print(dt,ppsd.times_data[i][0],ppsd.times_data[i-1][1])
                #     else:
                #         fBlankTime += dt
                # runrate = 1.0 - fBlankTime / 86400.
                # date = datetime.date(ppsd.times_data[0][0].year,ppsd.times_data[0][0].month,ppsd.times_data[0][0].day)
                # set_or_create_Day_data(ch,date,runrate)

        else:
            print(file , "Name is error.")

def Net2dbDemo():
    #addNetDemo("D:/django/taide/static/resource/station/SeiscomP3",2)
    # addNetDemo("D:/django/taide/static/resource/station/TDE-324CI",3)
    addNetDemo("/home/usrdata/usb/data",3)
    #addNetDemo("D:/svn/python/django/taide/static/resource/station/Adapt",1)

def getStaticStr():
    return os.path.join(os.path.dirname(__file__), 'static')


#   将来希望生成 XML 文件，并从XML 文件中添加台网、台站、分向的资料
def AddNetAll():
    Net2dbDemo()

"""
                parser = Parser()
                ppsd = PPSD(tr.stats, metadata=parser)
                ppsd.add(st)
                print(ppsd.times_data)


from obspy.io.xseed import Parser
from obspy.signal import PPSD
from obspy.imaging.cm import pqlx

parser = Parser()
ppsd = PPSD(tr.stats, metadata=parser)
ppsd.add(st)
print(ppsd.times_data)

# fig = ppsd.figure(figsize=(16,12))
ppsd.plot(xaxis_frequency=True, cmap=pqlx)
ppsd.plot(percentiles=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], cmap=pqlx)
ppsd.plot(cumulative=True, cmap=pqlx)
ppsd.plot(cmap=pqlx)
ppsd.plot("jpg/T1.24-1.png", cmap=pqlx)
ppsd.plot("jpg/T1.24-1.pdf", cmap=pqlx)
ppsd.plot("jpg/T1.24-2.png", xaxis_frequency=True, cmap=pqlx)
ppsd.plot("jpg/T1.24-`2.pdf", xaxis_frequency=True, cmap=pqlx)
ppsd.plot_spectrogram(filename="jpg/T1.24-3.png", cmap='CMRmap_r')
ppsd.plot_temporal(1, filename="jpg/T1.24-4.png")

st = read("data/BW.KW1..EHZ.D.2011.037")
ppsd.add(st)
ppsd.plot("jpg/T1.24-5.png", cmap=pqlx)


def DoData(fSrcDir,nNetMode=1):
    STATIC_PATH = os.path.join(os.path.dirname(__file__), 'static')
    sDenDir = 'networks'
    fDenDir = os.path.join(STATIC_PATH, sDenDir)
    mkfile(fDenDir, 0)
    if nNetMode==1:
        sDenDir = 'networks/adapt'
    elif nNetMode==2:
        sDenDir = 'networks/Seiscomp3'
    elif nNetMode==3:
        sDenDir = 'networks/TDE-324CI'
    fDenDir = os.path.join(STATIC_PATH, sDenDir)
    mkfile(fDenDir, 0)

"""

if __name__ == "__main__":
    AddNetAll()