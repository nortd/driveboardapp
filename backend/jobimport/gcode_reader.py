
__author__ = 'Stefan Hechenberger <stefan@nortd.com>'


import math
import sys
import re
import os.path
import StringIO




class GcodeReader:
    """Parse subset of G-Code.

    GCODE
    -----
    See: http://linuxcnc.org/docs/html/gcode.html

    G0 - rapid move
    G1 - linear move
    G2,G3 - arc move
    G4 - dwell

    G17 - select XY-plane (default)
    G18 - select XZ-plane
    G19 - select YZ-plane

    G20 - inch mode
    G21 - mm mode (default)

    G28 - park machine
        - without params, move to machine 0,0,0
        - with params, first go there (in current cs), typ retract Z
        - (unless G28.1 programmed a different origin)
        - "G28 G91 Z0, G90" typically before tool change, same as "G53 Z0, G53 X0 Y0"

    G38.2-G38.5 - probe

    G53 - use machine coorinates for same block (G53 Z15), non-modal
    G54 - use CS 1 from now on (default)
    G55-G59 - more custom CSes

    G90 - absolute mode (default)
    G91 - relative mode

    G92 - move CS (throw error)

    G93 - inverse time mode
    G94 - units/mm mode (default)
    G95 - units/rev mode


    M0, M1 - pause
    M2, M30 - end

    M3 - start spindel CW at whatever S has been set to
    M4 - start spindel CCW at whatever S has been set to
    M5 - stop spindel

    M6 - stop, prompt for tool change, non-modal
       - to whatever the most recent Tx was

    M7 - mist coolant on
    M8 - flood coolant on
    M9 - all coolant off

    M62-M65 - switch digital output


    Sx - spindle speed in RPMs

    Fx - feedrate (default: mm/min)

    Tx - set active tool mode, schedule actual switch with M6


    HOWTO
    -----
    One pass for every tool. UI to run one pass after the other.

    - tool
      - path
        - params: feedrate, spindel, coolant
        - segment
          - move
          - move
          - ...
        - params
        - segment
          - move
          - ...
        - ...
      - retract
    - tool
      - ...

    One path/tool. Within path, one segment for every param change.
    Treat rapid moves like feeds with different rate.

    """

    def __init__(self, tolerance):
        # tolerance settings, used in tessalation, path simplification, etc
        self.tolerance = tolerance
        self.tolerance2 = tolerance**2

        # parsed path data, paths by color
        # {'#ff0000': [[path0, path1, ..], [path0, ..], ..]}
        # Each path is a list of vertices which is a list of two floats.
        self.boundarys = {'#000000':[]}
        self.black_boundarys = self.boundarys['#000000']


    def parse(self, gcodestring):
        """Convert gcode to a job file."""

        paths = []
        current_path = []
        re_findall_attribs = re.compile('(S|F|X|Y|Z)(-?[0-9]+\.?[0-9]*(?:e-?[0-9]*)?)').findall

        intensity = 0.0
        feedrate = 1000.0
        target = [0.0, 0.0, 0.0]
        prev_motion_was_seek = True


        lines = ngcstring.split('\n')
        for line in lines:
            line = line.replace(' ', '')
            if line.startswith('G0'):
                attribs = re_findall_attribs(line[2:])
                for attr in attribs:
                    if attr[0] == 'X':
                        target[0] = float(attr[1])
                        prev_motion_was_seek = True
                    elif attr[0] == 'Y':
                        target[1] = float(attr[1])
                        prev_motion_was_seek = True
                    elif attr[0] == 'Z':
                        target[2] = float(attr[1])
                        prev_motion_was_seek = True
            elif line.startswith('G1'):
                if prev_motion_was_seek:
                    # new path
                    paths.append([[target[0], target[1], target[2]]])
                    current_path = paths[-1]
                    prev_motion_was_seek = False
                # new target
                attribs = re_findall_attribs(line[2:])
                for attr in attribs:
                    if attr[0] == 'X':
                        target[0] = float(attr[1])
                    elif attr[0] == 'Y':
                        target[1] = float(attr[1])
                    elif attr[0] == 'Z':
                        target[2] = float(attr[1])
                    elif attr[0] == 'S':
                        intensity = float(attr[1])
                    elif attr[0] == 'F':
                        feedrate = float(attr[1])
                current_path.append([target[0], target[1], target[2]])
            elif line.startswith('S'):
                attribs = re_findall_attribs(line)
                for attr in attribs:
                    if attr[0] == 'S':
                        intensity = float(attr[1])
            else:
                print "Warning: Unsupported Gcode"

        print "Done!"
        self.boundarys = {'#000000':paths}
        pass_ = ['1', feedrate, '', intensity, '', '#000000']
        return {'boundarys':self.boundarys}
