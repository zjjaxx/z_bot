from bot_core.strategyTemplate import StrategyTemplate

class Strategy(StrategyTemplate):
    name='macd'

    def init(self):
        print(Strategy.name," Strategy init")

    def strategy(self, event):
        pass

    def beforeOpen(self, event):
        print("macd,beforeOpen event",event)