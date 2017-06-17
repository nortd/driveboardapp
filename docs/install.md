
DriveboardApp Installation
==========================

In general simply download and run:
```
python driveboardapp/backend/app.py
```

If necessary, create a [configuration](configure.md) file for the app.


### Troubleshooting
If any issues occur it helps to install the [Arduino IDE installation](https://www.arduino.cc/en/Guide/HomePage) and get the blink LED example to run. This makes sure the basics work. For example on Linux the Arduino IDE will ask you to give access permission to the serial port.


Lasersaur Driveboard v14.04 Setup
---------------------------------
- make sure the Driveboard/Lasersaur can access the Internet
- ssh into the Driveboard/Lasersaur with `ssh lasersaur.local` and do the follwoing:
```
git clone https://github.com/nortd/driveboardapp.git
cd driveboardapp
scripts/install_packages.sh
scripts/upgrade_to_driveboardapp.sh
pkill python
python backend/flash.py
reboot
```
If for some reason you want to downgrade and use LasaurApp again run:
```
scripts/downgrade_to_lasaurapp.sh
reboot
```


MinimalDriveboard Setup
------------------------

DriveboardApp is quite flexible software and can be run on any Windows, OSX, or Linux computer. A [MinimalDriveboard](minimaldriveboard.md) can be connected via USB directly. In this case the DriveboardApp *backend* runs on the computer and the browser connects locally.

- Open the command line.
- Make sure you have Python 2.7, run `python --version`
  - If not, get 2.7.x installers from the [Python Website](http://python.org/download/).
  - On Windows we recommend using the [ActiveState distribution](http://www.activestate.com/activepython/downloads) as it sets all the PATH shortcuts.
- Download the latest [stable DriveboardApp](https://github.com/nortd/driveboardapp/archive/master.zip) and unzip to a convenient location.
  - For advanced users we recommend using `git clone https://github.com/nortd/driveboardapp.git` instead. This way you can easily update with `git pull`
- Change dicrectory to that location and run `python backend/app.py -b`

At this point your default browser should open at [http://localhost:4444](http://localhost:4444). DriveboardApp runs in any current Firefox or Chrome (Safari and IE may work too). Congrats!

If you get a serial port error you may have to configure it by [setting up a configuration](configure.md) file and point to the port where the Hardware is connected to. On Linux you may also have to set proper r/w permissions for the serial port.
