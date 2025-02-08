from .quetion_engine import QuetationEngine
import akshare as ak
class AKShareQuetationEngine(QuetationEngine):
    EventType = 'akshare'

    def fetch_quotation(self):
        return ak.stock_zh_a_spot_em()

    def init(self):
        # do something init
        pass
