from bot_core.strategyTemplate import StrategyTemplate


class Strategy(StrategyTemplate):
    name='boll'

    def init(self):
        print(Strategy.name," Strategy init")

    def strategy(self, event):
        self.logger.info("strategy event %s" %event.data[event.data["代码"]=="600036"].iloc[0].values)
        pass

    def beforeOpen(self, event):
        print("boll,beforeOpen event",event)