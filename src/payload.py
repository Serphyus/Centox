import os
from pathlib import Path
from string import Formatter
from typing import Dict


class Payload:
    def __init__(self, path: Path, defaults_args: dict) -> None:
        self._path = path
        self._default_args = defaults_args
        
        # read file content and find all its keyowrds
        self._content = self._read_file()
        self._kwargs = self._read_kwargs()


    def _read_file(self) -> str:
        with open(Path(self._path), 'r', encoding='utf-8') as file:
            return file.read()


    def _read_kwargs(self) -> Dict[str, str]: # add checking for payload args and boolean args ba>pa
        # a list which holds all kwargs
        kwargs = {}

        # loop through each formattable keyword inside {...}
        for key in map(lambda l: l[1], Formatter().parse(self._content)):
            # check that the key does not repeat or is None
            if key not in kwargs and key is not None:
                # check if keyword value exist in default_args
                # and set it as the kwargs[key] else ''
                kwargs[key] = self._default_args.get(key, '')

        # return all argument created with the kwargs
        return kwargs


    @property
    def path(self) -> Path:
        return self._path


    @property
    def kwargs(self) -> Dict[str, str]:
        return self._kwargs
    

    def parse(self) -> str:
        # format the file content with the kwargs
        # and return the formatted file content
        return self._content.format(**self._kwargs)