
- image raster cuts off some 5mm at the end
- when serial port ato changes, fails to do so in flash module


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
