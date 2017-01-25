
- laser freq
  - freq always ~270us
  - OCR0B = 0.5*TOP => 50%, OCR0B = 0.25*TOP => 33%

- python-imaging dependancy
- when serial port ato changes, fails to do so in flash module



DriveboardUSB TODO
------------------
- new freq control


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
