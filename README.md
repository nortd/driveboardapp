
DriveboardApp
=============

DriveboardApp is the official app to control Driveboard-based CNC machines like the [Lasersaur](http://lasersaur.com). It's aim is to provide a plesant way to load jobs into the machine. Its primary features are:

- load svg vector files and send them to the machine
- display the status of the machine
- pausing/continuing/stop a job
- firmware flashing

This app is written mostly in Javascript and Python and runs on most modern operating systems and browsers. This allows for very flexible setup. The backend can either run directly on the Driveboard or on the client computer. The frontend runs in a web browser either on the same client computer or on a tablet computer.

When running on the Driveboard you can directly use it from any laptop without having to install software. This is done this way because we imagine CNC machines being shared in shops. For example we see people controlling laser cutters from their laptops and not wanting to go through annoying setup processes. Besides this, html-based GUIs are just awesome :)

**DISCLAIMER:** Please be aware that operating CNC machines can be dangerous and requires full awareness of the risks involved. NORTD Labs does not warrant for any code or documentation and does not assume any risks whatsoever with regard to using this software.
