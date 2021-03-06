# -*- coding: utf-8 -*-
# author：zhangnick
# function:参数配置
# version:1.0

#机场坐标
AIRPORT_LNG = 200.00
AIRPORT_LAT = 60.00
# 机场标高
AIRPORT_HIGH = 100
# 特征上下限
#经度(100,120)
LNG_BEGIN = 100.0
LNG_END = 120.0
# 纬度(30,50)
LAT_BEGIN = 30.0
LAT_END = 50.0
# 高度(100,10000)
HIGH_BEGIN = 100
HIGH_END = 10000
# 速度(200,1000)
SPEED_BEGIN = 200
SPEED_END = 1000
# 跑道
RUNWAY_E = 20.0
RUNWAY_W = 2.0
#模型元数据文件
MODELFILE = '/home/udp_project/app_eta/ckpt/model.meta'
MODELPATH = '/home/udp_project/app_eta/ckpt/model'

# 二次雷达接口信息
HOST = ''  # 主机名
PORT = 56115  # 端口号
BUFSIZE = 1024  # 缓冲区大小1K

# 二次雷达数据保存路径前缀
PRE_FILEPATH = '/home/udp_project/app_eta/sdata/source_'
# 预测文件保存路径
PRED_FILEPATH = '/home/udp_project/app_eta/tdata/pred_'

# 队列容量
QUEUENUM = 100

#UDP socket超时时间 秒
SOCKETTIMEOUT = 10

# 关闭进程的信号量文件
RUNFLAG = '/home/udp_project/app_eta/bin/run_flag.txt'

# 读取队列，等待超时时间 秒
RQSLEEPTIME = 5

# 加入队列，等待超时时间 秒
WQSLEEPTIME = 5

# 消费队列过程中异常时，休眠时间 秒
CQSLEEPTIME = 2

# 读取信号量文件时间间隔 秒
FWAITTIME = 10

# 读取信号量文件异常时，时间间隔 秒
FEWAITTIME = 3600