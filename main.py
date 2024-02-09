#!/usr/bin/env python3
import logging
from pathlib import Path

from centox.console import Logger
from centox.handler import Handler


def main() -> None:
    working_dir = Path(__file__).resolve().parent
    
    logo_path = Path(working_dir, "assets/logo.txt")
    with open(logo_path, "r", encoding="utf8") as file:
        print("\x1b[36m%s\x1b[0m" % file.read())

    handler = Handler(working_dir)
    handler.run()


if __name__ == "__main__":
    Logger.init(logging.DEBUG)

    try:
        main()
    except Exception as e:
        logging.error(e)