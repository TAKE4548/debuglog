# !/usr/bin/env/ python3
# -*- coding: utf-8 -*-


from __future__ import annotations
import functools
from typing import Optional, Any
from collections import namedtuple
from symtable import Function
from datetime import datetime as dt
from datetime import timedelta as td
from copy import deepcopy


class TimeMeasurer:
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
    measurers = {}
    Splittime = namedtuple("Splittime", ["event", "time"])
    Laptime = namedtuple("Laptime", ["event", "time"])

    @classmethod
    def _get_id(cls) -> int:
        ret = cls.__leatest_id
        cls.__leatest_id += 1
        return ret

    @classmethod
    def pop(cls, name: Optional[str] = None) -> TimeMeasurer:
        """指定した名前の `TimeMeasurer` を取り出す

        Args:
            name (Optional[str]):
                取得対象の :py:class: `TimeMeasurer` の名称.

        Return:
            Optional[TimeMeasurer]:
                取得した `TimeMeasurer` インスタンス.
                取得できなかった場合は、Noneが返る.

        Note:
            取り出した後の要素は削除される.
            要素を残して置きたい場合は、 :py:func: `get_measurer` を使う
        """
        return cls.measurers.pop(name, None)

    def __init__(self, name: Optional[str] = None):
        now = dt.now()
        self.__id = self.__class__._get_id()
        self.__name = self.__id if name is None else name
        self.__start = now
        self.__splittimes = []
        self.__class__.measurers[self.name] = self

    @property
    def name(self):
        return self.__name

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
    ) -> TimeMeasurer.Splittime:
        """スプリットタイムを記録する

        Args:
            event (Optional[str]):
                記録タイミングのイベント名.
                不要な場合は省略可.

        Return:
            TimeMeasurer.Splittime: 記録したスプリットタイム
        """
        now = dt.now()
        self.__splittimes.append(
            self.__class__.Splittime(event, now - self.start)
        )
        return self.__splittimes[-1]

    def get_splittime(self) -> TimeMeasurer.Splittime:
        """スプリットタイムを先頭から順番に取得する

        yield:
            TimeMeasurer.Splittime: 取得したスプリットタイム

        Note:
            スプリットタイムはスタートからの経過時間.
            区間に限らず起点はスタート時刻で計算される.
            区間-区間はラップタイム
            :py:meth:`get_laptime` を使用.
        """
        for splt in self.__splittimes:
            yield splt

    def get_laptime(self) -> TimeMeasurer.Laptime:
        """ラップタイム先頭から順番に取得する

        yield:
            TimeMeasurer.Laptime: 取得したラップタイム

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

    def __add__(self, other: TimeMeasurer) -> TimeMeasurer:
        """TimeMeasurer同士を加算する

        Args:
            other (TimeMeasurer):
                加数とするTimeMeasurerのインスタンス

        Return:
            TimeMeasurer:
                `self` の末尾に `other` のスプリットタイム
                を接続した :py:class: `TimeMeasurer` インスタンス
        """
        ret = deepcopy(self)
        return ret.__splittimes.extend(other.__splittimes)

    def __iadd__(self, other: TimeMeasurer) -> TimeMeasurer:
        """自身に別のTimeMeasurerを加算

        Args:
            other (TimeMeasurer):
                加数とするTimeMeasurerのインスタンス

        Return:
            TimeMeasurer: 更新した `self`
        """
        return self.__splittimes.extend(other.__splittimes)

    def __repr__(self):
        """文字列としての扱い"""
        delimiter = '\t'
        terminater = '\n'
        ret = "start{}{}{}".format(delimiter, self.start, terminater)
        for i, lap in enumerate(self.get_laptime()):
            ret += "{}{}{}{}".format(lap.event, delimiter, lap.time, terminater)
        return ret[:-1]


def get_measurer(name: Optional[str] = None) -> TimeMeasurer:
    """指定した名前の `TimeMeasurer` を管理辞書から取得する

    取得後も管理辞書は変化しない.(取得したインスタンスは管理辞書に残る)

    Args:
        name (Optional[str]):
            取得対象の :py:class: `TimeMeasurer` の名称.
            Noneを指定すると指定した名前で新規に作成される.

    Return:
        TimeMeasurer:
            取得・新規作成した `TimeMeasurer` インスタンス.
    """
    measurer = TimeMeasurer.measurers.get(name)
    # 存在しなければ新規作成
    if measurer is None:
        measurer = TimeMeasurer(name)
        TimeMeasurer.measurers[name] = measurer
    return measurer


def pop_measurer(name: Optional[str]) -> Optional[TimeMeasurer]:
    """指定した名前の `TimeMeasurer` を管理辞書から取得する

    取得後のインスタンスは管理辞書から削除される.

    Args:
        name (Optional[str]):
            取得対象の :py:class: `TimeMeasurer` の名称.

    Return:
        Optional[TimeMeasurer]:
            取得した `TimeMeasurer` インスタンス.
            取得できなかった場合は、Noneが返る.
    """
    return TimeMeasurer.pop(name)


def time_record(
    name: Optional[str]
) -> Any:
    """関数・メソッドの実行時間を記録するデコレータ

    設定した関数の名称 + `_start` , `_end` のイベント名で時刻を記録する

    Args:
        name (Optional[str]):
            記録対象の `TimeMeasurer` の名称を指定する.
            存在しない名称でも新規作成される.

    Example:
        >>> import debuglog
        >>> import time
        >>> @debuglog.time_record("sample")
        ... def sample():
        ...     time.sleep(1)
        ...
        >>> sample()
        >>> debuglog.get_measurer("sample")
        start\t2019-12-23 00:38:57.633082
        sample_start\t0:00:00
        sample_end\t0:00:01.000287
    """
    def __time_record(
        func: Function,
    ):
        @functools.wraps(func)
        def __wrapper(*args, **kwargs):
            measurer = get_measurer(name)
            measurer.record_split("{}_start".format(func.__qualname__))
            ret = func(*args, **kwargs)
            measurer.record_split("{}_end".format(func.__qualname__))
            return ret
        return __wrapper
    return __time_record
