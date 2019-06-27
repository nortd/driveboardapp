# -*- coding: UTF-8 -*-
# Configuration of DriveboardApp
#
# NOTE!
# -----
# To change config parameters create a file named
# config.name_of_config.json in the config directory
# (use --list-configs to find it)
# and write something like this:
#
# {
#     "network_port": 4411,
#     "serial_port": "COM3"
# }
#

import os
import sys
import glob
import json
import copy

from encodings import hex_codec  # explicit for pyinstaller
from encodings import ascii  # explicit for pyinstaller
from encodings import utf_8  # explicit for pyinstaller
from encodings import mac_roman  # explicit for pyinstaller


conf = {
    'appname': 'driveboardapp',
    'version': '18.07',
    'company_name': 'com.nortd.labs',
    'network_host': '',                    # '' for all nics
    'network_port': 4444,
    'serial_port': '',                     # set to '' for auto (req. firmware)
    'baudrate': 57600,
    'rootdir': None,                       # defined further down (../)
    'confdir': None,                       # defined further down
    'hardware': None,                      # defined further down
    'firmware': None,                      # defined further down
    'tolerance': 0.01,
    'workspace': [1220,610,0],
    'grid_mm': 100,
    'seekrate': 6000,
    'feedrate': 2000,
    'intensity': 0,
    'kerf': 0.3,
    'pxsize': 0.4,                 # size (mm) of beam for rastering
    'max_jobs_in_list': 20,
    'usb_reset_hack': False,
    'fill_leadin': 10,
    'raster_leadin': 20,
    'max_segment_length': 5.0,
    'users': {
        'laser': 'laser',
    },
    'enable_gzip': True,           # allow gzip upload of files / jobs
    'mill_mode': False,
    'mill_max_rpm': 18000,
}
conf_defaults = copy.deepcopy(conf)

userconfigurable = {
    'network_host': "IP (NIC) to run server on. Leave '' for all.",
    'network_port': "Port to run server on.",
    'serial_port': "Serial port for Driveboard hardware.",
    'firmware': "Default firmware. Use designator matching the * in config.*.h",
    'workspace': "[x,y,z] dimensions of machine's work area in mm.",
    'grid_mm': "Visual grid of UI in mm.",
    'seekrate': "Default seek rate in mm/min",
    'feedrate': "Default feed rate in mm/min.",
    'intensity': "Default intensity setting 0-100.",
    'kerf': "Typical kerf of a cut.",
    'pxsize': "Default kerf setting for rastering.",
    'max_jobs_in_list': "Jobs to keep in the history list.",
    'fill_leadin': "Leadin for vector fills in mm.",
    'raster_leadin': "Leadin for raster fills in mm.",
    'users': "List of user cendentials for UI access.",
    'enable_gzip': "Enable gzip compression in job uploads.",
    'mill_mode': "Activate CNC mill mode.",
    'mill_max_rpm': "Maximum spindle RPM."
}


### make some 'smart' default setting choices


### rootdir
# This is to be used with all relative file access.
# _MEIPASS is a special location for data files when creating
# standalone, single file python apps with pyInstaller.
# Standalone is created by calling from 'other' directory:
# python pyinstaller/pyinstaller.py --onefile app.spec
if hasattr(sys, "_MEIPASS"):
    conf['rootdir'] = sys._MEIPASS
else:
    # root is one up from this file
    conf['rootdir'] = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))
#
###


### stordir
# This is to be used to store queue files and similar
if sys.platform == 'darwin':
    directory = os.path.join(os.path.expanduser('~'),
                             'Library', 'Application Support',
                             conf['company_name'], conf['appname'])
elif sys.platform == 'win32':
    directory = os.path.join(os.path.expandvars('%APPDATA%'),
                             conf['company_name'], conf['appname'])
else:
    directory = os.path.join(os.path.expanduser('~'), "." + conf['appname'])
if not os.path.exists(directory):
    os.makedirs(directory)
conf['confdir'] = directory
#
###



