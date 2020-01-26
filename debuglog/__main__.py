# !/usr/bin/env/ python3
# -*- coding: utf-8 -*-


import json
import argparse
from pathlib import Path


def load_configs():
    json_path = Path(__file__).parent / "config.json"

    class ConfigView:
        def __init__(self, d):
            self.__dict__ = d

    with json_path.open() as f:
        configs = ConfigView(json.load(f))
    return configs


def rm_logfile(args):
    """既存のログファイルを削除する"""
    yes_ptns = ('y', "yes")
    no_ptns = ('n', "no")
    # 確認省略のオプションがoffなら確認する
    if not args.yes:
        print("{}を削除してよろしいですか？(Y/n)".format(args.path.resolve()))
        while True:
            ans = input(">>>")
            if ans in yes_ptns:
                break
            elif ans in no_ptns:
                print("中止しました")
                return
            else:
                print("Yesなら\"{}\", Noなら\"{}\"のいずれかを入力してください".format(
                    yes_ptns, no_ptns
                ))
    if args.path.exists():
        args.path.unlink()
        print("削除しました")
    else:
        print("ログファイル\"{}\"が存在しません".format(args.path))


def main():
    # 
    configs = load_configs()
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers()
    # 既存ログ削除用のパーサ
    rm_parser = sub_parsers.add_parser("rm", help="see rm -h")
    rm_parser.set_defaults(handler=rm_logfile)
    rm_parser.add_argument(
        "-p", "--path", type=Path,
        default=Path(configs.DEFAULT_LOG_DIR) / configs.DEFAULT_LOG_FILE
    )
    rm_parser.add_argument("-y", "--yes", action="store_true")
    # モードに応じて実行
    args = parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
