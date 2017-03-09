# -*- coding: UTF-8 -*-
import os
import time

import web
import lasersaur


thislocation = os.path.dirname(os.path.realpath(__file__))

# web.start()
lasersaur.local()


jobfile = os.path.join(thislocation,'testjobs','full-bed.svg')
# jobfile = os.path.join(thislocation,'testjobs','key.svg')
lasersaur.run_file(jobfile, feedrate=4000, intensity=53, progress=True, local=True)


# web.stop()
