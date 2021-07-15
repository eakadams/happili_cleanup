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
import datetime as dt

def get_obsid_array(startdate=None,enddate=None):
    """
    Get array of obsids on happili node
    Optionally between startdate and enddate

    Parameters
    ----------
    startdate : str (optional)
         Optional startdate in YYMMDD format
    enddate : str (optional)
         Optional enddate in YYMMDD format

    Returns
    -------
    obsid_array : array
         Array of obsids as strings
    """
    #do as full ObsID directory to start
    taskdirlist = glob.glob(
    "/data/apertif/[1-2][0-9][0-1][0-9][0-3][0-9][0-9][0-9][0-9]")
    #and return it in sorted order
    taskdirlist.sort()
    #take only the ObsID part
    obsid_list = [x[-9:] for x in taskdirlist]
    #create arrays, more useful later
    obsid_array = np.array(obsid_list)
    obsid_int_array = np.array(obsid_list,dtype=int)

    #now check for date range
    if startdate is not None:
        #put startdate into taskid format
        #so can do numerical comparison
        startid_str = startdate + '000'
        startid = np.int(startid_str)
        #find indices of sources that comes after startid
        ind_start = np.where(obsid_int_array > startid)[0]
        if len(ind_start) == 0:
            print('Start date comes after last obs. Starting from first obs')
        else:
            #keep obs that comes after start
            obsid_array = obsid_array[ind_start]
    #and repeat for enddate
    if enddate is not None:
        endid_str = enddate + '999'
        endid = np.int(endid_str)
        ind_end = np.where(obsid_int_array < endid)[0]
        if len(ind_end) == 0:
            print('End date comes before first obs. Going to last obs')
        else:
            #keep obs that comes after start
            obsid_array = obsid_array[ind_end]
    
    return obsid_array


def get_obsid_beam_dir(obsid,beam,mode='happili-01'):
    """
    Get directory path for obsid + beam
    Default assumes happili-01 setup / access to 02-04
    Can also run in happili-05 mode where everything is local

    Parameters
    ----------
    obsid : str
         Obsid provided as a string
    beam : int
         beam provided as an int

    Returns
    -------
    obsid_beam_dir : str
        path to obsid / beam
    """

    if mode == 'happili-05':
        obsid_beam_dir = '/data/apertif/{0}/{1:02d}'.format(obsid,beam)
    else:
        #if not happili-05 mode, default to happili-01 mode
        if beam < 10:
            obsid_beam_dir = '/data/apertif/{0}/{1:02d}'.format(obsid,beam)
        elif beam < 20:
            obsid_beam_dir = '/data2/apertif/{0}/{1:02d}'.format(obsid,beam)
        elif beam < 30:
            obsid_beam_dir = '/data3/apertif/{0}/{1:02d}'.format(obsid,beam)
        else:
            obsid_beam_dir = '/data4/apertif/{0}/{1:02d}'.format(obsid,beam)

def get_scal_intermediate_dirs():
    pass
