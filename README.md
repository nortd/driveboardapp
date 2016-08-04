dxfgrabber branch notes
=======================

This branch replaces the lasersaur dxf reader with a parser driving
dxfgrabber.   All new work added by jet is under the existing
lasersaur licensing.  This work is done on jet's personal time,
not supported by any commercial entities, and donations are always welcome.

You'll need to install the latest dxfgrabber from console:

root@laserdev:~/LasaurApp# pip install dxfgrabber

Changes:

- dxf line colors from entity or entity layer
- dxf units converted to mm
- flip dxf files on the Y axis by default

In Testing:
- flip dxf files on the X axis by default

TODO list:
- fix circle/arc generation?  Make test file with holes from 1mm to
  25mm for tests.
- TEXT YES TEXT I'M WORKING ON THAT DILUTE! DILUTE! OK!
- more dxf entities
- remapping/reducing dxf color sets down to a set of 0..7
  (which will probably change when we start rasterizing)

--- start of DriverboardApp official README.md ---


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
- Download and run `python driveboardapp/backend/app.py -b`


Lasersaur Installation
----------------------
- make sure the Lasersaur can access the Internet
- ssh into the Lasersaur with `ssh lasersaur.local` and do the follwoing:
```
git clone https://github.com/nortd/driveboardapp.git
cd driveboardapp
scripts/install_packages.sh
scripts/upgrade_to_driveboardapp.sh
python backend/flash.py
reboot
```
If for some reason you want to downgrade and use LasaurApp again run:
```
scripts/downgrade_to_lasaurapp.sh
reboot
```


**DISCLAIMER:** Please be aware that operating CNC machines can be dangerous and requires full awareness of the risks involved. NORTD Labs does not warrant for any code or documentation and does not assume any risks whatsoever with regard to using this software.
