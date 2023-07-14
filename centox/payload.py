import json
import logging
from pathlib import Path
from contextlib import suppress
from typing import Any, Dict


class Payload:
    def __init__(self, payload_dir: Path) -> None:
        self._typing_delay = 0
        self._typing_delay_offset = 0
        self._payload_dir = payload_dir

        self.reset()


    def reset(self) -> None:
        with open(Path(self._payload_dir, "manifest.json"), "r") as file:
            self._manifest = json.load(file)
        
        with open(Path(self._payload_dir, "payload"), "r") as file:
            self._raw_payload = file.read()


    @property
    def raw(self) -> str:
        return self._raw_payload

    @property
    def description(self) -> str:
        return self._manifest["description"]


    @property
    def require_admin(self) -> bool:
        return self._manifest["require_admin"]

    
    def set_arg(self, arg: str, value: str) -> None:
        if arg not in self._manifest["args"]:
            logging.error(f"{arg} is not a valid argument")
            return

        self._manifest["args"][arg] = value


    def get_args(self) -> Dict[str, str]:
        return self._manifest["args"]