from django.apps import AppConfig
from threading import Thread
from bot_core.main_engine import MainEngine
import tushare as ts


class BotServerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bot_server"

    def ready(self):
        # 一次性获取全部数据
        ts.set_token('13120ee255c17b868d0e3523d0be88f6d805645738e8637720b994a3')
        pro = ts.pro_api()
        __thread=Thread(target=self.runTask,name="bot_task",daemon=True)
        __thread.start()

    def runTask(self):
        main_engine=MainEngine()
        main_engine.start()

       

       

