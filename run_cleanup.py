#Clean up date on happili

from __future__ import print_function

__author__ = "E.A.K. Adams"

"""
Command line script to execute happili cleanup

Currently, it focuses on intermediate selfcal directories
But would have the potential to be expanded for other cleanup,
e.g., raw calibrator files
"""

import argparse
from modules.functions import delete_intermediate_scal_dirs
from modules.functions import cleanup_continuum_intermediates
from modules.functions import delete_cal_vis
from modules.functions import final_scal_cleanup

parser = argparse.ArgumentParser(
    description='Clean up Apercal data products on happili')
parser.add_argument("--startdate", help='Start date, YYMMDD',
                    type=str, default=None)
parser.add_argument("--enddate", help='End date, YYMMDD',
                    type=str, default=None)
parser.add_argument("--scal_inter", default=True, type=bool,
                    help='Clean up intermediate selfcal files')
parser.add_argument("--cont_inter", default=True, type=bool,
                    help='Clean up intermediate continuum files')
parser.add_argument("--cal_vis", default=True, type=bool,
                    help='Clean up calibrator visibilities')
parser.add_argument("--mode", default='happili-01', type=str,
                    help='Running on happili-01 or happili-05')
parser.add_argument("--verbose", default=True, type=bool,
                    help='Verbose printing of file deletion')
parser.add_argument("--run", default=False, type=bool,
                    help='Whether to actually run deletion')
args = parser.parse_args()

print(args)

if args.scal_inter is True:
    delete_intermediate_scal_dirs(startdate=args.startdate,
                                  enddate=args.enddate,
                                  mode=args.mode,
                                  run=args.run,
                                  verbose=args.verbose)
    final_scal_cleanup(startdate=args.startdate, enddate=args.enddate, mode=args.mode,
                       run=args.run, verbose=args.verbose)
if args.cont_inter is True:
    cleanup_continuum_intermediates(startdate=args.startdate,
                                    enddate=args.enddate,
                                    mode=args.mode,
                                    run=args.run,
                                    verbose=args.verbose)
if args.cal_vis is True:
    delete_cal_vis(startdate=args.startdate, enddate=args.enddate, mode=args.mode,
                   run=args.run, verbose=args.verbose)



