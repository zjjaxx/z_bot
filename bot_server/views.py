from django.shortcuts import render
import akshare as ak
from django.http import HttpResponse,JsonResponse,HttpResponseServerError
from .models import StockModel,StrategyModel,StrategyOrder,StrategyBase,StratepyTrade
from .util.time import setAction
from django.utils import timezone
from datetime import datetime, time, timedelta



def dragon_list(request):
    try:
        stock_board_industry_summary_ths_df = ak.stock_board_industry_summary_ths()
        data = []
        for index, row in stock_board_industry_summary_ths_df.iterrows():
            # 创建一个字典，每一列的数据作为键值对
            data.append({
                "block": row["板块"],
                "block_rate":row['涨跌幅'],
                "input": row["净流入"],
                "codeName": row["领涨股"],
                "price": row["领涨股-最新价"],
                "pnl_rate": row["领涨股-涨跌幅"]
            })
        return JsonResponse({"success":True,"msg":"ok","data":data})
    except Exception as e:
    # 记录完整错误堆栈
        return JsonResponse({
            "success": False,
            "msg": "服务暂时不可用，请稍后重试",
            "data": e
        }, status=500)
def virtual_list(request):
    try:
        stock_board_concept_name_em_df = ak.stock_board_concept_name_em()
        data = []
        for index, row in stock_board_concept_name_em_df.iterrows():
            # 创建一个字典，每一列的数据作为键值对
            data.append({
                "block": row["板块名称"],
                "block_rate":row['涨跌幅'],
                "codeName": row["领涨股票"],
                "pnl_rate": row["领涨股票-涨跌幅"]
            })
        return JsonResponse({"success":True,"msg":"ok","data":data})
    except Exception as e:
    # 记录完整错误堆栈
        return JsonResponse({
            "success": False,
            "msg": "服务暂时不可用，请稍后重试",
            "data": e
        }, status=500)
    
def stock_dayly_recommand(request):
    try:
        local_now = timezone.now()
        today_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
        # 计算当天结束时间
        today_end = today_start + timedelta(days=1) - timedelta(seconds=1)
        
        strategies = StrategyModel.objects.filter(
            updated__range=(today_start, today_end)
        ).values()
        return JsonResponse({"success":True,"msg":"ok","data":list(strategies)})
    except Exception as e:
    # 记录完整错误堆栈
        return JsonResponse({
            "success": False,
            "msg": "服务暂时不可用，请稍后重试",
            "data": e
        }, status=500)
def strategy_history_list(request):
    try:
        strategies=StrategyModel.objects.values()
        return JsonResponse({"success":True,"msg":"ok","data":list(strategies)})
    except Exception as e:
    # 记录完整错误堆栈
        return JsonResponse({
            "success": False,
            "msg": "服务暂时不可用，请稍后重试",
            "data": e
        }, status=500)
def strategy_top_list(request):
    try:
        strategies=StrategyModel.objects.filter(strateType=1).values()
        strategies=list(map(setAction,strategies)) 
        return JsonResponse({"success":True,"msg":"ok","data":list(strategies)})
    except Exception as e:
    # 记录完整错误堆栈
        return JsonResponse({
            "success": False,
            "msg": "服务暂时不可用，请稍后重试",
            "data": e
        }, status=500)
def getStrategySymbol(request):
    try:
        strategy_name=request.GET.get("strategy_name")
        strategy_symbols=StrategyOrder.objects.filter(strategy_name=strategy_name).values_list("symbol",flat=True).distinct()
        return JsonResponse({"success":True,"msg":"ok","data":list(strategy_symbols)})
    except Exception as e:
    # 记录完整错误堆栈
        return JsonResponse({
            "success": False,
            "msg": "服务暂时不可用，请稍后重试",
            "data": e
        }, status=500)  

def getStrategyOrderDetail(request):
    try:
        strategy_name=request.GET.get("strategy_name")
        symbol=request.GET.get("symbol")
        # 按date字段降序排列
        strategy_orders=StrategyOrder.objects.filter(strategy_name=strategy_name,symbol=symbol).order_by('-date').values()
        return JsonResponse({"success":True,"msg":"ok","data":list(strategy_orders)})
    except Exception as e:
    # 记录完整错误堆栈
        return JsonResponse({
            "success": False,
            "msg": "服务暂时不可用，请稍后重试",
            "data": e
        }, status=500)

def getStrategyOrder(request):
    try:
        strategy_name=request.GET.get("strategy_name")
        # 按date字段降序排列
        strategy_orders=StrategyOrder.objects.filter(strategy_name=strategy_name).order_by('-date').values()
        return JsonResponse({"success":True,"msg":"ok","data":list(strategy_orders)})
    except Exception as e:
    # 记录完整错误堆栈
        return JsonResponse({
            "success": False,
            "msg": "服务暂时不可用，请稍后重试",
            "data": e
        }, status=500)
def getStrategyTrade(request):
    try:
        strategy_name=request.GET.get("strategy_name")
        # 按date字段降序排列
        strategy_trades=StratepyTrade.objects.filter(strategy_name=strategy_name).order_by('-entry_date').values()
        return JsonResponse({"success":True,"msg":"ok","data":list(strategy_trades)})
    except Exception as e:
    # 记录完整错误堆栈
        return JsonResponse({
            "success": False,
            "msg": "服务暂时不可用，请稍后重试",
            "data": e
        }, status=500)
def getStockCyq(request):
    try:
        print(request.GET.get("code"))
        stock_cyq_em_df = ak.stock_cyq_em(symbol=request.GET.get("code"), adjust="")
        data = []
        for index, row in stock_cyq_em_df.iterrows():
            # 创建一个字典，每一列的数据作为键值对
            data.append({
                "rate": row["获利比例"],
                "average":row["平均成本"],
                "90_low":row["90成本-低"],
                "90_high":row["90成本-高"],
                "90_concentration":row["90集中度"],
                "70_low":row["70成本-低"],
                "70_high":row["70成本-高"],
                "70_concentration":row["70集中度"],
            })
        return JsonResponse({"success":True,"msg":"ok","data":data})
    except Exception as e:
        print(e)
    # 记录完整错误堆栈
        return JsonResponse({
            "success": False,
            "msg": "服务暂时不可用，请稍后重试",
            "data": e
        }, status=500)
def getStrategyList(request):
    try:
        strategies=StrategyBase.objects.values()
        return JsonResponse({"success":True,"msg":"ok","data":list(strategies)})
    except Exception as e:
        return JsonResponse({
            "success": False,
            "msg": "服务暂时不可用，请稍后重试",
            "data": e
        }, status=500)