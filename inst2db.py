# coding:utf-8

import glob
import os
import re
from typing import List

from instruments.models import National, Company, Sensor_base, Sensor_info, Digitizer_base,Zero,Pole,\
    Digitizer_gain,Digitizer_rate,Digitizer_filter
from bs4 import BeautifulSoup
from doobspy import parser_sensor_resp,parser_digitizer_resp

# 首次添加国家信息，国家信息是关键底层信息，不轻易删除
def AddNationalFirst():
    STATIC_PATH = os.path.join(os.path.dirname(__file__), 'static')
    fName = 'National\\National.txt'
    # print(STATIC_PATH,fName)
    fName = os.path.join(STATIC_PATH, fName)
    # print(fName)
    f = open(fName, "rt")
    f.seek(0)
    for line in f:
        line = line.strip()
        num = line.count(',')
        if (num >= 4):
            name, chnName, I32Name, I64Name, I128Name = line.split(',')
            I32Name = "National\\32\\" + I32Name
            I64Name = "National\\64\\" + I64Name
            I128Name = "National\\128\\" + I128Name
            # print(name, chnName, I32Name, I64Name, I128Name)

            oldNational = National()
            oldNational = National.objects.filter(Name=name)
            if (len(oldNational) == 0):
                obj, created = National.objects.get_or_create(Name=name,
                                                              ChnName=chnName,
                                                              Icon32=I32Name,
                                                              Icon64=I64Name,
                                                              Icon128=I128Name)
                if (created):
                    obj.save()
            else:
                oldNational[0].ChnName = chnName
                oldNational[0].Icon32 = I32Name
                oldNational[0].Icon64 = I64Name
                oldNational[0].Icon128 = I128Name
                oldNational[0].save()
        else:
            print(line, " has only", num, ',  we need at least 4 !')
            continue

    f.close()
    print(National.objects.all())


def mkfile(path, mode):
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")
    # 判断路径是否存在
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        print('mode=', mode, ',', path, 'is not existed!')
        if (mode == 0):
            # 如果不存在则创建目录
            os.makedirs(path)
        elif (mode == 1):
            # 如果不存在文件则创建文件
            f = open(path, 'wt')
            f.write(path)
            f.close()
        return False
    else:
        return True


# 首次添加厂家信息, 厂家信息是关键底层信息，不轻易删除
def AddCompanyFirst():
    STATIC_PATH = os.path.join(os.path.dirname(__file__), 'static')
    fName = 'resource\\company\\company.txt'
    # print(STATIC_PATH,fName)
    fName = os.path.join(STATIC_PATH, fName)
    # print(fName)
    f = open(fName, "rt")
    f.seek(0)
    for line in f:
        line = line.strip()
        num = line.count(',')
        if (num >= 3):
            name, chnName, national, cWeb = line.split(',')
            if (cWeb == '----'):
                cWeb = ''
            sDir = 'company\\' + name
            fCoDir = os.path.join(STATIC_PATH, sDir)
            mkfile(fCoDir, 0)
            sInfoName = os.path.join(STATIC_PATH, sDir + "\\" + name + "_info.txt")
            mkfile(sInfoName, 1)
            sInfo = 'company\\' + name + '\\' + name + "_info.txt"
            sIcon = 'company\\' + name + '\\' + name + '_icon.png'
            sIconFile = STATIC_PATH + '\\resource\\company\\' + name + '_icon.png'
            if (mkfile(sIconFile,2)):       # 文件存在
                cmd = 'copy ' + sIconFile + ' ' +  STATIC_PATH + '\\company\\' + name
                print(cmd)
                os.system(cmd)
            print(name, chnName, national, sIcon, cWeb, sInfo)
            SelNational = National.objects.filter(Name=national)
            if (len(SelNational) != 0):
                addCompany = Company.objects.filter(Name=name, CNational=SelNational[0])
                if (len(addCompany) == 0):
                    obj, created = Company.objects.get_or_create(Name=name,
                                                                 ChnName=chnName,
                                                                 CNational=SelNational[0],
                                                                 CIcon=sIcon,
                                                                 CWeb=cWeb,
                                                                 CInfo=sInfo)
                    if (created):
                        obj.save()
                else:
                    # print(addCompany)
                    addCompany[0].ChnName = chnName
                    addCompany[0].CIcon = sIcon
                    addCompany[0].CWeb = cWeb
                    addCompany[0].CInfo = sInfo
                    addCompany[0].save()
            else:
                print("National=%s is not existed, cann't add!", national)
        else:
            print(line, " has only", num, ',  we need at least 3 !')
            continue
    f.close()
    print(Company.objects.all())

def files(curr_dir='.', ext='*.html'):
    """当前目录下的文件"""
    for i in glob.glob(os.path.join(curr_dir, ext)):
        yield i


def all_files(rootdir, ext):
    """当前目录下以及子目录的文件"""
    for name in os.listdir(rootdir):
        if os.path.isdir(os.path.join(rootdir, name)):
            try:
                for i in all_files(os.path.join(rootdir, name), ext):
                    yield i
            except:
                pass
    for i in files(rootdir, ext):
        yield i


def remove_files(rootdir, ext, show=False):
    """删除rootdir目录下的符合的文件"""
    for i in files(rootdir, ext):
        if show:
            print(i)
        os.remove(i)


def remove_all_files(rootdir, ext, show=False):
    """删除rootdir目录下以及子目录下符合的文件"""
    for i in all_files(rootdir, ext):
        if show:
            print(i)
        os.remove(i)

