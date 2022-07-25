#Functions for cleaning up happili

from __future__ import print_function

__author__ = "E.A.K. Adams"

"""
Functions for cleaning up happili

Main things to address / think about:
- Functionality for finding all processed data (use a lot)
- Identifying intermediate scal steps
- Listing user usage, to more easily contact people
"""

import numpy as np
import os
import glob
import shutil
import tarfile


def get_obsid_array(startdate=None, enddate=None):
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
    # do as full ObsID directory to start
    taskdirlist = glob.glob(
        "/data/apertif/[1-2][0-9][0-1][0-9][0-3][0-9][0-9][0-9][0-9]")
    # and return it in sorted order
    taskdirlist.sort()
    # take only the ObsID part
    obsid_list = [x[-9:] for x in taskdirlist]
    # create arrays, more useful later
    obsid_array = np.array(obsid_list)
    obsid_int_array = np.array(obsid_list,dtype=int)

    # now check for date range
    if startdate is not None:
        # put startdate into taskid format
        # so can do numerical comparison
        startid_str = startdate + '000'
        startid = np.int(startid_str)
        # find indices of sources that comes after startid
        ind_start = np.where(obsid_int_array > startid)[0]
        if len(ind_start) == 0:
            print('Start date comes after last obs. Starting from first obs')
        else:
            # keep obs that comes after start
            # do for both arrays, since one is returned
            # and the other is used in next call
            obsid_array = obsid_array[ind_start]
            obsid_int_array = obsid_int_array[ind_start]
    # and repeat for enddate
    if enddate is not None:
        endid_str = enddate + '999'
        endid = np.int(endid_str)
        ind_end = np.where(obsid_int_array < endid)[0]
        if len(ind_end) == 0:
            print('End date comes before first obs. Going to last obs')
        else:
            # keep obs only before end
            obsid_array = obsid_array[ind_end]
            # for completeness, int array also
            obsid_int_array = obsid_int_array[ind_end]
    
    return obsid_array


def get_obsid_beam_dir(obsid, beam, mode='happili-01'):
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
        obsid_beam_dir = '/data/apertif/{0}/{1:02d}'.format(obsid, beam)
    else:
        # if not happili-05 mode, default to happili-01 mode
        if beam < 10:
            obsid_beam_dir = '/data/apertif/{0}/{1:02d}'.format(obsid, beam)
        elif beam < 20:
            obsid_beam_dir = '/data2/apertif/{0}/{1:02d}'.format(obsid, beam)
        elif beam < 30:
            obsid_beam_dir = '/data3/apertif/{0}/{1:02d}'.format(obsid, beam)
        else:
            obsid_beam_dir = '/data4/apertif/{0}/{1:02d}'.format(obsid, beam)

    return obsid_beam_dir


def get_scal_intermediate_dirs(startdate=None, enddate=None,
                               mode='happili-01'):
    """
    Get the intermediate selfcal directories

    Optionally do this for a range of dates
    Intermediate selfcal directories are everything in
    /data/apertif/ObsID/BB/selfcal/00-0N, where N
    is the second to last major cycle of selfcal.
    Thus, this keeps the final major cycle of self-calibration

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

    # first get obsid array
    obsid_array = get_obsid_array(startdate=startdate, enddate=enddate)

    # then get initial path for each beam / obsid combination
    obs_beam_dir_list = []
    for obsid in obsid_array:
        for b in range(40):
            obdir = get_obsid_beam_dir(obsid,b,mode=mode)
            obs_beam_dir_list.append(obdir)

    # then need to find selfcal directories
    selfcal_dir_list = []
    for beamdir in obs_beam_dir_list:
        major_selfcal_list = glob.glob(
            os.path.join(beamdir,"selfcal/0[0-9]"))
        # need to sort into order
        major_selfcal_list.sort()
        # check length of list
        # updating to only keep last directory,
        # so list needs to be at least two elements long
        if len(major_selfcal_list) > 1:
            # slice out everything except last element
            intermediate_selfcal_list = major_selfcal_list[0:-1]
            # append to list, but avoid nesting
            for scdir in intermediate_selfcal_list:
                selfcal_dir_list.append(scdir)

    return selfcal_dir_list


def delete_intermediate_scal_dirs(startdate=None, enddate=None,
                                  mode='happili-01',
                                  run=False,
                                  verbose=True):
    """
    Delete the intermediate selfcal directories

    Optionally do this for a range of dates
    Intermediate selfcal directories are everything in
    /data/apertif/ObsID/BB/selfcal/00-0N, where N 
    is the second to last major cycle of selfcal.
    Thus, this keeps the
    final major cycle of self-calibration
    That will be cleaned up separately as the model should be saved

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
    # first get directories for deletion
    
    scal_dir_list = get_scal_intermediate_dirs(startdate=startdate,
                                               enddate=enddate,
                                               mode=mode)

    # then iterate through each directory
    # print statement and delete, as set by flags
    for scdir in scal_dir_list:
        if run is True:
            # do a try/except
            # because may not have permission to delete data
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
                

