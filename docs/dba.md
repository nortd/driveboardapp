
DriveboardApp File Format
=========================

The native file format has the extension .dba and is technically a json text file. It can save paths, fills, and images along with pass definition.

Simple Example
--------------
```
{
  "passes":
  [
    {
      "items":[0],
      "feedrate":400,
      "intensity":15
    }
  ],
  "items":[{"def":0}],
  "defs":[
    {"kind":"path", "data":[[[100,520],[105,520]]]}
  ]
}
```

Complete File Description
-------------------------

```
{
  "head": {                      # optional
      "noreturn": True,          # optional, do not return to origin, default: False
      "optimized": 0.08,         # optional, tolerance to which it was optimized, default: 0 (not optimized)
   },
  "passes": [                    # optional
      {
          "items": [0],          # item by index
          "relative": True,      # optional, default: False
          "seekrate": 6000,      # optional, rate to first vertex
          "feedrate": 2000,      # optional, rate to other vertices
          "intensity": 100,      # optional, default: 0 (in percent)
          "seekzero": False,     # optional, default: True
          "pierce_time": 0,      # optional, default: 0
          "pxsize": 0.4,         # optional
          "air_assist": "pass",  # optional (feed, pass, off), default: pass
          "aux_assist": "off",   # optional (feed, pass, off), default: off
      }
  ],
 "items": [
    {"def":0, "translate":[0,0,0], "color":"#BADA55"}   # translate, color are optional
 ],
 "defs": [
    {"kind":"path", "data":[[[0,10,0]]]},               # data is a list of polylines
    {"kind":"fill", "data":[[[0,10,0]]], "pxsize":0.4},
    {"kind":"image", "data":<data in base64>, "pos":[0,0], "size":[300,200]},
 ],
 "stats":{"items":[{"bbox":[x1,y1,x2,y2], "len":100}], "all":{}}   # optional
}
```
