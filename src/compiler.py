import os
import subprocess
from random import randint
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Sequence

from .console import Console
from .payload import Payload


class Compiler:
    def __init__(self, encoder_dir: Path) -> None:
        # set bin_path as java to be used since
        # the encoder is compiled as a .jar file
        self._bin_path = "java"

        # store the encoder path
        self._encoder = Path(encoder_dir, 'encoder.jar')

        # read all available keyboard  layouts
        with open(Path(encoder_dir, 'layouts'), 'r') as file:
            self._layouts = [line.strip() for line in file.readlines()]

        # read all available payload format
        with open(Path(encoder_dir, 'formats'), 'r') as file:
            self._formats = [line.strip() for line in file.readlines()]

        # create a temporary folder to use as storage
        self._tmp_dir = TemporaryDirectory()


    @property
    def layouts(self) -> Sequence[str]:
        return self._layouts

    
    @property
    def formats(self) -> Sequence[str]:
        return self._formats


    def _write_payload(self,
            payload: Payload,
            payload_path: Path,
            keyboard_layout: str,
            payload_format: str,
            global_args: dict,
        ) -> Path:
        
        # create the final payload
        parsed_lines = payload.parse()

        if not parsed_lines:
            Console.error_msg('unable to compile since the payload is empty')
            return

        Console.debug_msg('converting payload to format: %s' % payload_format)

        # if the payload format is a bash bunny
        # add QUACK to the beginning of each line
        if payload_format == 'bunny':
            for index, line in enumerate(parsed_lines):
                parsed_lines[index] = 'Q ' + line
            
            parsed_lines.insert(0, 'LED ATTACK')
            parsed_lines.insert(1, 'Q SET_LANGUAGE %s' % keyboard_layout)
            parsed_lines.append('LED FINISH')

        # omg payloads requires no tweaking from the
        # ducky format but it needs to set a ducky_lang
        # after an initial delay
        elif payload_format == 'omg':
            layout_line = 'DUCKY_LANG %s ' % keyboard_layout
            if not parsed_lines[0].startswith('DELAY '):
                Console.warning_msg('no delay detected before setting the ducky_lang')
                parsed_lines.insert(0, layout_line)
            else:            
                parsed_lines.insert(1, layout_line)

        # if a typing delay is used to evade keystroke injection prevention
        # software then create a funciton to generate random delays for each
        # keystroke using the average delay and offset for a min/max value
        if global_args['typing_delay_average']:
            _average = int(global_args['typing_delay_average'])
            _offset = int(global_args['typing_delay_offset'])

            max_delay = _average + _offset
            min_delay = _average - _offset

            # the minimum delay can not 
            if min_delay < 0: min_delay = 0
            if max_delay < 0: max_delay = 0

            Console.debug_msg('minimum typing delay: %s ms' % min_delay)
            Console.debug_msg('maximum typing delay: %s ms' % max_delay)

            if max_delay == 0:
                Console.warning_msg('disabling typing delay since max delay must be > 0')
            else:
                # create a lambda function that gives a random typing delay
                create_delay = lambda: randint(min_delay, max_delay)

                # check for each line that types strings and for each char in
                # the string add a delay after typing it to simulate a more human
                # typing speed and behaviour
                for line in parsed_lines:
                    if line.startswith('STRING '):
                        for char in line[7:]:
                            final_payload.append('STRING %s' % char)
                            final_payload.append('DELAY %s' % create_delay())
                    else:
                        # if the line does not type a string then 
                        # add the line as is to the final payload
                        final_payload.append(line)

        else:
            # if not delay is spesified leave the lines unchanged
            final_payload = parsed_lines
        
        # write all lines of the final paylaod to
        # a file stored in a temporary folder
        with open(payload_path, 'w') as file:
            Console.debug_msg('writing raw payload to -> %s' % payload_path)
            file.write('\n'.join(final_payload))


    def compile_payload(self,
            payload: Payload,
            output: Path,
            keyboard_layout: str,
            payload_format: str,
            global_args: dict
        ) -> None:

        # create a temporary directory for the payload
        tmp_dir = TemporaryDirectory()
        Console.debug_msg('created temporary folder -> %s' % tmp_dir.name)

        
        # create a payload path for the final raw payload
        payload_path = Path(tmp_dir.name, 'payload')

        # parse and write the final payload
        self._write_payload(
            payload,
            payload_path,
            keyboard_layout,
            payload_format,
            global_args,
        )

        # checks if the output path is already a file
        if output.is_file():
            Console.warning_msg('overwriting existing %s file' % output.name)

            # try to remove the file
            try:
                os.remove(output)
            except OSError:
                # if unable to remove the existing file
                # an error message will be outputted and
                # the payload compilation will be aborted
                Console.error_msg('unable to overwrite file: %s' % output.name)
                return

        if payload_format == 'ducky':
            # generate an injection binary if using rubber ducky
            command = '%s -jar %s -i %s -o "%s" -l %s' % (self._bin_path, self._encoder,
                                                          payload_path, output, keyboard_layout)

            # compile the payload to binary
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )

            # wait for the process to finish
            Console.debug_msg('compiling payload to injection binary...')
            process.wait()

            if process.stderr.read() != b'' or not output.is_file():
                Console.error_msg('unable to generate inject.bin')
            else:
                Console.debug_msg('injection compiled successfully -> %s' % output)
        else:
            os.system('mv %s %s' % (payload_path, output))