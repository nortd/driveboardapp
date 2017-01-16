# -*- coding: UTF-8 -*-
import os
import cProfile as profile
import timeit
import pstats
import argparse
import glob

import lasersaur
import jobimport



### Setup Argument Parser
argparser = argparse.ArgumentParser(description='time/profile job import.', prog='profile_import.py')
argparser.add_argument('jobfile', metavar='jobfile', nargs='?', default=None,
                       help='Lasersaur job file to show.')
argparser.add_argument('-a', '--animate', dest='animate', action='store_true',
                       default=False, help='animate job')
argparser.add_argument('-f', '--fast', dest='fast', action='store_true',
                       default=False, help='animate fast')
argparser.add_argument('-n', '--nooptimize', dest='nooptimize', action='store_true',
                       default=False, help='do not optimize geometry')
argparser.add_argument('--tolerance', dest='tolerance',
                       default=0.08, help='tolerance in mm')
argparser.add_argument('-p', '--profile', dest='profile', action='store_true',
                    default=False, help='run with profiling')
argparser.add_argument('-t', '--timeit', dest='timeit', action='store_true',
                    default=False, help='run with timing')
args = argparser.parse_args()



def main():
    thislocation = os.path.dirname(os.path.realpath(__file__))
    if args.jobfile:
        jobfile = os.path.join(thislocation, "testjobs", args.jobfile)
        print jobfile
        with open(jobfile) as fp:
            job = fp.read()
        job = jobimport.convert(job, tolerance=float(args.tolerance),
                                     optimize=not(args.nooptimize))

        # stats
        total_points = 0
        for path in job['vector']['paths']:
            for polyline in path:
                for point in polyline:
                    total_points += 1
        print "STATS:"
        print "\ttotal points: %s" % total_points
        if 'vector' in job and 'optimized' in job['vector']:
            print "\ttolerance: %s" % job['vector']['optimized']
    else:
        jobpath = os.path.join(thislocation, "testjobs")
        cwd_temp = os.getcwd()
        os.chdir(jobpath)
        files = glob.glob("*.*")
        os.chdir(cwd_temp)
        print "Name one of the following files:"
        for file_ in files:
            print file_


if args.profile:
    profile.run("main()", 'profile.tmp')
    p = pstats.Stats('profile.tmp')
    p.sort_stats('cumulative').print_stats(30)
    os.remove('profile.tmp')
elif args.timeit:
    t = timeit.Timer("main()", "from __main__ import main")
    print t.timeit(1)
    # print t.timeit(3)
else:
    main()
