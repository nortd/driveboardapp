
DriveboardApp Configuration
===========================

The user configuration file is `config.json` and is located in the DriveboardApp storage directory. This directory is printed to the console when starting-up the app. It is used to build the *conf* dictionary which gets used in both the *backend* and *frontend*.

How to change
-------------
You can simply edit this file to configure the app. Alternatively you can also set configuration entries through the web interface by using a special url.

 - For example, setting the serial port to `/dev/ttyACM1` can be achieved by calling `http://127.0.0.1:4444/config/serial_port//dev/ttyACM1`
 - Setting the grid spacing to one inch call `http://127.0.0.1:4444/config/grid_mm/25.4`

To reset any entry to the default do something like this:

 - `http://127.0.0.1:4444/config/grid_mm/_default_`

 To list the configuration call:

 - `http://127.0.0.1:4444/config`

 Note: Not all entries are user-configurable through this config file.



Firmware Configuration
----------------------
Custom firmwares can be created by adding special `config.xxxx.h` files in the `firmware/src` directory. For example `config.driveboardusb.h` is the configuration file for the Driveboard Element. When you click 'Rebuild Firmware' the backend will then build one firmware for every config file in the `src` directory.

To flash a custom firmware open `/flash/xxxx` with your browser. Alternatively you can configure this custom firmware as your new default by opening `/config/firmware/xxxx`. Then a click on 'Flash Firmware' will use this newly configured firmware from now on.
