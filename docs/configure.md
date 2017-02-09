
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

The main configuration file for the firmware is [config.h](../firmware/src/config.h) and an alternative configuration can be created by adding a *config.user.h* file. This file has to be complete and is typically the *config.h* with some modifications. The main reason this is done like this is to prevent your changes being overwritten when you update the software with a `git pull`.

Any updates or changes to the firmware are not automatically loaded onto the Driveboard. For this use the *Flash from source* feature in the user interface. After flashing it's recommended to restart the Driveboard. For your own sanity you should also change the `define VERSION` entry in *config.user.h* and make sure this number is reflected in the *About* dialog of the user interface.
