{
     "head": {
       "noreturn": True,            # do not return to origin, default: False
       "optimized": 0.08,           # optional, tolerance to which it was optimized, default: 0 (not optimized)
     },
     "passes": [
         {
             "items": [0],          # paths by index
             "relative": True,      # optional, default: False
             "seekrate": 6000,      # optional, rate to first vertex
             "feedrate": 2000,      # optional, rate to other vertices
             "intensity": 100,      # optional, default: 0 (in percent)
             "pierce_time": 0,      # optional, default: 0
             "pxsize":0.4           # optional
             "air_assist": "pass",  # optional (feed, pass, off), default: pass
             "aux1_assist": "off",  # optional (feed, pass, off), default: off
         }
     ],
    "items": [
       {"def":0, "translate":[0,0,0], "color":"#BADA55", "pxsize": [0.4]}
    ],
    "defs": [
       {"kind":"path", "data":[[[0,10,0]]]},
       {"kind":"fill", "data":[[[0,10,0]]], "pxsize":0.4},
       {"kind":"image", "data":<data in base64>, "pos":[0,0], "size":[300,200]},
    ],
   "stats":{}
}


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
