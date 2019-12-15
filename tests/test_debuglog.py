# !/usr/bin/env/ python3
# -*- coding: utf-8 -*-


import sys
import unittest
import logging
import time
import re
from typing import Union
from datetime import timedelta as td
from pathlib import Path

import debuglog


class DebugLogTestBase(unittest.TestCase):
    def setUp(self):
        self.debug_logger = debuglog.get_debug_logger()

    def tearDown(self):
        self._killLogger(self.debug_logger)

    @staticmethod
    def _killLogger(logger: logging.Logger):
        """loggerを削除する

        Args:
            logger (logging.Logger): 削除したいロガー
        """
        name = logger.name
        for handler in logger.handlers:
            handler.close()
        del logging.Logger.manager.loggerDict[name]


class TestLoggerGetting(DebugLogTestBase):
    """ `debuglog.get_debug_logger()` 関連のテスト"""

    def test_make_logger(self):
        """ハンドラが設定されたロガーが取得されるか確認"""
        for handler in self.debug_logger.handlers:
            # 標準出力と標準エラー出力へのハンドラが設定されていること
            if type(handler) is logging.StreamHandler:
                self.assertTrue(
                    handler.stream is sys.stderr or
                    handler.stream is sys.stdout
                )
            else:
                # ファイルハンドラが設定されていること
                self.assertIs(type(handler), logging.FileHandler)
                handler.close()

    def test_unique_path(self):
        """パスを指定してファイルハンドラに設定されるか確認"""
        test_fname = "./test_debug.log"
        self._killLogger(self.debug_logger)
        self.debug_logger = debuglog.get_debug_logger(path=Path(test_fname))
        for handler in self.debug_logger.handlers:
            if type(handler) is logging.FileHandler:
                self.assertEqual(
                    handler.baseFilename, str(Path(test_fname).resolve())
                )
                handler.close()
        Path(test_fname).unlink()

    @staticmethod
    def __make_test_file(path: Union[str, Path], msg: str):
        with open(path, 'w') as f:
            f.write(msg)
        return path

    def test_overwrite(self):
        """上書き指定でファイルが上書きされているか確認"""
        # 初期メッセージを書いたファイルを用意
        base_msg = "test massage"
        log_msg = "over_write"
        path = self.__make_test_file("test_file.log", base_msg)
        # 追記OFFで適当なログメッセージを出力
        self._killLogger(self.debug_logger)
        self.debug_logger = debuglog.get_debug_logger(path=path, can_append=False)
        self.debug_logger.debug(log_msg)
        # ログファイルに初期メッセージが含まれていないことを確認
        for handler in self.debug_logger.handlers:
            if type(handler) is not logging.FileHandler:
                continue
            handler.close()
            with open(handler.baseFilename, 'r') as f:
                modify_msg = f.read()
            self.assertNotIn(base_msg, modify_msg)
        # 使ったテストファイルを削除
        Path(path).unlink()

    def test_loglevel(self):
        """DEBUG以上のログメッセージが出力さるか確認"""
        # 初期メッセージを書いたファイルを用意
        d_msg = "debug massage"
        e_msg = "error massage"
        with self.assertLogs(self.debug_logger, level="DEBUG") as cm:
            self.debug_logger.debug(d_msg)
            self.debug_logger.error(e_msg)
        self.assertEqual(cm.output, [
            ':'.join(["DEBUG", self.debug_logger.name, d_msg]),
            ':'.join(["ERROR", self.debug_logger.name, e_msg])
        ])


class TestDebugLogDecorator(DebugLogTestBase):
    """ `debuglog.calledlog()` 関連のテスト"""
    @staticmethod
    @debuglog.calledlog
    def sleep1():
        time.sleep(1)

    @staticmethod
    @debuglog.calledlog
    def sleep2():
        time.sleep(2)

    def test_calledlog(self):
        """関数呼出しによるデコレータの効果を確認する"""
        # 上書きモードでロガーを作り直す
        self._killLogger(self.debug_logger)
        self.debug_logger = debuglog.get_debug_logger(can_append=False)
        # デコレータを設定した関数を呼ぶ
        with self.assertLogs(self.debug_logger, level="DEBUG") as cm:
            self.sleep1()
            self.sleep2()
        # ログが出るか確認
        head = ':'.join(["DEBUG", "{}.{}".format(self.debug_logger.name, Path(__file__).stem)])
        sep1 = '=' * 80
        sep2 = '-' * 80
        for o, v in zip(cm.output, [
            head + ':' + "--- Changed ChildLogger \"{}.{}\" -----".format(self.debug_logger.name, Path(__file__).stem),
            head + ':' + sep1,
            head + ':' + "Started the {}.{}.sleep1".format(self.__module__, self.__class__.__name__),
            head + ':' + sep2,
            head + ':' + sep2,
            head + ':' + "Proccessing Time\t{}(\.[0-9]+)?".format(td(seconds=1)),
            head + ':' + "Terminated the {}.{}.sleep1".format(self.__module__, self.__class__.__name__),
            head + ':' + sep1,
            head + ':' + "--- Changed ChildLogger \"{}.{}\" -----".format(self.debug_logger.name, Path(__file__).stem),
            head + ':' + sep1,
            head + ':' + "Started the {}.{}.sleep2".format(self.__module__, self.__class__.__name__),
            head + ':' + sep2,
            head + ':' + sep2,
            head + ':' + "Proccessing Time\t{}(\.[0-9]+)?".format(td(seconds=2)),
            head + ':' + "Terminated the {}.{}.sleep2".format(self.__module__, self.__class__.__name__),
            head + ':' + sep1
        ]):
            # 処理時間の値は正規表現で不変部分のみ判定
            if "Proccessing" in v:
                self.assertTrue(re.fullmatch(v, o))
            else:
                self.assertEqual(o, v)
