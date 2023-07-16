import os
import sys
import logging
import subprocess
from pathlib import Path
from shutil import rmtree

from centox.console import Logger


def exec_cmd(command: str) -> None:
    process = subprocess.Popen(
        command.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    return process


def install_dependencies(working_dir: Path) -> None:
    logging.debug("installing required packages")

    # install all required packages using apt
    proc = exec_cmd("apt-get install -y python3 python3-pip")
    proc.wait()

    # check if required the packages is installed
    for executable in ["python3", "pip3"]:
        if not exec_cmd(f"which {executable}").stdout.read():
            logging.error("unable to install all dependencies")
            sys.exit()

    # set the requiremments path
    requirements_path = Path(working_dir, "requirements.txt")
    
    # install required packages
    logging.debug("installing python requirements")
    proc = exec_cmd("pip3 install -r %s" % requirements_path)
    proc.wait()


def install_centox(working_dir: Path) -> None:
    # set path to centox program
    centox_dest = Path("/usr/share/centox")

    # remove currently installed centox
    if centox_dest.is_dir():
        logging.warning("replacing current centox installation")
        rmtree(centox_dest)

    logging.debug("installing centox to /usr/share/centox")
    
    # create the centox directory
    centox_dest.mkdir()

    # copies all required files to the centox dir using
    # the -p argument to preserve all current attributes
    exec_cmd("cp -rp {0}/assets {0}/centox {0}/main.py {1}".format(working_dir, centox_dest))
    
    # create executable file
    with open("/usr/bin/centox", "w") as file:
        file.write("#!/bin/sh\npython3 /usr/share/centox/main.py")

    # give correct file permissions
    exec_cmd("chmod 755 /usr/bin/centox")
    exec_cmd("chmod -R 755 /usr/share/centox")

    logging.debug("Centox installed successfully")


def setup(working_dir: Path):
    install_dependencies(working_dir)
    install_centox(working_dir)


if __name__ == "__main__":
    Logger.init(logging.DEBUG)

    # make sure setup.py is run as root
    if os.geteuid() != 0:
        logging.critical("must run setup.py as root")
        sys.exit()

    setup(Path(__file__).resolve().parent)