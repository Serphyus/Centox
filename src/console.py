import sys
import atexit
from pathlib import Path
from typing import Callable, Sequence


KEY_BREAK = 3
KEY_BACKSPACE = 8
KEY_ENTER = 10
KEY_ESC = 27
KEY_SPACE = 32
KEY_DOWN = 258
KEY_UP = 259


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


    """@classmethod
    def get_input(cls,
            prompt: str,
            type: Type = str,
            prefix: str = None,
            help_msg: str = None,
            validate: Callable[[str], Type] = None,
            prefix_div: bool = True,
            reset_screen: bool = True
        ) -> object:

        if reset_screen:
            cls.output_logo()

        if prefix is not None:
            if prefix_div:
                prefix += '\n%s' % ('='*len(prefix))
            print(prefix+'\n')
        
        while True:
            try:
                user_input = input(prompt).strip()

                if user_input.lower() in ['?', 'help']:
                    if help_msg is None:
                        help_msg = 'No help msg'
                    
                    cls.show_help(help_msg)
                    cls.reset_lines(help_msg.count('\n') + 6)

                    continue

                user_input = type(user_input)

                if validate is not None:
                    if not validate(user_input):
                        cls.reset_lines(1)
                        continue

                return user_input
            except Exception:
                cls.reset_lines(1)
                continue


    @classmethod
    def menu_input(cls, title: str, options: Sequence[str], help_msg: str = None) -> object:
        prefix = '%s\n%s\n' % (title, '='*len(title))
        for index, opt in enumerate(options):
            prefix += '\n [%s] %s' % (index+1, opt)

        user_input = cls.get_input('Choice: ', int, prefix, help_msg,
                                   lambda i: i-1 in range(len(options)),
                                   prefix_div=False)

        return user_input-1"""