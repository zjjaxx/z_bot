from django.db import models
from django.utils import timezone

# 股票模型
class StockModel(models.Model):
    # 股票代码，主键
    code = models.CharField(max_length=10, unique=True,primary_key=True)
    # 创建时间。默认使用当前时间
    created = models.DateTimeField(default=timezone.now)
    # 更新时间。每次更新时自动更新为当前时间
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

# 策略模型
class StrategyModel(models.Model):
    strateOperateChoices=[
        (1,"重仓买入"),
        (3,"轻仓买入"),
        (-1,"卖出"),
        (2,"中等仓位")
    ]
    #一对多
    stock = models.ForeignKey(StockModel,on_delete=models.CASCADE)
    # 策略类型，枚举
    strateType = models.CharField(max_length=100,unique=True)
    # 操作
    strateOperate=models.IntegerField(choices=strateOperateChoices)
    # 操作时间
    strateOperateTime=models.DateField()
    # 策略描述
    strateDesc = models.CharField(max_length=100)
      # 胜率
    winRate=models.FloatField()
    # 总收益比率
    pnl=models.FloatField()
    # 创建时间。默认使用当前时间
    created = models.DateTimeField(default=timezone.now)
    # 更新时间。每次更新时自动更新为当前时间
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Strategy: {self.strateDesc}"
    
