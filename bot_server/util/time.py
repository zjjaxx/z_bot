from datetime import datetime
def setAction(item):
        # 解析目标日期
    target_date = item["strateOperateTime"]
    # 获取当前日期（不含时间）
    current_date = datetime.now().date()
    if current_date>target_date:
        if item["strateOperate"]==-1:
            item['action']='观望'
        else :
            item['action']='持有'
    else :
        if item["strateOperate"]==-1:
                item['action']='卖出'
        else :
            item['action']='买入'
    return item