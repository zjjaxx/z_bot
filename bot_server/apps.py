from django.apps import AppConfig
from threading import Thread
from bot_core.main_engine import MainEngine


class BotServerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bot_server"

    def ready(self):
        __thread=Thread(target=self.runTask,name="bot_task",daemon=True)
        __thread.start()

    def runTask(self):
        main_engine=MainEngine()
        main_engine.start()

       

       

