"""(Private) Serial port lister for Windows.

Do not import on other operating systems.

Adapted from code by Eli Bendersky:
    http://eli.thegreenplace.net/2009/07/31/listing-all-serial-ports-on-windows-with-python/
"""

import sys
if sys.version_info.major > 2:
    import winreg
else:
    import _winreg as winreg

port_prefix = b'\\\\.\\' # two backlashes, a dot, and another backslash
# port_prefix is not necessary for COM1 through COM9, but doesn't hurt

def portiter():
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, b'HARDWARE\\DEVICEMAP\\SERIALCOMM') # open the registry
    i = 0
    while True: # loop until we run out of devices
        try:
            name = bytes(winreg.EnumValue(key, i)[1]) # get the device name
            # EnumValue gets item number i, returning a tuple containing the name in position 1
        except OSError: # that's all the devices
            break
        yield name, port_prefix + name
        i += 1
