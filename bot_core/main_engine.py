
from .event_engine import EventEngine
from .akshare_quetaion_engine import AKShareQuetationEngine
from .utils.load import load_modules
class MainEngine:
    def __init__(self):
        # 初始化事件引擎
        self.event_engine=EventEngine()
        # 初始化行情引擎
        self.akshare_quetation_engine=AKShareQuetationEngine(self.event_engine)
        # 加载策略
        self.modules=load_modules()
        # 初始化策略实例
        self.strategies=[]
        self.initStrategies()
        #注册行情事件
        self.registryEvent()

    def initStrategies(self):
        for module in self.modules:
            strategyClass= getattr(module, 'Strategy', None)
            if not strategyClass == None :
                strategy=strategyClass(self.event_engine)
                self.strategies.append(strategy)

    def registryEvent(self):
        # 根据策略的order属性排序
        # 优先使用实例的order属性，如果没有则尝试使用类的order属性，如果都没有则默认为999
        sorted_strategies = sorted(
            self.strategies,
            key=lambda s: getattr(s, 'order', getattr(s.__class__, 'order', 999))
        )
        
        # 按排序后的顺序注册事件
        for strategy in sorted_strategies:
            self.event_engine.register(AKShareQuetationEngine.EventType, strategy.run)
            self.event_engine.register("beforeOpen", strategy.beforeOpen)

    def start(self):
        self.event_engine.start()
        self.akshare_quetation_engine.start()
