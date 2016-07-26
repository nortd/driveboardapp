

- bugs
  - laser burst in tight turns (forward port)

- beauty bugs
  - stall between certain x-axis jogs
    - send a pierce command in between

- optimizations
  - compact statserver message

- features
  - quick fill, slow fill
  - pass assignment for rasters
  - raster_size should probably go into the dba file
  - gcode editor
  - importers
    - load dxf
    - load gcode
  - raster fills



PIL/Pillow dependancy
----------------------
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
