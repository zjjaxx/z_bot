from django.shortcuts import render
import akshare as ak
from django.http import HttpResponse,JsonResponse,HttpResponseServerError



def dragon_list(request):
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