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

import numpy as np
import os
import glob
import shutil


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
            #do for both arrays, since one is returned
            #and the other is used in next call
            obsid_array = obsid_array[ind_start]
            obsid_int_array = obsid_int_array[ind_start]
    #and repeat for enddate
    if enddate is not None:
        endid_str = enddate + '999'
        endid = np.int(endid_str)
        ind_end = np.where(obsid_int_array < endid)[0]
        if len(ind_end) == 0:
            print('End date comes before first obs. Going to last obs')
        else:
            #keep obs only before end
            obsid_array = obsid_array[ind_end]
            #for completeness, int array also
            obsid_int_array = obsid_int_array[ind_end]
    
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
    mode : string
        Running mode - happili-01 or happili-05
        Default is happili-01

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

    return obsid_beam_dir

def get_scal_intermediate_dirs(startdate=None,enddate=None,
                               mode='happili-01'):
    """
    Get the intermediate selfcal directories

    Optionally do this for a range of dates
    Intermediate selfcal directories are everything in
    /data/apertif/ObsID/BB/selfcal/01-0N, where N 
    is the second to last major cycle of selfcal.
    Thus, this keeps the initial starting point
    and final major cycle of self-calibration

    Different mode for happili-01 vs happili-05

    Parameters
    ----------
    startdate : str (optional)
         Optional startdate in YYMMDD format
    enddate : str (optional)
         Optional enddate in YYMMDD format
    mode : string
        Running mode - happili-01 or happili-05
        Default is happili-01

    Returns
    -------
    scal_dir_list : list
         List of all intermediate selfcal directories in date range
    """

    #first get obsid array
    obsid_array = get_obsid_array(startdate=startdate,enddate=enddate)

    #then get initial path for each beam / obsid combination
    obs_beam_dir_list = []
    for obsid in obsid_array:
        for b in range(40):
            obdir = get_obsid_beam_dir(obsid,b,mode=mode)
            obs_beam_dir_list.append(obdir)

    #then need to find selfcal directories
    selfcal_dir_list = []
    for beamdir in obs_beam_dir_list:
        major_selfcal_list = glob.glob(
            os.path.join(beamdir,"selfcal/0[0-9]"))
        #need to sort into order
        major_selfcal_list.sort()
        #check length of list
        #want to exclude first and last, so list needs
        #to be at least three elements long
        if len(major_selfcal_list) > 2:
            #slice out all the middle elements
            intermediate_selfcal_list = major_selfcal_list[1:-1]
            #append to list, but avoid nesting
            for scdir in intermediate_selfcal_list:
                selfcal_dir_list.append(scdir)


    return selfcal_dir_list


def delete_intermediate_scal_dirs(startdate=None,enddate=None,
                                  mode='happili-01',
                                  run=False,
                                  verbose=True):
    """
    Delete the intermediate selfcal directories

    Optionally do this for a range of dates
    Intermediate selfcal directories are everything in
    /data/apertif/ObsID/BB/selfcal/01-0N, where N 
    is the second to last major cycle of selfcal.
    Thus, this keeps the initial starting point
    and final major cycle of self-calibration

    Different mode for happili-01 vs happili-05

    Defaults to a verbose running, but not actually doing

    Parameters
    ----------
    startdate : str (optional)
         Optional startdate in YYMMDD format
    enddate : str (optional)
         Optional enddate in YYMMDD format
    mode : string
        Running mode - happili-01 or happili-05
        Default is happili-01
    run : Boolean
        Actually run and do deletion?
        Default is False
    verbose : Boolean
        Print a record of what is (to be) deleted?
        Default is True
    """
    #first get directories for deletion
    
    scal_dir_list = get_scal_intermediate_dirs(startdate=startdate,
                                               enddate=enddate,
                                               mode=mode)

    #then iterate through each directory
    #print statement and delete, as set by flags
    for scdir in scal_dir_list:
        if run is True:
            #do a try/except
            #because may not have permisison to delete data
            try:
                shutil.rmtree(scdir)
                if verbose is True:
                    print('Deleting {}'.format(scdir))
            except:
                if verbose is True:
                    print('Unable to delete {}'.format(scdir))
        else:
            if verbose is True:
                print('Practice run only; deleting {}'.format(scdir))
                
