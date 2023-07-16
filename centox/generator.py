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
    

    def generate(self, payload: Payload) -> str:
        output = []

        # creates constants out of the payload arguments
        for arg, value in payload.get_args().items():
            output.append(f"DEFINE #{arg} {value}")

        for line in payload.raw.splitlines():
            # if the user has spesified a typing delay or typing delay
            # offset, each character typed will have a 
            if line.startswith("STRING"):
                if self.typing_delay or self.typing_delay_offset:
                    # converts the #ARGUMENTS to strings. this is done
                    # rather than using the DEFINE functionality so that
                    # there can be created a delay between all characters.
                    if line[8:] in payload.get_args().keys():
                        line = f"STRING {payload.get_args()[line[8:]]}"
                    
                    line = line[7:]

                    for char in line:
                        # calculate random delay between each keystroke
                        # with a random offset if spesified. this offset
                        # can never be below 0
                        offset = self.typing_delay_offset
                        rand_offset = randint(-offset, offset)
                        delay = max(0, self.typing_delay + rand_offset)
                        
                        output.append(f"DELAY {delay}")
                            
                        if char == " ":
                            output.append("SPACE")
                        else:
                            output.append(f"STRING {char}")

                    continue
        
            output.append(line)
        
        return "\n".join(output)