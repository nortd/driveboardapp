
DriveboardApp Configuration
===========================

The main configuration file is [config.py](../backend/config.py). It contains the *conf* dictionary which gets used in both the *backend* and *frontend*.

How to change
-------------
Instead of changing the *conf* fields directly in *config.py* create a *userconfig.py* file in the same directory. Then set the fields you want to change in this file. For example if you want to change the serial port, workspace size and web credentials write the following into *userconfig.py*:

```
conf = {
    'serial_port': '/dev/ttyACM1',
    'workspace': [1000,1000,0],
    'users': {
        'user1': 'password1',
    }
}
```
This way you always retain the default settings and your new settings won't be overwritten when updating the software with `git pull`.


Firmware Configuration
----------------------

Similarly the main configuration file for the firmware is [config.h](../firmware/src/config.h) and an alternative configuration can be created by adding a *config.user.h* file. This file has to be complete and is typically the *config.h* with some modifications. The main reason this is done like this is to prevent your changes being overwritten when you update the software with a `git pull`.

Any updates or changes to the firmware are not automatically loaded onto the Driveboard. For this use the *Flash from source* feature in the user interface. After flashing it's recommended to restart the Driveboard. For your own sanity you should also change the `define VERSION` entry in *config.user.h* and make sure this number is reflected in the *About* dialog of the user interface.
