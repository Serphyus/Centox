import sys
from tabulate import tabulate
from typing import Sequence


class Console:
    @staticmethod
    def _log_msg(symbol: str, color: str, msg: str) -> str:
        return '\x1b[%sm[%s]\x1b[0m %s' % (color, symbol, msg)


    @classmethod
    def error_msg(cls, msg: str, exit_call: bool = False) -> None:
        print(cls._log_msg('-', '91', msg))
        if exit_call:
            sys.exit()


    @classmethod
    def warning_msg(cls, msg: str) -> None:
        print(cls._log_msg('!', '93', msg))


    @classmethod
    def debug_msg(cls, msg: str) -> None:
        print(cls._log_msg('*', '96', msg))


    @staticmethod
    def clear_screen() -> None:
        print('\x1b[H\x1b[2J\x1b[3J', end='')
    

    @staticmethod
    def create_table(
            keys: Sequence[str],
            table: Sequence[Sequence[str]]
        ) -> str:

        allignment = []
        if table:
            for _ in keys:
                allignment.append('left')

        return tabulate(
            table, keys,
            colalign=allignment
        )