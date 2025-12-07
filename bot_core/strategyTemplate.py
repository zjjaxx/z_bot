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
from bot_server.form import StockModelForm,StrategyModelForm,StrategyOrderModelForm,StrategyBaseModelForm,StratepyTradeModelForm
from bot_server.models import StockModel,StrategyModel,StrategyOrder,StrategyBase,StratepyTrade
from django.db import transaction

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

    def get_block_top(self):
        codes=[]
        try:
            stock_board_industry_name_em_df = ak.stock_board_industry_name_em()
            block_code_list=stock_board_industry_name_em_df["板块名称"].to_numpy()
            for block_code in block_code_list:
                stock_board_industry_cons_em_df = ak.stock_board_industry_cons_em(symbol=block_code)
                stock_board_industry_cons_em_df=stock_board_industry_cons_em_df.sort_values(by="涨跌幅",ascending=False).head(10)
                for code in list(stock_board_industry_cons_em_df["代码"].to_numpy()):
                    codes.append(code)
            codes = [code for code in codes if not (code.startswith('9') or code.startswith('2'))]
            return codes
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type,exc_value,exc_traceback)))
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
    def get_sh_code(self):
        try: 
            sh_df=pd.read_excel("./strategies/data/sh.xlsx", dtype={"代码": str})
            return sh_df['代码'].to_numpy()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type,exc_value,exc_traceback)))
    def get_sz_code(self):
        try: 
            sz_df=pd.read_excel("./strategies/data/sz.xlsx", dtype={"代码": str})
            return sz_df['代码'].to_numpy()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type,exc_value,exc_traceback)))
    def get_top(self):
        try: 
            top_df=pd.read_excel("./strategies/data/middle.xlsx", dtype={"代码": str})
            return top_df['代码'].to_numpy()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(repr(traceback.format_exception(exc_type,exc_value,exc_traceback)))
    def get_top_guxi(self):
        try: 
            top_df=pd.read_excel("./strategies/data/top-guxi.xlsx", dtype={"代码": str})
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

    def save_strategy(self,info):
        symbol,signal,strateDesc,strateName,strateBackTestRate,strateLossCount,strateWinCount=info
        try:
            with transaction.atomic():
                # 1. 检查 StockModel 
                # _stock= StockModel.objects.filter(code=symbol).first()
                # # 如果没有股票，并且是卖出的
                # if (not _stock) and signal==-1:
                #     return False
                stock, _ = StockModel.objects.get_or_create(code=symbol)
                    # 2. 检查是否已经存在与 StockModel 相关联的 StrategyModel 数据
                existing_strategy = StrategyModel.objects.filter(stock=stock,strateName=strateName).first()
                # 已存在 卖出
                # if existing_strategy and signal==-1:
                #     existing_strategy.strateOperate=signal
                #     existing_strategy.strateOperateTime=datetime.now().date()
                #     existing_strategy.save()
                # 已存在 买入
                if existing_strategy and signal>=1:
                    # existing_strategy.strateType=2 if signal>1 else 1
                    existing_strategy.strateOperate=signal
                    existing_strategy.strateDesc=strateDesc
                    existing_strategy.strateLossCount=strateLossCount
                    existing_strategy.strateWinCount=strateWinCount
                    existing_strategy.strateBackTestRate=strateBackTestRate
                    # existing_strategy.strateOperateTime=datetime.now()
                    existing_strategy.save()
                # 不存在 买入
                elif not existing_strategy and signal>0:
                    # 2. 准备策略数据并创建 StrategyModel
                    strategy_data = {
                        "stock": stock,  # 使用已经创建或存在的 StockModel 实例
                        # "strateType":2 if signal>1 else 1,
                        "strateName":strateName,
                        "strateDesc":strateDesc,  
                        "strateOperate":signal,
                        "strateLossCount":strateLossCount,
                        "strateWinCount":strateWinCount,
                        "strateBackTestRate":strateBackTestRate
                        # "strateOperateTime":datetime.now(),
                    }

                    # 使用 StrategyModelForm 创建表单并校验
                    strate_form = StrategyModelForm(data=strategy_data)
                    # 校验表单
                    if strate_form.is_valid():
                        # 保存 StrategyModel 实例
                        strate_form.save()
                    else:
                        self.logger.info(strate_form.errors)
        except Exception as e:
            self.logger.info(f"An error occurred: {e}")
    def save_strategy_base(self,info):
        risk_coefficient,strategy_name,strategy_desc,strategy_rate,strategy_win_count,strategy_loss_count,strategy_total_count,strategy_total_profit=info
        try:
            with transaction.atomic():
                strategy_base=StrategyBase.objects.filter(strategy_name=strategy_name).first()
                if(not strategy_base):
                    strategy_base_data = {
                        "risk_coefficient":risk_coefficient,
                        "strategy_name":strategy_name,
                        "strategy_rate":strategy_rate,
                        "strategy_desc":strategy_desc,
                        "strategy_win_count":strategy_win_count,
                        "strategy_loss_count":strategy_loss_count,
                        "strategy_total_count":strategy_total_count,
                        "strategy_total_profit":strategy_total_profit,
                    }
                    # 使用 StrategyBaseModelForm 创建表单并校验
                    strategy_base_form = StrategyBaseModelForm(data=strategy_base_data)
                    # 校验表单
                    if strategy_base_form.is_valid():
                        # 保存 StrategyBaseModel 实例
                        strategy_base_form.save()
                    else:
                        self.logger.info(strategy_base_form.errors)
                else:
                    strategy_base.risk_coefficient=risk_coefficient
                    strategy_base.strategy_rate=strategy_rate
                    strategy_base.strategy_win_count=strategy_win_count
                    strategy_base.strategy_desc=strategy_desc
                    strategy_base.strategy_loss_count=strategy_loss_count
                    strategy_base.strategy_total_count=strategy_total_count
                    strategy_base.strategy_total_profit=strategy_total_profit
                    strategy_base.save()
        except Exception as e:
            self.logger.info(f"An error occurred: {e}") 
    def save_strategy_trade(self,trade,strategy_name):
        symbol,entry_date,exit_date,entry,exit,shares,pnl,agg_pnl,return_pct,bars,pnl_per_bar=trade 
        try:
            with transaction.atomic():
                strategy_trade=StratepyTrade.objects.filter(strategy_name=strategy_name,symbol=symbol,entry_date=entry_date).first()
                if(strategy_trade):
                    return False 
                strategy_trade_data = {
                    "strategy_name":strategy_name,
                    "symbol":symbol,
                    "entry_date":entry_date,
                    "exit_date":exit_date,
                    "entry":entry,
                    "exit":exit,
                    "shares":shares,
                    "pnl":pnl,
                    "agg_pnl":agg_pnl,
                    "return_pct":return_pct,
                    "bars":bars,
                    "pnl_per_bar":pnl_per_bar,
                }
                # 使用 StratepyTradeModelForm 创建表单并校验
                strategy_trade_form = StratepyTradeModelForm(data=strategy_trade_data)
                # 校验表单
                if strategy_trade_form.is_valid():
                    # 保存 StratepyTradeModel 实例
                    strategy_trade_form.save()
                else:
                    self.logger.info(strategy_trade_form.errors)
        except Exception as e:
            self.logger.info(f"An error occurred: {e}") 

    def save_strategy_order(self,order,strategy_name):
        type,symbol,date,shares,fill_price=order            
        try:
            with transaction.atomic():
                strategy_order=StrategyOrder.objects.filter(strategy_name=strategy_name,symbol=symbol,date=date).first()
                if(strategy_order):
                    return False
                strategy_order_data = {
                    "strategy_name":strategy_name,
                    "symbol":symbol,
                    "date":date,
                    "type":type,
                    "shares":shares,
                    "fill_price":fill_price,
                }
                # 使用 StrategyOrderModelForm 创建表单并校验
                strategy_order_form = StrategyOrderModelForm(data=strategy_order_data)
                # 校验表单
                if strategy_order_form.is_valid():
                    # 保存 StrategyOrderModel 实例
                    strategy_order_form.save()
                else:
                    self.logger.info(strategy_order_form.errors)
                
        except Exception as e:
            self.logger.info(f"An error occurred: {e}") 