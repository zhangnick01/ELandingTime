# -*- coding: utf-8 -*-
# author：zhangnick time:2018/9/4
# function: 预测落地时间
import sys
import os
import tensorflow as tf
from datetime import datetime
import settings
import time

# tensorflow 输出日志级别
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def check(pnum,value):
    """
        检查输入参数是否在限定范围,并做归一化
    :param pnum:  1 经度 2 纬度 3 高度 4 速度 5 跑道
    :param value: 数值
    :return: 归一化返回值 检查失败则返回 0
    """
    if pnum == 1:
        if value > settings.LNG_BEGIN and value < settings.LNG_END:
            return round((value - settings.LNG_BEGIN)/(settings.LNG_END - settings.LNG_BEGIN),4)
    if pnum == 2:
        if value > settings.LAT_BEGIN and value < settings.LAT_END:
            return round((value - settings.LAT_BEGIN)/(settings.LAT_END - settings.LAT_BEGIN),4)
    if pnum == 3:
        if value > settings.HIGH_BEGIN and value < settings.HIGH_END:
            return round(value/settings.HIGH_END,4)
    if pnum == 4:
        if value > settings.SPEED_BEGIN and value < settings.SPEED_END:
            return round(value/settings.SPEED_END,4)
    if pnum == 5:
        if value == settings.RUNWAY_E or value == settings.RUNWAY_W:
            return round(value/36,2)

    return 0

def predata(data_list):
    """
        对模型输入参数归一化
        参数：0 经度 1 纬度 2 高度 3 速度 4 跑道
    :return:经度、纬度、高度、速度、方位角、跑道、机场经度、机场纬度、机场标高
    """
    lng = check(1,float(data_list[0]))
    lat = check(2,float(data_list[1]))
    high = check(3,float(data_list[2]))
    speed = check(4,float(data_list[3]))
    runway = check(5,float(data_list[4]))

    #参数输入有误则返回0
    if lng == 0 or lat == 0 or high == 0 or speed == 0 or runway == 0:
        return [[0]]
    # 机场坐标和标高归一化
    airport_lng = round((settings.AIRPORT_LNG - settings.LNG_BEGIN)/(settings.LNG_END - settings.LNG_BEGIN),4)
    airport_lat = round((settings.AIRPORT_LAT - settings.LAT_BEGIN) / (settings.LAT_END - settings.LAT_BEGIN), 4)
    airport_high = round(settings.AIRPORT_HIGH / settings.HIGH_END, 4)
    # 飞机方位角，暂未用
    vec = 0.0
    # 组装模型输入参数
    x_data = [[lng] + [lat] + [high] + [speed] + [vec]
              + [runway] + [airport_lng] + [airport_lat] + [airport_high]]
    return x_data

def pred(iproc,flag_dict,q):
    """
        预测落地时长
    :param q: [经度、纬度、速度、高度、跑道、接收时间、航班号]
    :return:
    """
    try:
        pred_filepath = settings.PRED_FILEPATH
        saver = tf.train.import_meta_graph(settings.MODELFILE)
        with tf.Session() as sess:
            # 加载模型
            saver.restore(sess,settings.MODELPATH)
            # 预测值
            final_output = tf.get_collection('pred_network')[0]
            # 模型输入特征
            graph = tf.get_default_graph()
            x_data = graph.get_operation_by_name('x_data').outputs[0]
            # 信号量为1时，无限循环读取队列中报文数据
            while flag_dict['run_flag'] == 1:
                try:
                    queue_output = q.get(True, timeout=settings.RQSLEEPTIME)
                    # 对模型参数预处理
                    x = predata(queue_output[0:5])
                    # 二次雷达报文接收时间
                    base_dt = queue_output[5]
                    # 模型参数归一化失败，则取下一条
                    if str(x[0][0]) == '0':
                        print('check is failed : ',queue_output)
                        continue
                    # 调用预测模型
                    # print('pre-begin:', datetime.now())
                    pv = sess.run(final_output, feed_dict={x_data: x})
                    # print('pre-end:', datetime.now())
                    # 拼接预测文件名称 前缀+日期+小时+进程名
                    predfile = pred_filepath + '_' + base_dt[0:8] + '_' + base_dt[9:11] +'_'+ iproc + '.txt'
                    with open(predfile,'a') as f:
                        f.write(str(pv[0][0])+','+str(queue_output)+'\n')
                except:
                    print(iproc,'-Warning\'s information', sys.exc_info()[0])
                    time.sleep(settings.CQSLEEPTIME)
    except:
        print(iproc, '-Error\'s information ', sys.exc_info()[0])