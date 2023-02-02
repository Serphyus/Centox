#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from centox.handler import Handler
from centox.console import Console


def output_logo(abs_path: Path) -> None:
    # outputs the logo in cyan colors
    with open(Path(abs_path, 'assets', 'logo.txt'), 'r', encoding='utf8') as file:
        print('\x1b[36m%s\x1b[0m' % file.read())


def check_dependencies() -> None:
    dependencies = ['java']

    # get a list of all environmen paths
    env_paths = os.environ['PATH'].split(':')

    # checks dependencies and gives outputs
    # an error message when one is missing
    Console.debug_msg('checking dependencies')
    for executable in dependencies:
        # checks if any of the paths in the environment
        # variable PATH has the dependency file in it
        if not any(map(lambda p: Path(p, executable).is_file(), env_paths)):
            Console.error_msg('unable to locate: %s\n' % executable)
            sys.exit()


def main(abs_path: Path) -> None:
    check_dependencies()

    # create the handler
    Console.debug_msg('creating payload handler')
    handler = Handler(abs_path)

    # run the handler
    Console.debug_msg('starting payload handler')
    handler.run()


if __name__ == '__main__':
    # check if python version is 3.9 or higher
    if sys.version_info.major < 3 or sys.version_info.minor < 9:
        Console.error_msg('centox requires python 3.9 or higher', True)

    # get abs path of running python file
    abs_path = Path(__file__).resolve().parent

    # output the logo
    output_logo(abs_path)

    # run main method
    main(abs_path)