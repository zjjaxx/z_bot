from django.contrib import admin

# Register your models here.

from .models import StockModel,StrategyModel

admin.site.register(StockModel)
admin.site.register(StrategyModel)
