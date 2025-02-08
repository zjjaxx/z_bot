# coding:utf-8
import sys
import traceback
import os
import sys
import logbook
from logbook import Logger, StreamHandler, FileHandler

logbook.set_datetime_format('local')

class StrategyTemplate:
    name = 'DefaultStrategyTemplate'

    def __init__(self):
        self.logger=None
        self.init()
        self.initLogger( name='logInfo', log_type='file', filepath='./logger/info.log', loglevel='DEBUG')

    def initLogger(self, name='logInfo', log_type='stdout', filepath='logInfo.log', loglevel='DEBUG'):
        """Log对象
        :param name: log 名字
        :param :logtype: 'stdout' 输出到屏幕, 'file' 输出到指定文件
        :param :filename: log 文件名
        :param :loglevel: 设定log等级 ['CRITICAL', 'ERROR', 'WARNING', 'NOTICE', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
        :return log handler object
        """
        self.logger = Logger(name)
        if log_type == 'stdout':
            StreamHandler(sys.stdout, level=loglevel).push_application()
        if log_type == 'file':
            if os.path.isdir(filepath) and not os.path.exists(filepath):
                os.makedirs(os.path.dirname(filepath))
            file_handler = FileHandler(filepath, level=loglevel)
            self.logger.handlers.append(file_handler)

    def init(self):
        # 进行相关的初始化操作
        pass
    
    def strategy(self, event):
        """:param event event.data 为所有股票的信息，结构如下
        {'162411':
        {'ask1': '0.493',
         'ask1_volume': '75500',
         'ask2': '0.494',
         'ask2_volume': '7699281',
         'ask3': '0.495',
         'ask3_volume': '2262666',
         'ask4': '0.496',
         'ask4_volume': '1579300',
         'ask5': '0.497',
         'ask5_volume': '901600',
         'bid1': '0.492',
         'bid1_volume': '10765200',
         'bid2': '0.491',
         'bid2_volume': '9031600',
         'bid3': '0.490',
         'bid3_volume': '16784100',
         'bid4': '0.489',
         'bid4_volume': '10049000',
         'bid5': '0.488',
         'bid5_volume': '3572800',
         'buy': '0.492',
         'close': '0.499',
         'high': '0.494',
         'low': '0.489',
         'name': '华宝油气',
         'now': '0.493',
         'open': '0.490',
         'sell': '0.493',
         'turnover': '420004912',
         'volume': '206390073.351'}}
        """

    def run(self, event):
        try:
            self.strategy(event)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type,
                                                           exc_value,
                                                           exc_traceback)))

    def beforeOpen(self, event):
        pass