def FindCompany_list(Name='all'):
    Company_list = []
    if Name== 'all':     #  全部搜索一遍
        Company_list = Company.objects.order_by('id')
    else:
        bNational = False
        print(Name)
        National_list = National.objects.order_by('id')
        for national in National_list:
            print(Name, national.Name)
            if Name == national.Name:    # Name是国名
                bNational = True
                Company_list = Company.objects.filter(CNational=national).order_by('id')
                break
        if (not bNational):     #  不是国家
            Company_nl = Company.objects.order_by('id')
            for company in Company_nl:
                print(Name,company.Name)
                if Name == company.Name:  # Name是企业名
                    print(Name)
                    Company_list.append(company)
                    break
    if (len(Company_list)==0):     #  没有处理任何数据
        print("Name is not found in Company or National!")
    return Company_list

# 从各厂家仪器Dataless文件中，获取仪器基本信息
def FindSensorsFirst(Name = 'all'):
    Company_list = FindCompany_list(Name)
    if (len(Company_list)==0):  # list 无元素
        return

    # print(Company_list)
    # 生成 'instruments'、'instruments\\sensor' 目录
    STATIC_PATH = os.path.join(os.path.dirname(__file__), 'static')
    sDenDir = 'instruments'
    fDenDir = os.path.join(STATIC_PATH, sDenDir)
    mkfile(fDenDir, 0)
    sDenDir = 'instruments\\sensor'
    fDenDir = os.path.join(STATIC_PATH, sDenDir)
    mkfile(fDenDir, 0)

    nCompany = 0
    movies = []  # 将所有的仪器集合到一起，并排序
    for company in Company_list:
        fSrcDir = "resource\\IRIS\\sensors\\" + company.Name
        print('Stage 1    : Processing Company = %d, Company=%s ...',company.Name)        #  第一级厂商，标识处理
        fSrcDir = os.path.join(STATIC_PATH, fSrcDir)
        listV_title1 = ['Manufacturer', 'Model', 'Period / Frequency', 'Sensitivity', 'RESP Filename', 'Comments']
        listV_title2 = ['Manufacturer', 'Model', 'Period/Frequency', 'Sensitivity', 'RESP Filename', 'Comments']
        listV_title3 = ['Manufacturer', 'Model', 'Frequency / Period', 'Sensitivity', 'RESP Filename', 'Comments']
        listV_title4 = ['Manufacturer', 'Model', 'Period / Frequency', 'Sensitivity (V/m/s**2)', 'RESP Filename', 'Comments']

        if (mkfile(fSrcDir, 2)):  # 如果目录存在，搜索
            sDenDir = 'instruments\\sensor\\' + company.Name
            nFile = 0
            for fName in all_files(fSrcDir, "*.html"):  # 遍历该目录下的每一个html文件
                print('Stage 1.%d  : Parsero html %d, html=%s ...', nFile, fName)   # 第二级html文件，标识处理
                f = open(fName, "rt")
                rd = f.read()
                f.close()
                # 解析html文件的表头
                # soup = BeautifulSoup(rd,"lxml")
                soup = BeautifulSoup(rd, "html5lib")
                tr0 = soup.find_all('tr')[0:1]
                if (tr0 == []):  # 未解析表结构则退出该遍历
                    # print('No Table is found in File',fName)
                    continue
                info0 = list(tr0[0].stripped_strings)
                #print(info0)
                # info0 = list(tr0[0].strings)
                bInV1 = True
                for ListV in listV_title1:
                    if (ListV not in info0):
                        bInV1 = False
                        break  # False 的话，则直接退出for循环，当前模式不对
                bInV2 = True
                for ListV in listV_title2:
                    if (ListV not in info0):
                        bInV2 = False
                        break  # False 的话，则直接退出for循环，当前模式不对
                bInV3 = True
                for ListV in listV_title3:
                    if (ListV not in info0):
                        bInV3 = False
                        break  # False 的话，则直接退出for循环，当前模式不对
                bInV4 = True
                for ListV in listV_title4:
                    if (ListV not in info0):
                        bInV4 = False
                        break  # False 的话，则直接退出for循环，当前模式不对

                if (bInV1 or bInV2 or bInV3 or bInV4):  # V 模式
                    if bInV1:
                        listV_title = listV_title1
                    elif bInV2:
                        listV_title = listV_title2
                    elif bInV3:
                        listV_title = listV_title3
                    elif bInV4:  # 加速度模式
                        listV_title = listV_title4

                    listV_index = []
                    for ListV in listV_title:
                        Index = info0.index(ListV)
                        listV_index.append(Index)
                    # print(listV_index)

                    # 解析html文件的表内容
                    trs = soup.find_all('tr')[1:]
                    for tr in trs:
                        move = {}
                        infos = list(tr.stripped_strings)
                        # infos = list(tr.strings)
                        move['Manufacturer'] = company.Name  # infos[listV_index[0]]
                        move['Model'] = re.sub(r"[\/\\\:\*\?\"\<\>\|\,\;\ \+\&]", '_', infos[listV_index[1]]).strip()

                        # 将 s/Hz 转化为 Hz存储，去冗余信息
                        s0 = infos[listV_index[2]]
                        if (bInV3):  # Freq/Period 写反了的
                            (sFreq, sT) = s0.split('/')
                        else:
                            (sT, sFreq) = s0.split('/')
                        sT.strip()  # 去除空格
                        sFreq = sFreq.replace('Hz', "").strip() + 'Hz'  # 去除空格
                        move['Frequency_info'] = sFreq
                        sSensitivity = infos[listV_index[3]]
                        # 设置 sensorType
                        if ('V/M/S**2' in sSensitivity):
                            sSensitivity = sSensitivity.replace('V/M/S**2', '').strip() + 'V/M/S**2'
                            move['sensorType'] = 2000  # 加速度型
                        elif ('V/M/S' in sSensitivity):
                            sSensitivity = sSensitivity.replace('V/M/S', '').strip() + 'V/M/S'
                            move['sensorType'] = 1000  # 速度型
                        else:
                            move['sensorType'] = 0  # 未知型
                        move['Sensitivity_info'] = sSensitivity
                        move['SensorInfo_dir'] = re.sub(r"[\/\\\:\*\?\"\<\>\|\,\;\ \+\&]", '_',sFreq + '_' + sSensitivity).strip()
                        #move['Sensor_dir'] =

                        #if (len(listV_index) > listV_index[5]):
                        #    move['Comments'] = infos[listV_index[5]]
                        #else:
                        #    move['Comments'] = ""

                        move['del_flag'] = False  #默认不删除
                        move['add_flag'] = True   #默认添加sensor_base
                        move['RESP Src Filename'] = os.path.join(fSrcDir, infos[listV_index[4]]).strip()
                        fDenDir = os.path.join(STATIC_PATH, sDenDir)
                        move['sAbsSensorDir'] = fDenDir + '\\' + move['Model']
                        move['sAbsDenFile'] =         move['sAbsSensorDir'] + '\\' + company.Name + '_' + move['Model'] + '_' + move['SensorInfo_dir'] + '.resp'
                        move['sSensorDir'] =    sDenDir + '\\' + move['Model']
                        move['sDenFile'] =           move['sSensorDir']    + '\\' + company.Name + '_' + move['Model'] + '_' + move['SensorInfo_dir']
                        movies.append(move)
                else:
                    # print(fName)
                    print(fName,":"  +  "is bad Info")
                    print(info0)
                    pass
                nFile += 1
        else:
            #print('dir'+fSrcDir+'is not existed!')
            pass
        nCompany += 1
    # print(movies)
    print('Stage 1    : Process Company=%d, Success=%d.  \n\n' % (nCompany,len(movies)))

    # 删除movies list中 model错误，文件不存在的内容
    print('Stage 2    : Reorganize Company Info...')
    for move in movies:
        bFindFile = mkfile(move['RESP Src Filename'], 2)
        if (move['Model'] == 'Model' or bFindFile == False):  # 名字叫Model 肯定是错的
            if (bFindFile == False):
                print('File', move['RESP Src Filename'], 'is not found!')
                print('move is', move)
            movies.remove(move)

    # 剔除movies list中 model+Freq+Sensitivity 全部相同的内容
    # movies list中 model相同的内容，其新model为model+Freq+Sensitivity 不重复 sensor_base
    nIndex = 0
    for move1 in movies:
        nIndex += 1
        for move2 in movies[nIndex:]:
            # 同名、同频带、同灵敏度的设备，删后一个
            if (move1['Model'] == move2['Model']
                    and move1['Sensitivity_info'] == move2['Sensitivity_info']
                    and move1['Frequency_info'] == move2['Frequency_info']
                    and not move1['del_flag']):
                move2['del_flag'] = True
            # 同名、不同频带或不同灵敏度的设备，后一个不加sensor_base，仅仅加sensor_info
            elif (move1['Model'] == move2['Model'] and not move1['del_flag']):
                move2['add_flag'] = False

    nDelNum = 0
    nTtNum = 0
    nMainNum = 0
    for move in movies:
        if move['del_flag']:
            movies.remove(move)     # print(move)
            nDelNum += 1
        else:
            if move['add_flag']:
                nMainNum += 1
            nTtNum += 1
    print('Stage 2    : Delete Error Sensor=%d,Main Model=%d,Total Model=%d\n\n' % (nDelNum,nMainNum,nTtNum))

    # 添加Sensor 数据库
    nSensorCt = 0
    nSensorInfoCt = 0
    nZPCt = 0
    print('Stage 3    : Processing  Add Sensor...')
    for move in movies:
        if (move['add_flag']):
            mkfile(move['sAbsSensorDir'], 0)  # 生成sensor\厂家 目录
            SelCompany = Company.objects.filter(Name=move['Manufacturer'])
            if (len(SelCompany) != 0):  # 仅当厂家存在时才可添加，厂家不存在，不能添加
                addSensor = Sensor_base.objects.filter(Name=move['Model'], ICompany=SelCompany[0])
                if (len(addSensor) == 0):
                    print('Stage 3.1  :  Add Sensor Main Model=%d, %s-%s...' % (nSensorCt, SelCompany[0].Name, move['Model']))
                    obj, created = Sensor_base.objects.get_or_create(Name=move['Model'],
                                                                     ICompany=SelCompany[0],
                                                                     IMainType=move['sensorType'],
                                                                     IDir=move['sSensorDir'])
                    if (created):
                        obj.save()
                else:
                    print('Stage 3.1  :  Modified Sensor Num=', nSensorCt,SelCompany[0].Name, move['Model'])
                    addSensor[0].IMainType = move['sensorType']
                    #addSensor[0].IComments = move['Comments']
                    addSensor[0].IDir=move['sSensorDir']
                    addSensor[0].save()
                nSensorCt += 1

        SelSensor = Sensor_base.objects.filter(Name=move['Model'], ICompany=SelCompany[0])
        if (len(SelSensor) != 0):
            print('Stage 3.2  :  Parsering response File  Num= ',nSensorInfoCt,SelCompany[0].Name,move['Model'],move['Sensitivity_info'],move['Frequency_info'] )
            # 复制文件
            if (not mkfile(move['sAbsDenFile'], 2)):  # 文件不存在就复制文件
                cmd = 'copy ' + move['RESP Src Filename'] + ' ' + move['sAbsDenFile']
                print(cmd)
                os.system(cmd)
            sDir = os.path.join(STATIC_PATH,move['sDenFile'])
            sName =SelCompany[0].ChnName + ' ' + move['Model']  # + '_' + move['Sensitivity_info'] + '_' + move['Frequency_info']
            type = move['sensorType']
            (paz,Ymax,Ymin,Tmax,Tmin,Tzero) = parser_sensor_resp(sDir,sName,type)

            print('Stage 3.3  :  Adding Sensor Response Num = ',nSensorInfoCt, SelCompany[0].Name,move['Model'],move['Sensitivity_info'],move['Frequency_info'] )
            # 删除现有的 Sensor_info，然后再添加 Sensor_info，可以保证将所有关联的 零极点都删除
            Sensor_info.objects.filter(Sensor=SelSensor[0],ISensitivityInfo=move['Sensitivity_info'],IFreqInfo=move['Frequency_info']).delete()
            addSensor_info, created =  Sensor_info.objects.get_or_create(Sensor=SelSensor[0],
                                                                     ISensitivityInfo=move['Sensitivity_info'],
                                                                     IFreqInfo=move['Frequency_info'],
                                                                     IParUrl=move['sDenFile'],
                                                                     IGainNormalization=paz['gain'],
                                                                     IGain=paz['seismometer_gain'])
            if (created):
                nSensorInfoCt += 1
                #先删除ZeroPole, 再重新增加zero,pole
                Zero.objects.filter(sensor_info=addSensor_info).delete()
                Pole.objects.filter(sensor_info=addSensor_info).delete()
                nZCt = nPCt = 0
                for zero in paz['zeros']:
                    nZCt += 1
                    nZPCt += 1
                    sComplex = str(zero)
                    Zero.objects.create(sensor_info=addSensor_info,fReal=zero.real,fImag=zero.imag,sComplex =sComplex,nZPMode=0)
                for pole in paz['poles']:
                    nPCt += 1
                    nZPCt += 1
                    sComplex = str(pole)
                    Pole.objects.create(sensor_info=addSensor_info,fReal=pole.real,fImag=pole.imag,sComplex =sComplex,nZPMode=1)
                addSensor_info.ZeroNum = nZCt
                addSensor_info.PoleNum = nPCt
                addSensor_info.save()
            else:
                print("addSensor_info %s-%s-%s is not existed, cann't add!" % (move['Model'],move['Sensitivity_info'],move['Frequency_info']))
        else:
            print("sensor=%s is not existed, cann't add!" %  move['Model'])
    else:
        print("company=%s is not existed, cann't add!" % (move['Manufacturer']))
    print('Stage 4  :  Adding Sensor OK!   , nSensorCt=%d, nSensorInfoCt=%d, nZPCt=%d' % (nSensorCt, nSensorInfoCt, nZPCt))

