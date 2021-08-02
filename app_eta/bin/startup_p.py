# -*- coding: utf-8 -*-
# author：zyan time:2018/9/4
# function: 获取空管自动化系统报文[0:"应答机编码"]
# [1:"经纬度"][2:"经纬度"][3:"高度"][4:"速度（马赫）"]
# [5:"方位角"][6:"三字码航班号"][7:"降落机场四字码"][8:"起飞机场四字码"]
# [9:"计划起飞时间"][10:"预计起飞时间"][11:"预计降落时间"]
# 调用预测模型，预测落地时间

from multiprocessing import queues
from multiprocessing import Manager
import multiprocessing
import sys,time
import get_udp
import pred_eta
import settings

# 创建队列,用于保存报文数据
q = queues.Queue(settings.QUEUENUM,ctx=multiprocessing)

def w_runflag(runflagfile):
    """
        将1写入信号量文件
    """
    with open(runflagfile,'w') as f:
        f.write('1')

def r_runflag(flag_dict,runflagfile):
    """
        每10秒读取记录是否执行的信号量文件
    :param flag_dict:信号量字典，在各个进程间共享
    :return:
    """
    # 等其他进程启动 5秒
    time.sleep(5)
    while True:
        try:
            with open(runflagfile,'r') as f:
                f_flag = f.read()
            if f_flag.rstrip('\n') == '0':
                flag_dict['run_flag'] = 0
                break
            else:
                time.sleep(settings.FWAITTIME)
        except:
            print('r1 Error read ',runflagfile,'-',sys.exc_info()[0])
            time.sleep(settings.FEWAITTIME)
def main():
    """
        主函数 单进程消费udp接口数据，并加入队列，多个进程消费队列，调用预测模型
    """
    m = Manager()
    # 信号量字典，在各个进程间共享
    flag_dict = m.dict({'run_flag': 1})
    print('begin:')
    # 启动时，将1写入信号量文件
    try:
        w_runflag(settings.RUNFLAG)
    except:
        print('Error: ', sys.exc_info()[0])
        print('Error write runflag file ')
        return 0
    # 进程r1,读取信号量文件
    r1 = multiprocessing.Process(target=r_runflag, args=(flag_dict,settings.RUNFLAG,))
    r1.start()
    print('r1 process started successfully! ')
    # 进程p1,获取雷达报文，加入队列
    p1 = multiprocessing.Process(target=get_udp.getudp, args=(flag_dict, q,))
    p1.start()
    print('p1 process started successfully! ')
    # 进程g1,读取队列，调用模型
    g1 = multiprocessing.Process(target=pred_eta.pred, args=('g1',flag_dict, q,))
    g1.start()
    print('g1 process started successfully! ')
    # 进程g2,读取队列，调用模型
    g2 = multiprocessing.Process(target=pred_eta.pred, args=('g2',flag_dict, q,))
    g2.start()
    print('g2 process started successfully! ')
    print('All processes started successfully! ')

    r1.join()
    print('r1-end!')
    p1.join()
    print('p1-end!')
    g1.join()
    print('g1-end!')
    g2.join()
    print('g2-end!')
    print('All processes is stoped successfully!')
if __name__ == '__main__':
    main()