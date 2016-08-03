
DriveBoardApp Backend
=====================

DriveboardApp consists of three pieces of software. The *backend* sits in between the [firmware](firmware.md) and the [frontend](frontend.md). Its main purpose is to connect to the hardware over serial and provide functionality to the graphical user interface. This functionality is provided primarily by two modules: *driveboard.py* and *web.py* and also know as the [low-level API](api_low.md) and [high-level API](api_high.md).
