"""(Private) Serial port lister for Mac OS X.

Do not import on other operating systems.

Inspired by osxserialports by Pascal Oberndoerfer.
"""

import sys
import ctypes
from ctypes.util import find_library

# we could also do this with a glob of /dev, something like '/dev/tty.*', but that is somewhat more fragile

# load cdll libraries
corefound = ctypes.CDLL(find_library('CoreFoundation'))
iokit = ctypes.CDLL(find_library('IOKit'))

# defining argument and return types is necessary to stop ctypes treating everything as 32-bit integers
# however, we don't really care about the contents of the various structs, so c_void_p is good enough
corefound.__CFStringMakeConstantString.argtypes = [ctypes.c_char_p]
corefound.__CFStringMakeConstantString.restype = ctypes.c_void_p
iokit.IOServiceMatching.argtypes = [ctypes.c_char_p]
iokit.IOServiceMatching.restype = ctypes.c_void_p
iokit.IOServiceGetMatchingServices.argtypes  = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
iokit.IOIteratorNext.argtypes = [ctypes.c_void_p]
iokit.IOIteratorNext.restype = ctypes.c_void_p
iokit.IORegistryEntryCreateCFProperty.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
iokit.IORegistryEntryCreateCFProperty.restype = ctypes.c_void_p
corefound.CFStringGetCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
corefound.CFRelease.argtypes = [ctypes.c_void_p]
iokit.IOObjectRelease.argtypes = [ctypes.c_void_p]

# useful constants from IOKit and CoreFoundation, not easily accessible with ctypes
kIOSerialBSDServiceValue = b'IOSerialBSDClient'
kIOTTYDeviceKey = corefound.__CFStringMakeConstantString(b'IOTTYDevice')
kIODialinDeviceKey = corefound.__CFStringMakeConstantString(b'IODialinDevice')
kCFStringEncodingASCII = 0x600
kCFDefaultAllocator = None # null pointers
kIOMasterPortDefault = None
kNilOptions = 0

MAXSTRLEN = 1024 # I doubt device names will be longer than this

def getstring(dev, key):
    cf = iokit.IORegistryEntryCreateCFProperty(dev, key, kCFDefaultAllocator, kNilOptions) # get from device object
    buf = ctypes.create_string_buffer(MAXSTRLEN) # c string (byte array)
    corefound.CFStringGetCString(cf, buf, MAXSTRLEN, kCFStringEncodingASCII) # convert from CFString to c string
    corefound.CFRelease(cf)
    return buf.value # the .value goes from ctypes byte arrays to python strings

def portiter():
    itr = ctypes.c_void_p() # iterator of ports
    # populate the iterator
    iokit.IOServiceGetMatchingServices(kIOMasterPortDefault, iokit.IOServiceMatching(kIOSerialBSDServiceValue), ctypes.byref(itr))
    while True:
        ds = iokit.IOIteratorNext(itr) # going through each item in the iterator
        if not ds: # a null pointer means we've exhausted the iterator
            break
        yield (getstring(ds, kIOTTYDeviceKey), getstring(ds, kIODialinDeviceKey)) # device name and dialin address
        iokit.IOObjectRelease(ds)
    iokit.IOObjectRelease(itr)
