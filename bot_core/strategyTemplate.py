# coding:utf-8
import sys
import traceback
import os
import sys
import logbook
from logbook import Logger, StreamHandler, FileHandler

from datetime import datetime,timedelta
from pybroker import Strategy, StrategyConfig, ExecContext
from pybroker.ext.data import AKShare
import akshare as ak
import requests
import json

logbook.set_datetime_format('local')

token="d37e7e9a1d4857e2457f107b973cb35a178649de1560b83689dfbe31057c29d4"
channel_id="963253371"
headers={
    'Authorization': 'Bearer '+token
}
url = 'http://127.0.0.1:5500/v1/message.create'
class StrategyTemplate:
    name = 'DefaultStrategyTemplate'

    def __init__(self):
        self.logger=None
        self.init()
        # 初始化日志
        self.initLogger( name='logInfo', log_type='stdout', filepath='./logger/info.log', loglevel='DEBUG')
        # 回溯
        # bootstrap_sample_size=100
        self.config = StrategyConfig()
        self.strategy = Strategy(
            data_source=AKShare(),
            start_date=datetime.now()-timedelta(days=365*2),
            end_date=datetime.now(),
            config=self.config)

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
    def queryStockData(self,symbol):
        stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=(datetime.now()-timedelta(days=365*2)).strftime('%Y%m%d'), end_date=datetime.now().strftime('%Y%m%d'), adjust="hfq")
        return stock_zh_a_hist_df
    
    # 千股千评
    def searchStock(self):
        df = ak.stock_comment_em()
        df = df[df["最新价"] < df["主力成本"]]
        # 2. 标准化指标
        # 综合得分：越高越好，直接标准化
        df["综合得分_标准化"] = (df["综合得分"] - df["综合得分"].min()) / (df["综合得分"].max() - df["综合得分"].min())

        # 目前排名：越低越好，反向标准化
        df["目前排名_标准化"] = 1 / df["目前排名"]

        # 3. 计算综合评分（权重均为 1/3）
        df["综合评分"] = (df["综合得分_标准化"] + df["目前排名_标准化"]) / 2

        # 4. 按综合评分降序排序，取前10只股票
        top_10 = df.sort_values(by="综合评分", ascending=False).head(10)
        return top_10

    def hot_stock(self):
        stock_hot_follow_xq_df = ak.stock_hot_follow_xq(symbol="最热门")
        return stock_hot_follow_xq_df.head(300)

    def beforeOpen(self, event):
        pass

    
    def convert_to_json(self,obj):
        # 判断是否是字符串
        if isinstance(obj, str):
            return obj  # 如果已经是字符串，直接返回
        else:
            return json.dumps(obj)  # 否则，转换为 JSON 字符串
        
    def send_message(self,message):
        try:
            requests.post(url, headers=headers,json={
                "channel_id":channel_id,
                "content":self.convert_to_json(message) 
            })
        except requests.exceptions.RequestException as e:
            # 捕获请求异常（例如连接错误，超时等）
            print(f"Request failed: {e}")
        
        except Exception as e:
            # 捕获其他异常
            print(f"An unexpected error occurred: {e}")

