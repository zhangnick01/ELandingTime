# -*- coding: utf-8 -*-
# author：zhangnick01
# function: 获取空管自动化系统报文[0:"应答机编码"]
# [1:"经纬度"][2:"经纬度"][3:"高度"][4:"速度"]
# [5:"方位角"][6:"三字码航班号"][7:"降落机场四字码"][8:"起飞机场四字码"]
# [9:"计划起飞时间"][10:"预计起飞时间"][11:"预计降落时间"]
# 将 [1:"经纬度"][2:"经纬度"][3:"高度"][4:"速度"]插入队列
import socket
import time
import settings
import sys
from multiprocessing import queues
from multiprocessing import Manager
import multiprocessing

def chooserunway(lflag,row_list):
    """
        根据进出港航班的位置信息，判断当时落地跑道
    lflag:跑道
    row_list:二次雷达报文
    :return:
    """
    # 经度
    flight_lng = float(row_list[1])
    # 落场
    flight_in = row_list[7]
    # 起场
    flight_out = row_list[8]
    # 飞行高度
    flight_high = int(row_list[3])
    # 飞行速度
    flight_feed = int(row_list[4])
    # 方位角
    flight_angle = int(row_list[5])
    
    if (flight_in == 'ZBHH' or flight_out == 'ZBHH') and flight_high < 1800 :
        if 65 < flight_angle <= 80 and lflag != '08' and flight_lng < 111.81 and 200 < flight_feed < 500:
            lflag = '08'

        elif 245 < flight_angle <= 255 and lflag != '26' and flight_lng > 111.83 and 200 < flight_feed < 500:
            lflag = '26'
    return lflag

def getudp(flag_dict,q):
    """
        连接udp
    :return:
    """
    landing_flag = '00'
    file_list = []

    pre_filepath = settings.PRE_FILEPATH

    HOST = settings.HOST               #主机名
    PORT = settings.PORT               #端口号
    BUFSIZE = settings.BUFSIZE         #缓冲区大小1K
    ADDR = (HOST,PORT)

    udpSerSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSerSock.bind(ADDR)       #绑定地址到套接字
    # 设置udp socket超时时间
    udpSerSock.settimeout(settings.SOCKETTIMEOUT)
    # 接收报文记录总数
    i = 0
    j = 0
    # 生成文件的数量，j每隔1万条生成一个新文件
    k = 1

    while flag_dict['run_flag'] == 1:                 #信号量为1时，等待连接到来
        try:
            i += 1
            print('p1-Waiting for message ....'+str(i))
            data, addr = udpSerSock.recvfrom(BUFSIZE)          #接收UDP
            data =data.decode()
            out_data = data.split(',')
            # 接收时间
            rec_dt = time.strftime('%Y%m%d %H:%M:%S', time.localtime())

            # 报文异常
            if len(out_data) < 10:
                print('Input data is wrong:'+data)
                continue
            if out_data[7] !='ZBHH' and out_data[8] !='ZBHH':
                continue
            # 计算跑道
            landing_flag = chooserunway(landing_flag,out_data)
            # out_data.append(landing_flag)
            if out_data[7] == 'ZBHH':
                # 准备模型输入参数经度、纬度、速度、高度、跑道、接收时间、航班号
                queue_input = [float(out_data[1]),float(out_data[2]),
                               float(out_data[3]),float(out_data[4]),float(landing_flag),rec_dt,out_data[6]]
                # 将参数入队列
                q.put(queue_input, True, timeout=settings.WQSLEEPTIME)
                print('Queue\'s number is ',q.qsize())

            j += 1
            if j % 10000 == 0:
                k += 1
            filepath = pre_filepath + '_' + rec_dt[0:8] + '_' + str(k) + '.txt'

            # 将报文临时存储到列表
            file_list.append(str(j) + ',' + str(i) + ',' + rec_dt + ','+ data + ',' + landing_flag + '\n')

            # 每10条写入文件
            if len(file_list) == 10 :
                with open(filepath,'a') as f:
                    for row in file_list:
                        f.write(row)
                file_list.clear()

        except Exception:
            print('Waring: ',sys.exc_info()[0])

    udpSerSock.close()          #关闭服务器
