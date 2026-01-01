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
class StrategyBase(models.Model):
    riskChoices=[
        (1,"稳健"),
        (2,"激进"),
        (3,"未知")
    ]
    # 策略名称
    strategy_name = models.CharField(max_length=100)
    # 策略描述
    strategy_desc = models.CharField(max_length=1000,default="")
    # 风险系数
    risk_coefficient = models.IntegerField(choices=riskChoices,default=1)
    # 策略胜率
    strategy_rate = models.FloatField(default=0)
    # 胜场次数
    strategy_win_count = models.IntegerField(default=0)
    # 败场次数
    strategy_loss_count = models.IntegerField(default=0)
    # 总交易次数
    strategy_total_count = models.IntegerField(default=0)
    # 策略总盈亏金额
    strategy_total_profit = models.FloatField(default=0)
    # 创建时间。默认使用当前时间
    created = models.DateTimeField(default=timezone.now)
    # 更新时间。每次更新时自动更新为当前时间
    updated = models.DateTimeField(auto_now=True)
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
    strateName = models.CharField(max_length=100)
    # 操作
    strateOperate=models.IntegerField(choices=strateOperateChoices)
    # 策略描述
    strateDesc = models.CharField(max_length=1000)
    # 策略亏损次数
    strateLossCount=models.IntegerField(default=0)
    # 策略盈利次数
    strateWinCount=models.IntegerField(default=0)
    # 策略回测胜率
    strateBackTestRate= models.FloatField(default=0)
    # 创建时间。默认使用当前时间
    created = models.DateTimeField(default=timezone.now)
    # 更新时间。每次更新时自动更新为当前时间
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Strategy: {self.strateDesc}"
    
class StrategyOrder(models.Model):
    ORDER_TYPE=[
        ("buy","买入"),
        ("sell","卖出")
    ]
    # 订单类型
    type = models.CharField(choices=ORDER_TYPE,max_length=4)
    # 股票代码
    symbol = models.CharField(max_length=10)
    # 日期
    date = models.DateField()
    # 股票交易数量
    shares=models.IntegerField()
    # 策略
    strategy_name = models.CharField(max_length=100,default="boll_rsi_v1")
    # 订单填充价格
    fill_price=models.FloatField()
    # 订单创建时间。默认使用当前时间
    created = models.DateTimeField(default=timezone.now)
    # 更新时间。每次更新时自动更新为当前时间
    updated = models.DateTimeField(auto_now=True)

class StrategySymbol(models.Model):
    # 策略名称
    strategy_name = models.CharField(max_length=100)
    # 股票代码
    symbol = models.CharField(max_length=10)
    # 创建时间。默认使用当前时间
    created = models.DateTimeField(default=timezone.now)
    # 更新时间。每次更新时自动更新为当前时间
    updated = models.DateTimeField(auto_now=True)

class StratepyTrade(models.Model):
    # 策略名称
    strategy_name = models.CharField(max_length=100)
    # 股票代码
    symbol = models.CharField(max_length=10)
    # 买入日期
    entry_date = models.DateField()
    # 卖出日期
    exit_date = models.DateField()
    # 买入价格
    entry = models.FloatField()
    # 卖出价格
    exit = models.FloatField()
    # 股票交易数量
    shares=models.IntegerField()
    # 盈亏金额
    pnl=models.FloatField()
    # 累计盈亏金额
    agg_pnl=models.FloatField()
    # 回报率
    return_pct=models.FloatField()
    # 持仓周期的K线数量​
    bars=models.IntegerField(default=0)
    # 每根K线的平均盈亏​
    pnl_per_bar=models.FloatField(default=0)
    # 订单创建时间。默认使用当前时间
    created = models.DateTimeField(default=timezone.now)
    # 更新时间。每次更新时自动更新为当前时间
    updated = models.DateTimeField(auto_now=True)

class Metrics(models.Model):
     # 策略名称
    strategy_name = models.CharField(max_length=100)
    # 股票代码
    symbol = models.CharField(max_length=10)
    # 总收益
    total_pnl=models.FloatField()
    # 未实现盈亏
    unrealized_pnl=models.FloatField()
    # 总回报百分比
    total_return_pct=models.FloatField()
    # 最大回撤
    max_drawdown=models.FloatField()
    # 最大回撤百分比
    max_drawdown_pct=models.FloatField()
    # 平均收益率
    avg_pnl=models.FloatField()
    # 平均回报率
    avg_return_pct=models.FloatField()
    # 平均利润率
    avg_profit_pct=models.FloatField()
    # 平均损失
    avg_loss=models.FloatField()
    # 平均损失百分比
    avg_loss_pct=models.FloatField()
    # 最大收益
    largest_win_pct=models.FloatField()
    # 最大亏损
    largest_loss=models.FloatField()
    # 最大亏损百分比
    largest_loss_pct= models.FloatField()
    # 夏普率
    sharpe=models.FloatField()
    # 索提诺比率
    sortino=models.FloatField()
    # 盈利系数
    profit_factor=models.FloatField()
    # 溃疡指数
    ulcer_index=models.FloatField()
    upi=models.FloatField()
    equity_r2=models.FloatField()
    std_error=models.FloatField()
