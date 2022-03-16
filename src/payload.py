import os
from pathlib import Path
from string import Formatter
from typing import Sequence, Dict

from .menu import Menu
from .argument import Argument


class Payload:
    def __init__(self, path: Path) -> None:
        self._path = path
        
        self._platform = None

        self._cont = ''
        self._args: Sequence[Argument] = []

        self._layout = ''

        self._available = os.listdir(self._path)


    def _read_file(self) -> str:
        with open(Path(self._path, self._platform), 'r', encoding='utf-8') as file:
            return file.read()


    def _read_args(self) -> Sequence[Dict[str, str]]:
        keywords = []
        for key in map(lambda l: l[1], Formatter().parse(self._cont)):
            if key not in keywords and key is not None:
                keywords.append(key)
        return [Argument(key) for key in keywords]


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