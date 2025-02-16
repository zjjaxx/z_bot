import pandas as pd
def convert_bar_data_to_df(data) -> pd.DataFrame:
    # 提取所有字段的 Numpy 数组
    dates = data.date
    opens = data.open
    highs = data.high
    lows = data.low
    closes = data.close
    volumes = data.volume

    # 构建 DataFrame
    df = pd.DataFrame({
        'date': dates,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    })
    
    # 将日期转换为 datetime 类型并设为索引
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    return df
def weekly_format(df):
    # 转换为周K数据（以每周五为结束日）
    weekly = df.resample('W-FRI').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    return weekly
def monthly_format(df):
    # 转换为月K数据（以自然月最后交易日为准）
    monthly = df.resample('ME').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    return monthly