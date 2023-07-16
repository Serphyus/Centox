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
- [x] USB Rubber Ducky (Previous Model)
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
---------  ------------------------------------
list       lists all available payloads
use        choose a payload to use
set        configure payload arguments
options    show all available payload arguments
generate   generates the current payload
help       shows this help message
```

how to generate payloads:
```
[Centox] $ use windows/shell/python
[+] initializing payload: windows/shell/python

[Centox] $ options

 Payload: windows/shell/python

Generator arguments    Value
---------------------  -------
TYPING_DELAY           0
TYPING_DELAY_OFFSET    0

Payload arguments    Value
-------------------  -------
START_DELAY          3000
RUN_DELAY            500
IP
PORT                 9999

[Centox] $ set IP 192.168.68.42

[Centox] $ generate ducky_payload
[+] generating payload
[+] creating file: ducky_payload
```
