from pathlib import Path
from string import Formatter
from typing import Dict, Sequence


class Payload:
    def __init__(self, path: Path, defaults: dict) -> None:
        self._path = path
        self._defaults = defaults
        
        # read file content and find all its keyowrds
        self._content = self._read_file()
        self._kwargs = self._read_kwargs()


    def _read_file(self) -> str:
        # reads the payload file
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

                value = self._defaults.get(key, '')
                if value:
                    value = value['default']
                kwargs[key] = value

        # return all argument created with the kwargs
        return kwargs


    @property
    def path(self) -> Path:
        return self._path


    @property
    def kwargs(self) -> Dict[str, str]:
        return self._kwargs
    

    def parse(self) -> Sequence[str]:
        final_kwargs = {}

        # check if any of the payloads arguments matches any
        # default argument that contains assigned values and
        # update their value for the final_kwargs.
        for key, value in self._kwargs.items():
            if key in self._defaults:
                if self._defaults[key]['values'] is not None:
                    value = self._defaults[key]['values'][value]
            final_kwargs[key] = value

        # create a list that will contain each line
        # of the payload after removing the comments
        payload_lines = []
        
        # looop through formatted payload lines
        for line in self._content.format(**final_kwargs).splitlines():
            if not line.startswith('REM '):
                payload_lines.append(line)

        return payload_lines