from bot_server.models import StockModel,StrategyModel,StrategyOrder,StrategyBase,StratepyTrade
# 引入表单类
from django import forms

class StockModelForm(forms.ModelForm):
    class Meta:
        # 指明数据模型来源
        model = StockModel
        # 定义表单包含的字段
        fields = ('code',)
class StrategyModelForm(forms.ModelForm):
    class Meta:
        # 指明数据模型来源
        model = StrategyModel
        # 定义表单包含的字段
        fields = ('stock',"strateName","strateOperate","strateDesc","strateBackTestRate","strateLossCount","strateWinCount")

class StrategyOrderModelForm(forms.ModelForm):
    class Meta:
        # 指明数据模型来源
        model = StrategyOrder
        # 定义表单包含的字段
        fields = ('type','symbol','date','shares','fill_price','strategy_name')

class StrategyBaseModelForm(forms.ModelForm):
    class Meta:
        # 指明数据模型来源
        model = StrategyBase
        # 定义表单包含的字段
        fields = ('strategy_name','strategy_rate','strategy_desc','strategy_win_count','strategy_loss_count','strategy_total_count','strategy_total_profit')

class StratepyTradeModelForm(forms.ModelForm):
    class Meta:
        # 指明数据模型来源
        model = StratepyTrade
        # 定义表单包含的字段
        fields = ('strategy_name','symbol','entry_date','exit_date','entry','exit','shares','pnl','agg_pnl','return_pct','bars','pnl_per_bar')