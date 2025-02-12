from django.contrib import admin

# Register your models here.

from .models import StockModel,StrategyModel,DailyRecommendModel

admin.site.register(StockModel)
admin.site.register(StrategyModel)
admin.site.register(DailyRecommendModel)