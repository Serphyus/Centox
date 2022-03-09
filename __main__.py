import os
import sys
import subprocess
from string import Formatter
from typing import Type, Callable, Sequence, Union

import psutil
from shutil import copy
from pathlib import Path
from tempfile import TemporaryDirectory


keyboard_layouts = [
    'be', 'br', 'ca', 'ch', 'de',
    'dk', 'es', 'fi', 'fr', 'gb',
    'hr', 'it', 'no', 'pt', 'ru',
    'si', 'sv', 'tr', 'us'
]


class Console:
    abs_path: Path


    @classmethod
    def output_logo(cls) -> None:
        with open(Path(cls.abs_path, 'assets/logo.txt'), 'r', encoding='utf8') as file:
            print('\033[2J\033[H\033[36m%s\033[0m' % file.read())


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


    @staticmethod
    def reset_lines(lines: int) -> None:
        print('\033[%sA\033[0J' % lines, end='')


    @staticmethod
    def show_help(msg: str) -> None:
        print('\n[Help Menu]\n'+ msg)
        input('\nPress enter to return')


    @classmethod
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

        return user_input-1


def check_dependencies() -> None:
    dependencies = ['java']

    delimeter = ';' if sys.platform == 'win32' else ':'
    env_paths = os.environ['PATH'].split(delimeter)

    for executable in dependencies:
        if sys.platform == 'win32':
            executable += '.exe'

        if not any(map(lambda p: Path(p, executable).is_file(), env_paths)):
            Console.error_msg('unable to locate: %s\n' % executable, True)


def get_payload(payload_path: Path) -> str:
    available = os.listdir(payload_path)
    selected = Console.menu_input('Choose a Payload', available)

    selected_payload = Path(payload_path, available[selected])

    platforms = [p for p in os.listdir(selected_payload) if Path(selected_payload, p).is_file()]
    choice = Console.menu_input('Choose target', platforms, 'Choose a platform to target')

    return Path(selected_payload, platforms[choice])


def get_layout() -> str:
    help_msg = 'Available layouts:\n'
    help_msg += ', '.join(keyboard_layouts)
    
    layout = Console.get_input('Layout: ', str, 'Choose keyboard layout', help_msg,
                       lambda l: l in keyboard_layouts)
    
    return layout


def create_payload_injection(payload_path: Path) -> str:
    with open(payload_path, 'r') as file:
        payload = file.read()
    
    keywords =  set([arg for (_, arg, _, _) in Formatter().parse(payload) if arg])

    values = []
    for key in keywords:
        value = Console.get_input('%s: ' % key.capitalize(),
                                    str, "Provide arguments",
                                    validate=lambda s: bool(s))
        
        values.append(value)
    
    return payload.format(**dict(zip(keywords, values)))


def generate_injection(
        layout: str,
        input_path: Path,
        output_path: Path = None
    ) -> None:
    
    bin_path = Path(abs_path, 'assets', 'encoder', 'encoder.jar')
    
    if output_path.is_file():
        Console.warning_msg('overwriting existing inject.bin')
        os.remove(output_path)
    
    process = subprocess.Popen(
        'java -jar %s -l %s -i %s -o %s' % (bin_path, layout, input_path, output_path),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )

    process.wait()

    if not output_path.is_file():
        Console.error_msg('unable to generate inject.bin')
        return

    Console.event_msg('injection compiled successfully -> %s' % output_path)


def get_inject_output() -> Union[Path, None]:
    help_msg = 'Select mount point for deploying inject.bin'

    mounts = [*map(lambda p: p.mountpoint, psutil.disk_partitions())]
    choice = Console.menu_input('Choose mount point', mounts, help_msg)

    return Path(mounts[choice], 'inject.bin')


def main(abs_path: Path) -> None:
    check_dependencies()

    tmp_dir = TemporaryDirectory()

    while True:
        payload_path = get_payload(Path(abs_path, 'assets', 'payloads'))
        layout = get_layout()

        script = create_payload_injection(payload_path)
        inject_output = get_inject_output()

        Console.output_logo()

        injection_path = Path(tmp_dir, 'injection')
        with open(tmp_dir, 'w') as file:
            file.write(script)

        generate_injection(layout, injection_path, inject_output)
        
        input('\nPress enter to return')


if __name__ == '__main__':
    abs_path = Path(__file__).resolve().parent
    
    Console.abs_path = abs_path

    try:
        main(abs_path)
    except KeyboardInterrupt:
        print()
        Console.error_msg('keyboard interrupt')