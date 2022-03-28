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
    Console.debug_msg('installing required packages')

    # install all required packages using apt
    proc = exec_cmd('apt-get install -y python3 python3-pip default-jdk')
    proc.wait()

    # check if required the packages is installed
    for executable in ['java', 'python3', 'pip3']:
        if not exec_cmd('which %s' % executable).stdout.read():
            Console.error_msg('unable to install java openjdk', True)

    # set the requiremments path
    requirements_path = Path(abs_path, 'requirements.txt')
    
    # install required packages
    Console.debug_msg('installing python requirements')
    proc = exec_cmd('pip3 install -r %s' % requirements_path)
    proc.wait()


def install_centox(abs_path: Path) -> None:
    # set path to centox program
    centox_dest = Path('/usr/share/centox')

    # remove currently installed centox
    if centox_dest.is_dir():
        Console.warning_msg('replacing current centox installation')
        rmtree(centox_dest)

    Console.debug_msg('installing centox to /usr/share/centox')
    
    # create the centox directory
    centox_dest.mkdir()

    # copies all files to the centox directory using
    # the -p argument to preserve current attributes
    exec_cmd('cp -rp %s/* %s' % (abs_path, centox_dest))
    
    # create executable file
    with open('/usr/bin/centox', 'w') as file:
        file.write('#!/bin/sh\npython3 /usr/share/centox/centox.py')

    # give centox executable priviliges
    exec_cmd('chmod +rx /usr/bin/centox')

    Console.debug_msg('Centox installed successfully')


def main(abs_path: Path):
    install_dependencies(abs_path)
    install_centox(abs_path)


if __name__ == '__main__':
    # make sure setup.py is run as root
    if os.geteuid() != 0:
        Console.error_msg('must run setup.py as root', True)

    # get current python version
    version = tuple(map(int, platform.python_version_tuple()[:2]))
    
    # check if python version is 3.9 or higher
    if version[0] < 3 or version[1] < 9:
        Console.error_msg('centox requires python 3.9 or higher', True)

    main(Path(__file__).resolve().parent)