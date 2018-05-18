
- image raster cuts off some 5mm at the end
- when serial port ato changes, fails to do so in flash module

v18.05
-------
- revamped serial connection
  - auto connects on usb plugin
  - asks to upload firmware on vanilla arduino
- revamped configuration files
  - loads by default config.json
  - has now --config option to load other configurations
  - has --list-configs to show available configs and config dir
- many small optimizations
- revamped homing cycle, faster, better
- smaller, compressed job files
- milling mode with fusion 360 support (experimental)


bugs
----
- stall between certain x-axis jogs
  - send a pierce command in between
- unplugging usb is not always ahndled gracfully

beauty bugs
-----------
- dba files: optimize should maybe split up into simplified and sorted

optimizations
-------------
- consider changing laser drive board for more frequency control


features
--------
- lasertags
- pixel size assignment for image rasters
- gcode editor
- importers
  - load dxf
  - load gcode
