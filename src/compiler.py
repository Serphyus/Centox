import os
import atexit
import subprocess
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


    def _write_payload(self, payload: Payload) -> Path:
        # create temporary directory to
        # store unencoded payload to and
        # register it to delete itself at exit
        tmp_folder = TemporaryDirectory()
        atexit.register(tmp_folder.cleanup)

        Console.debug_msg('created temporary folder -> %s' % tmp_folder.name)

        # create temporary file path for payload
        path = Path(tmp_folder.name, 'payload')

        # creat empty payload file
        path.touch()
        
        # create the final payload
        final_payload = payload.parse()
        
        # write payload to temporary file
        with open(path, 'w') as file:
            Console.debug_msg('writing raw payload to -> %s' % path)
            file.write(final_payload)
        
        # return file path of payload
        return path


    def compile_payload(self, payload: Payload, output: Path, layout: str) -> None:
        # parse and write the final payload
        payload_path = self._write_payload(payload)

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
                Console.error_msg('unable to overwrite old inject.bin')
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
        Console.debug_msg('compiling payload to injection binary')
        process.wait()

        # check if the file was generated successfully
        if output.is_file():
            Console.debug_msg('injection compiled successfully -> %s' % output)
        else:
            Console.error_msg('unable to generate inject.bin')