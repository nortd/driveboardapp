# -*- coding: UTF-8 -*-
# Super Awesome DriveboardFirmware python flash script.
#
# Copyright (c) 2011 Nortd Labs
# Open Source by the terms of the Gnu Public License (GPL3) or higher.

import os, sys, subprocess, shutil, glob
from config import conf

# Make sure you have the Arduino IDE installed (we've tested this on 022 and newer).
# While build.py does not use the IDE directly it makes use of its tool chain.
# On Linux all you need is the "arduino-core" package.
# Please verify the following locations are correct for you platform:

if sys.platform == "darwin":  # OSX
    AVRDUDEAPP    = "/Applications/Arduino.app/Contents/Java/hardware/tools/avr/bin/avrdude"
    AVRGCCAPP     = "/Applications/Arduino.app/Contents/Java/hardware/tools/avr/bin/avr-gcc"
    AVROBJCOPYAPP = "/Applications/Arduino.app/Contents/Java/hardware/tools/avr/bin/avr-objcopy"
    AVRSIZEAPP    = "/Applications/Arduino.app/Contents/Java/hardware/tools/avr/bin/avr-size"
    AVROBJDUMPAPP = "/Applications/Arduino.app/Contents/Java/hardware/tools/avr/bin/avr-objdump"
    AVRDUDECONFIG = "/Applications/Arduino.app/Contents/Java/hardware/tools/avr/etc/avrdude.conf"

elif sys.platform == "win32": # Windows
    AVRDUDEAPP    = "C:\\arduino\\hardware\\tools\\avr\\bin\\avrdude"
    AVRGCCAPP     = "C:\\arduino\\hardware\\tools\\avr\\bin\\avr-gcc"
    AVROBJCOPYAPP = "C:\\arduino\\hardware\\tools\\avr\\bin\\avr-objcopy"
    AVRSIZEAPP    = "C:\\arduino\\hardware\\tools\\avr\\bin\\avr-size"
    AVROBJDUMPAPP = "C:\\arduino\\hardware\\tools\\avr\\bin\\avr-objdump"
    AVRDUDECONFIG = "C:\\arduino\\hardware\\tools\\avr\\etc\\avrdude.conf"

elif sys.platform == "linux" or sys.platform == "linux2":  #Linux
    AVRDUDEAPP    = "avrdude"
    AVRGCCAPP     = "avr-gcc"
    AVROBJCOPYAPP = "avr-objcopy"
    AVRSIZEAPP    = "avr-size"
    AVROBJDUMPAPP = "avr-objdump"
    AVRDUDECONFIG = "/etc/avrdude.conf"



# =============================================================================
# No need to edit anything below this line


def build_all():
    """Build firmwares for all config files.
    Each config.*.h becomes a firmware called firmware.*.hex
    """
    firmware_dir = os.path.join(conf['rootdir'], 'firmware')
    source_dir = os.path.join(firmware_dir, 'src')
    # set cwd
    cwd_temp = os.getcwd()
    os.chdir(source_dir)
    # gather all firmware config files
    config_files = glob.glob("config.*.h")

    ret = 0
    for config_file in config_files:
        hardware_designator = config_file.split('.')[1:-1][0]
        # activate
        shutil.copy('config.h', '~config.h')
        shutil.copy(config_file, 'config.h')
        try:
            firmware_name = "firmware.%s" % (hardware_designator)
            print "INFO: building for %s" % (config_file)
            # buid
            r = build_firmware(firmware_name)
            if r != 0:
                ret = 1
        finally:
            # revert config.h
            if os.path.exists('~config.h'):
                shutil.move('~config.h', 'config.h')
    # restore cwd
    os.chdir(cwd_temp)
    return ret



def build_firmware(firmware_name="DriveboardFirmware"):
    """Build the firmware and name it firmware_name.hex.
    The source code is assumed to be in ../firmware/src/
    And the hex file will be placed in ../firmware/
    Returns 0 on success.
    """
    ret = 0

    firmware_dir = os.path.join(conf['rootdir'], 'firmware')
    source_dir = os.path.join(firmware_dir, 'src')

    cwd_temp = os.getcwd()
    os.chdir(source_dir)

    DEVICE = "atmega328p"
    CLOCK = "16000000"
    BUILDNAME = firmware_name
    OBJECTS  = ["main", "serial", "protocol", "planner", "sense_control", "stepper"]

    COMPILE = AVRGCCAPP + " -Wall -Os -DF_CPU=" + CLOCK + " -mmcu=" + DEVICE + " -I. -ffunction-sections" + " --std=c99"
    # COMPILE = AVRGCCAPP + " -Wall -O3 -DF_CPU=" + CLOCK + " -mmcu=" + DEVICE + " -I. -ffunction-sections" + " --std=c99"

    for fileobj in OBJECTS:
        command = '%(compile)s -c %(obj)s.c -o %(obj)s.o' % {'compile': COMPILE, 'obj':fileobj}
        ret += subprocess.call(command, shell=True)

    command = '%(compile)s -o main.elf %(alldoto)s  -lm' % {'compile': COMPILE, 'alldoto':".o ".join(OBJECTS)+'.o'}
    ret += subprocess.call(command, shell=True)

    command = '%(objcopy)s -j .text -j .data -O ihex main.elf %(product)s.hex' % {'objcopy': AVROBJCOPYAPP, 'obj':fileobj, 'product':BUILDNAME}
    ret += subprocess.call(command, shell=True)

    # command = '%(size)s *.hex *.elf *.o' % {'size':AVRSIZEAPP}
    command = '%(size)s --mcu=%(mcu)s --format=avr *.elf' % {'size':AVRSIZEAPP, 'mcu':DEVICE}
    ret += subprocess.call(command, shell=True)

    # command = '%(objdump)s -t -j .bss main.elf' % {'objdump':AVROBJDUMPAPP}
    # ret += subprocess.call(command, shell=True)

    if ret != 0:
        return "Error: failed to build"

    try:
        ## clean after upload
        print "Cleaning up build files."
        for fileobj in OBJECTS:
            f = '%s.o' % (fileobj)
            if os.path.isfile(f):
                os.remove(f)
        if os.path.isfile('main.elf'):
            os.remove('main.elf')

        ## move firmware hex file
        print "Moving firmware to standard location."
        firmware_src = firmware_name+'.hex'
        firmware_dst = os.path.join(firmware_dir, firmware_src)
        shutil.move(firmware_src, firmware_dst)
        print firmware_dst
    finally:
        #restore previous cwd
        os.chdir(cwd_temp)

    return 0


if __name__ == '__main__':
    build_all()
