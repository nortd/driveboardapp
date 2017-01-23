# -*- coding: UTF-8 -*-
import sys
import os
import time
import argparse

import web
from config import conf

__author__  = 'Stefan Hechenberger <stefan@nortd.com>'


### Setup Argument Parser
argparser = argparse.ArgumentParser(description='Run DriveboardApp.', prog='driveboardapp')
argparser.add_argument('-v', '--version', action='version', version='%(prog)s ' + conf['version'],
                       default=False, help='print version of this app')
argparser.add_argument('-d', '--debug', dest='debug', action='store_true',
                       default=False, help='print more verbose for debugging')
# argparser.add_argument('-b', '--browser', dest='browser', action='store_true',
#                        default=False, help='launch interface in browser')
argparser.add_argument('-n', '--nobrowser', dest='nobrowser', action='store_true',
                       default=False, help='do not launch interface in browser')
argparser.add_argument('-c', '--cli', dest='cli', action='store_true',
                       default=False, help='run without server GUI window')
argparser.add_argument('-u', '--usbhack', dest='usbhack', action='store_true',
                       default=False, help='use usb reset hack (advanced)')
args = argparser.parse_args()

try:
    import Tkinter
except ImportError:
    args.cli = True

if not args.cli:
    import window
    root = window.init()

print "DriveboardApp v" + conf['version']
conf['usb_reset_hack'] = args.usbhack

# start server in thread
web.start(browser=(not args.nobrowser), debug=args.debug)

# main thread loop
while 1:
    try:
        if not args.cli:
            try:
                root.update()
            except Tkinter.TclError:
                break
        time.sleep(0.1)
    except KeyboardInterrupt:
        break
web.stop()
print "END of DriveboardApp"
