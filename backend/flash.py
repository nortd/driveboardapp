# -*- coding: UTF-8 -*-
# Super Awesome DriveboardFirmware python flash script.
#
# Copyright (c) 2011 Nortd Labs
# Open Source by the terms of the Gnu Public License (GPL3) or higher.

import os, sys, time, subprocess, stat
from config import conf


def flash_upload(serial_port=conf['serial_port'], resources_dir=conf['rootdir'], firmware=conf['firmware']):
    firmware = firmware.replace("/", "").replace("\\", "")  # make sure no evil injection
    FIRMWARE = os.path.join(resources_dir, 'firmware', "firmware.%s.hex" % (firmware))

    if not os.path.exists(FIRMWARE):
        print "ERROR: invalid firmware path"
        print FIRMWARE
        return

    if not (conf['hardware'] == 'beaglebone' or conf['hardware'] == 'raspberrypi'):
        DEVICE = "atmega328p"
        CLOCK = "16000000"
        PROGRAMMER = "arduino"
        BITRATE = "115200"

        if sys.platform == "darwin":  # OSX
            AVRDUDEAPP    = os.path.join(resources_dir, "firmware/tools_osx/avrdude")
            AVRDUDECONFIG = os.path.join(resources_dir, "firmware/tools_osx/avrdude.conf")
            # chmod +x
            st = os.stat(AVRDUDEAPP)
            os.chmod(AVRDUDEAPP, st.st_mode | stat.S_IEXEC)

        elif sys.platform == "win32": # Windows
            AVRDUDEAPP    = os.path.join(resources_dir, 'firmware', "tools_win", "avrdude")
            AVRDUDECONFIG = os.path.join(resources_dir, 'firmware', "tools_win", "avrdude.conf")

        elif sys.platform == "linux" or sys.platform == "linux2":  #Linux
            # AVRDUDEAPP    = os.path.join(resources_dir, "/usr/bin/avrdude")
            # AVRDUDECONFIG = os.path.join(resources_dir, "/etc/avrdude.conf")
            # AVRDUDEAPP    = os.path.join(resources_dir, 'firmware', "tools_linux", "avrdude64")
            AVRDUDEAPP    = os.path.join(resources_dir, 'firmware', "tools_linux", "avrdude")
            AVRDUDECONFIG = os.path.join(resources_dir, 'firmware', "tools_linux", "avrdude.conf")
            # chmod +x
            # st = os.stat(AVRDUDEAPP)
            # os.chmod(AVRDUDEAPP, st.st_mode | stat.S_IEXEC)

        # call avrdude, returns 0 on success
        command = ('"%(dude)s" -c %(programmer)s -b %(bps)s -P %(port)s -p %(device)s -C "%(dudeconf)s" -Uflash:w:"%(firmware)s":i'
            % {'dude':AVRDUDEAPP, 'programmer':PROGRAMMER, 'bps':BITRATE, 'port':serial_port, 'device':DEVICE, 'dudeconf':AVRDUDECONFIG, 'firmware':FIRMWARE})

        print command
        return subprocess.call(command, shell=True)

        # PROGRAMMER = "avrisp"  # old way, required pressing the reset button
        # os.system('%(dude)s -c %(programmer)s -b %(bps)s -P %(port)s -p %(device)s -C %(dudeconf)s -B 10 -F -U flash:w:%(firmware)s:i'
        #     % {'dude':AVRDUDEAPP, 'programmer':PROGRAMMER, 'bps':BITRATE, 'port':serial_port, 'device':DEVICE, 'dudeconf':AVRDUDECONFIG, 'firmware':FIRMWARE})

        # fuse setting taken over from Makefile for reference
        #os.system('%(dude)s -U hfuse:w:0xd2:m -U lfuse:w:0xff:m' % {'dude':AVRDUDEAPP})

    elif conf['hardware'] == 'beaglebone' or conf['hardware'] == 'raspberrypi':
        # Make sure you have avrdude installed:
        # beaglebone:
        # opkg install libreadline5_5.2-r8.9_armv4.ipk
        # opkg install avrdude_5.10-r1.9_armv7a.ipk
        # get the packages from http://www.angstrom-distribution.org/repo/
        # raspberrypi:
        # sudo apt-get install avrdude

        AVRDUDEAPP    = "avrdude"
        AVRDUDECONFIG = "/etc/avrdude.conf"
        SERIAL_PORT = serial_port
        DEVICE = "atmega328p"
        PROGRAMMER = "arduino"    # use this for bootloader
        SERIAL_OPTION = '-P %(port)s' % {'port':SERIAL_PORT}
        BITRATE = "115200"

        command = ('"%(dude)s" -c %(programmer)s -b %(bps)s %(serial_option)s -p %(device)s -C "%(dudeconf)s" -Uflash:w:"%(product)s":i' %
                  {'dude':AVRDUDEAPP, 'programmer':PROGRAMMER, 'bps':BITRATE, 'serial_option':SERIAL_OPTION, 'device':DEVICE, 'dudeconf':AVRDUDECONFIG, 'product':FIRMWARE})

        ### Trigger the atmega328's reset pin to invoke bootloader

        if conf['hardware'] == 'beaglebone':
            print "Flashing from BeagleBone ..."
            # The reset pin is connected to GPIO2_7 (2*32+7 = 71).
            # Setting it to low triggers a reset.
            # echo 71 > /sys/class/gpio/export
            try:
                import Adafruit_BBIO.GPIO as GPIO
                GPIO.setup("P8_46", GPIO.OUT)
                GPIO.output("P8_46", GPIO.LOW)
                GPIO.setup("P8_44", GPIO.OUT)
                GPIO.output("P8_44", GPIO.LOW)
                time.sleep(0.5)
                GPIO.output("P8_46", GPIO.HIGH)
                GPIO.output("P8_44", GPIO.HIGH)
            except ImportError:
                try:
                    fw = file("/sys/class/gpio/export", "w")
                    fw.write("%d" % (71))
                    fw.close()
                    fwb = file("/sys/class/gpio/export", "w")
                    fwb.write("%d" % (73))
                    fwb.close()
                except IOError:
                    # probably already exported
                    pass
                # set the gpio pin to output
                # echo out > /sys/class/gpio/gpio71/direction
                fw = file("/sys/class/gpio/gpio71/direction", "w")
                fw.write("out")
                fw.close()
                fwb = file("/sys/class/gpio/gpio73/direction", "w")
                fwb.write("out")
                fwb.close()
                # set the gpio pin low -> high
                # echo 1 > /sys/class/gpio/gpio71/value
                fw = file("/sys/class/gpio/gpio71/value", "w")
                fw.write("0")
                fw.flush()
                fwb = file("/sys/class/gpio/gpio73/value", "w")
                fwb.write("0")
                fwb.flush()
                time.sleep(0.5)
                fw.write("1")
                fw.flush()
                fw.close()
                fwb.write("1")
                fwb.flush()
                fwb.close()
                time.sleep(0.1)
        elif conf['hardware'] == 'raspberrypi':
            print "Flashing from Raspberry Pi ..."
            import thread
            import RPi.GPIO as GPIO
            def trigger_reset():
                GPIO.setmode(GPIO.BCM)  # use chip pin number
                pinReset = 2
                GPIO.setup(pinReset, GPIO.OUT)
                GPIO.output(pinReset, GPIO.LOW)
                time.sleep(0.8)
                GPIO.output(pinReset, GPIO.HIGH)
                time.sleep(0.1)
            thread.start_new_thread(trigger_reset, ())
            # GPIO.setmode(GPIO.BCM)  # use chip pin number
            # pinReset = 2
            # # GPIO.setup(pinReset, GPIO.OUT)
            # GPIO.output(pinReset, GPIO.LOW)
            # time.sleep(0.5)
            # GPIO.output(pinReset, GPIO.HIGH)
            # time.sleep(0.1)

        print command
        return subprocess.call(command, shell=True)


