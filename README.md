
DriveboardApp
=============

DriveboardApp is the official app to control Driveboard-based CNC machines like the [Lasersaur](http://lasersaur.com). Its aim is to provide a simple yet powerful way to control the machine. Its primary features are:

- load svg vector files and send them to the machine
- display the status of the machine
- pausing/continuing/stop a job
- firmware flashing

This app is written in Javascript (frontend aka gui), Python (backend aka web server) and C (firmware). This allows for very flexible setups. The backend can either run directly on the Driveboard or on the client computer. The frontend runs in a web browser either on the same client computer or on a tablet computer.

- frontend
- backend
  - [API](api.md)
- firmware
  - [serial protocol](protocol.md) 
- jobs
  - [dba file format)](dba.md)

**DISCLAIMER:** Please be aware that operating CNC machines can be dangerous and requires full awareness of the risks involved. NORTD Labs does not warrant for any code or documentation and does not assume any risks whatsoever with regard to using this software.
