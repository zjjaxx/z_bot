from bot_server.models import StockModel,StrategyModel
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
        fields = ('stock',"strateName","strateType","strateOperate","strateOperateTime","strateDesc")