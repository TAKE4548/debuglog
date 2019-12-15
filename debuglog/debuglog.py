# !/usr/bin/env/ python3
# -*- coding: utf-8 -*-
"""デバッグ用のログ機能を提供するモジュール

標準の `logging` モジュールを使い、
デバッグ用のログとして必要そうな機能を持つ

note:
    本モジュールを `import` すると、`logging` モジュールに
    `"PRINT_INFO"` という名称で、
    `logging.INFO` より `1` だけ高いレベルが追加される。
"""


import logging
import sys
from pathlib import Path
from typing import Optional, Union
from symtable import Function
from datetime import datetime as dt


# 表示用のINFOレベルを設定
logging.addLevelName(logging.INFO + 1, "PRINT_INFO")


# ロガーのデフォルト設定
_DEFAULT_LOGGER_NAME = "debug"
_DEFAULT_LOG_FILE = Path("./log/debug.log")

# ハンドラのフォーマッタ
_STREAM_HANDLER_FORMAT = logging.Formatter('\t'.join([
    "{levelname}",
    "{message}"
]), style='{')

_FILE_HANDLER_FORMAT = logging.Formatter('\t'.join([
    "{asctime}",
    "{filename}",
    "{lineno}",
    "{levelname}",
    "{message}"
]), style='{')

# 表示用のセパレータ
_SEPARATER1 = '=' * 80
_SEPARATER2 = '-' * 80


def __set_formatter(
    _format: Union[str, logging.Formatter]
) -> logging.Formatter:
    """ログフォーマッタを返す

    Args:
        _format (Union[str, logging.Formatter]):
            設定するフォーマット.

    Return:
        logging.Formatter: フォーマットを反映したフォーマッタ.

    Raises:
        TypeError:
            `_format` に `str` , `logging.Formatter`
            以外のタイプを渡した時に発生.

    Note:
        指定するフォーマットについては、公式ドキュメントを参照.
        https://docs.python.org/ja/3/library/logging.html#formatter-objects
    """
    # 元々logging.Formatterならそのまま返す
    if isinstance(_format, logging.Formatter):
        pass
    # 文字列指定の時はlogging.Formatterを作成
    if type(_format, str):
        _format = logging.Formatter(_format)
    else:
        raise TypeError(_format)
    return _format


def set_fhandler_format(_format: Union[str, logging.Formatter]):
    """ファイルハンドラのフォーマットを設定する

    Args:
        _format (Union[str, logging.Formatter]):
            設定するフォーマット.

    Return:
        logging.Formatter: フォーマットを反映したフォーマッタ.

    Raises:
        TypeError:
            `_format` に `str` , `logging.Formatter`
            以外のタイプを渡した時に発生.

    Note:
        指定するフォーマットについては、公式ドキュメントを参照.
        https://docs.python.org/ja/3/library/logging.html#formatter-objects
    """
    global _FILE_HANDLER_FORMAT
    _FILE_HANDLER_FORMAT = __set_formatter(_format)


def set_shandler_format(_format: Union[str, logging.Formatter]):
    """ストリームハンドラのフォーマットを設定する

    Args:
        _format (Union[str, logging.Formatter]):
            設定するフォーマット.

    Return:
        logging.Formatter: フォーマットを反映したフォーマッタ.

    Raises:
        TypeError:
            `_format` に `str` , `logging.Formatter`
            以外のタイプを渡した時に発生.

    Note:
        指定するフォーマットについては、公式ドキュメントを参照.
        https://docs.python.org/ja/3/library/logging.html#formatter-objects
    """
    global _STREAM_HANDLER_FORMAT
    _STREAM_HANDLER_FORMAT = __set_formatter(_format)


def __get_stdout_handler() -> logging.StreamHandler:
    """標準出力用のログハンドラを生成して返す"""
    class StdOutFilter(logging.Filter):
        def filter(self, record):
            return record.levelno == logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_STREAM_HANDLER_FORMAT)
    handler.addFilter(StdOutFilter())
    return handler


def __get_stderr_handler() -> logging.StreamHandler:
    """標準エラー出力用のログハンドラを生成して返す"""
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(_STREAM_HANDLER_FORMAT)
    handler.setLevel(logging.WARNING)
    return handler


