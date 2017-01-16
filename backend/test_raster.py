# -*- coding: UTF-8 -*-
import os
import time
import random
import unittest
import json
import threading
import pprint

import web
import lasersaur
from config import conf


# assertEqual(a, b)
# assertNotEqual(a, b)
# assertTrue(x)
# assertFalse(x)
# assertIsNone(x)

# assertIsInstance(a, b)
# assertNotIsInstance(a, b)

# assertAlmostEqual(a, b)
# assertNotAlmostEqual(a, b)
# assertGreater(a, b)
# assertGreaterEqual(a, b)
# assertLess(a, b)
# assertLessEqual(a, b)


# assertListEqual(a, b)
# assertIn(a, b)
# assertDictEqual(a, b)
# assertDictContainsSubset(a, b)


thislocation = os.path.dirname(os.path.realpath(__file__))


def setUpModule():
    web.start(threaded=True, debug=False)
    time.sleep(0.5)
    lasersaur.local()

def tearDownModule():
    web.stop()



class TestOpenRaster(unittest.TestCase):
    def test_config(self):
        img = Image.open(os.path.join(thislocation, 'testjobs', 'bat.png'))
        # img_g = img.convert('LA')  # to grayscale
        img_g = img.convert('L')  # to grayscale
        w = 80
        h = int(img_g.size[1]*(float(w)/img_g.size[0]))
        img_s = img_g.resize((w,h), resample=Image.BICUBIC)
        # img_s.show()
        data = img_s.getdata()
        for lx in xrange(h):
            for rx in xrange(w):
                x = data[w*lx+rx]
                if x < 100:
                    sys.stdout.write('.')
                elif x < 150:
                    sys.stdout.write('o')
                elif x < 200:
                    sys.stdout.write('0')
                else:
                    sys.stdout.write('X')
            sys.stdout.write('\n')



class TestRaster(unittest.TestCase):

    def testLoad(self):
        jobfile = os.path.join(thislocation,'testjobs','raster_bat.svg')
        job = lasersaur.open_file(jobfile)
        # if 'vector' in job:
        #     job['vector']['passes'] = [{
        #             "paths":[0],
        #             "feedrate":4000,
        #             "intensity":53
        #         }]
        if 'raster' in job:
            job['raster']['passes'] = [{
                    "images":[0],
                    "feedrate":4000,
                    "intensity":53
                }]
        print job.keys()
        pprint.pprint(job['raster']['passes'])
        jobname = lasersaur.load(job)
        self.assertIn(jobname, lasersaur.listing())
        lasersaur.run(jobname, progress=True)
        print "done!"


if __name__ == '__main__':
    unittest.main()

    # for partial test run like this:
    # python test.py Class
    # E.g:
    # python test.py TestQueue
