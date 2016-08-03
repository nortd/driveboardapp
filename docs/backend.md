
DriveBoardApp Backend
=====================

DriveboardApp consists of three pieces of software. The *backend* sits in between the [firmware](firmware.md) and the [frontend](frontend.md). Its main purpose is to connect to the hardware over serial and provide functionality to the graphical user interface. This functionality is provided primarily by two modules: *driveboard.py* and *web.py*, also know as the [low-level API](api_low.md) and [high-level API](api_high.md).


Threading
---------
The *backend's* python code relys heavily on threading to simultaneously stream data to the hardware, fullfill web requests from the user interface and process jobs.

- app.py runs web.start()
- web.start() runs driveboard.connect() and S.start()
- driveboard.connect() runs statserver.start() and SerialLoop.start()
- statserver.start() spawns:
  - THREAD1: serverthread
  - THREAD2: messagethread
- SerialLoop.start() spawns:
  - THREAD3: serial thread
- S.start() spawns:
  - THREAD4: web server thread
- main thread enters a loop listening to keyboard interrupts (Ctrl-C)
