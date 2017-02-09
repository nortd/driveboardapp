"""(Private) Serial port lister for Linux."""

import glob

sys_prefix = b'/sys/class/tty/' # listing of all TTY devices connected
sys_suffix = b'/device/' # that are actual devices
sys_search = sys_prefix + b'*' + sys_suffix
dev_prefix = b'/dev/' # address for accessing such devices

# you can also do a glob of /dev directly, something like '/dev/ttyS*', but that is somewhat more fragile

def portiter():
    for x in glob.iglob(sys_search):
        y = x[len(sys_prefix):-len(sys_suffix)]
        yield (y, dev_prefix + y)
