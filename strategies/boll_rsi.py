from bot_core.strategyTemplate import StrategyTemplate
import pybroker as pb
import talib
import re
from bot_server.form import StockModelForm,StrategyModelForm
from bot_server.models import StockModel,StrategyModel
from django.db import transaction
from pybroker import Strategy as PBStrategy, StrategyConfig as PBStrategyConfig
from pybroker.ext.data import AKShare
from datetime import datetime,timedelta
from .base.CustomAkShare import CustomAKShare
from numba import njit
import pandas as pd
import numpy as np
from .utils.k_format import weekly_format,monthly_format,convert_bar_data_to_df

class Strategy(StrategyTemplate):
    # unique唯一
    name='boll_rsi'
    back_test_info={
        "win_count":0,
        "loss_count":0,
        "pnl":0
    }
    def init(self):
        print(Strategy.name," Strategy init")

    def strategy(self, event):
        pass
    
    def buy_cmma_cross(self,ctx):
        if not ctx.long_pos():
            # Buy if the next bar is predicted to have a positive return:
            if ctx.indicator('boll')[-1] ==1:
                # ctx.stop_profit_pct = 60
                # ctx.stop_loss_pct = 10
                ctx.buy_shares = ctx.calc_target_shares(1)
            elif ctx.indicator('boll')[-1] ==2:
                  ctx.stop_profit_pct = 50
                  # ctx.stop_loss_pct = 10
                  ctx.buy_shares = ctx.calc_target_shares(0.6)
            elif ctx.indicator('boll')[-1] ==3:
                ctx.stop_profit_pct = 25
                # ctx.stop_loss_pct = 10
                ctx.buy_shares = ctx.calc_target_shares(0.3)
        else:
            # Sell if the next bar is predicted to have a negative return:
            if ctx.indicator('boll')[-1] < 0:
                ctx.sell_shares =ctx.calc_target_shares(1)

    def beforeOpen(self, event):
        Strategy.back_test_info={
            "win_count":0,
            "loss_count":0,
            "pnl":0
        }
        # self.send_message("开始回测MACD指标~")
        self.logger.info("开始回测BOLL_MACD指标~")
        symbols=self.get_top()
        for symbol in symbols:
            symbol=str(symbol)
            # symbol=re.sub(r'\D', '', symbol) 
            self.exec_backtest(symbol=symbol)
        # self.send_message("回测MACD指标结束~")
        self.logger.info(f"回测BOLL_MACD指标结束~ 回测总计: 胜场{Strategy.back_test_info['win_count']} 负场:{Strategy.back_test_info['loss_count']} 总收益{Strategy.back_test_info['pnl']}")
    
    def calc_boll_macd(self,data):
        # 策略
        # 选股：A股市值大于700亿
        # 买点条件判断：
        # 1. 当前股价在月K级别突破boll下轨，并且趋势走平或向上、带宽缩窄 同时根据股价是否在历史高位来判断买点
        # 2. 当前股票在周K级别突破boll下轨，并且月线在中轨之上，趋势向上，同时股价在历史低位判断买点
        # 卖出条件判断
        # 1. 当前股价在月K级别RSI超过70
        
        macd_dif,macd_dea,macd_hist = talib.MACD(data.close)
        boll_upper,boll_middle,boll_lower = talib.BBANDS(data.close,timeperiod=20,nbdevup=2.2,nbdevdn=1.8,matype=0)

        # 日K
        daily_df=convert_bar_data_to_df(data=data)
        daily_df['macd_dif']=macd_dif
        daily_df['macd_dea']=macd_dea

        # 增加250日最低价分位判断（当前价处于近1年最低10%区间）
        lookback_period = 250  # 约1年
        bottom_threshold = 0.3
        middle_threshold = 0.6
        top_threshold = 0.9
        daily_df['250_low'] = daily_df['close'].rolling(lookback_period).mean()

        daily_df['30_quantile'] = daily_df['250_low'].quantile(bottom_threshold)
        daily_df['60_quantile'] = daily_df['250_low'].quantile(middle_threshold)
        daily_df['90_quantile'] = daily_df['250_low'].quantile(top_threshold)

        
        # 金叉条件：DIF 上穿 DEA
        daily_df['golden_cross'] = (daily_df['macd_dif'] > daily_df['macd_dea']) & (daily_df['macd_dif'].shift(1) <= daily_df['macd_dea'].shift(1))
        # 死叉条件：DIF 下穿 DEA
        daily_df['death_cross'] = (daily_df['macd_dif'] < daily_df['macd_dea']) & (daily_df['macd_dif'].shift(1) >= daily_df['macd_dea'].shift(1))  
        # 周K
        weekly_df=weekly_format(daily_df)
        weekly_close = weekly_df['close'].values
        weekly_upper, weekly_middle, weekly_lower = talib.BBANDS(
            weekly_close, timeperiod=20, nbdevup=2.2, nbdevdn=1.8, matype=0
        )
        weekly_df['weekly_upper']=weekly_upper
        weekly_df['weekly_lower']=weekly_lower
     
        # 月K
        monthly_df=monthly_format(daily_df)
        monthly_close = monthly_df['close'].values
        monthly_upper, monthly_middle, monthly_lower = talib.BBANDS(
            monthly_close, timeperiod=20, nbdevup=2.2, nbdevdn=1.2, matype=0
        )
        monthly_df['monthly_middle'] = monthly_middle
        monthly_df['monthly_lower'] = monthly_lower
        monthly_df['monthly_upper'] = monthly_upper

        #2. 计算带宽 ```python # 计算带宽（百分比） 
        monthly_df["bandwidth"] = (monthly_df["monthly_upper"] - monthly_df["monthly_lower"]) / monthly_df["monthly_middle"] * 100 
        # 计算带宽的滚动统计量（20日窗口） 20日均值
        monthly_df["band_ma20"] = monthly_df["bandwidth"].rolling(20).mean()
        # 20日标准差
        monthly_df["band_std20"] = monthly_df["bandwidth"].rolling(20).std() 
        #判断缩窄和扩张 ```python # 缩窄条件：带宽 < 均值 - 1倍标准差 
        monthly_df["is_squeeze"] = monthly_df["bandwidth"] < (monthly_df["band_ma20"] - monthly_df["band_std20"])
        # 扩张条件：带宽 > 均值 + 1倍标准差 
        monthly_df["is_expansion"] = monthly_df["bandwidth"] > (monthly_df["band_ma20"] + monthly_df["band_std20"])
        # 合并周线数据到日线（按最近周五对齐）
        daily_df = pd.merge_asof(
            daily_df, weekly_df[['weekly_upper', 'weekly_lower']],
            left_index=True, right_index=True, direction='backward'
        )
        
        # 合并月线数据到日线（按自然月最后一天对齐）
        daily_df = pd.merge_asof(
            daily_df, monthly_df[['monthly_middle',"monthly_upper","monthly_lower","is_squeeze"]],
            left_index=True, right_index=True, direction='backward'
        )
        
        # 计算月线中轨趋势（当前月大于上月则为向上）
        # monthly_df['monthly_middle_before'] = monthly_df['monthly_middle'].shift(2)
        monthly_df['monthly_trend_up'] =( monthly_df['monthly_middle'] >= monthly_df['monthly_middle'].shift(1) ) & (monthly_df['monthly_middle'].shift(1)>= monthly_df['monthly_middle'].shift(2))
        monthly_df['monthly_trend_down'] =( monthly_df['monthly_middle'] < monthly_df['monthly_middle'].shift(1)) & (monthly_df['monthly_middle'].shift(1) < monthly_df['monthly_middle'].shift(2))
        #rsi
        rsi_period = 14 
        monthly_df['RSI'] = talib.RSI(monthly_df['close'], timeperiod=rsi_period)
        # 合并月线趋势到日线
        daily_df = pd.merge_asof(
            daily_df, monthly_df[['monthly_trend_up',"monthly_trend_down","RSI"]],
            left_index=True, right_index=True, direction='backward'
        )
         # 生成信号
        buy_condition_30 = (daily_df['close'] <= daily_df['30_quantile'])
        buy_condition_60 = (daily_df['close'] > daily_df['30_quantile']) & (daily_df['close'] <= daily_df['60_quantile'])
        buy_condition_90 = (daily_df['close'] > daily_df['60_quantile']) & (daily_df['close'] <= daily_df['90_quantile'])


        # 生成信号
        buy_condition_bottom = (
            (daily_df['close'] <= daily_df['monthly_lower']) 
            & buy_condition_30
            & daily_df['is_squeeze']
            & daily_df['monthly_trend_up']
        ) 
        buy_condition_middle = (
            (daily_df['close'] <= daily_df['monthly_lower']) 
            & buy_condition_60
            & daily_df['is_squeeze']
            & daily_df['monthly_trend_up']
        )
        buy_condition_top = (
            (daily_df['close'] <= daily_df['monthly_lower'])
            & buy_condition_90
            & daily_df['is_squeeze']
            & daily_df['monthly_trend_up']
        )
       
        sell_condition = (daily_df['RSI']>=70 )

        daily_df['signal'] = 0
        daily_df.loc[buy_condition_bottom, 'signal'] = 1
        daily_df.loc[buy_condition_middle, 'signal'] = 2
        daily_df.loc[buy_condition_top, 'signal'] = 3

        daily_df.loc[sell_condition, 'signal'] = -1

        return daily_df['signal'].to_numpy()
      
    def exec_backtest(self,symbol):
        boll_macd = pb.indicator('boll',self.calc_boll_macd)
        strategyContext = PBStrategy(
            data_source=AKShare(),
            start_date=datetime.now()-timedelta(days=365*4),
            end_date=datetime.now(),
            config=PBStrategyConfig(return_signals=True))
        strategyContext.add_execution(fn=self.buy_cmma_cross, symbols=symbol, indicators=[boll_macd])
        # calc_bootstrap=True
        result = strategyContext.backtest(adjust="hfq")
        signal=result.signals[symbol]['boll'].iloc[-1]
        total_pnl=result.metrics_df[result.metrics_df['name']=='total_pnl'].iloc[0,1]
        initial_market_value=result.metrics_df[result.metrics_df['name']=='initial_market_value'].iloc[0,1]
        unrealized_pnl=result.metrics_df[result.metrics_df['name']=='unrealized_pnl'].iloc[0,1]
        trade_count=result.metrics_df[result.metrics_df['name']=='trade_count'].iloc[0,1]
        all_pnl=total_pnl+unrealized_pnl
        win_rate=result.metrics_df[result.metrics_df['name']=='win_rate'].iloc[0,1]
        pnl_rate_per_year=all_pnl/initial_market_value/2.33*100
        if all_pnl>0:
            Strategy.back_test_info['win_count']+=1
            Strategy.back_test_info['pnl']+=all_pnl
        elif all_pnl<0:
            Strategy.back_test_info['loss_count']+=1
            Strategy.back_test_info['pnl']+=all_pnl
        if not signal==0:
            self.logger.info(f"code: {symbol} all_pnl:{str(all_pnl)} win_rate:{win_rate} trade_count:{trade_count} unrealized_pnl:{unrealized_pnl} signal:{signal}")
            self.logger.info(result.trades[["type",'entry_date',	'exit_date',"shares","pnl"]])
            self.logger.info(result.orders[["type","date","shares","fill_price"]])
            # message=f"boll提醒!!!!! \n boll策略 股票代码: {str(symbol)} \n 2年10万本金,回测结果:\n 收益: {str(total_pnl)} \n 浮盈收益(还有股票未卖出): {str(unrealized_pnl)} \n 总收益: {str(all_pnl)} \n 胜率: {str(win_rate)}% \n 🌈✨🎉 Thank you for using the service! 🎉✨🌈"
            # self.send_message(message=message)
            # self.logger.info(message)
            #model 数据写入
            # 使用事务来确保所有操作的原子性
            try:
                with transaction.atomic():
                    # 1. 检查 StockModel 是否存在，如果不存在则创建它
                    _stock= StockModel.objects.filter(code=symbol).first()
                    if (not _stock) and signal==-1:
                        return False
                    stock, _ = StockModel.objects.get_or_create(code=symbol)
                     # 2. 检查是否已经存在与 StockModel 相关联的 StrategyModel 数据
                    existing_strategy = StrategyModel.objects.filter(stock=stock,strateType=Strategy.name).first()
                    # 已存在 卖出
                    if existing_strategy and  signal==-1:
                        existing_strategy.strateOperate=signal
                        existing_strategy.strateOperateTime=datetime.now().date()
                        existing_strategy.pnl=pnl_rate_per_year
                        existing_strategy.winRate=win_rate
                        existing_strategy.save()
                    # 不存在 买入
                    elif not existing_strategy and signal>0:
                        # 2. 准备策略数据并创建 StrategyModel
                        strategy_data = {
                            "stock": stock,  # 使用已经创建或存在的 StockModel 实例
                            "strateType": Strategy.name,  # 策略类型
                            "strateDesc": "boll+rsi策略: \n 选股：A股市值大于700亿 \n 买点条件判断：\n 1. 当前股价在月K级别突破boll下轨，并且趋势走平或向上、带宽缩窄 同时根据股价是否在历史高位来判断买点 \n 2. 当前股票在周K级别突破boll下轨，并且月线在中轨之上，趋势向上，同时股价在历史低位判断买点 \n 卖出条件判断: \n 1. 当前股价在月K级别RSI超过70",  
                            "winRate": win_rate,
                            "strateOperate":signal,
                            "strateOperateTime":datetime.now().date(),
                            "pnl": pnl_rate_per_year,
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




        