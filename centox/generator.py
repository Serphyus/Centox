import logging
from random import randint
from contextlib import suppress
from typing import Dict, Any

from centox.payload import Payload


class Generator:
    def __init__(self) -> None:
        self._typing_delay = 0
        self._typing_delay_offset = 0


    def _convert_to_int(self, value: str) -> Any:
        with suppress(Exception):
            return int(value)


    @property
    def typing_delay(self) -> int:
        return self._typing_delay


    @typing_delay.setter
    def typing_delay(self, value: str) -> None:
        value = self._convert_to_int(value)

        if value is None:
            logging.error("typing delay must be a number")
        elif value < 0:
            logging.error("typing delay must be 0 or higher")
        else:
            self._typing_delay = value


    @property
    def typing_delay_offset(self) -> int:
        return self._typing_delay_offset


    @typing_delay_offset.setter
    def typing_delay_offset(self, value: str) -> None:
        value = self._convert_to_int(value)

        if value is None:
            logging.error("typing delay offset must be a number")
        elif value < 0:
            logging.error("typing delay offset must be 0 or higher")
        else:
            self._typing_delay_offset = value
    

    def _random_offset(self) -> int:
        # random value of the given range with a max value of 0
        # range: {-typing_delay_offset, ..., typing_delay_offset}
        rand_offset = randint(
            -self.typing_delay_offset,
            self.typing_delay_offset
        )

        return max(0, self.typing_delay + rand_offset)


    def generate(self, payload: Payload) -> str:
        output = []
        instructions = payload.raw

        # formats in all arguments from the payload manifest
        instructions = instructions.format(**payload.get_args())
        
        for line in instructions.splitlines():
            if line.startswith("STRING"):
                if self.typing_delay or self.typing_delay_offset:
                    # instructions after the "STRING "
                    line = line[7:]

                    for char in line:
                        output.append(f"DELAY {self._random_offset()}")
                        
                        if char == " ":
                            output.append("SPACE")
                        else:
                            output.append(f"STRING {char}")

                    continue
        
            output.append(line)
        
        return "\n".join(output)