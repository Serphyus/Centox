import os
import sys
from pathlib import Path

from src.handler import Handler
from src.console import Console


def output_logo(abs_path: Path) -> None:
    with open(Path(abs_path, 'assets', 'logo.txt'), 'r', encoding='utf8') as file:
        print('\033[H\033[36m%s\033[0m' % file.read())


def check_dependencies() -> None:
    dependencies = ['java']

    delimeter = ';' if sys.platform == 'win32' else ':'
    env_paths = os.environ['PATH'].split(delimeter)

    Console.debug_msg('checking dependencies')
    for executable in dependencies:
        if sys.platform == 'win32':
            executable += '.exe'

        if not any(map(lambda p: Path(p, executable).is_file(), env_paths)):
            Console.error_msg('unable to locate: %s\n' % executable, True)


def main(abs_path: Path) -> None:
    # checks for dependencies
    check_dependencies()

    # create the handler
    Console.debug_msg('creating payload handler')
    handler = Handler(abs_path)

    # run the handler
    Console.debug_msg('starting payload handler')
    handler.run()


if __name__ == '__main__':
    # get abs path of running python file
    abs_path = Path(__file__).resolve().parent

    # clear screen and output logo
    Console.clear_screen()
    output_logo(abs_path)

    # run main method
    main(abs_path)