### auto-check hardware
#
conf['hardware'] = 'standard'
if sys.platform == "linux2":
    try:
        import RPi.GPIO
        conf['hardware'] = 'raspberrypi'
    except ImportError:
        # try to import Adafruit GPIO library for Debian 9 based official BB image
        try:
            global GPIO
            import Adafruit_BBIO.GPIO as GPIO
        except ImportError:
            # Adafruit GPIO library unavailable. Do nothing and continue.
            pass
        # os.uname() on BBB:
        # ('Linux', 'lasersaur', '3.8.13-bone20',
        #  '#1 SMP Wed May 29 06:14:59 UTC 2013', 'armv7l')
        if os.uname()[4].startswith('arm'):
            conf['hardware'] = 'beaglebone'
#
###


if conf['hardware'] == 'standard':
    if not conf['firmware']:
        conf['firmware'] = 'driveboardusb'
elif conf['hardware'] == 'beaglebone':
    if not conf['firmware']:
        conf['firmware'] = 'driveboard1403'
    conf['serial_port'] = '/dev/ttyO1'
    # if running as root
    if os.geteuid() == 0:
        conf['network_port'] = 80

    # Beaglebone white specific
    if os.path.exists("/sys/kernel/debug/omap_mux/uart1_txd"):
        # we are not on the beaglebone black, setup uart1
        # echo 0 > /sys/kernel/debug/omap_mux/uart1_txd
        fw = file("/sys/kernel/debug/omap_mux/uart1_txd", "w")
        fw.write("%X" % (0))
        fw.close()
        # echo 20 > /sys/kernel/debug/omap_mux/uart1_rxd
        fw = file("/sys/kernel/debug/omap_mux/uart1_rxd", "w")
        fw.write("%X" % ((1 << 5) | 0))
        fw.close()

    ### if running on BBB/Ubuntu 14.04, setup pin muxing UART1
    pin24list = glob.glob("/sys/devices/ocp.*/P9_24_pinmux.*/state")
    for pin24 in pin24list:
        os.system("echo uart > %s" % (pin24))

    pin26list = glob.glob("/sys/devices/ocp.*/P9_26_pinmux.*/state")
    for pin26 in pin26list:
        os.system("echo uart > %s" % (pin26))


    ### Set up atmega328 reset control
    # The reset pin is connected to GPIO2_7 (2*32+7 = 71).
    # Setting it to low triggers a reset.
    # echo 71 > /sys/class/gpio/export

    ### if running on BBB/Ubuntu 14.04, setup pin muxing GPIO2_7 (pin 46)
    pin46list = glob.glob("/sys/devices/ocp.*/P8_46_pinmux.*/state")
    for pin46 in pin46list:
        os.system("echo gpio > %s" % (pin46))

    if ('GPIO' in globals()):
        GPIO.setup("P8_46", GPIO.OUT)
        GPIO.output("P8_46", GPIO.HIGH)
    else:
        try:
            fw = file("/sys/class/gpio/export", "w")
            fw.write("%d" % (71))
            fw.close()
        except IOError:
            # probably already exported
            pass
        # set the gpio pin to output
        # echo out > /sys/class/gpio/gpio71/direction
        fw = file("/sys/class/gpio/gpio71/direction", "w")
        fw.write("out")
        fw.close()
        # set the gpio pin high
        # echo 1 > /sys/class/gpio/gpio71/value
        fw = file("/sys/class/gpio/gpio71/value", "w")
        fw.write("1")
        fw.flush()
        fw.close()

    ### Set up atmega328 reset control - BeagleBone Black
    # The reset pin is connected to GPIO2_9 (2*32+9 = 73).
    # Setting it to low triggers a reset.
    # echo 73 > /sys/class/gpio/export

    ### if running on BBB/Ubuntu 14.04, setup pin muxing GPIO2_9 (pin 44)
    pin44list = glob.glob("/sys/devices/ocp.*/P8_44_pinmux.*/state")
    for pin44 in pin44list:
        os.system("echo gpio > %s" % (pin44))

    if ('GPIO' in globals()):
        GPIO.setup("P8_44", GPIO.OUT)
        GPIO.output("P8_44", GPIO.HIGH)
    else:
        try:
            fw = file("/sys/class/gpio/export", "w")
            fw.write("%d" % (73))
            fw.close()
        except IOError:
            # probably already exported
            pass
        # set the gpio pin to output
        # echo out > /sys/class/gpio/gpio73/direction
        fw = file("/sys/class/gpio/gpio73/direction", "w")
        fw.write("out")
        fw.close()
        # set the gpio pin high
        # echo 1 > /sys/class/gpio/gpio73/value
        fw = file("/sys/class/gpio/gpio73/value", "w")
        fw.write("1")
        fw.flush()
        fw.close()

    ### read stepper driver configure pin GPIO2_12 (2*32+12 = 76).
    # Low means Geckos, high means SMC11s

    ### if running on BBB/Ubuntu 14.04, setup pin muxing GPIO2_12 (pin 39)
    pin39list = glob.glob("/sys/devices/ocp.*/P8_39_pinmux.*/state")
    for pin39 in pin39list:
        os.system("echo gpio > %s" % (pin39))

    if ('GPIO' in globals()):
        GPIO.setup("P8_39", GPIO.IN)
        ret = GPIO.input("P8_39")
    else:
        try:
            fw = file("/sys/class/gpio/export", "w")
            fw.write("%d" % (76))
            fw.close()
        except IOError:
            # probably already exported
            pass
        # set the gpio pin to input
        fw = file("/sys/class/gpio/gpio76/direction", "w")
        fw.write("in")
        fw.close()
        # set the gpio pin high
        fw = file("/sys/class/gpio/gpio76/value", "r")
        ret = fw.read()
        fw.close()
        # print "Stepper driver configure pin is: " + str(ret)

