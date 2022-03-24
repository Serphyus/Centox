import os
import atexit
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from .console import Console
from .payload import Payload


class Generator:
    def __init__(self, encoder: Path, payload: Payload, output: Path) -> None:
        # set bin_path as java to be used since
        # the encoder is compiled as a .jar file
        self._bin_path = "java"

        # store the encoder path
        self._encoder = encoder

        # payload to encode
        self._payload = payload

        # set output path for final injection
        self._output = output


    def write_payload(self) -> Path:
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
        final_payload = self._payload.parse()
        
        # write payload to temporary file
        with open(path, 'w') as file:
            Console.debug_msg('writing raw payload to -> %s' % path)
            file.write(final_payload)
        
        # return file path of payload
        return path


    def generate(self) -> None:
        payload_path = self.write_payload()

        if self._output.is_file():
            Console.warning_msg('overwriting existing injection')

            try:
                os.remove(self._output)
            except OSError:
                Console.error_msg("unable to overwrite old inject.bin", True)

        command = '%s -jar %s -l %s -i %s -o %s' % (
            self._bin_path, self._encoder, self._payload.layout,
            payload_path, self._output)

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )

        Console.debug_msg("compiling payload to injection binary")

        process.wait()

        if self._output.is_file():
            Console.debug_msg('injection compiled successfully -> %s' % self._output)
        else:
            Console.error_msg('unable to generate inject.bin')