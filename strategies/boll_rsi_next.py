from bot_core.strategyTemplate import StrategyTemplate
from bot_core.tushare import TushareDataSource
import pybroker as pb
import talib
import re
import time
from bot_server.form import StockModelForm,StrategyModelForm
from bot_server.models import StockModel,StrategyModel
from django.db import transaction
from pybroker import Strategy as PBStrategy, StrategyConfig as PBStrategyConfig
from pybroker.ext.data import AKShare
from datetime import datetime,timedelta
from .base.CustomAkShare import CustomAKShare
import pandas as pd
import numpy as np
from .utils.k_format import weekly_format,monthly_format,convert_bar_data_to_df
pb.enable_data_source_cache('cache_data')

def buy_cmma_cross(ctx):
    if not ctx.long_pos():
        # Buy if the next bar is predicted to have a positive return:
        if ctx.indicator('boll')[-1] ==1:
            ctx.buy_shares = ctx.calc_target_shares(target_size=1,cash=20000)
    else:
        # Sell if the next bar is predicted to have a negative return:
        if ctx.indicator('boll')[-1] < 0:
            ctx.sell_all_shares()

def calc_boll_macd(data):
    daily_df=convert_bar_data_to_df(data=data)
    lookback_period = 250*3 
    bottom_threshold = 0.3
    middle_threshold = 0.6
    top_threshold = 0.9
    daily_df['250_low'] = daily_df['close'].rolling(lookback_period).mean()
    daily_df['30_quantile'] = daily_df['250_low'].quantile(bottom_threshold)
    daily_df['60_quantile'] = daily_df['250_low'].quantile(middle_threshold)
    daily_df['90_quantile'] = daily_df['250_low'].quantile(top_threshold)
    weekly_df=weekly_format(daily_df)
    weekly_close = weekly_df['close'].values
    weekly_upper, weekly_middle, weekly_lower = talib.BBANDS(
        weekly_close, timeperiod=20, nbdevup=2.0, nbdevdn=1.8, matype=0
    )
    weekly_df['weekly_upper']=weekly_upper
    weekly_df['weekly_lower']=weekly_lower
    monthly_df=monthly_format(daily_df)
    monthly_close = monthly_df['close'].values
    monthly_upper, monthly_middle, monthly_lower = talib.BBANDS(
        monthly_close, timeperiod=20, nbdevup=2.0, nbdevdn=1.2, matype=0
    )
    monthly_df['monthly_middle'] = monthly_middle
    monthly_df['monthly_lower'] = monthly_lower
    monthly_df['monthly_upper'] = monthly_upper
    daily_df = pd.merge_asof(
        daily_df, weekly_df[['weekly_upper', 'weekly_lower']],
        left_index=True, right_index=True, direction='backward'
    )
    daily_df = pd.merge_asof(
        daily_df, monthly_df[['monthly_middle',"monthly_upper","monthly_lower"]],
        left_index=True, right_index=True, direction='backward'
    )
    monthly_df['monthly_trend_up'] =( monthly_df['monthly_middle'] >= monthly_df['monthly_middle'].shift(1) ) & (monthly_df['monthly_middle'].shift(1)>= monthly_df['monthly_middle'].shift(2))
    monthly_df['monthly_trend_down'] =( monthly_df['monthly_middle'] < monthly_df['monthly_middle'].shift(1)) & (monthly_df['monthly_middle'].shift(1) < monthly_df['monthly_middle'].shift(2))
    rsi_period = 14 
    monthly_df['RSI'] = talib.RSI(monthly_df['close'], timeperiod=rsi_period)
    daily_df = pd.merge_asof(
        daily_df, monthly_df[['monthly_trend_up',"monthly_trend_down","RSI"]],
        left_index=True, right_index=True, direction='backward'
    )
    buy_condition_30 = (daily_df['close'] <= daily_df['30_quantile'])
    buy_condition_60 = (daily_df['close'] > daily_df['30_quantile']) & (daily_df['close'] <= daily_df['60_quantile'])
    buy_condition_90 = (daily_df['close'] > daily_df['60_quantile']) & (daily_df['close'] <= daily_df['90_quantile'])
    threshold_pct = 0.03 
    daily_df['diff_pct'] = (daily_df['close'] / daily_df['monthly_middle'] - 1).abs()
    daily_df['is_close'] = daily_df['diff_pct'] < threshold_pct
    buy_condition_bottom = (
        (daily_df['close'] <= daily_df['weekly_lower']) 
        & daily_df['is_close']
        & buy_condition_30
        & daily_df['monthly_trend_up']
    ) 
    buy_condition_middle = (
        (daily_df['close'] <= daily_df['weekly_lower']) 
        & daily_df['is_close']
        & buy_condition_60
        & daily_df['monthly_trend_up']
    )
    
    sell_condition = (daily_df['RSI']>=70 )
    daily_df['signal'] = 0
    daily_df.loc[buy_condition_bottom, 'signal'] = 1
    daily_df.loc[sell_condition, 'signal'] = -1
    return daily_df['signal'].to_numpy()

