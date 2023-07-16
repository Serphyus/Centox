#!/usr/bin/env python3
import logging
from pathlib import Path

from centox.console import Logger
from centox.handler import Handler


def output_logo(working_dir: Path) -> None:
    with open(Path(working_dir, "assets/logo.txt"), "r", encoding="utf8") as file:
        print("\x1b[36m%s\x1b[0m" % file.read())


def main(working_dir: Path) -> None:
    output_logo(working_dir)

    logging.debug("initializing payload handler")
    handler = Handler(working_dir)
    
    logging.debug("starting payload handler")
    handler.run()


if __name__ == "__main__":
    Logger.init(logging.DEBUG)

    main(Path(__file__).resolve().parent)