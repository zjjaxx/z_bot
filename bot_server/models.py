from django.db import models
from django.utils import timezone

# 股票模型
class StockModel(models.Model):
    # 股票代码，主键
    code = models.CharField(max_length=10, unique=True)
    # 创建时间。默认使用当前时间
    created = models.DateTimeField(default=timezone.now)
    # 更新时间。每次更新时自动更新为当前时间
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

# 策略模型
class StrategyModel(models.Model):
    # 股票代码，主键
    code = models.ForeignKey(StockModel,on_delete=models.CASCADE)
    # 策略类型，枚举
    strateType = models.IntegerField()
    # 策略描述，文本类型
    strateDesc = models.CharField(max_length=100)
      # 胜率
    winRate=models.FloatField()
    # 总收益比率
    pnl=models.FloatField()
    # 总收益描述
    pnl_desc=models.CharField(max_length=1000)
    # 创建时间。默认使用当前时间
    created = models.DateTimeField(default=timezone.now)
    # 更新时间。每次更新时自动更新为当前时间
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Strategy: {self.strateDesc}"
    
