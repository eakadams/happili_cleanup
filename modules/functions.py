#Functions for cleaning up happili

from __future__ import print_function

__author__ = "E.A.K. Adams"

"""
Functions for cleaning up happili

Main things to address / think about:
- Functionality for finding all processsed data (use a lot)
- Identifying intermediate scal steps
- Listing user usage, to more easily contact people
"""

from astropy.io import ascii
import numpy as np
import os
import glob

def get_obsid_list(startdate=None,enddate=None):
    """
    Get list of obsids on happili node
    Optionally between startdate and enddate

    Parameters
    ----------
    startdate : str (optional)
         Optional startdate in YYMMDD format
    enddate : str (optional)
         Optional enddate in YYMMDD format

    Returns
    -------
    obsid_list : list
         List of obsids
    """
    #do as full ObsID directory to start
    taskdirlist = glob.glob(
    "/data/apertif/[1-2][0-9][0-1][0-9][0-3][0-9][0-9][0-9][0-9]")
    #and return it in sorted order
    taskdirlist.sort()
    #take only the ObsID part
    obsid_list = [x[-9:] for x in taskdirlist]

    #now check for date range
    if startdate is not None:
        #get indices where startdate is in obsid
        ind_start = [i for i, s in enumerate(obsis_list) if startdate in s]
        #check that start date overlaps
        #if not, print a warning
        if len(ind_start) == 0:
            print('Start date not in ObsID list. Starting from first obs')
        else:
            #start from first index in ind_start.
            #sorted by obsid, so this works
            obsid_list = obsid_list[ind_start[0]:]
    #and repeat for enddate
    if enddate is not None:
        ind_end = [i for i, s in enumerate(obsis_list) if enddate in s]
        if len(ind_end) == 0:
            print('End date not in ObsID list. Going to last obs')
        else:
            #take last index in ind_end
            #remember exclusive
            last_ind = ind_end[-1]+1
            obsid_list = obsid_list[:last_ind]
    
    return obsid_list


def get_obsid_dirs(startdate=None,enddate=None):
    """
    Get a ??? of obsid directories.
    Optional start and end date

    Parameters
    ----------
    startdate : int (optional)
         Optional startdate in YYMMDD format
    enddate : int (optional)
         Optional enddate in YYMMDD format

    Returns
    -------
    obsid_dirs : ????
        ???? of obsid directories (/data?/apertif/ObsID)
    """

    pass


def get_scal_intermediate_dirs():
    pass
