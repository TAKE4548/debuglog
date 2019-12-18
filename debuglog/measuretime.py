# !/usr/bin/env/ python3
# -*- coding: utf-8 -*-


from __future__ import annotations
from typing import Optional
from collections import namedtuple
from datetime import datetime as dt
from datetime import timedelta as td


class MeasureTime:
    """時間計測の機能を提供するクラス

    Attributes:
        name (str):
            時間計測インスタンスの名前
        start (datetime.datetime):
            計測開始時刻
        end (datetime.datetime):
            最終記録時刻
    """
    __leatest_id = 0
    Splittime = namedtuple("Splittime", ["event", "time"])
    Laptime = namedtuple("Laptime", ["event", "time"])

    @classmethod
    def _get_id(cls) -> int:
        ret = cls.__leatest_id
        cls.__leatest_id += 1
        return ret

    def __init__(self, name: Optional[str] = None):
        now = dt.now()
        self.__id = self.__class__._get_id()
        self.name = self.__id if name is None else self.__id
        self.__start = now
        self.__splittimes = []

    @property
    def start(self) -> dt:
        """計測開始時刻を取得する"""
        return self.__start

    @property
    def end(self) -> dt:
        """最終記録時刻を取得する"""
        try:
            return self.__start + self.__splittimes[-1].time
        except IndexError:
            return self.__start

    @property
    def totaltime(self) -> td:
        """スタートから最終記録時刻までの時間を取得する"""
        return self.end - self.start

    def record_restart(self):
        """計測をやり直す

        通常はインスタンス生成時の時刻をスタートとするが、
        インスタンス生成と計測開始のタイミングを分けたい場合、
        本メソッドを呼んだところがスタートとなる.
        """
        self.__start = dt.now()
        self.__splittimes.clear()

    def record_split(
        self,
        event: Optional[str] = None
    ) -> MeasureTime.Splittime:
        """スプリットタイムを記録する

        Args:
            event (Optional[str]):
                記録タイミングのイベント名.
                不要な場合は省略可.

        Return:
            MeasureTime.Splittime: 記録したスプリットタイム
        """
        now = dt.now()
        self.__splittimes.append(
            self.__class__.Splittime(event, now - self.start)
        )
        return self.__splittimes[-1]

    def get_splittime(self) -> MeasureTime.Splittime:
        """スプリットタイムを先頭から順番に取得する

        yield:
            MeasureTime.Splittime: 取得したスプリットタイム

        Note:
            スプリットタイムはスタートからの経過時間.
            区間に限らず起点はスタート時刻で計算される.
            区間-区間はラップタイム
            :py:meth:`get_laptime` を使用.
        """
        for splt in self.__splittimes:
            yield splt

    def get_laptime(self) -> MeasureTime.Laptime:
        """ラップタイム先頭から順番に取得する

        yield:
            MeasureTime.Laptime: 取得したラップタイム

        Note:
            ラップタイムは前区間からの経過時間.
            前区間の記録時刻を起点に計算される.
            スタート-区間はスプリットタイム
            :py:meth:`get_splittime` を使用.
        """
        prev = td(seconds=0)
        for splt in self.__splittimes:
            lap = splt.time - prev
            prev += splt.time
            yield self.__class__.Laptime(splt.event, lap)
