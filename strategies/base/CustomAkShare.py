r"""Contains extension classes."""

"""Copyright (C) 2023 Edward West. All rights reserved.

This code is licensed under Apache 2.0 with Commons Clause license
(see LICENSE for details).
"""
import sys
import traceback
from datetime import datetime
import time
from typing import Optional
from bot_core.event_engine import Event
import akshare
import pandas as pd
from yahooquery import Ticker

from pybroker.common import DataCol, to_datetime
from pybroker.data import DataSource


class CustomAKShare(DataSource):
    r"""Retrieves data from `AKShare <https://akshare.akfamily.xyz/>`_."""

    _tf_to_period = {
        "": "daily",
        "1day": "daily",
        "1week": "weekly",
    }
    def __init__(self,event_engine):
        super().__init__()
        self.event_engine=event_engine
    
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
        symbols_simple = [item.split(".")[0] for item in symbols_list]
        result = pd.DataFrame()
        formatted_tf = self._format_timeframe(timeframe)
        if formatted_tf in CustomAKShare._tf_to_period:
            period = CustomAKShare._tf_to_period[formatted_tf]
            for i in range(len(symbols_list)):
                try:
                    temp_df = akshare.index_zh_a_hist(
                        symbol=symbols_simple[i],
                        start_date=start_date_str,
                        end_date=end_date_str,
                        period=period,
                    )
                    if not temp_df.columns.empty:
                        temp_df["symbol"] = symbols_list[i]
                    result = pd.concat([result, temp_df], ignore_index=True)
                except Exception as e:
                    event = Event(event_type="beforeOpen")
                    self.event_engine.put(event)
                    print(f"无法获取 {symbols_simple[i]} 的历史数据: {str(e)}")
                # time.sleep(1)
        if result.columns.empty:
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
        if result.empty:
            return result
        result.rename(
            columns={
                "日期": DataCol.DATE.value,
                "开盘": DataCol.OPEN.value,
                "收盘": DataCol.CLOSE.value,
                "最高": DataCol.HIGH.value,
                "最低": DataCol.LOW.value,
                "成交量": DataCol.VOLUME.value,
            },
            inplace=True,
        )
        result["date"] = pd.to_datetime(result["date"])
        result = result[
            [
                DataCol.DATE.value,
                DataCol.SYMBOL.value,
                DataCol.OPEN.value,
                DataCol.HIGH.value,
                DataCol.LOW.value,
                DataCol.CLOSE.value,
                DataCol.VOLUME.value,
            ]
        ]
        print("result",result)
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
