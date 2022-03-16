import os
from typing import Any, Sequence

from .console import Console
from .argument import Argument

class Menu:
    def __init__(self,
            keys: Sequence[str],
            options: Sequence[list],
            item_padding: int = 2,
            side_padding: int = 3,
            exit_option: str = None,
        ) -> None:

        self._item_padding = item_padding
        self._side_padding = side_padding

        self._keys = keys
        self._options = []
        
        self._exit_option = exit_option

        self._set_options(*options)


    def _update_paddings(self) -> None:
        self._opt_spacing = [*map(lambda s: len(s), self._keys)]

        for opt in self._options:
            paddings = [*map(lambda s: len(str(s)), opt)]
            
            for index, padding in enumerate(paddings):
                if isinstance(padding, Argument):
                    padding.current

                if padding > self._opt_spacing[index]:
                    self._opt_spacing[index] = padding
        
        self._number_space = len(str(len(self._options))) + 3


    def _update_separator(self) -> None:
        sep_len = self._number_space
        
        sep_len += sum(self._opt_spacing)
        sep_len += len(self._keys) * self._item_padding

        self._menu_separator = ('=' * sep_len)


    def _set_options(self, *options):
        for opt in options:
            self._options.append(opt)
        
        self._update_paddings()
        self._update_separator()


    def _add_side_padding(self, extra: int = 0) -> None:
        Console.move_forward(self._side_padding + extra)


    def _output_menu_top(self) -> None:
        top_menu = ' ' * self._number_space
        for index, key in enumerate(self._keys):
            offset = (self._opt_spacing[index] + self._item_padding)
            top_menu += f'{key:<{offset}}'
        
        self._add_side_padding()
        print(top_menu)
        self._add_side_padding()
        print(self._menu_separator)


    def _output_option(self, number: int, option: Sequence[str]) -> None:
        self._add_side_padding()

        Console.save_pos()
        print('\033[36m[\033[93m%s\033[36m]\033[0m' % number, end='')
        Console.load_pos()

        Console.move_forward(self._number_space)

        for index, val in enumerate(option):
            if isinstance(val, bool):
                color = '92' if val else '91'
                val = '\033[%sm%s\033[0m' % (color, val)

            Console.save_pos()
            print(val, end='')
            Console.load_pos()

            offset = (self._opt_spacing[index] + self._item_padding)
            Console.move_forward(offset)

        print()


    def _output_menu(self) -> None:
        self._output_menu_top()
        
        for index, opt in enumerate(self._options):
            self._output_option(index + 1, opt)
        
        if self._exit_option is not None and len(self._keys):
            print()
            option = [self._exit_option]# + ["" for _ in range(len(self._keys)-1)]
            self._output_option(len(self._options) + 1, option)
        
        print()

    
    def prompt(self) -> Any:
        Console.clear_screen()
        Console.output_logo()

        self._output_menu()

        prompt = (' ' * self._side_padding) + 'Choice: '

        valid_range = len(self._options)

        while True:
            user_input = input(prompt)

            reset = int((len(user_input) + len(prompt)) / os.get_terminal_size()[0])
            Console.reset_lines(reset)

            if user_input.isdigit():
                index = int(user_input) - 1

                if index in range(valid_range):
                    return index

                elif self._exit_option is not None:
                    if index == valid_range:
                        return None