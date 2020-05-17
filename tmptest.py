#_*_coding=utf-8 _*_

import psutil
import time
import matplotlib.dates
import matplotlib.pyplot as plt
def cpu_count():
    print('-----------------------------cpu信息---------------------------------------')
    print(u"物理CPU个数: %s" % psutil.cpu_count(logical=False))
    print(u"CPU核心总数: %s" % psutil.cpu_count())
    cpu1=psutil.cpu_percent(1)
    cpu = (str(cpu1))+ '%'
    sys=time.localtime(time.time())
    sys_time = time.strftime("%H:%M:%S",sys)
    print(u"cup使用率: %s" % cpu)
    cpu_list=["cup使用率",cpu1,sys_time]
    return cpu_list
def a():
    while 1:
        yield cpu_count()
if __name__=="__main__":
    fig=plt.figure(figsize=(10,5))
    plt.xlabel("time")
    plt.xticks(rotation=60)
    plt.ylim(0,100)
    plt.yticks([a for a in range(101) if a%5==0])
    plt.ylabel("data")
    plt.title("test")
    plt.grid(True) #添加网格
    plt.ion()  #interactive mode on
    try:
        while 1:
            data = next(a())
            plt.plot(data[2],data[1],linewidth = '1', label = "cpu",marker = 'o')
            plt.pause(0.1)
    except Exception as e:
        plt.ioff()
    plt.show()