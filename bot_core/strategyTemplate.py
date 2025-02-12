# coding:utf-8
import sys
import traceback
import os
import sys
import logbook
from logbook import Logger, StreamHandler, FileHandler
from datetime import datetime,timedelta
from pybroker import Strategy, StrategyConfig
from pybroker.ext.data import AKShare
import akshare as ak
import requests
import numpy as np
import json

seachCount=50
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
        self.strategyContext = Strategy(
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
    # 龙虎榜
    def get_tiger(self):
        try:
            stock_lhb_detail_em_df = ak.stock_lhb_detail_em(start_date=(datetime.now()-timedelta(days=7)).strftime('%Y%m%d'), end_date=datetime.now().strftime('%Y%m%d'))
            tiger_stocks=stock_lhb_detail_em_df.head(seachCount)
            return tiger_stocks['代码'].to_numpy() 
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type,
                                                           exc_value,
                                                           exc_traceback)))  


    def strategy(self, event):
        pass

    def run(self, event):
        try:
            self.strategy(event)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type,
                                                           exc_value,
                                                           exc_traceback)))
    def queryStockHistoryData(self,symbol):
        try:
            stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=(datetime.now()-timedelta(days=365*2)).strftime('%Y%m%d'), end_date=datetime.now().strftime('%Y%m%d'), adjust="hfq")
            return stock_zh_a_hist_df
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type,
                                                           exc_value,
                                                           exc_traceback)))
    
    # 千股千评
    def searchStock(self):
        try:
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
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type,exc_value,exc_traceback)))
    # 机构评级
    def get_institute_recommend(self):
        try:
            stock_institute_recommend_df = ak.stock_institute_recommend(symbol="股票综合评级").head(seachCount)
            return stock_institute_recommend_df['股票代码'].to_numpy()   
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type,exc_value,exc_traceback)))
                                                                                                                                                                                                                                                                             
    def hot_stock(self):
        try:
            stock_hot_follow_xq_df = ak.stock_hot_follow_xq(symbol="最热门")
            hot_stocks=stock_hot_follow_xq_df.head(seachCount) 
            return hot_stocks['股票代码'].to_numpy()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type,exc_value,exc_traceback)))
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

    def seek_stock(self):
        hot_symbols=self.hot_stock()
        tiger_symbols=self.get_tiger()
        institute_recommend_symbols=self.get_institute_recommend()
        merged_symbols = np.unique(np.concatenate([hot_symbols,institute_recommend_symbols, tiger_symbols]))
        print("merged_symbols",merged_symbols)
        return merged_symbols

