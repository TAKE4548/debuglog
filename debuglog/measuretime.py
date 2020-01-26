# !/usr/bin/env/ python3
# -*- coding: utf-8 -*-


from __future__ import annotations
import functools
import csv
from typing import Optional, Union, Any, Dict, Sequence
from pathlib import Path
from collections import namedtuple
from symtable import Function
from datetime import datetime as dt
from datetime import timedelta as td
from copy import deepcopy
from random import random
from time import sleep

from matplotlib import pyplot as plt, ticker

from .__main__ import load_configs


DEFAULT_LOG_DIR = Path(load_configs().DEFAULT_LOG_DIR)


class TimeMeasurer:
    """時間計測の機能を提供するクラス

    Attributes:
        __leatest_id (int): インスタンス生成の度に更新されるユニークなid
        name (str): 時間計測インスタンスの名前
        start (datetime.datetime): 計測開始時刻
        end (datetime.datetime): 最終記録時刻
        totaltime (datetime.timedelta): 計測開始から最終記録時刻までの時間
    """
    __leatest_id = 0
    _measurers = {}
    Splittime = namedtuple("Splittime", ["event", "time"])
    """スプリットタイムの名前付きタプル

    Attributes:
        event (str): 記録時のイベント識別子
        time (datetime.timedelta): 記録時の測定開始時刻からの経過時間
    """
    Laptime = namedtuple("Laptime", ["event", "time"])
    """ラップタイムの名前付きタプル

    Attributes:
        event (str): 記録時のイベント識別子
        time (datetime.timedelta): 記録時の直前記録イベントからの経過時間
    """

    ROW_START_EVT = "Start"
    COL_EVTNAME = "Event"
    COL_TIME = "Time"
    COL_SPLITTIME = "SplitTime"
    COL_LAPTIME = "LapTime"

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
        return cls._measurers.pop(name, None)

    def __init__(self, name: Optional[str] = None):
        now = dt.now()
        self.__id = self.__class__._get_id()
        self.__name = self.__id if name is None else name
        self.__start = now
        self.__splittimes = []
        self.__class__._measurers[self.name] = self

    @property
    def name(self) -> str:
        """設定した識別名"""
        return self.__name

    @property
    def start(self) -> dt:
        """計測開始時刻"""
        return self.__start

    @property
    def end(self) -> dt:
        """最終記録時刻"""
        try:
            return self.__start + self.__splittimes[-1].time
        except IndexError:
            return self.__start

    @property
    def totaltime(self) -> td:
        """スタートから最終記録時刻までの時間"""
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
        self.__splittimes.append(self.__class__.Splittime(
            str(len(self.__splittimes)) if event is None else event,
            now - self.start
        ))
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
            prev = splt.time
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
        for i, (split, lap) in enumerate(
            zip(self.get_splittime(), self.get_laptime())
        ):
            ret += delimiter.join(map(str, [lap.event, split.time, lap.time]))
            ret += terminater
        return ret[:-1]

    def to_csv(
        self,
        path: Union[str, Path, None] = None,
        sep: str = ',',
        encoding: str = "utf-8"
    ) -> Path:
        """記録をcsv出力する

        Args:
            path (Union[str, Path]):
                出力するcsvファイルのパス
            sep (str):
                csvの区切り文字.
                デフォルトは ``,`` .
            encoding (str):
                ファイルのエンコード.
                デフォルトは ``utf-8`` .

        Return:
            出力したcsvファイルへのパス
        """
        if path is None:
            path = DEFAULT_LOG_DIR / (self.name + ".csv")
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f, delimiter=sep)
            writer.writerow([
                self.__class__.COL_EVTNAME,
                self.__class__.COL_TIME,
                self.__class__.COL_SPLITTIME,
                self.__class__.COL_LAPTIME
            ])
            writer.writerow(
                [self.__class__.ROW_START_EVT, self.start, '-', '-']
            )
            rows = []
            for lap, split in zip(self.get_laptime(), self.get_splittime()):
                rows.append(
                    [lap.event, self.start + split.time, split.time, lap.time]
                )
            writer.writerows(rows)
        return Path(path)

    def plot(self, ax=None, **kwargs):
        """時間記録をプロットする"""
        plt.rcParams["font.size"] = 18

        def __set_initial_param(
            params_dict: Dict[str, Any],
            kws: Sequence[str],
            value: Any
        ):
            if all((k not in params_dict.keys() for k in kws)):
                params_dict[kws[0]] = value

        def __autolocator(n: int = 5):
            unit_time = int((self.totaltime / (n - 1)).total_seconds())
            major_locator = ticker.MultipleLocator(unit_time)
            minor_locator = ticker.MultipleLocator(unit_time / 5)
            unit = "s"
            return major_locator, minor_locator, unit

        self.__ax = (
            ax
            if ax is not None else
            self.__ax
            if getattr(
                self, "_{}__ax".format(self.__class__.__name__), None
            ) is not None else
            plt.figure(figsize=(12, 9)).add_subplot()
        )
        x = [0]
        y = [0.0]
        bar = [0.0]
        labels = ["start"]
        for i, (split, lap) in enumerate(
            zip(self.get_splittime(), self.get_laptime()), 1
        ):
            labels.append(split.event)
            x.append(i)
            y.append(split.time.total_seconds())
            bar.append(lap.time.total_seconds())
        __set_initial_param(kwargs, ["ls", "linestyle"], '-')
        __set_initial_param(kwargs, ["lw", "linewidth"], 1)
        __set_initial_param(kwargs, ["color"], 'b')
        __set_initial_param(kwargs, ["marker"], '.')
        __set_initial_param(kwargs, ["label"], "経過時間")
        self.__ax.plot(x, y, **kwargs)
        self.__ax.bar(x, bar, label="単一処理時間")
        self.__ax.xaxis.set_major_locator(ticker.AutoLocator())
        self.__ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
        self.__ax.set_xticklabels(labels, rotation=90, ha="right", fontsize=12)
        major_locator, minor_locator, unit = __autolocator()
        self.__ax.set_ylabel("経過時間[{}]".format(unit))
        self.__ax.yaxis.set_major_locator(major_locator)
        self.__ax.yaxis.set_minor_locator(minor_locator)
        self.__ax.grid(True)
        self.__ax.legend()
        return self.__ax

    def show(self, *args, force_plot=False, **kwargs):
        if force_plot or getattr(
            self, "_{}__ax".format(self.__class__.__name__), None
        ) is None:
            self.plot(*args, **kwargs)
        plt.tight_layout()
        plt.show()

    @classmethod
    def from_csv(cls, path: Union[str, Path]) -> TimeMeasurer:
        """TimeMeasurerオブジェクトの出力csvからインスタンスを生成する"""
        # csvを読み込み
        with open(path) as f:
            reader = csv.reader(f)
            # ヘッダ取得してインデックス変換
            head = next(reader)
            i_evt = head.index(cls.COL_EVTNAME)
            i_time = head.index(cls.COL_TIME)
            i_stime = head.index(cls.COL_SPLITTIME)
            # 開始イベントの取得
            start = next(reader)
            # 開始以降のイベント取得
            evts = []
            for row in reader:
                hours, minutes, seconds = map(
                    lambda x:
                        int(x)
                        if '.' not in x else
                        (int(x.split('.')[0]), int(x.split('.')[1])),
                    row[i_stime].split(':'))
                microseconds = 0
                if type(seconds) is tuple:
                    microseconds = seconds[1]
                    seconds = seconds[0]
                evts.append(cls.Splittime(row[i_evt], td(
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds,
                    microseconds=microseconds
                )))
        # 新しいTimeMeasuererインスタンス生成
        self = get_measurer()
        self.__start = dt.fromisoformat(start[i_time])
        self.__splittimes = evts
        return self


def from_csv(*args, **kwargs):
    return TimeMeasurer.from_csv(*args, **kwargs)


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
    measurer = TimeMeasurer._measurers.get(name)
    # 存在しなければ新規作成
    if measurer is None:
        measurer = TimeMeasurer(name)
        TimeMeasurer._measurers[name] = measurer
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


if __name__ == "__main__":
    @time_record("test")
    def random_sleep():
        sleep(random())

    mt = get_measurer("test")
    for i in range(3):
        random_sleep()
    mt.show()
