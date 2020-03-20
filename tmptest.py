# -*- coding: utf-8 -*-
import datetime
import os
import configparser


def show_path(path, all_path):
    file_list = os.listdir(path)
    for file in file_list:
        file = os.path.join(os.path.abspath(path), file)
        if os.path.isfile(file):
            all_path.append(file)
        elif os.path.isdir(file):
            show_path(file, all_path)


def newCalFile(ini_path, all_path, inoutfiles):
    del_flag = False
    min_time = 4102415999 #2099-12-31 23:59:59
    if not os.path.exists(ini_path):
        open(ini_path, 'w')
    cf = configparser.ConfigParser()
    cf.read(ini_path)
    start_time = cf.getfloat('TIME_START', 'timestamp')
    for file in all_path:
        mtime = os.path.getmtime(file)
        if len(file.split('.')) > 3 and mtime >= start_time:
            calName = file.split('.')[-1]
            chnName = file.split('.')[-3]
            if cf.has_option(calName, chnName):
                if cf.getfloat(calName, chnName) == mtime:
                    outfile = 'Pulse_' + chnName + '.png'
                    inoutfiles.append((file, os.path.join(os.path.dirname(file), outfile), chnName))
                    cf.remove_option(calName, chnName)
                    continue
            if not cf.has_section(calName):
                cf.add_section(calName)
                if not cf.has_option(calName, chnName):
                    cf.set(calName, chnName, str(mtime))
            else:
                if not cf.has_option(calName, chnName):
                    cf.set(calName, chnName, str(mtime))
            cf.set(calName, chnName, str(mtime))
            if mtime < min_time:
                min_time = mtime
    if min_time != 4102415999:
        cf.set('TIME_START', 'timestamp', str(min_time))
            # if del_flag:
            #     cf.remove_section(calName)
            #     del_flag = False
    cf.write(open(ini_path, 'w'))


def timeInit(ini_path):
    now = datetime.datetime.timestamp(datetime.datetime.now())
    cf = configparser.ConfigParser()
    cf.read(ini_path)
    if not cf.has_section('TIME_START'):
        cf.add_section('TIME_START')
    if not cf.has_option('TIME_START', 'timestamp'):
        cf.set('TIME_START', 'timestamp', str(now - 60))
        cf.write(open(ini_path, 'w'))

all_path = []
inoutfiles = []
show_path('D:/django/trunk/cal_data', all_path)
timeInit('caltime.ini')
newCalFile('caltime.ini', all_path, inoutfiles)
print(inoutfiles)
