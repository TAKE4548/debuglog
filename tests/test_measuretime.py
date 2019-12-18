# !/usr/bin/env/ python3
# -*- coding: utf-8 -*-


import unittest
import time
from datetime import timedelta as td
from datetime import datetime as dt

import debuglog


class TestMeasureTime(unittest.TestCase):
    """ `MeasureTime` 関連のテスト"""
    err = td(milliseconds=100)  # 時刻比較で±100msは許容する

    def setUp(self):
        self.mt = debuglog.MeasureTime()

    def tearDown(self):
        del self.mt

    def test_starttime(self):
        """計測開始時刻が正しく設定されるか確認する"""
        # わざとちょっと待ってからインスタンスを作り直す
        time.sleep(1)
        self.mt = debuglog.MeasureTime()
        # 直後の時刻とほぼ一致するか
        now = dt.now()
        self.assertGreaterEqual(self.mt.start, now - self.err)
        self.assertLessEqual(self.mt.start, now + self.err)

    def test_restarttime(self):
        """計測開始時刻が正しく設定されるか確認する"""
        # わざとちょっと待ってからインスタンスを作り直す
        time.sleep(1)
        self.mt.record_restart()
        # 直後の時刻とほぼ一致するか
        now = dt.now()
        self.assertGreaterEqual(self.mt.start, now - self.err)
        self.assertLessEqual(self.mt.start, now + self.err)

    def test_endtime_norecord(self):
        """記録がないときの最終記録時刻が計測開始時刻であるか確認する"""
        self.assertEqual(self.mt.end, self.mt.start)

    def test_endtime_recorded(self):
        """記録があるときの最終記録時刻が記録時刻で変化するか確認する"""
        for _ in range(2):
            self.mt.record_split()
            # 直後の時刻とほぼ一致するか
            now = dt.now()
            self.assertGreaterEqual(self.mt.end, now - self.err)
            self.assertLessEqual(self.mt.end, now + self.err)

    def test_totaltime(self):
        """トータルタイムが正しく取得できるか確認する"""
        self.assertEqual(self.mt.totaltime, td(seconds=0))
        self.mt.record_split()
        self.assertEqual(self.mt.totaltime, self.mt.end - self.mt.start)

    def test_record_event(self):
        """イベント名を指定した記録が保持されているか確認する"""
        test_txt = "test{}"
        for i in range(2):
            self.mt.record_split(test_txt.format(i))
        for i, split in enumerate(self.mt.get_splittime()):
            self.assertEqual(split.event, test_txt.format(i))

    def test_record_noevent(self):
        """イベント名を指定しなかった記録が保持されているか確認する"""
        for i in range(2):
            self.mt.record_split()
        for split in self.mt.get_splittime():
            self.assertIsNone(split.event)

    def test_record(self):
        """記録された時間が正しいか確認する"""
        self.mt.record_split()
        now = dt.now()
        split = next(self.mt.get_splittime()).time
        self.assertGreaterEqual(split + self.mt.start, now - self.err)
        self.assertLessEqual(split + self.mt.start, now + self.err)

    def test_splittime(self):
        """スプリットタイムが正しく取得できるか確認する"""
        self.mt.record_split()
        splittime = self.mt.get_splittime()
        self.assertEqual(next(splittime).time, self.mt.totaltime)

    def test_laptime(self):
        """ラップタイムが正しく取得できるか確認する"""
        self.mt.record_split()
        prev = self.mt.end
        self.mt.record_split()
        laptime = self.mt.get_laptime()
        self.assertEqual(next(laptime).time, prev - self.mt.start)
        self.assertEqual(next(laptime).time, self.mt.end - prev)
