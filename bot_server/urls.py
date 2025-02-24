# 引入views.py
from . import views
from django.urls import path

urlpatterns = [
    # path函数将url映射到视图
    path('dragon_list/', views.dragon_list, name='dragon_list'),
    path('virtual_list/', views.virtual_list, name='virtual_list'),
    path('strategy_top_list/', views.strategy_top_list, name='strategy_top_list'),
    path('strategy_middle_list/', views.strategy_middle_list, name='strategy_middle_list'),
]
