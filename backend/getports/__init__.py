"""Serial port lister.

The function `ports` returns a tuple of pairs.
The first element of each pair is the name of a serial device as a bytes object,
and the second element is the address of the device as a bytes object.
Names are more-or-less human readable, and addresses may be passed directly to pySerial's Serial class to create the port.

The function `portiter` is the same except for returning an iterable.
If only looping through once, it is likely more efficient.
"""

import sys

__all__ = ['portiter', 'ports']


p = sys.platform
if p == 'win32':
    from wingetports import portiter
elif p == 'darwin': # mac
    from macgetports import portiter
elif p.startswith('linux'):
    from linuxgetports import portiter
else:
    raise OSError('Unsupported platform {}'.format(p))

def ports():
    return tuple(portiter())
