import pandas as pd
import pybroker
import tushare as ts
import pandas as pd
from datetime import datetime
from pybroker.data import DataSource

class TushareDataSource(DataSource):

    def __init__(self):
        super().__init__()
    def _fetch_data(self, symbols, start_date, end_date, _timeframe, _adjust):
        # 确保日期格式正确，转换为tushare需要的'YYYYMMDD'格式
        try:
            # 处理字符串类型的日期
            if isinstance(start_date, str):
                # 处理带时间的日期格式 'YYYY-MM-DD HH:MM:SS'
                if ' ' in start_date:
                    start_date = start_date.split(' ')[0]
                # 处理带连字符的日期格式 'YYYY-MM-DD'
                if '-' in start_date:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y%m%d')
            
            if isinstance(end_date, str):
                # 处理带时间的日期格式 'YYYY-MM-DD HH:MM:SS'
                if ' ' in end_date:
                    end_date = end_date.split(' ')[0]
                # 处理带连字符的日期格式 'YYYY-MM-DD'
                if '-' in end_date:
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y%m%d')
        except Exception as e:
            print(f"日期格式转换错误: {e}")
        print(symbols, start_date, end_date, _timeframe, _adjust)
        df = ts.pro_bar(ts_code="000001.SZ", adj='hfq', start_date="20150101", end_date="20240102")
        # 确保返回的数据格式包含date、symbol、open、high、low、close这些字段
        print(df)
        if df is not None and not df.empty:
            # 重命名字段以符合要求的格式
            df = df.rename(columns={
                "vol": "volume",
                'ts_code': 'symbol',
                'trade_date': 'date'
            })
            
            # 将date列转换为datetime类型
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
            
            # 只保留需要的字段
            df = df[['date', 'symbol', 'open', 'high', 'low', 'close',"volume"]]
            print(df)
        return df