# 从各厂家仪器Dataless文件中，获取仪器基本信息
def FindDigitizerFirst(Name = 'all'):
    Company_list = FindCompany_list(Name)
    if (len(Company_list)==0):  # list 无元素
        return

    STATIC_PATH = os.path.join(os.path.dirname(__file__), 'static')
    # 生成 'instruments'、'instruments\\digitizer' 目录
    sDenDir = 'instruments'
    fDenDir = os.path.join(STATIC_PATH, sDenDir)
    mkfile(fDenDir, 0)
    sDenDir = 'instruments\\digitizer'
    fDenDir = os.path.join(STATIC_PATH, sDenDir)
    mkfile(fDenDir, 0)

    nCompany = 0
    movies = []  # 将所有的仪器集合到一起，并排序
    ListV_title_list = []
    for company in Company_list:
        fSrcDir = "resource\\IRIS\\dataloggers\\" + company.Name
        print('Stage 1    : Processing Company = %d, Company=%s ...',company.Name)        #  第一级厂商，标识处理
        fSrcDir = os.path.join(STATIC_PATH, fSrcDir)

        listV_title1 = ['Manufacturer', 'Model', 'RESP Filename','Gain','Sensitivity',        'Sample Rate',                            ]
        #daq_dataloggers_daq24usbxr
        listV_title2 = ['Manufacturer', 'Model', 'RESP Filename','Gain','Full Scale Voltage', 'Sample Rate',                            'Filter Phase Type']
        #TAIDE              "Manufacturer  Model  Gain  Full Scale Voltage  Sample Rate  Filter Phase Type  RESP Filename"
        #GeoDevice          "Manufacturer  Model  Gain  Full Scale Voltage  Sample Rate  Filter Phase Type  RESP Filename"
        listV_title3 = ['Manufacturer', 'Model', 'RESP Filename','Gain','Full Scale Voltage', 'Sample Rate',  ]
        #eentec_dr4000_dataloggers
        listV_title4 = ['Manufacturer', 'Model', 'RESP Filename','Gain', 'Input Range',       'Primary Sample Rate','Final Sample Rate', 'Final Filter Phase']
        #geotech_smart24_dataloggers    Filter type = Linear/Minimum
        listV_title5 = ['Manufacturer', 'Model', 'RESP Filename','Gain',  'Input Range',      'Sample Rate',                             'Filter Type']
        #kinemetrics_etna2_dataloggers, Filter type = Causal/Non-causal
        #kinemetrics_rock_dataloggers         "Manufacturer  Model  Gain  Input Range  Sample Rate  Filter Type  RESP Filename  Source  Comments"
        listV_title6 = ['Manufacturer', 'Model', 'RESP Filename','Input Range (Gain)',        'Sample Rate',                             'IIR DC Filter Corner','Final Filter Phase']
        #nanometrics_titan_SMA_EA_dataloggers
        #nanometrics_meridian_posthole_dataloggers
        #nanometrics_centaur_dataloggers
        listV_title7 = ['Manufacturer', 'Model', 'RESP Filename', 'Input Range (Gain)',       'Sample Rate',                             'IIR DC Filter Corner']
        # nanometrics_HRD24_dataloggers"Manufacturer  Model  Gain  Sample Rate  IIR DC Filter Corner  RESP Filename  Source  Comments"
        # nanometrics_europat_trident_dataloggers"Manufacturer  Model  Gain  Sample Rate  IIR DC Filter Corner  RESP Filename  Source  Comments"
        #seismic_source_ADS1282_dataloggers      "Manufacturer  Model  Gain  Sample Rate  IIR DC Filter Corner  RESP Filename"
        listV_title8 = ['Manufacturer', 'Model', 'RESP Filename', 'Gain', 'Input Range',      'Sample Rate']
        #lunitek_sentinel_dataloggers         "Manufacturer  Model  Digitizer  Gain  Input Range  Sample Rate  RESP Filename  Source  Comments"
        #geobit_sri32sng_dataloggers
        listV_title9 = ['Manufacturer','Model', 'RESP Filename', 'Gain',                     'Sample Rate'                              ,'Linear Filters','Firmware Date']
        #quanterra_Q330Splus_dataloggers        "Manufacturer  Model  Gain  Sample Rate  Linear Filters  Firmware Date  RESP Filename"
        listV_title10 = ['Manufacturer','Model', 'RESP Filename', 'Gain',                     'Sample Rate',                              'Filter Type']
        #kinemetrics_makalu_dataloggers       "Manufacturer  Model  Gain  Sample Rate  Filter Type  RESP Filename  Source  Comments"
        listV_title11 = ['Manufacturer','Model', 'RESP Filename', 'Gain',                     'Sample Rate',                              'channel']
        #quanterra_QEP_dataloggers             "Manufacturer  Model  Channel  Sample Rate  RESP Filename  "
        listV_title12 = ['Manufacturer','Model', 'RESP Filename', 'Gain',                     'Sample Rate']
        #agecodagis_kephren_dataloggers
        #earthdata_PS6_24_dataloggers
        #eqmet_sma_dataloggers
        #kinemetrics_etna_dataloggers         "Manufacturer  Model  Gain  Sample Rate  Filter Type  RESP Filename  Source  Comments"
        #kinemetrics_k2_dataloggers           "Manufacturer  Model  Gain  Sample Rate  Filter Type  RESP Filename  Source  Comments"
        #reftek_72A08_1stream                 "Manufacturer  Model    Gain  All Streams (Hz)  Sample Rate  RESP Filename"
        #reftek_125a_dataloggers              "Manufacturer  Model  Gain  Sample Rate  RESP Filename"
        #sercel_slimwave_dataloggers          "Manufacturer  Model  Gain  Sample Rate  RESP Filename"
        #solgeo_DYMAS24_dataloggers           "Manufacturer  Model  Gain  Sample Rate  RESP Filename"
        #omnirecs_datacube_dataloggers        "Manufacturer  Model  Gain  Sample Rate  RESP Filename"
        #osop_dataloggers                     "Manufacturer  Model  Gain  Sample Rate  RESP Filename"
        listV_title13 = ['Manufacturer', 'Model','RESP Filename', 'Preamp Gain',              'Sample Rate']
        #quanterra_Q412x_dataloggers"Manufacturer  Model  Preamp Gain  Sample Rate  RESP Filename"
        #quanterra_Q730_dataloggers "Manufacturer  Model  Preamp Gain  Sample Rate  RESP Filename"
        #quanterra_Qx80_dataloggers"Manufacturer  Model  Preamp Gain  Sample Rate  Firmware Version  RESP Filename
        ListV_title_list.append(listV_title1)
        ListV_title_list.append(listV_title2)
        ListV_title_list.append(listV_title3)
        ListV_title_list.append(listV_title4)
        ListV_title_list.append(listV_title5)
        ListV_title_list.append(listV_title6)
        ListV_title_list.append(listV_title7)
        ListV_title_list.append(listV_title8)
        ListV_title_list.append(listV_title9)
        ListV_title_list.append(listV_title10)
        ListV_title_list.append(listV_title11)
        ListV_title_list.append(listV_title12)
        ListV_title_list.append(listV_title13)

        ListV_title = []

        if (mkfile(fSrcDir, 2)):  # 如果目录存在，搜索
            sDenDir = 'instruments\\digitizer\\' + company.Name
            nFile = 0
            for fName in all_files(fSrcDir, "*.html"):  # 遍历该目录下的每一个html文件
                print('Stage 1     : Parser html %d, html=%s ...'% (nFile, fName))   # 第二级html文件，标识处理
                f = open(fName, "rt")
                rd = f.read()
                f.close()
                # 解析html文件的表头
                soup = BeautifulSoup(rd,"lxml")
                #soup = BeautifulSoup(rd, "html5lib")
                tr_all = soup.find_all('tr')
                tr0 = tr_all[0:1]
                if (tr0 == []):  # 未解析表结构则退出该遍历
                    print('No Table is found in File',fName)
                    continue
                info0 = list(tr0[0].stripped_strings)

                #print(info0)
                # info0 = list(tr0[0].strings)
                nSelMode = 1
                for i in range(13):
                    bInV = True
                    ListV_title = ListV_title_list[i]
                    for ListV in ListV_title:
                        if (ListV not in info0):
                            #print(ListV,ListV_title,info0)
                            bInV = False
                            break  # False 的话，则直接退出for循环，当前模式不对
                    if (bInV):      #在当前模式内
                        break       #搜索结束，退出
                    else:
                        nSelMode += 1

                print(nSelMode,ListV_title)
                if (len(ListV_title)!=0 and nSelMode<=13):       #  有数据
                    listV_index = []
                    nIndexMax = 0
                    for ListV in ListV_title:
                        Index = info0.index(ListV)
                        if (Index>nIndexMax):
                            nIndexMax = Index
                        listV_index.append(Index)
                        #print(listV_index)

                    # 解析html文件的表内容
                    for tr in tr_all[1:]:
                        move = {}
                        infos = list(tr.stripped_strings)
                        if (len(infos)<nIndexMax):      # 防止解析不到数据，数组超界错误
                            continue
                        #print(tr.stripped_strings,infos)
                        # infos = list(tr.strings)
                        move['Manufacturer'] = company.Name  # infos[listV_index[0]]
                        move['Model'] = re.sub(r"[\/\\\:\*\?\"\<\>\|\,\;\ \+\&]", '_', infos[listV_index[1]]).strip()
                        move['RESP Src Filename'] = os.path.join(fSrcDir, infos[listV_index[2]]).strip()

                        if nSelMode==1:
                            #listV_title1 = ['Manufacturer', 'Model', 'RESP Filename','Gain','Sensitivity','Sample Rate']
                            if (infos[listV_index[3]]=='1'):
                                move['gain'] = infos[listV_index[4]]
                            else:
                                move['gain'] = infos[listV_index[4]] + 'G' + infos[listV_index[3]]
                            move['Sample Rate'] = infos[listV_index[5]]
                            move['Filter'] = '----'                        
                        elif nSelMode==2:
                            #listV_title2 = ['Manufacturer', 'Model', 'RESP Filename','Gain','Full Scale Voltage', 'Sample Rate',                            'Filter Phase Type']
                            if (infos[listV_index[3]]=='1'):
                                move['gain'] = infos[listV_index[4]]
                            else:
                                move['gain'] = infos[listV_index[4]] + 'G' + infos[listV_index[3]]
                            move['Sample Rate'] = infos[listV_index[5]]
                            move['Filter'] = infos[listV_index[6]]
                        elif nSelMode==3:
                            #listV_title3 = ['Manufacturer', 'Model', 'RESP Filename','Gain','Full Scale Voltage', 'Sample Rate',  ]
                            if (infos[listV_index[3]]=='1'):
                                move['gain'] = infos[listV_index[4]]
                            else:
                                move['gain'] = infos[listV_index[4]] + 'G' + infos[listV_index[3]]
                            move['Sample Rate'] = infos[listV_index[5]]
                            move['Filter'] = '----'
                        elif nSelMode==4:
                            #listV_title4 = ['Manufacturer', 'Model', 'RESP Filename','Gain', 'Input Range',       'Primary Sample Rate','Final Sample Rate', 'Final Filter Phase']
                            if (infos[listV_index[3]]=='1'):
                                move['gain'] = infos[listV_index[4]]
                            else:
                                move['gain'] = infos[listV_index[4]] + 'G' + infos[listV_index[3]]
                            move['Sample Rate'] = 'P' + infos[listV_index[5]] + '-F' + infos[listV_index[6]]
                            move['Filter'] = infos[listV_index[7]]
                        elif nSelMode==5:
                            #listV_title5 = ['Manufacturer', 'Model', 'RESP Filename','Gain',  'Input Range',      'Sample Rate',                             'Filter Type']
                            if (infos[listV_index[3]]=='1'):
                                move['gain'] = infos[listV_index[4]]
                            else:
                                move['gain'] = infos[listV_index[4]] + 'G' + infos[listV_index[3]]
                            move['Sample Rate'] = infos[listV_index[5]]
                            move['Filter'] = infos[listV_index[6]]
                        elif nSelMode==6:
                            #listV_title6 = ['Manufacturer', 'Model', 'RESP Filename','Input Range (Gain)',        'Sample Rate',                             'IIR DC Filter Corner','Final Filter Phase']
                            move['gain'] =  infos[listV_index[3]]
                            move['Sample Rate'] = infos[listV_index[4]]
                            if (infos[listV_index[5]]=='Off'):
                                move['Filter'] = infos[listV_index[6]]
                            else:
                                move['Filter'] = 'LF' + infos[listV_index[5]] + 'HF' + infos[listV_index[6]]
                        elif nSelMode==7:
                            #listV_title7 = ['Manufacturer', 'Model', 'RESP Filename', 'Input Range (Gain)', 'Sample Rate',                          'IIR DC Filter Corner']
                            move['gain'] =  infos[listV_index[3]]
                            move['Sample Rate'] = infos[listV_index[4]] 
                            move['Filter'] = infos[listV_index[5]]
                        elif nSelMode==8:
                            #listV_title8 = ['Manufacturer', 'Model', 'RESP Filename', 'Gain', 'Input Range', 'Sample Rate']
                            if (infos[listV_index[3]]=='1'):
                                move['gain'] = infos[listV_index[4]]
                            else:
                                move['gain'] = infos[listV_index[4]] + 'G' + infos[listV_index[3]]
                            move['Sample Rate'] = infos[listV_index[5]]
                            move['Filter'] = '----'
                        elif nSelMode==9:
                            #listV_title9 = ['Manufacturer', 'Model', 'RESP Filename', 'Gain', 'Sample Rate',                                        'Linear Filters', 'Firmware Date']
                            move['gain'] =  infos[listV_index[3]]
                            move['Sample Rate'] = infos[listV_index[4]] 
                            move['Filter'] =  infos[listV_index[5]] + 'F' + infos[listV_index[6]]
                        elif nSelMode==10:
                            #listV_title10 = ['Manufacturer', 'Model', 'RESP Filename', 'Gain', 'Sample Rate', 'Filter Type']
                            move['gain'] =  infos[listV_index[3]]
                            move['Sample Rate'] = infos[listV_index[4]] 
                            move['Filter'] =  infos[listV_index[5]]
                        elif nSelMode==11:
                            #listV_title11 = ['Manufacturer', 'Model', 'RESP Filename', 'Gain', 'Sample Rate', 'channel']
                            move['gain'] =  infos[listV_index[3]]
                            move['Sample Rate'] = infos[listV_index[4]] 
                            move['Filter'] =  infos[listV_index[5]]
                        elif nSelMode==12:
                            #listV_title12 = ['Manufacturer', 'Model', 'RESP Filename', 'Gain', 'Sample Rate']
                            move['gain'] =  infos[listV_index[3]]
                            move['Sample Rate'] = infos[listV_index[4]] 
                            move['Filter'] = '----'
                        elif nSelMode==13:
                            #listV_title13 = ['Manufacturer', 'Model', 'RESP Filename', 'Preamp Gain', 'Sample Rate']
                            move['gain'] =  infos[listV_index[3]]
                            move['Sample Rate'] = infos[listV_index[4]] 
                            move['Filter'] = '----'

                        move['gain'] = re.sub(r"[\ ]", '',move['gain']).strip()
                        move['Sample Rate'] = re.sub(r"[\ ]", '',move['Sample Rate']).strip()
                        move['Filter'] = re.sub(r"[\ ]", '',move['Filter']).strip()

                        move['del_flag'] = False  #默认不删除
                        move['add_flag'] = True   #默认添加digitizer_base
                        move['add_flag_gain'] = True   #默认添加digitizer_base
                        move['add_flag_gain_rate'] = True   #默认添加digitizer_base

                        fDenDir = os.path.join(STATIC_PATH, sDenDir)          # 绝对路径+ 'instruments\\digitizer\\' + company.Name
                        move['sAbsDenDir'] = fDenDir + '\\' + move['Model']   # 绝对路径+ 'instruments\\digitizer\\' + company.Name + '\\' + move['Model']
                        if (move['Filter']=='----'):
                            move['sFileHeadName'] = company.Name + '_' + move['Model'] + '_' + move['gain'] + '_' + move['Sample Rate']
                        else:
                            move['sFileHeadName'] = company.Name + '_' + move['Model']  + '_' + move['gain'] + '_' + move['Sample Rate'] + '_' + move['Filter']
                        move['sFileHeadName'] = re.sub(r"[\/\\\:\*\?\"\<\>\|\,\;\ \+\&]", '_',move['sFileHeadName']).strip()

                        move['sAbsDenFile'] = move['sAbsDenDir'] + '\\' + move['sFileHeadName'] + '.resp'
                        move['sDenDir'] =    sDenDir + '\\' + move['Model']   # 相对路径
                        move['sDenFile'] =    move['sDenDir'] + '\\' + move['sFileHeadName']

                        movies.append(move)
                else:
                    # print(fName)
                    print(fName,":"  +  "is bad Info")
                    print(info0)
                    pass
                nFile += 1
        else:
            #print('dir'+fSrcDir+'is not existed!')
            pass
        nCompany += 1
    # print(movies)
    print('Stage 1    : Process Company=%d, Success=%d.  \n\n' % (nCompany,len(movies)))

    # 删除movies list中 model错误，文件不存在的内容
    print('Stage 2    : Reorganize Company Info...')
    for move in movies:
        bFindFile = mkfile(move['RESP Src Filename'], 2)
        if (move['Model'] == 'Model' or bFindFile == False):  # 名字叫Model 肯定是错的
            if (bFindFile == False):
                print('File', move['RESP Src Filename'], 'is not found!')
                print('move is', move)
            movies.remove(move)

    # 剔除movies list中 model+Freq+Sensitivity 全部相同的内容
    # movies list中 model相同的内容，其新model为model+Freq+Sensitivity 不重复 digitizer_base
    nIndex = 0
    for move1 in movies:
        nIndex += 1
        for move2 in movies[nIndex:]:
            # 同名、同增益、同采样率、同滤波器的设备，删后一个
            if (move1['Model'] == move2['Model']
                and move1['gain'] == move2['gain']
                and move1['Sample Rate'] == move2['Sample Rate']
                and move1['Filter'] == move2['Filter']
                and not move1['del_flag']):
                move2['del_flag'] = True
            # 同名、同增益、同采样率的设备，后一个不加digitizer_info2，仅仅加digitizer_info3
            elif (move1['Model'] == move2['Model'] and not move1['del_flag']
                and move1['gain'] == move2['gain']
                and move1['Sample Rate'] == move2['Sample Rate']):
                    move2['add_flag'] = False
                    move2['add_flag_gain'] = False
                    move2['add_flag_gain_rate'] = False
            # 同名、同增益的设备，后一个不加digitizer_info1，仅仅加digitizer_info2
            elif (move1['Model'] == move2['Model'] and not move1['del_flag']
                and move1['gain'] == move2['gain']):
                    move2['add_flag'] = False
                    move2['add_flag_gain'] = False
            # 同名的设备，后一个不加digitizer_base，仅仅加digitizer_info1
            elif (move1['Model'] == move2['Model'] and not move1['del_flag']):
                move2['add_flag'] = False
    nDelNum = 0
    nTtNum = 0
    nMainNum1 = nMainNum2 = nMainNum3 = 0
    for move in movies:
        if move['del_flag']:
            movies.remove(move)     # print(move)
            nDelNum += 1
        else:
            if move['add_flag']:
                nMainNum1 += 1
            if move['add_flag_gain']:
                nMainNum2 += 1
            if move['add_flag_gain_rate']:
                nMainNum3 += 1
            nTtNum += 1
    print('Stage 2    : Data size is %d,Delete Error Digitizer=%d,Main Model=%d, gain =%d, rate = %d, Total=%d\n\n' % (len(movies),nDelNum,nMainNum1,nMainNum2,nMainNum3,nTtNum))

    # 添加Digitizer 数据库
    nDigitizerCt = 0
    nDigitizerInfoCt = 0
    print('Stage 3    : Processing  Add Digitizer...')
    for move in movies:
        #print(move)
        mkfile(move['sAbsDenDir'], 0)  # 生成digitizer\厂家目录
        print(move['sAbsDenDir'])
        SelCompany = Company.objects.filter(Name=move['Manufacturer'])
        print(SelCompany[0])
        if (len(SelCompany) != 0):  # 仅当厂家存在时才可添加，厂家不存在，不能添加
            if (move['add_flag']):      #add_flag 则添加 Digitizer
                addDigitizer = Digitizer_base.objects.filter(Name=move['Model'], ICompany=SelCompany[0])
                if (len(addDigitizer) == 0):    #不能轻易删除Digitizer
                    print('Stage 3.1  :  Add Digitizer Main Model=%d, %s-%s...' % (nDigitizerCt, SelCompany[0].Name, move['Model']))
                    obj, created = Digitizer_base.objects.get_or_create(Name=move['Model'],
                                           ICompany=SelCompany[0],IDir=move['sDenDir'],IMainType=4000)
                    if (created):
                        obj.save()
                else:
                    print('Stage 3.1  :  Modified Digitizer Num=', nDigitizerCt,SelCompany[0].Name, move['Model'])
                    addDigitizer[0].IDigitizerDir=move['sDenDir']
                    addDigitizer[0].save()
                nDigitizerCt += 1

            SelDigitizer = Digitizer_base.objects.filter(Name=move['Model'], ICompany=SelCompany[0])
            if (len(SelDigitizer) != 0):  # 不能轻易删除Digitizer
                if (move['add_flag_gain']):  # add_flag_rate 则添加  Digitizer_rate
                    addDigitizerGain = Digitizer_gain.objects.filter(Digitizer=SelDigitizer[0],Gain=move['gain'])
                    if (len(addDigitizerGain) == 0):  # 不能轻易删除Digitizer_gain
                        print('Stage 3.1.1  :  Add Digitizer_gain, Main Model=%d, %s-%s-%s'
                              % (nDigitizerCt, SelCompany[0].Name, move['Model'], move['gain']))
                        obj, created = Digitizer_gain.objects.get_or_create(Digitizer=SelDigitizer[0],Gain=move['gain'])
                        if (created):
                            obj.save()

                SelGain = Digitizer_gain.objects.filter(Gain=move['gain'],Digitizer=SelDigitizer[0])
                if (len(SelGain) != 0):  # 不能轻易删除Digitizer
                    if (move['add_flag_gain_rate']):  # add_flag_rate 则添加  Digitizer_rate
                        addRate = Digitizer_rate.objects.filter(DigitizerGain = SelGain[0],Rate = move['Sample Rate'])
                        if (len(addRate) == 0):  # 不能轻易删除Digitizer_gain
                            print('Stage 3.1.1.1:  Add Digitizer_rate, Main Model=%d, %s-%s-%s-%s'
                                  % (nDigitizerCt, SelCompany[0].Name, move['Model'], move['gain'],move['Sample Rate']))
                            obj, created = Digitizer_rate.objects.get_or_create(DigitizerGain=SelGain[0],Rate=move['Sample Rate'])
                            if (created):
                                obj.save()

                    # 复制文件
                    if (not mkfile(move['sAbsDenFile'], 2)):  # 文件不存在就复制文件
                        cmd = 'copy ' + move['RESP Src Filename'] + ' ' + move['sAbsDenFile']
                        print(cmd)
                        os.system(cmd)
                    print('Stage 3.2  :  Parsering response File  Num= ', nDigitizerInfoCt, SelCompany[0].Name,
                          move['Model'],move['gain'], move['Sample Rate'], move['Filter'])
                    sDir = os.path.join(STATIC_PATH, move['sDenFile'])
                    sName = SelCompany[0].ChnName + ' ' + move['Model'] + ' '  + move['gain'] + ' ' + move['Sample Rate']
                    if (move['Filter'] != '----'):
                        sName = sName + ' ' + move['Filter']
                    #if (not mkfile(sDir + '.freq_amp.png',2)):
                    (sample_rate, sensitivity) = parser_digitizer_resp(sDir, sName)
                    SelRate = Digitizer_rate.objects.filter(DigitizerGain=SelGain[0],Rate=move['Sample Rate'])
                    Digitizer_filter.objects.filter(DigitizerRate=SelRate[0], Filter=move['Filter']).delete()
                    addDigitizer_filter, created = Digitizer_filter.objects.get_or_create(DigitizerRate=SelRate[0],
                                            Filter=move['Filter'],IParUrl=move['sDenFile'],
                                            rate=sample_rate,sensitivity=sensitivity)
                    if (created):
                        nDigitizerInfoCt += 1
                        print('Stage 3.3    :  Add Digitizer_rate, Main Model=%d, %s-%s-%s-%s-%s'
                              % (nDigitizerCt, SelCompany[0].Name, move['Model'], move['gain'], move['Sample Rate'],move['Filter']))
                    else:       # filter add error !
                        print("addDigitizer_filter %s-%s-%s-%s-%s is not existed, cann't add!"
                              % (SelCompany[0].Name, move['Model'], move['gain'], move['Sample Rate'],move['Filter']))
                else:  # Gain add error !    
                    print("SelGain %s-%s-%s-%s is not existed, cann't add!"
                          % ( SelCompany[0].Name, move['Model'], move['gain'], move['Sample Rate']))
            else:
                print("SelDigitizer %s-%s-%s-%s is not existed, cann't add!"
                          % ( SelCompany[0].Name, move['Model'], move['gain'], move['Sample Rate']))
        else:
            print("SelCompany %s-%s-%s-%s is not existed, cann't add!"
                      % ( SelCompany[0].Name, move['Model'], move['gain'], move['Sample Rate']))
    else:
        print("company=%s is not existed, cann't add!" % (move['Manufacturer']))
    print('Stage 4  :  Adding Digitizer OK!   , nDigitizerCt=%d, nDigitizerInfoCt=%d' % (nDigitizerCt, nDigitizerInfoCt))

def AddInstFirstAll():
    AddNationalFirst()
    AddCompanyFirst()
    FindSensorsFirst('all')
    FindDigitizerFirst('all')

