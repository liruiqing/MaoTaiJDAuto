# -*- coding:utf-8 -*-
import time
from datetime import datetime
from jdlogger import logger
from config import global_config

class Timer(object):
    def __init__(self, sleep_interval=0.5):
        # '2018-09-28 22:45:50.000'
        self.buy_time = datetime.strptime(global_config.getRaw('config','buy_time'), "%Y-%m-%d %H:%M:%S.%f")

        print(self.buy_time)
        print(type(self.buy_time))
        self.sleep_interval = sleep_interval

        date_today = datetime.now().date()
        date_today_str = str(date_today) + " "
        # print(date_today_str)
        date_today_str = date_today_str + "10:00:00.100000"
        # print(date_today_str)

        self.buy_time = datetime.strptime(date_today_str, "%Y-%m-%d %H:%M:%S.%f")
        # print(self.buy_time)



    def start(self):
        logger.info('正在等待到达设定时间:%s' % self.buy_time)
        now_time = datetime.now
        print(now_time())
        while True:
            if now_time() >= self.buy_time:
                logger.info('时间到达，开始执行……')
                break
            else:
                time.sleep(self.sleep_interval)
