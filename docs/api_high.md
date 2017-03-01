
High-Level API - web.py
=======================

This module provides a networked interface to the machine. It's a simple web server providing functionality over http. Commands are simple GET-requests with the exeption of */load* and */run* which use POST-requests to transfer potentially large job data. The API is so simple that you can control the machine by directly typing these commands into the URL-bar of a browser. The main intention for this API is to allow alternative user interfaces be easily written. For more elaborate use of this API see the [frontend](frontend.md) and [lasersaur.py](../backend/lasersaur.py).


```
/config
/status
/homing
/feedrate/<val:float>
/intensity/<val:float>
/relative
/absolute
/move/<x:float>/<y:float>/<z:float>
/air_on
/air_off
/aux_on
/aux_off
/offset/<x:float>/<y:float>/<z:float>
/clear_offset
/load
/listing
/listing/<kind>
/get/<jobname>
/star/<jobname>
/unstar/<jobname>
/remove/<jobname>
/clear
/listing_library
/get_library/<jobname>
/load_library/<jobname>
/run/<jobname>
/run
/pause
/unpause
/stop
/unstop
/build
/flash
/flash/<firmware>
/reset
```
