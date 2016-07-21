
Driveboard Serial Protocol
==========================

Communication between the **firmware** and the **backend** uses a highly optimized hybrid protocol. It uses less than half the bandwith of GCode while still being quite human-readable. This is achieved by encoding the commands as single bytes and numbers as four bytes. Raster data is transmitted as a stream of 8-bit gray values. The protocol uses an inverse order to simplify parsing.

Instruction Mode
----------------
```
<instructions> ::= <command> | <parameter><command> |                         
                   <parameter><parameter><parameter><command>

<command> ::= <lowbyte>

<parameter> ::= <number><lowbyte>

<number> ::= <highbyte><highbyte><highbyte><highbyte>

<lowbyte> ::= byte [0,127]

<highbyte> ::= byte [128,255]
```
#### Commands
For details on the encoding of a command see: pound defs in [protocol.h](../firmware/src/protocol.h)

#### Numbers
For details on the encoding of numbers see:
*get_curent_value()* in [protocol.c](../firmware/src/protocol.c)

#### Example
move command:
```
<number>x<number>y<number><move_command>
```

Raster Data Mode
----------------
```
<rasterpixel> ::= <highbyte>

<highbyte> ::= byte [128,255]
```
Raster data mode is typically used to laser-engrave an image. Each pixel is mapped to the size of the laser focus (*raster_size* in [config.py](../backend/config.py)). Internally this means the raster data needs to have one pixel per physical pixel. For example:

- laser focus: 0.4mm
- desired image width: 200mm
- required image resolution is then: 200/0.4 = 500 pixels

#### Example
Raster data mode works by sending a raster move instruction, enter raster data mode, send image line data, leave raster data mode:
```
<number><intensity_command>
<number><feedrate_command>
<number><pixelwidth_command>
<number>x<number>y<number>z<rastermove_command>
<data_start_command>
<rasterpixel><rasterpixel>...<rasterpixel>
<data_end_command>
```


Status
------
The firmware replies with a status codes in a similar manner. The presence of a status means the associated event occured.
```
<statuscode> ::= <status> | <parameter><status> |                         
                 <parameter><parameter><parameter><status>

<status> ::= <lowbyte>

<parameter> ::= <number><lowbyte>

<number> ::= <highbyte><highbyte><highbyte><highbyte>

<lowbyte> ::= byte [0,127]

<highbyte> ::= byte [128,255]
```

There a different kinds of status codes:
- non-stop events (like door open)
- stop events (like limit hit)
- current position
- ...

For details see: *_serial_read()* in [driveboard.py](../backend/driveboard.py)


Flow Control
------------
The **firmware** only sends a few things without requesting. Upon connecting the firmware sends the 'INFO_HELLO' statuscode. During normal communication the firmware sends the 'CMD_CHUNK_PROCESSED' byte whenever it has processed a certain amount of bytes from its rx buffer. This allows the **backend** to track the firmware's rx buffer and throttle the data accordingly. From there on out all the initiative is on the backend. It sends instructions and requests the firmware's status as needed.


Error Detection
---------------
To recognize a faulty connection quickly every byte is send twice. The firmware compares these two bytes and reports a transmission error should they ever not match.
