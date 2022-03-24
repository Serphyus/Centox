import os
import sys
from pathlib import Path

from src.handler import Handler
from src.console import Console


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

    # set abs_path in console for it to be able
    # to read and read and display the logo file
    Console.abs_path = abs_path

    # clear screen and output logo
    Console.clear_screen()
    Console.output_logo()

    # run main method
    main(abs_path)