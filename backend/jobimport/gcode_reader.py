
__author__ = 'Stefan Hechenberger <stefan@nortd.com>'


import math
import sys
import re
import os.path
import StringIO

debug = True


class GcodeReader:
    """Parse subset of G-Code.

    GCODE OVERVIEW
    --------------
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

    M3 - start spindle CW at whatever S has been set to
    M4 - start spindle CCW at whatever S has been set to
    M5 - stop spindle

    M6 - stop, prompt for tool change, non-modal
       - to whatever the most recent Tx was

    M7 - mist coolant on
    M8 - flood coolant on
    M9 - all coolant off

    M62-M65 - switch digital output


    Sx - spindle speed in RPMs

    Fx - feedrate (default: mm/min)

    Tx - set active tool mode, schedule actual switch with M6


    STRATEGY
    --------
    One pass for every tool. UI to run one pass after the other.

    - tool
      - path
        - params: feedrate, spindle, coolant
        - move
        - move
        - params: feedrate, spindle, coolant
        - move
        - move
        - ...
      - retract
    - tool
      - ...

    One path/tool. Within path, a series of moves and param changes.
    Treat rapid moves like feeds with different rate.


    OUTPUT
    ------
    Output is a job where every "pass" has one "item" that has one "def".
    This def is of kind "mill". A mill def has a data item which is a path.
    A mill path is a series of moves and param changes.

    A def looks like this:
    {'kind':'mill', 'data':[], 'tool':'', 'toolinfo':''}

    The format of a path is a series of possible ath items:
    - ('G0',(x,y,z))      (mapped to move with seekrate)
    - ('G1',(x,y,z))      (mapped to move with feedrate)
    - ('F',rate)          (mapped to feedrate)
    - ('S',freq)          (mapped to intensity)
    - ('MIST', onoff)     (mapped to air_on/off)
    - ('FLOOD', onoff)    (mapped to aux_on/off)

    Path example (job['defs'][0]['data']):
    [('G0',(x,y,z)), ('F', 1000), ('S', 18000), ('FLOOD', True), ('G1', (x,y,z))]


    """

    def __init__(self):
        # flags
        self.bTool = False

        # modal state
        self.G_motion = 'G0'
        self.X_pos = None
        self.Y_pos = None
        self.Z_pos = None
        self.F_rate = 0
        self.S_freq = 0
        self.S_on = False
        self.T_num = 0
        self.M_mist = False
        self.M_flood = False

        # tools table
        self.toolinfo = {}

        # regexes
        self.re_parts = re.compile('(X|Y|Z|G|M|T|S|F)(-?[0-9]+\.?[0-9]*(?:e-?[0-9]*)?)').findall
        self.re_toolchange = re.compile('(M6)').findall
        self.re_T = re.compile('(T)([0-9]+)').findall
        self.re_toolinfo = re.compile('\((T[0-9]+) *(.+) *\)').findall

        # output job
        self.job = {'passes':[], 'items':[], 'defs':[]}


    def next_pass(self):
        # print("INFO: Setting up pass for tool: T%s" % (self.T_num))
        self.job['defs'].append({'kind':'mill', 'data':[], 'tool':'', 'toolinfo':''})
        self.job['items'].append({'def':len(self.job['defs'])-1})
        self.job['passes'].append({'items':[len(self.job['items'])-1]})
        self.def_ = self.job['defs'][-1]
        self.path = self.def_['data']


    def on_toolchange(self, line):
        """Handle a tool change action (M6).
           Account for T action on same line (nothing more).
        """
        T_code = self.re_T(line)
        if len(T_code) == 1:
            self.T_num = T_code[0][1]
            nParts = 2
        else:
            nParts = 1
        # commit tool change
        if len(self.re_parts(line)) != nParts:
            print("ERROR: cannot handle anything but T on M6 toolchange line")
        else:
            self.next_pass()
            self.bTool = True
            # add tool, toolinfo to def
            tool = 'T'+str(self.T_num)
            self.def_['tool'] = tool
            if tool in self.toolinfo:
                self.def_['toolinfo'] = self.toolinfo[tool]


    def on_action(self, action):
        if not self.bTool:
            print("ERROR: no tool defined at: %s:%s" % action)
            return
        self.path.append(action)


    def parse(self, gcodestring):
        """Convert gcode to a job file."""
        for line in gcodestring.splitlines():
            # reject line condition
            if len(line) == 0 or line[0] not in ('X', 'Y', 'Z', 'G', 'M', 'T', 'S', 'F'):
                # parse tool table
                if line.startswith('(T'):
                    toolinfo = self.re_toolinfo(line)
                    if toolinfo:
                        self.toolinfo[toolinfo[0][0]] = (toolinfo[0][1])
                # reject
                else:
                    continue

            # on tool change action (M6)
            if self.re_toolchange(line):
                self.on_toolchange(line)
                continue

            bMotion = False
            bFeed = False
            bSpindle = False
            bMist = False
            bFlood = False

            # lines with valid start char
            for code_ in self.re_parts(line):
                # convert numeral
                code = [code_[0], float(code_[1])]
                if code[1].is_integer(): code[1] = int(code[1])
                # target coordinates
                if code[0] == 'X':
                    self.X_pos = code[1]
                    bMotion = True
                elif code[0] == 'Y':
                    self.Y_pos = code[1]
                    bMotion = True
                elif code[0] == 'Z':
                    self.Z_pos = code[1]
                    bMotion = True
                # params: feedrate, freq, tool
                elif code[0] == 'F':
                    self.F_rate = code[1]
                    bFeed = True
                elif code[0] == 'S':
                    self.S_freq = code[1]
                elif code[0] == 'T':
                    self.T_num = code[1]
                # spindle frequency change
                elif code[0] == 'M' and code[1] in (3,5):
                    if code[1] == 3:
                        self.S_on = True
                        bSpindle = True
                    elif code[1] == 5:
                        self.S_on = False
                        bSpindle = True
                # coolant valve change
                elif code[0] == 'M' and code[1] in (7,8,9):
                    if code[1] == 7:
                        if not self.M_mist:
                            self.M_mist = True
                            bMist = True
                    elif code[1] == 8:
                        if not self.M_flood:
                            self.M_flood = True
                            bFlood = True
                    elif code[1] == 9:
                        if self.M_mist:
                            self.M_mist = False
                            bMist = True
                        if self.M_flood:
                            self.M_flood = False
                            bFlood = True
                # motion style change
                elif code[0] == 'G' and code[1] in (0,1):
                    self.G_motion = 'G'+str(code[1])
                # handle reporting of unsupported gcode
                elif code[0] == 'G' and code[1] in (2,3):
                    print("ERROR: G2,G3 arc motions not supported")
                elif code[0] == 'G' and code[1] in (4,):
                    print("ERROR: G4 dwell motions not supported")
                elif code[0] == 'G' and code[1] in (53,):
                    print("ERROR: G53 machine CS motion not supported")
                elif code[0] == 'G' and code[1] in (55,56,57,58,59):
                    print("ERROR: G55-G59 CS not supported")
                elif code[0] == 'G' and code[1] in (91,):
                    print("ERROR: G91 relative motion not supported")
                elif code[0] == 'G' and code[1] in (92,):
                    print("ERROR: G92 shift CS not supported")
                elif code[0] == 'G' and code[1] in (93,95):
                    print("ERROR: G93,G95 alternative distance modes not supported")
                elif code[0] == 'M' and code[1] in (0,1):
                    print("ERROR: M0,M1 pause not supported")
                elif code[0] == 'M' and code[1] in (4,):
                    print("ERROR: M4 reverse spindle not supported")
                elif code[0] == 'M' and code[1] == (20,):
                    print("ERROR: inch units not supported")

            ### commit actions in right order
            # commit coolant
            if bMist:
                self.on_action(('MIST',self.M_mist))
            if bFlood:
                self.on_action(('FLOOD',self.M_flood))
            # commit spindle
            if bSpindle:
                if self.S_on:
                    self.on_action(('S',self.S_freq))
                else:
                    self.on_action(('S',0))
            # commit feedrate
            if bFeed:
                self.on_action(('F',self.F_rate))
            # commit motion
            if bMotion:
                self.on_action((self.G_motion,(self.X_pos, self.Y_pos, self.Z_pos)))

        return self.job


if __name__ == '__main__':
    path = sys.argv[1]
    with open(path, 'r') as content_file:
        content = content_file.read()
        reader = GcodeReader()
        job = reader.parse(content)
        print(job)
