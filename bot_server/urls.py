# 引入views.py
from . import views
from django.urls import path

urlpatterns = [
    # path函数将url映射到视图
    path('dragon_list/', views.dragon_list, name='dragon_list'),
    path('stock_dayly_recommand/', views.stock_dayly_recommand, name='stock_dayly_recommand'),
    path('strategy_history_list/', views.strategy_history_list, name='strategy_history_list'),
    path('virtual_list/', views.virtual_list, name='virtual_list'),
    path('strategy_top_list/', views.strategy_top_list, name='strategy_top_list'),
    path('getStockCyq/', views.getStockCyq, name='getStockCyq'),
    path('getStrategyOrder/', views.getStrategyOrder, name='getStrategyOrder'),
    path('getStrategyTrade/', views.getStrategyTrade, name='getStrategyTrade'),
    path('getStrategySymbol/', views.getStrategySymbol, name='getStrategySymbol'),
    path('getStrategyOrderDetail/', views.getStrategyOrderDetail, name='getStrategyOrderDetail'),
    path('getStrategyList/', views.getStrategyList, name='getStrategyList'),
    path('metrics_list/', views.metrics_list, name='metrics_list'),
]