def get_continuum_intermediates(startdate=None,enddate=None,
                               mode='happili-01'):
    """
    Get the intermediate continuum files ::: Bones copied from get_scal_intermediate_dirs

    This will select all files of the form image_mf_NN.fits residual_mf_NN with the highest NN for keeping and put up the rest for deletion. It will also select files of the form masks_* and models_* to be tarred and then deleted.

    TODO: Change text below
    Optionally do this for a range of dates
    Intermediate selfcal directories are everything in
    /data/apertif/ObsID/BB/selfcal/01-0N, where N 
    is the second to last major cycle of selfcal.
    Thus, this keeps the initial starting point
    and final major cycle of self-calibration

    Different mode for happili-01 vs happili-05

    This will return two lists one for compression masks_* and models_*, and one for files to be deleted which is all but the final output

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
    tar_list : list (str)
        List of files to be tarred
    del_list : list (str)
        List of files to be deleted
    """

    #first get obsid array
    obsid_array = get_obsid_array(startdate=startdate,enddate=enddate)

    #then get initial path for each beam / obsid combination
    obs_beam_dir_list = []
    for obsid in obsid_array:
        for b in range(40):
            obdir = get_obsid_beam_dir(obsid,b,mode=mode)
            obs_beam_dir_list.append(obdir)

    tar_list = []
    delete_list = []

    for beamdir in obs_beam_dir_list: 
        # TODO: Check that the below patterns are correct
        # Get all beam_ files excluding _mf_
        beam_file_list = find_patter_remove_mf(beamdir,"continuum/beam_*", 'beam_mf_')
        # Get all image_ files excluding _mf_
        image_file_list = find_patter_remove_mf(beamdir,"continuum/image_*", 'image_mf_')
        # Get all residual_ files excluding _mf_
        residual_file_list = find_patter_remove_mf(beamdir,"continuum/residual_*", 'residual_mf_')
        # Get Raw 3C**.MS files
        cms_file_list = find_patter_remove_mf(beamdir,"raw/3C**.MS", None)

        # Assuming we want to tar all TODO: Check
        # Get all mask_ files
        mask_file_list = find_patter_remove_mf(beamdir,"continuum/mask_*", None)
        # Get all model_ files
        model_file_list = find_patter_remove_mf(beamdir,"continuum/model_*", None)


        # Grab non final mf files
        residual_mf_files = grab_mf_keep_largest(beamdir, "continuum/residual_mf_*")

        image_mf_files = grab_mf_keep_largest(beamdir, "continuum/image_mf_*")

        
        # Concatenate to relevant lists
        tar_list += mask_file_list + model_file_list

        delete_list += beam_file_list + image_file_list + residual_file_list + residual_mf_list + image_mf_files + residual_mf_files + cms_file_list


    # Make sure no tar files are part of any of these lists -> should be redundant but just in case
    tar_list = pop_tar(tar_list)

    delete_list = pop_tar(delete_list)

    return tar_list, delete_list


def find_patter_remove_mf(directory, pattern_to_find,pattern_to_remove):
    """
    Helper function for get_continuum_intermediates
    Grabs all files of name pattern pattern in directory using glob
    and then removes all files with name pattern pattern_to_remove using list comp
    """
    #get list of files
    file_list = glob.glob(os.path.join(directory,pattern_to_find))
    #remove files with pattern_to_remove
    if pattern_to_remove is not None:
        file_list = [x for x in file_list if pattern_to_remove not in x]
    return file_list


