import os
import re
from pathlib import Path
from string import Formatter
from typing import Sequence, Dict

from .menu import Menu
from .argument import Argument


class Payload:
    def __init__(self, path: Path, default_args={"delay": "500"}) -> None:
        self._path = path
        
        self._platform = None

        self._cont = ''
        self._args = []

        self._layout = ''

        self._available = os.listdir(self._path)

        self._default_args = default_args


    def _read_file(self) -> str:
        with open(Path(self._path, self._platform), 'r', encoding='utf-8') as file:
            return file.read()


    def _read_args(self) -> Sequence[Dict[str, str]]:
        # a list of all kwargs which will
        # be used to create Argument objects
        payload_kwargs = []
        
        # a list of already assigned keys
        assigned_keys = []

        # loop through each formattable keyword inside {...}
        for key in map(lambda l: l[1], Formatter().parse(self._cont)):
            
            # check that the key does not repeat or is None
            if key not in assigned_keys and key is not None:
                # set a kwarg to store the new value in                
                kwargs = {'name': '', 'value': ''}

                # set key name
                kwargs['name'] = key
                
                # set default args
                if key in self._default_args:
                    kwargs['value'] = self._default_args[key]

                # store the kwargs
                payload_kwargs.append(kwargs)
                
                # add the assigned key so it does not repeat
                assigned_keys.append(key)

        print(payload_kwargs)

        # return all argument created with the kwargs
        return [Argument(**kwargs) for kwargs in payload_kwargs]


    @property
    def args(self) -> Sequence[Argument]:
        return self._args


    @property
    def layout(self) -> str:
        return self._layout


    def set_platform(self) -> None:
        keys = ['Platform']
        options = [[platform] for platform in self._available]

        menu = Menu(keys, options)
        self._platform = self._available[menu.prompt()]

        self._cont = self._read_file()
        self._args = self._read_args()
    

    def set_arguments(self) -> None:
        looped = True
        while looped:
            # the menu needs to be re initialized each
            # time the arguments values are updated
            options = [[arg.name, arg.value] for arg in self._args]

            menu = Menu(
                ['Argument', 'Value'],
                options,
                exit_option="Generate"
            )

            choice = menu.prompt()

            if choice is None:
                return
            
            self._args[choice].prompt()
    

    def set_layout(self) -> None:
        # import layouts here to avoid partial initialized moule
        from .generator import LAYOUTS

        # create a list of layout options
        options = [[layout] for layout in LAYOUTS]

        # create menu and prompt user
        menu = Menu(["Keyboard Layout"], options)
        choice = menu.prompt()

        self._layout = LAYOUTS[choice]
    

    def parse(self) -> str:
        # format the arguments to the script and return it
        kwargs = {arg.name: arg.value for arg in self._args}
        return self._cont.format(**kwargs)