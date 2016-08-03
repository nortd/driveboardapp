

driveboard.py
-------------

This module does all the serial communication. It knows the [hardware protocol](protocol.md) and provides a low-level API for talking to the hardware. It can perfectly well be used from the python CLI or in custom python scripts.

#### Example usage
```
import driveboard, sys, time
driveboard.connect()
driveboard.jobfile("../library/lasersaur.dba")
while not driveboard.status()['ready']:
    time.sleep(1)
    sys.stdout.write('.')
driveboard.close()
```


#### drivboard.py API
```
find_controller()
connect()
connected()
close()

flash()
build()
reset()
status()

homing()
feedrate(val)
intensity(val)
duration(val)
pixelwidth(val)
realtive()
absolute()
move(x, y, z)
rastermove(x, y, z)
rasterdata(data, start, end)
job(job)

pause()
unpause()
stop()
unstop()

air_on()
air_off()
aux1_on()
aux1_off()
aux2_on()
aux2_off()

set_offset_table()
set_offset_custom()
def_offset_table(x, y, z)
def_offset_custom(x, y, z)
sel_offset_table()
sel_offset_custom()
```
