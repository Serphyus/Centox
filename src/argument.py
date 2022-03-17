import sys
import readline

from .console import Console


class Argument:
    def __init__(self,
            name: str,
            value: str
        ) -> None:
        
        self._name = name
        self._value = value


    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> str:
        return self._value


    def _hook(self):
        readline.insert_text(self._value)
        readline.redisplay()


    def prompt(self) -> None:
        readline.set_pre_input_hook(self._hook)

        input_prompt = '%s: ' % self._name.capitalize()
        raw_user_input = input(input_prompt)
        readline.set_pre_input_hook()
        
        self._value = raw_user_input.strip()
        return self._value