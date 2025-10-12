r"""Contains extension classes."""

"""Copyright (C) 2023 Edward West. All rights reserved.

This code is licensed under Apache 2.0 with Commons Clause license
(see LICENSE for details).
"""
import os
from logbook import Logger, StreamHandler, FileHandler
from datetime import datetime
from typing import Optional
import time
import tushare as ts
import akshare
import pandas as pd
from yahooquery import Ticker

from pybroker.common import DataCol, to_datetime
from pybroker.data import DataSource


class TushareDataSource(DataSource):
    r"""Retrieves data from `AKShare <https://akshare.akfamily.xyz/>`_."""

    _tf_to_period = {
        "": "daily",
        "1day": "daily",
        "1week": "weekly",
    }
     

    def initLogger(self, name='logInfo', log_type='stdout', filepath='logInfo.log', loglevel='DEBUG'):
        """Log对象
        :param name: log 名字
        :param :logtype: 'stdout' 输出到屏幕, 'file' 输出到指定文件
        :param :filename: log 文件名
        :param :loglevel: 设定log等级 ['CRITICAL', 'ERROR', 'WARNING', 'NOTICE', 'INFO', 'DEBUG', 'TRACE', 'NOTSET']
        :return log handler object
        """
        self.logger = Logger(name)
        if log_type == 'stdout':
            StreamHandler(sys.stdout, level=loglevel).push_application()
        if log_type == 'file':
            if os.path.isdir(filepath) and not os.path.exists(filepath):
                os.makedirs(os.path.dirname(filepath))
            file_handler = FileHandler(filepath, level=loglevel)
            self.logger.handlers.append(file_handler)


    def __init__(self,symbol_type):   
        super().__init__()  
        self.symbol_type=symbol_type   
            # 初始化日志
        self.initLogger( name='logInfo', log_type='file', filepath='./logger/info.log', loglevel='DEBUG')    

    def _fetch_data(
        self,
        symbols: frozenset[str],
        start_date: datetime,
        end_date: datetime,
        timeframe: Optional[str],
        adjust: Optional[str],
    ) -> pd.DataFrame:
        """:meta private:"""
        start_date_str = to_datetime(start_date).strftime("%Y%m%d")
        end_date_str = to_datetime(end_date).strftime("%Y%m%d")
        symbols_list = list(symbols)
        symbols_simple = [item for item in symbols_list]
        result = pd.DataFrame()
        formatted_tf = self._format_timeframe(timeframe)
        if formatted_tf in TushareDataSource._tf_to_period:
            period = TushareDataSource._tf_to_period[formatted_tf]
            for i in range(len(symbols_list)):
                # 添加重试机制，直到请求成功
                success = False
                while not success:
                    try:
                        temp_df = ts.pro_bar(
                            ts_code=symbols_simple[i], 
                            adj=adjust if adjust is not None else "", 
                            start_date=start_date_str, end_date=end_date_str
                        )
                        # 检查是否获取到了有效数据
                        if temp_df is not None and not temp_df.empty:
                            temp_df["symbol"] = symbols_list[i]
                            result = pd.concat([result, temp_df], ignore_index=True)
                        success = True
                    except Exception as e:
                        self.logger.error(f"获取数据失败: {e}，1秒后重试...")
                        time.sleep(3)  # 等待1秒后重新请求
        if result.columns.empty:
            return pd.DataFrame(
                columns=[
                    DataCol.SYMBOL.value,
                    "trade_date",
                    DataCol.OPEN.value,
                    DataCol.HIGH.value,
                    DataCol.LOW.value,
                    DataCol.CLOSE.value,
                    "vol",
                ]
            )
        if result.empty:
            return result
        result.rename(
            columns={
                "trade_date": "date",
                DataCol.OPEN.value: DataCol.OPEN.value,
                DataCol.CLOSE.value: DataCol.CLOSE.value,
                DataCol.HIGH.value: DataCol.HIGH.value,
                DataCol.LOW.value: DataCol.LOW.value,
                "vol": "volume",
            },
            inplace=True,
        )
        result["date"] = pd.to_datetime(result["date"])
        result = result[
            [
                "date",
                DataCol.SYMBOL.value,
                DataCol.OPEN.value,
                DataCol.HIGH.value,
                DataCol.LOW.value,
                DataCol.CLOSE.value,
                "volume",
            ]
        ]
        print(result)
        return result


class YQuery(DataSource):
    r"""Retrieves data from Yahoo Finance using
    `Yahooquery <https://github.com/dpguthrie/yahooquery>`_\ ."""

    _tf_to_period = {
        "": "1d",
        "1hour": "1h",
        "1day": "1d",
        "5day": "5d",
        "1week": "1wk",
    }

    def __init__(self, proxies: Optional[dict] = None):
        super().__init__()
        self.proxies = proxies

    def _fetch_data(
        self,
        symbols: frozenset[str],
        start_date: datetime,
        end_date: datetime,
        timeframe: Optional[str],
        adjust: Optional[bool],
    ) -> pd.DataFrame:
        """:meta private:"""
        show_yf_progress_bar = (
            not self._logger._disabled
            and not self._logger._progress_bar_disabled
        )
        ticker = Ticker(
            symbols,
            asynchronous=True,
            progress=show_yf_progress_bar,
            proxies=self.proxies,
        )
        timeframe = self._format_timeframe(timeframe)
        if timeframe not in self._tf_to_period:
            raise ValueError(
                f"Unsupported timeframe: '{timeframe}'.\n"
                f"Supported timeframes: {list(self._tf_to_period.keys())}."
            )
        df = ticker.history(
            start=start_date,
            end=end_date,
            interval=self._tf_to_period[timeframe],
            adj_ohlc=adjust,
        )
        if df.columns.empty:
            return pd.DataFrame(
                columns=[
                    DataCol.SYMBOL.value,
                    DataCol.DATE.value,
                    DataCol.OPEN.value,
                    DataCol.HIGH.value,
                    DataCol.LOW.value,
                    DataCol.CLOSE.value,
                    DataCol.VOLUME.value,
                ]
            )
        if df.empty:
            return df
        df = df.reset_index()
        df[DataCol.DATE.value] = pd.to_datetime(df[DataCol.DATE.value])
        df = df[
            [
                DataCol.SYMBOL.value,
                DataCol.DATE.value,
                DataCol.OPEN.value,
                DataCol.HIGH.value,
                DataCol.LOW.value,
                DataCol.CLOSE.value,
                DataCol.VOLUME.value,
            ]
        ]
        return df
