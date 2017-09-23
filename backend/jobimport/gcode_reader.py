
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

        self.job = {'passes':[], 'items':[], 'defs':[]}
        self.next_pass()
        self.next_segment()


    def next_pass(self):
        self.job['defs'].append({'kind':'mill', 'data':[], 'params':[]})
        self.job['items'].append({'def':len(self.job['defs'])-1})
        self.job['passes'].append({'items':len(self.job['items'])-1})

        self.def_ = self.job['defs'][-1]
        self.path = self.def_['data']
        self.params = self.def_['params']


    def next_segment(self):
        self.path.append([])
        self.segment = self.path[-1]
        self.params.append([])
        self.segparam = self.params[-1]



    def parse(self, gcodestring):
        """Convert gcode to a job file."""

        # paths = []
        # current_path = []
        #
        # intensity = 0.0
        # feedrate = 1000.0
        # target = [0.0, 0.0, 0.0]
        # prev_motion_was_seek = True
        #
        # re_feed = re.compile('(G93|G94)').findall
        # re_F = re.compile('(F)([0-9]+\.?[0-9]*(?:e-?[0-9]*)?)').findall
        # re_S = re.compile('(S)([0-9]+\.?[0-9]*(?:e-?[0-9]*)?)').findall
        # re_T = re.compile('(T)([0-9]+)').findall
        # re_io = re.compile('(M62|M63|M64|M65|M66|M68)').findall
        # re_toolchange = re.compile('(M6|M61)').findall
        # re_spindle = re.compile('(M3|M4|M5)').findall
        # re_save = re.compile('(M70|M71|M72|M73)').findall
        # re_coolant = re.compile('(M7|M8|M9)').findall
        # re_overrides = re.compile('(M48|M49|M50|M51|M52|M53)').findall
        # re_custom = re.compile('(M1[0-9][0-9])').findall
        # re_dwell = re.compile('(G4)').findall
        # re_plane = re.compile('(G17|G18|G9)').findall
        # re_units = re.compile('(G20|G21)').findall
        # re_rcomp = re.compile('(G40|G41|G42)').findall
        # re_lcomp = re.compile('(G43|G49)').findall
        # re_cs = re.compile('(G5[4-9]|G59\.[1-3])').findall
        # re_path = re.compile('(G61|G61\.1|G64)').findall
        # re_dist = re.compile('(G90|G91)').findall
        # re_retract = re.compile('(G98|G99)').findall
        # re_goref = re.compile('(G28|G30|G10|G92|G92\.1|G92\.2)').findall
        # re_motion = re.compile('(G[0-3]|G33|G38\.[2-5]|G73|G76|G8[0-9]|G53)').findall
        # re_stop = re.compile('(M0|M1|M2|M30|M60)').findall
        # re_X = re.compile('(X)(-?[0-9]+\.?[0-9]*(?:e-?[0-9]*)?)').findall
        # re_Y = re.compile('(Y)(-?[0-9]+\.?[0-9]*(?:e-?[0-9]*)?)').findall
        # re_Z = re.compile('(Z)(-?[0-9]+\.?[0-9]*(?:e-?[0-9]*)?)').findall
        #
        #
        # # order of execution within every block (not sequential)
        # # see (22.): http://linuxcnc.org/docs/html/gcode/overview.html
        # block = collections.OrderedDict()
        # block["feed"] = []
        # block["F"] = []
        # block["S"] = []
        # block["T"] = []
        # block["io"] = []
        # block["toolchange"] = []
        # block["spindle"] = []
        # block["save"] = []
        # block["coolant"] = []
        # block["overrides"] = []
        # block["custom"] = []
        # block["dwell"] = []
        # block["plane"] = []
        # block["units"] = []
        # block["rcomp"] = []
        # block["lcomp"] = []
        # block["cs"] = []
        # block["path"] = []
        # block["dist"] = []
        # block["retract"] = []
        # block["goref"] = []
        # block["motion"] = []
        # block["stop"] = []
        # block["XYZ"] = []


        re_parts = re.compile('([X,Y,Z,G,M,T,S,F])(-?[0-9]+\.?[0-9]*(?:e-?[0-9]*)?)').findall

        # modal state
        G_motion = 0
        X_pos = 0.0
        Y_pos = 0.0
        Z_pos = 0.0
        F_rate = 0
        S_freq = 0
        T_num = 0

        F_rapidrate =


        for line in gcodestring.splitlines():
            # reject lines condition
            if len(line) == 0 or line[0] not in ('X', 'Y', 'Z', 'G', 'M', 'T', 'S', 'F'):
                if debug:
                    print("line rejected: %s" % (line))
                continue


            # lines with valid start char
            for code in re_parts(line):
                convert numeral
                code[1] = float(code[1])
                if code[1].is_integer(): code[1] = int(code[1])

                # collect state
                if code[0] == 'X':
                    X_pos = code[1]
                    bMotion = True
                elif code[0] == 'Y':
                    Y_pos = code[1]
                    bMotion = True
                elif code[0] == 'Z':
                    Z_pos = code[1]
                    bMotion = True

                elif code[0] == 'F':
                    F_rate = code[1]
                elif code[0] == 'S':
                    S_freq = code[1]
                elif code[0] == 'T':
                    T_num = code[1]

                # handle actions
                elif code[0] == 'M' and code[1] == 6:
                    #handle tool change
                    self.next_pass()
                elif code[0] == 'M' and code[1] in (3,4,5):
                    #handle spindel freq change
                    self.next_segment()
                    segparam.append({'S_freq': S_freq})
                elif code[0] == 'M' and code[1] in (7,8,9):
                    #handle coolant change
                    self.next_segment()
                    segparam.append({'M_cool':M_cool})
                elif code[0] == 'F':
                    #handle feedrate change
                    self.next_segment()
                    segparam.append({'F_rate':F_rate})
                elif code[0] == 'G' and (code[1] == 0 or code[1] == 1):
                    if code[1] != G_motion:
                        # handle implicit feedrate change
                        self.next_segment()
                        segparam.append({'F_rate':F_rapidrate})
                        G_motion = code[1]

                # handle reporting of unsupported gcode
                elif code[0] == 'G' and code[1] in (2,3):
                    print("ERROR: G2,G3 arc motions not supported")
                elif code[0] == 'G' and code[1] in (4):
                    print("ERROR: G4 dwell motions not supported")
                elif code[0] == 'G' and code[1] in (53):
                    print("ERROR: G53 machine CS motion not supported")
                elif code[0] == 'G' and code[1] in (55,56,57,58,59):
                    print("ERROR: G55-G59 CS not supported")
                elif code[0] == 'G' and code[1] in (91):
                    print("ERROR: G91 relative motion not supported")
                elif code[0] == 'G' and code[1] in (92):
                    print("ERROR: G92 shift CS not supported")
                elif code[0] == 'G' and code[1] in (93,95):
                    print("ERROR: G93,G95 alternative distance modes not supported")
                elif code[0] == 'M' and code[1] in (0,1):
                    print("ERROR: M0,M1 pause not supported")
                elif code[0] == 'M' and code[1] == 20:
                    print("ERROR: inch units not supported")

                # commit motion
                if bMotion:
                    segment.append((X_pos, Y_pos, Z_pos))
                    bMotion = False
