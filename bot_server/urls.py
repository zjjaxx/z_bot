# 引入views.py
from . import views
from django.urls import path

urlpatterns = [
    # path函数将url映射到视图
    path('dragon_list/', views.dragon_list, name='dragon_list'),
    path('strategy_top_list/', views.strategy_top_list, name='strategy_list'),
    path('strategy_middle_list/', views.strategy_middle_list, name='strategy_list'),
]