def reset_atmega():
    print "Resetting Atmega ..."
    if conf['hardware'] == 'beaglebone':
        try:
            import Adafruit_BBIO.GPIO as GPIO
            GPIO.setup("P8_46", GPIO.OUT)
            GPIO.output("P8_46", GPIO.LOW)
            GPIO.setup("P8_44", GPIO.OUT)
            GPIO.output("P8_44", GPIO.LOW)
            time.sleep(0.2)
            GPIO.output("P8_46", GPIO.HIGH)
            GPIO.output("P8_44", GPIO.HIGH)
        except ImportError:
            try:
                fw = file("/sys/class/gpio/export", "w")
                fw.write("%d" % (71))
                fw.close()
                fwb = file("/sys/class/gpio/export", "w")
                fwb.write("%d" % (73))
                fwb.close()
            except IOError:
                pass
            fw = file("/sys/class/gpio/gpio71/direction", "w")
            fw.write("out")
            fw.close()
            fwb = file("/sys/class/gpio/gpio73/direction", "w")
            fwb.write("out")
            fwb.close()
            fw = file("/sys/class/gpio/gpio71/value", "w")
            fw.write("0")
            fw.flush()
            fwb = file("/sys/class/gpio/gpio73/value", "w")
            fwb.write("0")
            fwb.flush()
            time.sleep(0.2)
            fw.write("1")
            fw.flush()
            fw.close()
            fwb.write("1")
            fwb.flush()
            fwb.close()
    elif conf['hardware'] == 'raspberrypi':
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)  # use chip pin number
        pinReset = 2
        GPIO.setup(pinReset, GPIO.OUT)
        GPIO.output(pinReset, GPIO.LOW)
        time.sleep(0.2)
        GPIO.output(pinReset, GPIO.HIGH)
    else:
        print "ERROR: forced reset only possible on beaglebone and raspberrypi"
        raise IOError


def usb_reset_hack():
    # Hack to reset usb (possibly linux-only), read flash with avrdude
    # This solves a problem on my dev machine where the serial connection
    # fails after replugging the usb arduino. It seems strictly related
    # to the USB stack on the Linux dev machine (possibly also on OSX or Win).
    # Note: This should be irrelevant on the Lasersaur/BBB.
    command = "avrdude -p atmega328p -P "+conf['serial_port']+" -c arduino -U flash:r:flash.bin:r -q -q"
    return subprocess.call(command, shell=True)


if __name__ == '__main__':
    ret = flash_upload()
    if ret != 0:
        print "ERROR: flash failed"
