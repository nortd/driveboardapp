

- bugs
  - buffer overflow
    - only when doing a raster after a homing
    - no problem when doing a homing, move, raster
  - export svg with raster fails on import
  - queue not updated when loading from library
  - stall between certain x-axis jogs
    - send a pierce command in between


- gcode editor

- load dxf
- load gcode

- raster
  - raster fills
  - image raster

- PIL/Pillow dependancy
  - apt-get update
  - apt-get install python-imaging

replace /etc/apt/sources.list
-----------------------------
deb http://old-releases.ubuntu.com/ubuntu/ raring main universe restricted multiverse
deb-src http://old-releases.ubuntu.com/ubuntu/ raring main universe restricted multiverse

deb http://old-releases.ubuntu.com/ubuntu/ raring-security main universe restricted multiverse
deb-src http://old-releases.ubuntu.com/ubuntu/ raring-security main universe restricted multiverse

deb http://old-releases.ubuntu.com/ubuntu/ raring-updates main universe restricted multiverse
deb-src http://old-releases.ubuntu.com/ubuntu/ raring-updates main universe restricted multiverse

deb http://old-releases.ubuntu.com/ubuntu/ raring-backports main restricted universe multiverse
deb-src http://old-releases.ubuntu.com/ubuntu/ raring-backports main restricted universe multiverse

deb http://old-releases.ubuntu.com/ubuntu/ raring-proposed main restricted universe multiverse
deb-src http://old-releases.ubuntu.com/ubuntu/ raring-proposed main restricted universe multiverse
