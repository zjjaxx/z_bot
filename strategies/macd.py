from bot_core.strategyTemplate import StrategyTemplate
import pybroker as pb
import talib
import re

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
        print("开始回测MACD指标~")
        
        # top_stocks=self.searchStock()
        # symbols=top_stocks['代码'].to_numpy()
        # for symbol in symbols:
        #     self.exec_backtest(symbol=symbol)

        hot_stocks=self.hot_stock()
        hot_symbols=hot_stocks['股票代码'].to_numpy()
        for symbol in hot_symbols:
            symbol=re.sub(r'\D', '', symbol) 
            self.exec_backtest(symbol=symbol)
         
    def exec_backtest(self,symbol):
        macd_dif = pb.indicator('macd_dif', lambda data: talib.MACD(data.close)[0])
        macd_dea = pb.indicator('macd_dea', lambda data: talib.MACD(data.close)[1])
        macd_hist = pb.indicator('macd_hist', lambda data: talib.MACD(data.close)[2])

        self.strategy.add_execution(fn=self.buy_cmma_cross, symbols=symbol, indicators=[macd_dif,macd_dea,macd_hist])

        result = self.strategy.backtest(calc_bootstrap=True)
        total_pnl=result.metrics_df[result.metrics_df['name']=='total_pnl'].iloc[0,1]
        unrealized_pnl=result.metrics_df[result.metrics_df['name']=='unrealized_pnl'].iloc[0,1]
        print("股票代码:",symbol,"2年10万本金收益为:",total_pnl)
        print("2年10万本金浮盈收益(还有股票未卖出)为:",unrealized_pnl)
        all_pnl=total_pnl+unrealized_pnl
        print("2年10万本金总收益为:",all_pnl)
        win_rate=result.metrics_df[result.metrics_df['name']=='win_rate'].iloc[0,1]
        print("胜率为:",win_rate,"%")
        stock_data=self.queryStockData(symbol)
        self.indicatorCalc(stock_data)


    def indicatorCalc(self,data):
        macd =talib.MACD(data['收盘'].to_numpy())
        macd_dif=macd[0]
        macd_dea=macd[1]
        # macd金叉提醒
        if macd_dif[-1]>macd_dea[-1] and macd_dif[-2]<=macd_dea[-2]:
            print("macd金叉提醒")
        elif macd_dif[-1]<macd_dea[-1] and macd_dif[-2]>=macd_dea[-2]:
            print("macd死叉提醒")
    

        	



        