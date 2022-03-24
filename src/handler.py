import os
from pathlib import Path
from configparser import ConfigParser
from tabulate import tabulate
from typing import Sequence

from .console import Console
from .payload import Payload
from .compiler import Compiler


class Handler:
    def __init__(self, abs_path: Path) -> None:
        self._abs_path = abs_path        
        
        # defaults selected payload to None
        self._current_payload: Payload = None

        # set directory where payloads are stored
        self._payload_dir = Path(self._abs_path, 'assets', 'payloads')

        # locate all available payloads and remove the prefix
        Console.debug_msg('locating available payloads')
        
        self._available_payloads = []
        for path in self._locate_payloads(self._payload_dir):
            self._available_payloads.append(path.relative_to(self._payload_dir))

        # load defaults.ini file
        Console.debug_msg('loading defaults config')
        self._defaults = self._load_defaults()

        # create compiler for payloads
        self._compiler = Compiler(Path(self._abs_path, 'assets', 'bin', 'encoder.jar'))


    def _load_defaults(self) -> None:
        defaults_path = Path(self._abs_path, 'assets', 'defaults.ini')
        
        if not defaults_path.is_file():
            Console.error_msg('unable to locate file: %s' % defaults_path.name, True)
        
        parser = ConfigParser()
        with open(defaults_path, 'r') as file:
            parser.read_file(file)

        return parser._sections


    def _locate_payloads(self, prefix: Path) -> list:
        files = []
        for sub_name in os.listdir(prefix):
            sub_path = Path(prefix, sub_name)
            if sub_path.is_file():
                files.append(sub_path)
            elif sub_path.is_dir():
                files += self._locate_payloads(sub_path)
        return files


    def list_payloads(self) -> None:
        print()
        payload_table = []
        for payload in self._available_payloads:
            with open(Path(self._payload_dir, payload), 'r') as file:
                description = file.readline()
                if not description.startswith('REM '):
                    Console.error_msg('unable to read description of %s' % payload.name)
                payload_table.append([payload, description[4:]])
        
        print(tabulate(payload_table, ['Payload', 'Description']))


    def use_payload(self, payload: str = None) -> None:
        if payload is None:
            Console.error_msg('missing payload argument')
            return
        
        if Path(payload) not in self._available_payloads:
            Console.error_msg('invalid payload selected')
            return
        
        self._current_payload = Payload(Path(self._payload_dir, payload), self._defaults)


    def set_variable(self, argument: str = None, value: str = None) -> None:
        if argument is None:
            Console.error_msg('missing argument')
            return
        
        if value is None:
            Console.error_msg('missing value argument')
            return
        
        if argument not in self._current_payload.kwargs:
            Console.error_msg('invalid argument %s' % argument)
            return
        
        self._current_payload.kwargs[argument] = value


    def show_options(self) -> None:
        argument_table = []
        if self._current_payload is not None:
            for key, value in self._current_payload.kwargs.items():
                argument_table.append([key, value])
        
        if self._current_payload is not None:
            path = self._current_payload.path
            payload_name = path.relative_to(self._payload_dir)
        else:
            payload_name = None

        print('\n Payload: %s\n' % payload_name)
        print(tabulate(argument_table, ['Argument', 'Value']))


    def generate_payload(self) -> None:
        self._compiler.compile_payload(self._current_payload, Path('inject.bin'), 'no')

    

    def show_help(self) -> None:
        help_table = [
            ['list', 'lists all available payloads'],
            ['use', 'choose a payload to use'],
            ['set', 'sets payload argument variables'],
            ['options', 'show all available arguments'],
            ['generate', 'generates the current payload'],
            ['help', 'shows this message']
        ]
        
        print('\n' + tabulate(help_table, ['Command', 'Description']))



    def _get_user_input(self) -> Sequence[str]:
        prompt = "\n\033[96m[Centox]\033[0m \033[95m$\033[0m "

        user_input = ""
        while not user_input:
            user_input = input(prompt).strip()

        return user_input.split()
    
    
    def run(self) -> None:
        # map all command callbacks
        callbacks = {
            'list': self.list_payloads,
            'use': self.use_payload,
            'set': self.set_variable,
            'options': self.show_options,
            'generate': self.generate_payload,
            'help': self.show_help,
            'clear': Console.clear_screen,
            'exit': lambda: exit()
        }

        while True:
            # get user input and unpack them
            # into a command and its arguments
            command, *args = self._get_user_input()
            command = command.lower()

            if command in callbacks:
                try:
                    # execute callback assosiated with command
                    callbacks[command](*args)
                except TypeError:
                    Console.error_msg('too many arguments')
            else:
                Console.error_msg('invalid command: %s' % command)