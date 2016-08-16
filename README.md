DriveboardApp
=============

DriveboardApp is the official app to control Driveboard-based CNC machines like the [Lasersaur](http://lasersaur.com). Its aim is to provide a simple yet powerful way to control the machine. Its primary features are:

- load svg vector files and send them to the machine
- display the status of the machine
- pausing/continuing/stopping a job
- firmware flashing

This software is written in Javascript (frontend), Python (backend) and C (firmware). The backend can either run directly on the Driveboard or on the client computer. The frontend runs in a web browser either on the same client computer or on a tablet computer.

- frontend
- [backend](docs/backend.md)
  - [Low-Level API](docs/api_low.md)
  - [High-Level API](docs/api_high.md)
- firmware
  - [serial protocol](docs/protocol.md)
- jobs
  - [dba file format](docs/dba.md)
- [configuration](docs/configure.md)


Installation
------------
- [installation](docs/install.md)

Hardware
--------
- [Driveboard](https://github.com/nortd/lasersaur/wiki/driveboard) via [Lasersaur project](http://www.lasersaur.com)
- [MinimalDriveboard](docs/minimaldriveboard.md)


**DISCLAIMER:** Please be aware that operating CNC machines can be dangerous and requires full awareness of the risks involved. NORTD Labs does not warrant for any code or documentation and does not assume any risks whatsoever with regard to using this software.
