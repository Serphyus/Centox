import os
import sys
import json
import shlex
import argparse
from pathlib import Path
from tabulate import tabulate
from typing import Sequence

from .console import Console
from .payload import Payload
from .compiler import Compiler

if sys.platform != 'win32':
    import readline


class Handler:
    def __init__(self, abs_path: Path) -> None:
        self._abs_path = abs_path        
        
        # defaults selected payload to None
        self._current_payload: Payload = None

        # set directory where payloads are stored
        self._payload_dir = Path(self._abs_path, 'assets', 'payloads')

        # locate all available payloads and remove the prefix
        Console.debug_msg('locating available payloads')
        
        # find all available payloads
        self._available_payloads = []
        for path in self._locate_payloads(self._payload_dir):
            self._available_payloads.append(path.relative_to(self._payload_dir))

        # load layouts file
        with open(Path(abs_path, 'assets', 'layouts'), 'r') as file:
            self._layouts = [layout.strip() for layout in file.readlines()]

        # load defaults.json file
        Console.debug_msg('loading defaults config')
        self._defaults = self._load_defaults()

        # create compiler for payloads
        self._compiler = Compiler(Path(self._abs_path, 'assets', 'bin', 'encoder.jar'))


    def _load_defaults(self) -> None:
        # set defaults file path
        defaults_path = Path(self._abs_path, 'assets', 'defaults.json')
        
        # check if defaults exists
        if not defaults_path.is_file():
            Console.error_msg('unable to locate file: %s' % defaults_path.name, True)
        
        # read the defaults.json config
        with open(defaults_path, 'r') as file:
            defaults = json.load(file)

        # return defaults from file
        return defaults


    def _locate_payloads(self, prefix: Path) -> list:
        # lists the payload directory and checks
        # each folder for payolads and returns a
        # list of the payloads found which will
        # combine after the recursion has finished
        files = []
        for sub_name in os.listdir(prefix):
            sub_path = Path(prefix, sub_name)
            if sub_path.is_file():
                files.append(sub_path)
            elif sub_path.is_dir():
                files += self._locate_payloads(sub_path)
        return files


    def list_payloads(self) -> None:
        # creates an empty table which will contain
        # elements with [path, description] contents
        payload_table = []

        # loops through each payload
        for payload in self._available_payloads:
            with open(Path(self._payload_dir, payload), 'r') as file:
                # reads the first line
                description = file.readline()
                
                # checks if the line is commented and contains a
                # description and then storing it, else a warning
                if description.startswith('REM '):
                    table_row = [payload, description[4:].strip()]
                else:
                    table_row = [payload, '\x1b[93m[!]\x1b[0m Unable to read description']

                # adds the new row to tha table of data
                payload_table.append(table_row)
        
        print('\n' + tabulate(payload_table, ['Payload', 'Description']))


    def use_payload(self, payload: str = None) -> None:
        # checks user provided a payload argument
        if payload is None:
            Console.error_msg('missing payload argument')
        
        # checks that the provided payload argument
        # does not matches an existing payload file
        elif Path(payload) not in self._available_payloads:
            Console.error_msg('invalid payload selected')
        
        # sets the new payload using the
        # payload dir and the payload path
        else:
            self._current_payload = Payload(Path(self._payload_dir, payload), self._defaults)


    def set_variable(self, argument: str = None, value: str = None) -> None:
        # makes sure a payload is selected
        if self._current_payload is None:
            Console.error_msg('no payload selected')
        
        # makes sure an argument is provided
        elif argument is None:
            Console.error_msg('missing argument')
        
        # makes values are provided
        elif value is None:
            Console.error_msg('missing value argument')
        
        # checks if the arguments is valid
        elif argument not in self._current_payload.kwargs:
            Console.error_msg('invalid argument %s' % argument)
        
        else:
            # checks if the argument is a special argument and 
            # makes sure the value matches the special argument
            if argument in self._defaults['special_args']:
                special_arg = self._defaults['special_args'][argument]

                # check if the value is valid                
                if value not in special_arg:
                    Console.error_msg('%s must be a value in: [%s]' % (value, ', '.join(special_arg.keys())))
                    return
            
            # sets the new value
            self._current_payload.kwargs[argument] = value


    def show_options(self) -> None:
        # outputs the name of the
        # current selected payload
        if self._current_payload is not None:
            path = self._current_payload.path
            payload_name = path.relative_to(self._payload_dir)
        else:
            payload_name = None
        print('\n Payload: %s\n' % payload_name)

        # output all the arguments and their
        # values of the current payload
        argument_table = []
        if self._current_payload is not None:
            for key, value in self._current_payload.kwargs.items():
                argument_table.append([key, value])
        print(tabulate(argument_table, ['Argument', 'Value']))


    def generate_payload(self, *args) -> None:
        # checks that a payload is selected
        if self._current_payload is None:
            Console.error_msg('no payload selected')
            return
        
        # use an argument parser for handling arguments
        parser = argparse.ArgumentParser(add_help=False, exit_on_error=False)
        parser.add_argument('-o', dest='output', type=str, default='inject.bin')
        parser.add_argument('-l', dest='layout', type=str)
        parser.add_argument('-h', dest='show_help', action='store_true')

        # parse command arguments
        try:
            args, unknown = parser.parse_known_args(args)
        except argparse.ArgumentError:
            Console.error_msg('invalid arguments')
            return
        
        if unknown:
            Console.error_msg('invalid arguments')
        
        elif args.show_help:
            # if the help arg is used it will
            # show a message of all available
            # command arguments
            help_table = [
                ['-o', 'spesifies the output file of the injection'],
                ['-l', 'specifies the keyboard layout for the injection'],
                ['-h', 'shows this help message']
            ]
            print('\n' + tabulate(help_table, ('Arg', 'Description')))

        elif args.output is None:
            Console.error_msg('missing output argument: -o')

        elif args.layout is None:
            Console.error_msg('missing layout argument: -l')

        else:
            # compile the current payload
            self._compiler.compile_payload(
                self._current_payload,
                Path(args.output),
                args.layout
            )


    def show_help(self) -> None:
        # output a help menu of all available
        # commands and their usage description
        help_table = [
            ['list', 'lists all available payloads'],
            ['use', 'choose a payload to use'],
            ['set', 'sets payload argument variables'],
            ['options', 'show all available arguments'],
            ['generate', 'generates the current payload'],
            ['help', 'shows this help message']
        ]
        
        print('\n' + tabulate(help_table, ('Command', 'Description')))


    def _get_user_input(self) -> Sequence[str]:
        # creates a prompt for commands
        prompt = '\n\033[96m[Centox]\033[0m \033[95m$\033[0m '

        # loops as long as user input is empty
        # and then returns it once the user has
        # entered a valid input
        user_input = []
        while not user_input:
            try:
                # split using shlex to preserve
                # double quoted strings as one
                user_input = shlex.split(input(prompt).strip())
            except ValueError:
                Console.error_msg('missing closing quote: "')
            except KeyboardInterrupt:
                print()
                Console.error_msg('keyboard interrupt')

        return user_input
    
    
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
            'exit': lambda: sys.exit()
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