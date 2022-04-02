import os
import atexit
import subprocess
from random import randint
from pathlib import Path
from tempfile import TemporaryDirectory

from .console import Console
from .payload import Payload


class Compiler:
    def __init__(self, encoder: Path) -> None:
        # set bin_path as java to be used since
        # the encoder is compiled as a .jar file
        self._bin_path = "java"

        # store the encoder path
        self._encoder = encoder

        # create a temporary folder to use as storage
        self._tmp_dir = TemporaryDirectory()


    def _write_payload(self, payload: Payload, global_args: dict, tmp_dir: Path) -> Path:
        # create the final payload
        parsed_lines = payload.parse()
        
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
                # create a lambda function for creating a new random
                # delay using the typing delay and setting the max and
                # min values using the offset to create more random
                # spacings between each keystroke. This is to evade
                # programs that detect and block inhumane typing speeds
                create_delay = lambda: randint(min_delay, max_delay)

        final_payload = []

        # check if a typing delay is set
        if global_args['typing_delay_average'] and max_delay > 0:

            # if a delay is used then each character must be individually
            # split using a delay which is done by checking if the current
            # line is a string and looping through each of the characters
            # to split them into a single keystroke followed up by a delay
            for line in parsed_lines:
                # ignore commented lines that begin with: REM
                if not line.startswith('REM '):
                    if line.startswith('STRING '):
                        for char in line[7:]:
                            final_payload.append('STRING %s' % char)
                            final_payload.append('DELAY %s' % create_delay())
                    else:
                        # if the line does not contain a string of letters
                        # add the line as is to the final payload
                        final_payload.append(line)
        else:
            # if not delay is spesified leave the lines unchanged
            final_payload = parsed_lines
        
        # create path for the payload file
        path = Path(tmp_dir, 'payload')

        # write all lines of the final paylaod to
        # a file stored in a temporary folder
        with open(path, 'w') as file:
            Console.debug_msg('writing raw payload to -> %s' % path)
            file.write('\n'.join(final_payload))
        
        return path


    def compile_payload(self,
            payload: Payload,
            output: Path,
            layout: str,
            global_args: dict
        ) -> None:

        # create a temporary directory for the payload
        tmp_dir = TemporaryDirectory()
        Console.debug_msg('created temporary folder -> %s' % tmp_dir.name)

        # parse and write the final payload
        payload_path = self._write_payload(payload, global_args, Path(tmp_dir.name))

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

        # construct the command for generating
        # the injection binary for rubber ducky
        command = '%s -jar %s -i %s -o "%s" -l %s' % (self._bin_path, self._encoder,
                                                    payload_path, output, layout)

        # creates a subprocess that compiles
        # the payload into an injection binary
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