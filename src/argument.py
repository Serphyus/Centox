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
    
    
    def _reset_input(self, user_input: str) -> None:
        line_size = os.get_terminal_size()[0]
        full_prompt = len(user_input) + len(self._prompt)

        total_reset = 1 + int(full_prompt / line_size)
        Console.reset_lines(total_reset)


    def get_input(self) -> None:
        while True:
            readline.set_pre_input_hook(self._hook)
            raw_user_input = input(self._prompt)
            readline.set_pre_input_hook()
            
            self._reset_input(raw_user_input)

            try:
                user_input = raw_user_input.strip()
                return user_input

            except Exception:
                continue