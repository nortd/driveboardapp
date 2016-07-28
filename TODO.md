

- quick fill, slow fill, or better optimized sorted line fill
- clean up config.py, rename raster_size

bugs
----
- move when no machine does not recover, false feedback


beauty bugs
-----------
- stall between certain x-axis jogs
  - send a pierce command in between
- dba files: optimize should maybe split up into simplified and sorted

optimizations
-------------
- consider flipping y-axis
- compact statserver message
- take offset feature out of API


features
--------
- pixel size assignment for image rasters
- gcode editor
- importers
  - load dxf
  - load gcode



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