def grab_mf_keep_largest(beamdir, pattern,filetype_to_keep='.fits'):
    """
    Helper function for get_continuum_intermediates
    Grabs all mf files but the one with the largest NN
    
    beamdir : str
        ---> Path to beam directory
    pattern: str
        ---> Pattern from beam directory i.e. continuum/residual_mf_*
    filetype_to_keep : str
        ---> If we only want to keep .fits files we use the default value if we want to keep miriad files this function needs to be expanded
    """
    # All above are without _mf_ files, to only keep the largest of the _mf_ files we filter all mf files with the same method as above and append all but the largest

    mf_list = find_patter_remove_mf(beamdir,pattern, None)
    # Sorts according to number in the file name
    sorted_mf_list = sorted(mf_list, key=lambda x: int(x.split('_')[-1].split('.')[0]))
    # TODO: Check if we want to keep the miriad files or not
    # to keep the fits file and not the miriad file, we iterate over the array in reverse as the largest number should be last, we check that it is indeed a fits file and then break, if it not but is say a .fits.pybdsf... or miriad file we skip over it and check the next one
    for i in range(len(sorted_mf_list)): #TODO: Also do we want to keep log files?
        if sorted_mf_list[-i].endswith(filetype_to_keep):
            sorted_mf_list.pop(-i) # This is an inplace operation
            break
    # After this loop finishes the only files present in the list will be the _mf_ files with lower NNs than the largest, note that this will delete all files if there is no fits file TODO: Check that this is acceptable behavior
    return sorted_mf_list

def pop_tar(file_list):
    """Safety function to make sure no tar files get deleted"""

    for file in file_list:
        if file.endswith('.tar') or file.endswith('.gz'):
            file_list.remove(file)
    return file_list


def delete_continuum_intermediates(startdate=None,enddate=None,
                                  mode='happili-01',
                                  run=False,
                                  verbose=True):
    """
    Delete the intermediate continuum files :: Copied from delete_intermediate_scal_dirs

    Optionally do this for a range of dates
    Intermediate selfcal directories are everything in
    /data/apertif/ObsID/BB/selfcal/00-0N, where N 
    is the second to last major cycle of selfcal.
    Thus, this keeps the
    final major cycle of self-calibration
    That will be cleaned up separately as the model should be saved

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
    #first get files for deletion
    
    tar_list, delete_list = get_continuum_intermediates(startdate=startdate,
                                               enddate=enddate,
                                               mode=mode)

    #then iterate through each file
    #print statement and delete, as set by flags
    for scdir in delete_list:
        if run is True:
            #do a try/except
            #because may not have permisison to delete data
            try:
                os.rm(scdir)
                if verbose is True:
                    print('Deleting {}'.format(scdir))
            except:
                if verbose is True:
                    print('Unable to delete {}'.format(scdir))
        else:
            if verbose is True:
                print('Practice run only; deleting {}'.format(scdir))

    #tar the files
    # Below to keep track of tar file directories
    tar_dir = None

    #print statement and delete, as set by flags
    for scdir in tar_list:
        if run is True:
            # As we need to write the correct files to the correct directories we will use the parent directory name to open the tar files
            parent_dir = os.path.abspath(os.path.join(scdir, '..'))
            if parent_dir != tar_dir:
                # The intent of this if statement is to assure we are operating in the correct file path
                tar_dir = parent_dir
                if 'tar_handle' in locals():
                    tar_handle.close()
                # Check that the tar file does not exists
                if not os.path.isfile(os.path.join(tar_dir, 'mask_models.tar')):
                    tar_handle = tarfile.open(os.path.join(tar_dir, 'mask_models.tar'), "w:gz") # TODO: Check if we want to use gz or not
                else:
                    print("Tar file exists behavior here is not specified yet")
                    print("Ideally untar file add all new files and then retar")
                    print("This was not implemented as this usage should not be required and it should be double checked wheter the files are already tared")
                    print("The content of tar list is:")
                    print(tar_list)
                    print("tar_list will be emptied to avoid deleting data")
                    tar_list = []
                    print("The content of tar list is now:")
                    print(tar_list)
                    break
                    

            # Now we try to add the file to the tar file in a try except clause, so that files can be poped from the lsit in case they cant be addded
            try:
                tar_handle.add(scdir)
                if verbose is True:
                    print('Tarring {}'.format(scdir))
            except:
                if verbose is True:
                    print('Unable to delete {}'.format(scdir))
                # Remove file from list to make sure it doesnt get deleted
                tar_list.remove(scdir)
        else:
            if verbose is True:
                parent_dir = os.path.abspath(os.path.join(scdir, '..'))
                if parent_dir != tar_dir:
                    # The intent of this if statement is to assure we are operating in the correct file path
                    tar_dir = parent_dir
                print('Practice run only; tarring {} into {}'.format(scdir, tar_dir))


    #delete files successfully added to their respective tar files
    #print statement and delete, as set by flags
    for scdir in tar_list:
        if run is True:
            #do a try/except
            #because may not have permisison to delete data
            try:
                os.rm(scdir)
                if verbose is True:
                    print('Deleting {}'.format(scdir))
            except:
                if verbose is True:
                    print('Unable to delete {}'.format(scdir))
        else:
            if verbose is True:
                print('Practice run only; deleting {}'.format(scdir))

