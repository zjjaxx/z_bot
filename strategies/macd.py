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
class Strategy(StrategyTemplate):
    name='macd'

    def init(self):
        print(Strategy.name," Strategy init")

    def strategy(self, event):
        pass
    
    def buy_cmma_cross(self,ctx):
        if ctx.long_pos() and  ctx.indicator('macd_dif')[-1] < ctx.indicator('macd_dea')[-1]  and ctx.indicator('macd_dif')[-2]>=ctx.indicator('macd_dea')[-2]:
            ctx.sell_shares = ctx.calc_target_shares(1)
            return
        if not ctx.long_pos() and ctx.indicator('macd_dif')[-1] > ctx.indicator('macd_dea')[-1] and ctx.indicator('macd_dif')[-2]<=ctx.indicator('macd_dea')[-2]:
            ctx.buy_shares = ctx.calc_target_shares(1)

    def beforeOpen(self, event):
        # self.send_message("开始回测MACD指标~")
        self.logger.info("开始回测MACD指标~")
        symbols=self.seek_stock()

        for symbol in symbols:
            symbol=re.sub(r'\D', '', symbol) 
            self.exec_backtest(symbol=symbol)
        # self.send_message("回测MACD指标结束~")
        self.logger.info("回测MACD指标结束~")
         
    def exec_backtest(self,symbol):
        macd_dif = pb.indicator('macd_dif', lambda data: talib.MACD(data.close)[0])
        macd_dea = pb.indicator('macd_dea', lambda data: talib.MACD(data.close)[1])
        macd_hist = pb.indicator('macd_hist', lambda data: talib.MACD(data.close)[2])
        strategyContext = PBStrategy(
            data_source=AKShare(),
            start_date=datetime.now()-timedelta(days=365*2),
            end_date=datetime.now(),
            config=PBStrategyConfig())
        strategyContext.add_execution(fn=self.buy_cmma_cross, symbols=symbol, indicators=[macd_dif,macd_dea,macd_hist])
        # calc_bootstrap=True
        result = strategyContext.backtest(adjust="hfq")
        total_pnl=result.metrics_df[result.metrics_df['name']=='total_pnl'].iloc[0,1]
        initial_market_value=result.metrics_df[result.metrics_df['name']=='initial_market_value'].iloc[0,1]
        unrealized_pnl=result.metrics_df[result.metrics_df['name']=='unrealized_pnl'].iloc[0,1]
        all_pnl=total_pnl+unrealized_pnl
        win_rate=result.metrics_df[result.metrics_df['name']=='win_rate'].iloc[0,1]
        pnl_rate=all_pnl/initial_market_value*100
        stock_data=self.queryStockHistoryData(symbol)
        calc_result=self.indicatorCalc(stock_data,symbol)
        if pnl_rate>20 and calc_result:
            message=f"macd金叉提醒!!!!! \n MACD金叉策略 股票代码: {str(symbol)} \n 2年10万本金,回测结果:\n 收益: {str(total_pnl)} \n 浮盈收益(还有股票未卖出): {str(unrealized_pnl)} \n 总收益: {str(all_pnl)} \n 胜率: {str(win_rate)}% \n 🌈✨🎉 Thank you for using the service! 🎉✨🌈"
            # self.send_message(message=message)
            self.logger.info(message)
            #model 数据写入
            # 使用事务来确保所有操作的原子性
            try:
                with transaction.atomic():
                    # 1. 检查 StockModel 是否存在，如果不存在则创建它
                    stock, _ = StockModel.objects.get_or_create(code=symbol)
                     # 2. 检查是否已经存在与 StockModel 相关联的 StrategyModel 数据
                    existing_strategy = StrategyModel.objects.filter(code=stock).first()
                    if existing_strategy:
                        print(f"Strategy for stock {symbol} already exists.")
                    else:
                        # 2. 准备策略数据并创建 StrategyModel
                        strategy_data = {
                            "code": stock,  # 使用已经创建或存在的 StockModel 实例
                            "strateType": 1,  # 策略类型
                            "strateDesc": "MACD金叉买入死叉卖出策略",  # 策略描述
                            "winRate": win_rate,
                            "pnl": all_pnl,
                            "pnl_desc": message  # 限制 pnl_desc 最大长度为 100
                        }

                        # 使用 StrategyModelForm 创建表单并校验
                        strate_form = StrategyModelForm(data=strategy_data)

                        # 校验表单
                        if strate_form.is_valid():
                            # 保存 StrategyModel 实例
                            strate_form.save()
                        else:
                            print(strate_form.errors)
            except Exception as e:
                print(f"An error occurred: {e}")

    def indicatorCalc(self,data,symbol):
        macd =talib.MACD(data['收盘'].to_numpy())
        macd_dif=macd[0]
        macd_dea=macd[1]
        # macd金叉提醒
        if macd_dif[-1]>macd_dea[-1] and macd_dif[-2]<=macd_dea[-2]:
            return True
        elif macd_dif[-1]<macd_dea[-1] and macd_dif[-2]>=macd_dea[-2]:
            # self.send_message(f"股票代码{symbol}:macd死叉提醒!!!!!")
            # self.logger.info(f"股票代码{symbol}:macd死叉提醒!!!!!")
            return False
        return False
        	



        