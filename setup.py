import os
import platform
import subprocess
from pathlib import Path
from shutil import rmtree
from src.console import Console


def exec_cmd(command: str) -> None:
    # creates a subprocess with piped
    # stdout and stderr io streams
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )

    return process


def install_dependencies(abs_path: Path) -> None:
    # set the requiremments path
    requirements_path = Path(abs_path, 'requirements.txt')
    
    # install required packages
    Console.debug_msg('installing python requirements')
    proc = exec_cmd('python3 -m pip -r %s' % requirements_path)
    proc.wait()


def install_centox(abs_path: Path) -> None:
    # set path to centox program
    centox_dest = Path('/usr/share/centox')

    # remove currently installed centox
    if centox_dest.is_dir():
        Console.warning_msg('replacing current centox install')
        rmtree(centox_dest)

    Console.debug_msg('installing centox to /usr/share/centox')
    
    # create the centox directory
    centox_dest.mkdir()

    # copies all files to the centox directory using
    # the -p argument to preserve current attributes
    exec_cmd('cp -rp %s/* %s' % (abs_path, centox_dest))
    
    # create bin file
    with open('/usr/bin/centox', 'w') as file:
        file.write('#!/bin/sh\npython3 /usr/share/centox/centox.py')

    # give centox executable priviliges
    exec_cmd('chmod +rx /usr/bin/centox')

    Console.debug_msg('Centox isntalled successfully')


def main(abs_path: Path):
    install_dependencies(abs_path)
    install_centox(abs_path)


if __name__ == '__main__':
    if os.geteuid() != 0:
        Console.error_msg('must run setup.py as root', True)

    # get current python version
    version = tuple(map(int, platform.python_version_tuple()[:2]))
    
    # check if python version is 3.9 or higher
    if version[0] < 3 or version[1] < 9:
        Console.error_msg('centox requires python 3.9 or higher', True)

    main(Path(__file__).resolve().parent)