elif conf['hardware'] == 'raspberrypi':
    if not conf['firmware']:
        conf['firmware'] = 'driveboard1403'
    conf['serial_port'] = '/dev/ttyAMA0'
    # if running as root
    if os.geteuid() == 0:
        conf['network_port'] = 80
    import RPi.GPIO as GPIO
    # GPIO.setwarnings(False) # surpress warnings
    GPIO.setmode(GPIO.BCM)  # use chip pin number
    pinSense = 7
    pinReset = 2
    pinExt1 = 3
    pinExt2 = 4
    pinExt3 = 17
    pinTX = 14
    pinRX = 15
    # read sens pin
    GPIO.setup(pinSense, GPIO.IN)
    isSMC11 = GPIO.input(pinSense)
    # atmega reset pin
    GPIO.setup(pinReset, GPIO.OUT)
    GPIO.output(pinReset, GPIO.HIGH)
    # no need to setup the serial pins
    # although /boot/cmdline.txt and /etc/inittab needs
    # to be edited to deactivate the serial terminal login
    # (basically anything related to ttyAMA0)


configpath = ''
def load(configname):
    if configname:
        path = os.path.join(conf['confdir'], 'config.'+configname+'.json')
    else:
        path = os.path.join(conf['confdir'], 'config.json')
    global configpath
    configpath = path
    #load
    if os.path.exists(path):
        # print "CONFIG: " + path
        # apply user config
        with open(path) as fp:
            try:
                userconf = json.load(fp)
                for k in userconfigurable.keys():
                    if k in userconf:
                        conf[k] = userconf[k]
            except ValueError:
                print "ERROR: failed to read config file"
    else:
        if not configname:
            # special case: default config not present, create
            print "INFO: creating default config file"
            with open(path, "w") as fp:
                confout = {k:v for k,v in conf.items() if k in userconfigurable}
                json.dump(confout, fp, indent=4)
        else:
            print "ERROR: invalid config specified"
            sys.exit()


def write_config_fields(subconfigdict):
    conftemp = None
    if os.path.exists(configpath):
        with open(configpath) as fp:
            conftemp = json.load(fp)
    else:
        conftemp = {}
    conftemp.update(subconfigdict)
    with open(configpath, "w") as fp:
        json.dump(conftemp, fp, indent=4)


def list_configs():
    print "Config files in " + conf['confdir'] + ":"
    tempdir = os.getcwd()
    os.chdir(conf['confdir'])
    cfiles = glob.glob('config.*.json')
    for cfile in cfiles:
        confname = cfile.split('.')[1]
        print "%s - (%s)" % (confname, cfile)
    os.chdir(tempdir)
