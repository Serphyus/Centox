import sys
import atexit
from pathlib import Path


class Console:
    abs_path: Path


    @classmethod
    def output_logo(cls) -> None:
        with open(Path(cls.abs_path, 'assets/logo.txt'), 'r', encoding='utf8') as file:
            print('\033[H\033[36m%s\033[0m' % file.read())


    @staticmethod
    def _log_msg(symbol: str, color: str, msg: str) -> str:
        return '\033[%sm[%s]\033[0m %s' % (color, symbol, msg)


    @classmethod
    def error_msg(cls, msg: str, exit_call: bool = False) -> None:
        print(cls._log_msg('-', '91', msg))
        if exit_call:
            sys.exit()


    @classmethod
    def warning_msg(cls, msg: str) -> None:
        print(cls._log_msg('!', '93', msg))


    @classmethod
    def event_msg(cls, msg: str) -> None:
        print(cls._log_msg('*', '94', msg))


    @classmethod
    def hide_cursor(cls) -> None:
        print('\033[?25l', end='')
        atexit.register(cls.show_cursor)


    @classmethod
    def show_cursor(cls) -> None:
        print('\033[?25h', end='')
        atexit.unregister(cls.show_cursor)

    
    @staticmethod
    def save_pos() -> None:
        print('\0337', end='')


    @staticmethod
    def load_pos() -> None:
        print('\0338', end='')


    @staticmethod
    def move_forward(spaces: int) -> None:
        print('\033[%sC' % spaces, end='')


    @staticmethod
    def reset_lines(lines: int) -> None:
        print('\033[%sA\033[0J' % lines, end='')


    @staticmethod
    def clear_screen() -> None:
        print('\033[2J', end='')