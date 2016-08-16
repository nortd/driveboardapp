

MinimalDriveboard
=================

Here you will find instructions on how to build a minimal Driveboard with an Arduino Uno. Compared to a regular [Driveboard](https://github.com/nortd/lasersaur/wiki/driveboard) this requires more wiring and also lacks some features (e.g. e-stop, hard-logic safety system). It takes some rigor to do this well. In any case this may be a good starting point to build your CNC machine from the ground up. The following shows a 2-axis setup as it is used by the [Lasersaur](http://www.lasersaur.com). A 3-axis setup is also possible but left as an exercise to the reader.



### Required Parts:
- Arduino Uno
- 2 Setpper Drivers (Geckodrive G201X)
- 2 Stepper Motors (Nanotec ST4118M1206-A, ST5918X3008-A)
- 4 Limit Switches (MK04-1B90C-500W, 876-2500000004)
- 1 Door Switch (MK04-1A66B-500W, 876-2500000004)
- 1 E-Valve (Airtec MS 20310 24V=)
- 6 resistors (10 kOhm)
- 1 resistor (360 Ohm)
- 1 diode (1N4004)
- 1 Solid State Relay (AQY212GH)
- 24V PSU, 3.2A


### Schematic
![MinimalDriveboard](img/MinimalDriveboard.png)
