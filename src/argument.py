import os
import readline

from .console import Console


class Argument:
    def __init__(self,
            prompt: str,
            prefill: str = "",
        ) -> None:
        
        self._prompt = prompt
        self._prefill = prefill
    

    def _hook(self):
        readline.insert_text(self._prefill)
        readline.redisplay()


    def prompt(self) -> None:
        readline.set_pre_input_hook(self._hook)
        raw_user_input = input(self._prompt)
        readline.set_pre_input_hook()
        
        self._prefill = raw_user_input.strip()
        return self._prefill