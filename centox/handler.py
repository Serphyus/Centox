import os
import sys
import json
import shlex
import logging
from pathlib import Path
from typing import Sequence

from tabulate import tabulate

from centox.payload import Payload
from centox.generator import Generator


class Handler:
    def __init__(self, working_dir: Path) -> None:
        logging.debug("initializing payload handler")
        
        self._running = False
        self._current_payload = None
        self._working_dir = working_dir
        self._generator = Generator()
        
        self._bind_callbacks()
        self._load_payloads()
        
    
    def _bind_callbacks(self) -> None:
        self._callbacks = {
            "list": self.list_available,
            "use": self.use_payload,
            "set": self.set_argument,
            "options": self.show_options,
            "generate": self.generate_payload,
            "help": self.show_help,
            "clear": self.clear_screen,
            "exit": self.stop
        }


    def _load_payloads(self) -> None:
        logging.debug("loading ducky payloads")

        self._available_payload = {}
        self._payloads_dir = Path(self._working_dir, "assets/payloads")

        payload_list = []
        for path in os.walk(Path(self._payloads_dir)):
            path = path[0]

            for stored in payload_list:
                if path.startswith(stored):
                    payload_list.remove(stored)
            
            payload_list.append(path)
        
        for payload_dir in map(Path, payload_list):
            payload_name = str(payload_dir.relative_to(self._payloads_dir))
            
            if sys.platform == "win32":
                payload_name = payload_name.replace("\\", "/")
            
            self._available_payload[payload_name] = Payload(payload_name, payload_dir)

    
    def _create_table(
            self,
            keys: Sequence[str],
            table: Sequence[Sequence[str]]
        ) -> str:

        allignment = []
        if table:
            for _ in keys:
                allignment.append('left')

        return tabulate(
            table, keys,
            colalign=allignment
        )

    
    def list_available(self) -> None:
        payload_table = []
        for name, payload in self._available_payload.items():
            payload_table.append((
                name,
                payload.description
            ))

        table = self._create_table(
            ("Payload", "Description"),
            payload_table
        )
        
        print(f"\n{table}")


    def use_payload(self, payload: str) -> None:
        if payload not in self._available_payload:
            logging.error(f"invalid payload: {payload}")
            return
        
        logging.debug(f"initializing payload: {payload}")
        self._current_payload = self._available_payload[payload]
        self._current_payload.reset()

    
    def set_argument(self, arg: str, value: str) -> None:
        arg = arg.upper()

        if arg == "TYPING_DELAY":
            self._generator.typing_delay = value
        
        elif arg == "TYPING_DELAY_OFFSET":
            self._generator.typing_delay_offset = value
        
        else:
            if self._current_payload is None:
                logging.error(f"{arg} is not a valid argument")
                return
            
            self._current_payload.set_arg(arg, value)
    
    
    def show_options(self) -> None:
        output = "\n Payload: "
        
        if self._current_payload is not None:
            output += self._current_payload.name

        generator_args = [
            ("TYPING_DELAY", self._generator.typing_delay),
            ("TYPING_DELAY_OFFSET", self._generator.typing_delay_offset)
        ]
        
        generator_output = self._create_table(
            ("Generator arguments", "Value"),
            generator_args
        )
        
        output += f"\n\n{generator_output}"

        if self._current_payload is not None:
            payload_args = []
            for key, value in self._current_payload.get_args().items():
                payload_args.append((key, value))

            payload_output = self._create_table(
                ("Payload arguments", "Value"),
                payload_args
            )

            output += f"\n\n{payload_output}"
        
        print(output)

    
    def generate_payload(self, output_path: str = None) -> None:
        if self._current_payload is None:
            logging.error("no payload has been selected")
            return

        logging.debug("generating payload")
        payload = self._generator.generate(self._current_payload)

        if output_path is None:
            print(f"\n{payload}")
            return
        
        output_path = Path(output_path)
        
        if output_path.is_file():
            logging.warning(f"file already exists")

            user_input = input("overwrite file [Y/N] ").lower().strip()

            if user_input == "n":
                return
            
            elif user_input != "y":
                logging.error("invalid choice")
            
        try:
            logging.debug(f"creating file: {output_path}")
            output_path.touch()
        
        except OSError:
            logging.error("unable to create output file")
            return
        
        with open(output_path, "w") as file:
            file.write(payload)


    def show_help(self) -> None:
        help_table = [
            ("list", "lists all available payloads"),
            ("use", "choose a payload to use"),
            ("set", "configure payload arguments"),
            ("options", "show all available payload arguments"),
            ("generate", "generates the current payload"),
            ("help", "shows this help message")
        ]
        
        help_output = self._create_table(
            ("Command", "Description"),
            help_table
        )

        print(f"\n{help_output}")
    
    
    def clear_screen(self) -> None:
        if sys.platform == "win32":
            os.system("cls")
        else:
            os.system("clear")

    
    def stop(self) -> None:
        self._running = False
    
    
    def _get_user_input(self) -> Sequence[str]:
        # creates a prompt for commands
        prompt = "\n\033[96m[Centox]\033[0m \033[95m$\033[0m "

        # loops until 
        user_input = []
        while not user_input:
            try:
                # split using shlex to preserve spaces in strings with quotes
                user_input = shlex.split(input(prompt).strip())
            
            except ValueError:
                logging.error("missing closing quote: \"")
            
            except KeyboardInterrupt:
                print()
                logging.error("keyboard interrupt")

        return user_input
    
    
    def run(self) -> None:
        logging.debug("starting payload handler")

        self._running = True

        while self._running:
            command, *args = self._get_user_input()
            command = command.lower()

            if command in self._callbacks:
                try:
                    # execute callback assosiated with command
                    self._callbacks[command](*args)
                
                except TypeError:
                    logging.error("invalid number of arguments")
            
            else:
                logging.error(f"invalid command: {command}")