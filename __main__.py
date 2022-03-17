import os
import sys

from typing import Union

import psutil
from shutil import copy
from pathlib import Path
from tempfile import TemporaryDirectory

from src.menu import Menu
from src.payload import Payload
from src.console import Console
from src.generator import Generator


def check_dependencies() -> None:
    dependencies = ['java']

    delimeter = ';' if sys.platform == 'win32' else ':'
    env_paths = os.environ['PATH'].split(delimeter)

    for executable in dependencies:
        if sys.platform == 'win32':
            executable += '.exe'

        if not any(map(lambda p: Path(p, executable).is_file(), env_paths)):
            Console.error_msg('unable to locate: %s\n' % executable, True)


def get_payload(abs_path: Path) -> Payload:
    # set the directory where payloads are located
    payload_dir = Path(abs_path, 'assets', 'payloads')

    # set the menu keys to display metadata
    # about each payload stored in options
    keys = ['Payload', 'Windows', 'MacOS', 'Linux']
    options = []
    
    # store path to each payload dir
    payload_paths = []
    for sub_path in os.listdir(payload_dir):
        payload_paths.append(Path(payload_dir, sub_path))
    
    # convert payload dir paths to options 
    for path in payload_paths:
        sub_folders = os.listdir(path)

        paylaod = [
            path.name,
            'Windows' in sub_folders,
            'MacOS' in sub_folders,
            'Linux' in sub_folders
        ]
        
        options.append(paylaod)
    
    # create menu and prompt user
    menu = Menu(keys, options)
    choice = menu.prompt()

    # return the selected payload
    return Payload(payload_paths[choice])


def get_injection_output() -> Path:
    
    # get a list of each partition mount point and name
    keys = ["Partition", "Mount Point"]
    options = []

    # add each partition and mountpoint to options    
    for partition in psutil.disk_partitions():
        options.append([partition.device, partition.mountpoint]) 

    # create menu and prompt user
    menu = Menu(keys, options)
    choice = menu.prompt()

    # return the mount point path with an inject.bin
    return Path(options[choice][1], 'inject.bin')


def generate_payload(payload: Payload, output: str) -> None:
    # clear screen and output logo
    Console.clear_screen()
    Console.output_logo()

    # set path to ducky script encoder
    encoder_path = Path(abs_path, 'assets', 'encoder', 'encoder.jar')

    # create a generator object to
    # generate the final payload and
    # store it to the output path
    generator = Generator(
        encoder_path,
        payload,
        output
    )

    generator.generate()

    input('\nPress enter to return')


def main(abs_path: Path) -> None:
    # checks for dependencies
    check_dependencies()

    payload = get_payload(abs_path)

    # set platform for payload to use
    payload.set_platform()
    
    # set arguments for payload
    payload.set_arguments()

    # select layout for payload
    payload.set_layout()

    output = get_injection_output()

    # generate payload
    generate_payload(payload, output)


if __name__ == '__main__':
    # get abs path of running python file
    abs_path = Path(__file__).resolve().parent

    # set abs_path in console for it to be
    # able to read and display the logo file
    Console.abs_path = abs_path

    # run main and catch ctrl-c keyboard interruptions
    try:
        main(abs_path)
    except KeyboardInterrupt:
        print()
        Console.error_msg('keyboard interrupt')