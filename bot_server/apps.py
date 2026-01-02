from django.apps import AppConfig
from threading import Thread
from bot_core.main_engine import MainEngine
import tushare as ts
import sys
import schedule
import time
from spider.core.index import crawl_stock_data


class BotServerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bot_server"

    def ready(self):
        # 检查是否正在执行管理命令（如migrate），如果是则不启动策略引擎
        # 只有在实际运行服务器时才启动策略引擎
        if len(sys.argv) > 1 and sys.argv[1] in ['migrate', 'makemigrations', 'shell', 'test', 'collectstatic']:
            return
        # 先执行一次爬虫任务（同步执行，等待完成）
        self.job()
        # 然后在后台线程中运行定时任务
        spider_thread = Thread(target=self.exec_schedule, name="Spider", daemon=True)
        spider_thread.start()
        
        # 一次性获取全部数据
        ts.set_token('13120ee255c17b868d0e3523d0be88f6d805645738e8637720b994a3')
        pro = ts.pro_api()
        __thread = Thread(target=self.runTask, name="bot_task", daemon=True)
        __thread.start()
    

    def runTask(self):
        main_engine=MainEngine()
        main_engine.start()

    def job(self):
        crawl_stock_data("https://xuangu.eastmoney.com/Result?id=xc0eb999efb008006172","./strategies/data/wfg_sh.xlsx")
        crawl_stock_data("https://xuangu.eastmoney.com/Result?id=xc0eb99344b50800969d","./strategies/data/wfg_sz.xlsx")
    
    def exec_schedule(self):
        # 设置定时任务
        schedule.every().day.at("19:30:00", "Asia/Shanghai").do(self.job)
        # 运行定时任务循环
        while True:
            schedule.run_pending()
            time.sleep(1)

       

       