def get_debug_logger(
    child_name: Optional[str] = None,
    path: Union[str, Path, None] = None,
    can_append: bool = True
) -> logging.Logger:
    """デバッグ用のロガーを取得する

    Args:
        child_name (Optional[str]):
            子ロガーを設定する場合の識別子.
            Noneの場合は親ロガーを返す.
            デフォルトはNone.
        path (Union[str, Path, None]):
            ロガー生成時に設定するファイルハンドラへのパス.
            未指定の場合、`_DEFAULT_LOG_FILE`
            に設定されているパスになる.
            ロガー取得時は設定していても無視される.
        can_append (bool):
            ファイルハンドラのファイルが既存の場合に追記するか.
            Trueで追記する、Falseだと先頭から上書きになる.
            デフォルトはTrue

    Return:
        logging.Logger: 取得/作成したロガー

    Note:
        もし、ハンドラを追加したいときは、
        本関数で `Logger` インスタンスを取得後に
        呼び出し元で `addHandler` を使用する.
        ハンドラは `logger` モジュールの標準的な手順で生成する.

    Examples:
        >>> import debuglog
        >>> debug_logger = debuglog.get_debug_logger()
        >>> debug_logger.debug("debug")
        >>> debug_logger.info("info")
        INFO\tinfo
        >>> debug_logger.warning("warning")
        WARNING\twarning

    .. code-block:: none
        :linenos:
        :caption: ./log/debug.log

        yyyy-MM-dd hh:mm:ss,xxx	debuglog.py	221	DEBUG	--- Maked RootLogger "debug" -----
        yyyy-MM-dd hh:mm:ss,xxx	<stdin>	1	DEBUG	debug
        yyyy-MM-dd hh:mm:ss,xxx	<stdin>	1	INFO	info
        yyyy-MM-dd hh:mm:ss,xxx	<stdin>	1	WARNING	warning
    """
    # ロガーを取得/作成
    root_logger = logging.getLogger(_DEFAULT_LOGGER_NAME)
    root_logger.setLevel(logging.DEBUG)
    # ハンドラ未設定(初回呼出し)時のみハンドラ設定
    if not root_logger.hasHandlers():
        # 未指定ならカレント下にデフォルト名で作る
        if path is None:
            path = _DEFAULT_LOG_FILE
        # ファイル/ディレクトリがなかったら作る
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.touch()
        # ファイルハンドラを追加
        handler = logging.FileHandler(
            filename=path,
            mode='a' if can_append else 'w',
            encoding='utf-8'
        )
        handler.stream.write('\n')
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(_FILE_HANDLER_FORMAT)
        root_logger.addHandler(handler)
        # info以上はターミナルにも出す
        root_logger.addHandler(__get_stderr_handler())
        root_logger.addHandler(__get_stdout_handler())
        root_logger.debug(
            "--- Maked RootLogger \"{}\" -----".format(root_logger.name)
        )
    if child_name is not None:
        root_logger = root_logger.getChild(child_name)
        root_logger.debug(
            "--- Changed ChildLogger \"{}\" -----".format(root_logger.name)
        )
    return root_logger


def calledlog(func: Function):
    """関数の呼出し開始と終了をデバッグログに出力するデコレータ

    修飾すると `logging.DEBUG` レベルでログファイルに、
    対象関数の呼出し開始と完了のタイミングを出力する.
    また、関数の呼出し開始～完了にかかった時間(≒処理時間)も出力する.

    Args:
        func (Function): 修飾する関数

    Return:
        Function: 修飾したラッパー関数

    Examples:
        >>> import debuglog
        >>> @debuglog.calledlog
        ... def sample():
        ...     print("sample")
        ...
        >>> sample()
        sample

    .. code-block:: none
        :linenos:
        :caption: ./log/debug.log

        yyyy-MM-dd hh:mm:ss,xxx	debuglog.py	223	DEBUG	--- Maked RootLogger "debug" -----
        yyyy-MM-dd hh:mm:ss,xxx	debuglog.py	228	DEBUG	--- Changed ChildLogger "debug.__main__" -----
        yyyy-MM-dd hh:mm:ss,xxx	debuglog.py	245	DEBUG	================================================================================
        yyyy-MM-dd hh:mm:ss,xxx	debuglog.py	246	DEBUG	Started the __main__.sample
        yyyy-MM-dd hh:mm:ss,xxx	debuglog.py	247	DEBUG	--------------------------------------------------------------------------------
        yyyy-MM-dd hh:mm:ss,xxx	debuglog.py	251	DEBUG	--------------------------------------------------------------------------------
        yyyy-MM-dd hh:mm:ss,xxx	debuglog.py	252	DEBUG	Proccessing Time	0:00:00.022490
        yyyy-MM-dd hh:mm:ss,xxx	debuglog.py	253	DEBUG	Terminated the __main__.sample
        yyyy-MM-dd hh:mm:ss,xxx	debuglog.py	254	DEBUG	================================================================================
    """
    def wapper(*args, **kwargs):
        fname = "{}.{}".format(func.__module__, func.__qualname__)
        debug_logger = get_debug_logger(child_name=func.__module__)
        debug_logger.debug(_SEPARATER1)
        debug_logger.debug("Started the {}".format(fname))
        debug_logger.debug(_SEPARATER2)
        startup = dt.now()
        ret = func(*args, **kwargs)
        terminated = dt.now()
        debug_logger.debug(_SEPARATER2)
        debug_logger.debug("Proccessing Time\t{}".format(terminated - startup))
        debug_logger.debug("Terminated the {}".format(fname))
        debug_logger.debug(_SEPARATER1)
        return ret
    return wapper
