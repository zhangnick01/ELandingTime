# -*- coding: utf-8 -*-
# author：zyan time:2018/9/5

import settings

def w_runflag(runflagfile):
    """
        将0写入信号量文件
    """
    with open(runflagfile,'w') as f:
        f.write('0')

def main():
    w_runflag(settings.RUNFLAG)

if __name__ == '__main__':
    main()
