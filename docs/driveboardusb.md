
DriveboardUSB
=============

![DriveboardUSB Ports](img/DriveboardUSB_ports.png)

Ports
-----

The board has 1x USB type-B, 2x barrel 2.1mm, 14x RJ45, 3x 12-pin headers.

### USB (1x)

Port for connecting to the computer running DriveboardApp.

### Power (2x)

The board is typically powered through two barrel connectors with 5V and 24V. The 5V are used for sensors and control and the 24V are used for driving the steppers and air valve. Alternatively the board can be jumpered to use the 5V from the Laser PSU. In any case the Arduino USB power is optically isolated from any external wiring.

- 5V - barrel 2.1mm, 100mA
- 24V - barrel 2.1mm, 3A (or 75% of summed stepper motor setting)


### Interlocks (9x)

These are the imputs for the limit, door, and chiller switches. Switches are expected to be normally closed (NC). When triggered they should disconnect the loop. The point of the RJ45 jacks is to use ethernet patch cables for external wiring: Flexible Cat5 or Cat6 shielded (FTP, STP, or SFTP) patch cables with 26 AWG.

- CHILLER - RJ45
- DOOR1 - RJ45
- DOOR2 - RJ45
- X1 - RJ45
- X2 - RJ45
- Y1 - RJ45
- Y2 - RJ45
- Z1 - RJ45
- Z2 - RJ45

![cat5 wiring](img/cat5-wiring-inter.png)


### Laser Control

![cat5 wiring](img/cat5-wiring-laser.png)

### Stepper Motors

![cat5 wiring](img/cat5-wiring-stepper.png)

### Air Valve

![cat5 wiring](img/cat5-wiring-air.png)