class Strategy(StrategyTemplate):
    order=1
    # unique唯一
    name='boll_rsi_next'
    back_test_info={
        "win_count":0,
        "loss_count":0,
        "pnl":0
    }
    def init(self):
        self.stockList=[]
        print(Strategy.name," Strategy init")
    


    def beforeOpen(self, event):
        return False
        Strategy.back_test_info={
            "win_count":0,
            "loss_count":0,
            "pnl":0
        }
        self.logger.info("开始回测boll_rsi_next指标~")
        sz_list = self.get_code_by_name("./strategies/data/wfg_sz.xlsx")
        sh_list = self.get_code_by_name("./strategies/data/wfg_sh.xlsx")
        sz_list=[ str(symbol)+".SZ" for symbol in sz_list]
        sh_list=[ str(symbol)+".SH" for symbol in sh_list]
        self.exec_backtest(symbols=sz_list+sh_list)
        self.logger.info(f"回测boll_rsi_next指标结束~ 回测总计: 胜场{Strategy.back_test_info['win_count']} 负场:{Strategy.back_test_info['loss_count']} 总收益{Strategy.back_test_info['pnl']}")
        strateBackTestRate=0
        self.save_strategy_base([1,self.name,"周线下轨,月线中轨且趋势向上,股价近3年内较最高点跌去70%",strateBackTestRate,Strategy.back_test_info['win_count'],Strategy.back_test_info['loss_count'],Strategy.back_test_info['win_count']+Strategy.back_test_info['loss_count'],Strategy.back_test_info['pnl']])
        # for i,value in enumerate(self.stockList):
        #     symbol,signal,strateDesc,strateName=value
        #     self.save_strategy([symbol,signal,strateDesc,strateName,strateBackTestRate,Strategy.back_test_info['loss_count'],Strategy.back_test_info['win_count']])
        # self.reset()

    def reset(self):
        self.stockList=[]
        Strategy.back_test_info={
            "win_count":0,
            "loss_count":0,
            "pnl":0
        }
  
    def exec_backtest(self,symbols):
        boll_macd = pb.indicator('boll',calc_boll_macd)
        strategyContext = PBStrategy(
            data_source=TushareDataSource(),
            start_date="20150219",
            end_date=datetime.now(),
            config=PBStrategyConfig(return_signals=True,initial_cash=10000000))
        strategyContext.add_execution(fn=buy_cmma_cross, symbols=symbols, indicators=[boll_macd])
        # calc_bootstrap=True
        # Disable parallel indicator computation to avoid multiprocessing import issues.
        result = strategyContext.backtest(
            adjust="hfq",
            calc_bootstrap=True,
            disable_parallel=True,
        )
        for symbol,value in result.signals.items():
            boll_value=value['boll'].tail(1).to_numpy()
            if boll_value.size>0 and boll_value[0]>0:
                self.stockList.append([
                    symbol,
                    1,
                    "boll_rsi_next策略: </br> 选股：A股市值大于500亿 </br> 买点条件判断：</br> 1.当前股票在周K级别突破boll下轨，并且月线在中轨附近，趋势向上，同时股价在历史低位判断买点 </br>",
                    self.name
                ])
        total_pnl=result.metrics_df[result.metrics_df['name']=='total_pnl'].iloc[0,1]
        initial_market_value=result.metrics_df[result.metrics_df['name']=='initial_market_value'].iloc[0,1]
        unrealized_pnl=result.metrics_df[result.metrics_df['name']=='unrealized_pnl'].iloc[0,1]
        all_pnl=total_pnl+unrealized_pnl
        win_rate=result.metrics_df[result.metrics_df['name']=='win_rate'].iloc[0,1]
        pnl_rate_per_year=all_pnl/initial_market_value/2.33*100
        # 保存订单信息
        orders_df = result.orders[["type","symbol","date","shares","fill_price"]]
        orders_array = orders_df.to_numpy()
        for order in orders_array:
            self.save_strategy_order(order,self.name)
        # 保存交易信息
        trades_df = result.trades[["symbol","entry_date","exit_date","entry","exit","shares","pnl","agg_pnl","return_pct","bars","pnl_per_bar"]]
        trades_array = trades_df.to_numpy()
        for trade in trades_array:
            self.save_strategy_trade(trade,self.name)
           # 保存指标信息
        metrics_info=[
            result.metrics_df[result.metrics_df['name']=='total_pnl'].iloc[0,1],
            result.metrics_df[result.metrics_df['name']=='unrealized_pnl'].iloc[0,1],   
            result.metrics_df[result.metrics_df['name']=='total_return_pct'].iloc[0,1],
            result.metrics_df[result.metrics_df['name']=='max_drawdown'].iloc[0,1],
            result.metrics_df[result.metrics_df['name']=='max_drawdown_pct'].iloc[0,1],
            result.metrics_df[result.metrics_df['name']=='avg_pnl'].iloc[0,1],
            result.metrics_df[result.metrics_df['name']=='avg_return_pct'].iloc[0,1],
            result.metrics_df[result.metrics_df['name']=='avg_profit_pct'].iloc[0,1],
            result.metrics_df[result.metrics_df['name']=='avg_loss'].iloc[0,1],
            result.metrics_df[result.metrics_df['name']=='avg_loss_pct'].iloc[0,1],
            result.metrics_df[result.metrics_df['name']=='largest_win_pct'].iloc[0,1],
            result.metrics_df[result.metrics_df['name']=='largest_loss'].iloc[0,1],
            result.metrics_df[result.metrics_df['name']=='largest_loss_pct'].iloc[0,1],
            result.metrics_df[result.metrics_df['name']=='sharpe'].iloc[0,1],
            result.metrics_df[result.metrics_df['name']=='sortino'].iloc[0,1],
            result.metrics_df[result.metrics_df['name']=='profit_factor'].iloc[0,1],    
            result.metrics_df[result.metrics_df['name']=='ulcer_index'].iloc[0,1],
            result.metrics_df[result.metrics_df['name']=='upi'].iloc[0,1],
            result.metrics_df[result.metrics_df['name']=='equity_r2'].iloc[0,1],
            result.metrics_df[result.metrics_df['name']=='std_error'].iloc[0,1],
        ]
        # self.save_strategy_metrics(metrics_info,self.name,symbol)
         
        # if all_pnl>0:
        #     Strategy.back_test_info['win_count']+=1
        #     Strategy.back_test_info['pnl']+=all_pnl
        # elif all_pnl<0:
        #     Strategy.back_test_info['loss_count']+=1
        #     Strategy.back_test_info['pnl']+=all_pnl
        # if  signal>0:
        #     # self.logger.info(f"code: {symbol} all_pnl:{str(all_pnl)} win_rate:{win_rate} trade_count:{trade_count} unrealized_pnl:{unrealized_pnl} signal:{signal}")
        #     self.logger.info(result.trades[["type",'entry_date',	'exit_date',"shares","pnl"]])
        #     self.logger.info(result.orders[["type","date","shares","fill_price"]])
        #     message=f"boll提醒!!!!! </br> boll策略 股票代码: {str(symbol)} </br> 2年10万本金,回测结果:</br> 收益: {str(total_pnl)} </br> 浮盈收益(还有股票未卖出): {str(unrealized_pnl)} </br> 总收益: {str(all_pnl)} </br> 胜率: {str(win_rate)}% </br> 🌈✨🎉 Thank you for using the service! 🎉✨🌈"
        #     self.send_message(message=message)
        #     self.logger.info(message)
        #     #model 数据写入
        #     # 使用事务来确保所有操作的原子性
        #     self.stockList.append([
        #         symbol,
        #         signal,
        #         "boll_rsi_next策略: </br> 选股：A股市值大于500亿 </br> 买点条件判断：</br> 1.当前股票在周K级别突破boll下轨，并且月线在中轨附近，趋势向上，同时股价在历史低位判断买点 </br>",
        #         self.name
        #     ])
          





        