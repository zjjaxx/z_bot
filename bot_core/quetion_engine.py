# coding: utf-8
import time
from threading import Thread
from .utils.time import is_trade_date,is_tradetime,get_next_trade_date
from dateutil import tz
from .event_engine import Event
import datetime 
import arrow



beforeOpenTime=datetime.time(0,0,0)

class QuetationEngine:
    """行情推送引擎基类"""
    EventType = 'base'
    PushInterval = 1

    def __init__(self, event_engine):
        self.event_engine = event_engine
        self.next_time=datetime.datetime.combine(self.now.date(),beforeOpenTime)
        # 行情、盘前线程
        self.quotation_thread = Thread(target=self.push_quotation, name="QuotationEngine.%s" % self.EventType,daemon=True)
        self.init()


    @property
    def now(self):
        """
        now 时间戳统一接口
        :return:
        """
        _time= arrow.get(time.time()).to("Asia/Shanghai").isoformat()
        return datetime.datetime.fromisoformat(_time).replace(tzinfo=None)

    def update_next_time(self):
        """
        下次激活时间
        :return:
        """
        next_date=get_next_trade_date(self.now)
        self.next_time = datetime.datetime.combine(next_date,beforeOpenTime)
          


    def start(self):
        self.quotation_thread.start()
  

    def push_quotation(self):
        while True:
            if(is_trade_date(self.now) and  is_tradetime(self.now)):
                try:
                    response_data = self.fetch_quotation()
                except:
                    self.wait()
                    continue
                event = Event(event_type=self.EventType, data=response_data)
                self.event_engine.put(event)
            
    
            if self.now.timestamp()>=self.next_time.timestamp():
                self.update_next_time()
                event = Event(event_type="beforeOpen")
                self.event_engine.put(event)

            self.wait()
              

    def fetch_quotation(self):
        # return your quotation
        return None

    def init(self):
        # do something init
        pass

    def wait(self):
        # for receive quit signal
        for _ in range(int(self.PushInterval) + 1):
            time.sleep(1)
