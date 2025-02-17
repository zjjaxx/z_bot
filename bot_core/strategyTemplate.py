# coding:utf-8
import sys
import traceback
import os
import logbook
from logbook import Logger, StreamHandler, FileHandler
from datetime import datetime,timedelta
import pandas as pd
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

    def __init__(self,event_engine):
        self.logger=None
        self.event_engine=event_engine
        self.init()
        # 初始化日志
        self.initLogger( name='logInfo', log_type='file', filepath='./logger/info.log', loglevel='DEBUG')
        # 回溯
        # bootstrap_sample_size=100
     

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
            print(repr(traceback.format_exception(exc_type, exc_value,exc_traceback)))  

    def strategy(self, event):
        pass

    def run(self, event):
        try:
            self.strategy(event)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type,exc_value,exc_traceback)))
    
    # 股票2年历史数据
    def queryStockHistoryData(self,symbol):
        try:
            stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=(datetime.now()-timedelta(days=365*2)).strftime('%Y%m%d'), end_date=datetime.now().strftime('%Y%m%d'), adjust="hfq")
            return stock_zh_a_hist_df
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type,exc_value,exc_traceback)))
        
    # 股票2年历史数据
    def queryStockHistoryDataPolyfill(self,symbol):
        try:
            stock_zh_a_hist_df = ak.index_zh_a_hist(symbol=symbol, period="daily", start_date=(datetime.now()-timedelta(days=365*2)).strftime('%Y%m%d'), end_date=datetime.now().strftime('%Y%m%d'))
            return stock_zh_a_hist_df
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type,exc_value,exc_traceback)))
    
    # 机构评级推荐
    def get_institute_recommend(self):
        try:
            stock_institute_recommend_df = ak.stock_institute_recommend(symbol="股票综合评级").head(seachCount)
            return stock_institute_recommend_df['股票代码'].to_numpy()   
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type,exc_value,exc_traceback)))
    def generate_dynamic_bins(self,window_low, window_high, step=0.1):
        #"""根据窗口内的价格范围生成动态分箱"""
        min_price = np.floor(window_low * 10) / 10  # 向下取整到0.1的倍数
        max_price = np.ceil(window_high * 10) / 10   # 向上取整到0.1的倍数
        bins = np.arange(min_price, max_price + step, step)
        return bins    
    def apply_time_decay(self,volumes, decay_rate=0.03):
        #"""指数衰减权重（时间越近权重越高）"""
        n = len(volumes)
        decay_weights = np.exp(decay_rate * np.arange(n))  # 从旧到新：权重递增
        decay_weights = decay_weights / decay_weights.sum()  # 归一化
        return volumes * decay_weights
                                                                                                                                                                                                                                                  
    # 获利盘计算
    def get_profit_rate(self,df, window=120, step=0.1, decay_rate=0.05):
            profit_ratios = []
    
            for i in range(len(df)):
                if i < window:
                    profit_ratios.append(np.nan)
                    continue
                
                # 提取窗口数据
                window_data = df.iloc[i - window:i]
                window_close = window_data['close'].values
                window_low = window_data['low'].min()
                window_high = window_data['high'].max()
                window_vol = window_data['volume'].values
                
                # 动态生成分箱
                bins = self.generate_dynamic_bins(window_low, window_high, step)
                
                # 应用时间衰减后的成交量
                decayed_vol = self.apply_time_decay(window_vol, decay_rate)
                
                # 统计每个分箱的累计成交量
                bin_vol = np.zeros(len(bins) - 1)  # 分箱区间数
                for price, vol in zip(window_close, decayed_vol):
                    bin_idx = np.digitize(price, bins) - 1
                    if 0 <= bin_idx < len(bin_vol):
                        bin_vol[bin_idx] += vol
                
                # 计算获利盘比例
                current_price = df.iloc[i]['close']
                lower_bins = bins[:-1] < current_price  # 当前价格以下的区间
                profitable_vol = bin_vol[lower_bins].sum()
                total_vol = bin_vol.sum()
                
                ratio = profitable_vol / total_vol if total_vol > 0 else 0.0
                profit_ratios.append(ratio)
            
            return pd.Series(profit_ratios, index=df.index)

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

    def get_dragon(self):
        try:
            # 获取股票列表
            stock_info_a_code_name_df = ak.stock_info_a_code_name()
            # 获取行业龙头
            stock_board_industry_summary_ths_df = ak.stock_board_industry_summary_ths()
            stock_board_industry_summary_ths_df["领涨股"]
            df_merged = stock_board_industry_summary_ths_df.merge(stock_info_a_code_name_df, left_on='领涨股', right_on='name', how='left')
            return df_merged["code"].to_numpy() 
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type,exc_value,exc_traceback)))
    def get_top(self):
        try: 
            top_df=pd.read_excel("./strategies/data/top.xlsx", dtype={"代码": str})
            return top_df['代码'].to_numpy()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type,exc_value,exc_traceback)))
    def seek_stock(self):
        dragon_symbols=self.get_dragon()
        tiger_symbols=self.get_tiger()
        institute_recommend_symbols=self.get_institute_recommend()
        dragon_str = [str(s) for s in dragon_symbols]
        institute_str = [str(s) for s in institute_recommend_symbols]
        tiger_str = [str(s) for s in tiger_symbols]
        merged_symbols = np.unique(np.concatenate([dragon_str,institute_str, tiger_str]))
        return merged_symbols

