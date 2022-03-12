import os
import re
from typing import Any, Sequence

from .console import Console
from .section import Section


class Menu:
    def __init__(self,
            keys: Sequence[str],
            sections: Sequence[Section],
            item_padding: int = 2,
            side_padding: int = 3,
        ) -> None:

        # counter for how many lines to return
        # when outputting the sections
        self._total_lines = 0

        # item padding will set a space padding
        # between each section padding to avoid
        # blending sections or keys together
        self._item_padding = item_padding
        
        # side padding will be the menus
        # x offset from the left side
        self._side_padding = side_padding

        self._keys = keys
        
        self._sections = []
        self._dividers = []
        
        self.add_sections(*sections)


    def _strip_ascii(self, string: str) -> str:
        regex = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
        return regex.sub('', string)


    def _update_paddings(self) -> None:
        # first set the sector_space
        self._sect_size = [*map(lambda s: len(s), self._keys)]

        for sect in self._sections:
            for index, padding in enumerate(sect.paddings):
                if padding > self._sect_size[index]:
                    self._sect_size[index] = padding
        
        self._number_space = len(str(len(self._sections))) + 3


    def _update_separator(self) -> None:
        # start value at 4 to account for
        # the space taken by number section
        sep_len = self._number_space
        
        sep_len += sum(self._sect_size)
        sep_len += len(self._keys) * self._item_padding

        self._menu_separator = ('=' * sep_len)


    def add_sections(self, *sections: Section):
        for sect in sections:
            if sect is None:
                self._dividers.append(len(self._sections)-1)
            
            else:
                self._sections.append(sect)
        
        self._update_paddings()
        self._update_separator()


    def _add_side_padding(self, extra: int = 0) -> None:
        Console.move_forward(self._side_padding + extra)


    def _output_menu_top(self) -> None:
        self._total_lines += 2

        top_menu = ' ' * self._number_space
        for index, key in enumerate(self._keys):
            offset = (self._sect_size[index] + self._item_padding)
            top_menu += f'{key:<{offset}}'
        
        self._add_side_padding()
        print(top_menu)
        self._add_side_padding()
        print(self._menu_separator)


    def _output_section(self, number: int, section: Sequence[str]) -> None:
        self._add_side_padding()

        Console.save_pos()
        print('\033[36m[\033[93m%s\033[36m]\033[0m' % number, end='')
        Console.load_pos()

        Console.move_forward(self._number_space)

        for index, val in enumerate(section.contents):
            Console.save_pos()
            print(val, end='')
            Console.load_pos()

            offset = (self._sect_size[index] + self._item_padding)
            Console.move_forward(offset)

        print()


    def _output_menu(self) -> None:
        Console.reset_lines(self._total_lines)
        self._total_lines = 0

        self._output_menu_top()
        for index, sect in enumerate(self._sections):
            self._output_section(index + 1, sect)
            self._total_lines += 1
            
            if index in self._dividers:
                self._add_side_padding(self._number_space)

                item_padding = len(self._keys) * self._item_padding

                print('-' * (sum(self._sect_size) + item_padding))
                self._total_lines += 1
        
        print()


    def prompt(self, prefix: str) -> Any:
        Console.hide_cursor()
        self._output_menu()
        Console.show_cursor()

        prompt = (' ' * self._side_padding) + '%s ' % prefix
        self._total_lines += 2

        while True:
            user_input = input(prompt)

            if user_input.isdigit():
                index = int(user_input) - 1

                if index == len(self._sections):
                    Console.reset_lines(self._total_lines)
                    return

                if index in range(len(self._sections)):
                    return self._sections[index].call()

            reset = 1 + int((len(user_input) + len(prompt)) / os.get_terminal_size()[0])
            Console.reset_lines(reset)