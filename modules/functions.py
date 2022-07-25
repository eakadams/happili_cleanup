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
import re


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


def get_cal_vis(startdate=None, enddate=None, mode='happili-01'):
    """
    Get calibrator visibilities

    Optionally do this for a range of dates

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
    cal_vis_list : list
         List of all calibrator visibilities in date range
    """

    # first get obsid array
    obsid_array = get_obsid_array(startdate=startdate, enddate=enddate)

    # then get initial path for each beam / obsid combination
    obs_beam_dir_list = []
    for obsid in obsid_array:
        for b in range(40):
            obdir = get_obsid_beam_dir(obsid, b, mode=mode)
            if os.path.isdir(obdir):
                obs_beam_dir_list.append(obdir)

    # then need to find selfcal directories
    cal_vis_list = []
    for beamdir in obs_beam_dir_list:
        beam_cal_list = glob.glob(
            os.path.join(beamdir, "raw/3C*MS"))
        # need to sort into order
        beam_cal_list.sort()
        # and add to list
        cal_vis_list = cal_vis_list + beam_cal_list

    return cal_vis_list


def delete_cal_vis(startdate=None, enddate=None, mode='happili-01',
                   run=False, verbose=True):
    """
    Delete calibrator visibilities

    Optionally do this for a range of dates

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

    cal_vis_list = get_cal_vis(startdate=startdate, enddate=enddate, mode=mode)

    # then iterate through each directory
    # print statement and delete, as set by flags
    for cvis in cal_vis_list:
        if run is True:
            # do a try/except
            # because may not have permission to delete data
            try:
                shutil.rmtree(cvis)
                if verbose is True:
                    print('Deleting {}'.format(cvis))
            except:
                if verbose is True:
                    print('Unable to delete {}'.format(cvis))
        else:
            if verbose is True:
                print('Practice run only; deleting {}'.format(cvis))


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
            if os.path.isdir(obdir):
                obs_beam_dir_list.append(obdir)

    # then need to find selfcal directories
    selfcal_dir_list = []
    for beamdir in obs_beam_dir_list:
        major_selfcal_list = glob.glob(
            os.path.join(beamdir, "selfcal/0[0-9]"))
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


def final_scal_cleanup(startdate=None, enddate=None,
                       mode='happili-01', run=False, verbose=True):
    """
    Do final selfcal cleanup. This is keeping last model in last major cycle and amp cycle
    Plus removing the paramteric directory (pm)

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
    # first get obsid array
    obsid_array = get_obsid_array(startdate=startdate, enddate=enddate)
    # then get initial path for each beam / obsid combination
    obs_beam_dir_list = []
    for obsid in obsid_array:
        for b in range(40):
            obdir = get_obsid_beam_dir(obsid, b, mode=mode)
            # test if beam exists before appending it
            if os.path.isdir(obdir):
                obs_beam_dir_list.append(obdir)
    # now iterate through
    for beamdir in obs_beam_dir_list:
        # roughly check whether or not I hve run this based on presence of pm dir
        # skip if already run
        pm_scal = os.path.join(beamdir, "selfcal/pm")
        if os.path.isdir(pm_scal):
            major_selfcal_list = glob.glob(
                os.path.join(beamdir, "selfcal/0[0-9]"))
            # need to sort into order
            major_selfcal_list.sort()
            last_scal = major_selfcal_list[-1]
            amp_scal = os.path.join(beamdir, "selfcal/amp")
            # first delete parametric; easiest
            if run is True:
                try:
                    shutil.rmtree(pm_scal)
                    if verbose is True:
                        print('Deleting {}'.format(pm_scal))
                except:
                    if verbose is True:
                        print('Unable to delete {}'.format(pm_scal))
            else:
                if verbose is True:
                    print('Practice run only; deleting {}'.format(pm_scal))
            # then do last major cycle
            major_models = glob.glob(os.path.join(last_scal, 'model_*'))
            major_models.sort()
            last_model = major_models[-1]
            last_scal_contents = glob.glob(last_scal + "/*")
            amp_models = glob.glob(os.path.join(amp_scal, 'model_*'))
            amp_models.sort()
            last_amp_model = amp_models[-1]
            last_amp_contents = glob.glob(amp_scal+"/*")
            if run is True:
                try:
                    # gztar phse model
                    shutil.make_archive(last_model, 'gztar', last_model)
                    if verbose is True:
                        print('gztar last phase selfcal model, {}'.format(last_model))
                    # then clean up
                    for scdir in last_scal_contents:
                        try:
                            shutil.rmtree(scdir)
                            if verbose is True:
                                print('Deleting {}'.format(scdir))
                        except:
                            if verbose is True:
                                print('Unable to delete {}'.format(scdir))
                except:
                    if verbose is True:
                        print('Unable to gztar last phase selfcal model, {}'.format(last_model))
                try:
                    # gztar amp
                    shutil.make_archive(last_amp_model, 'gztar', last_amp_model)
                    if verbose is True:
                        print('gztar last amp selfcal model, {}'.format(last_amp_model))
                    # then clean up
                    for scdir in last_amp_contents:
                        try:
                            shutil.rmtree(scdir)
                            if verbose is True:
                                print('Deleting {}'.format(scdir))
                        except:
                            if verbose is True:
                                print('Unable to delete {}'.format(scdir))
                except:
                    if verbose is True:
                        print('Unable to gztar last amp selfcal model, {}'.format(last_amp_model))
            else:
                if verbose is True:
                    print('Practice run only; gztar last phase selfcal model, {}'.format(last_model))
                    for scdir in last_scal_contents:
                        print('Practice run only; deleting {}'.format(scdir))
                    print('Practice run only; gztar last amp selfcal model, {}'.format(last_amp_model))
                    for scdir in last_amp_contents:
                        print('Practice run only; deleting {}'.format(scdir))
        else:
            if verbose is True:
                print('Parametric selfcal directory already removed; skipping cleanup for {}'.format(beamdir))


def get_continuum_intermediates(startdate=None, enddate=None,
                                mode='happili-01'):
    """
    Get the intermediate continuum files

    This will select all files of the form image_mf_NN.fits and residual_mf_NN that do not have the highest NN,
    so that they can be later deleted.
    This selects the model and mask of the highest NN to be later zipped (and original deleted).
    Beam images are also selected as intermediate product to be removed.

    Optionally do this for a range of dates

    Different mode for happili-01 vs happili-05

    This will return two lists: one for compression of masks_* and models_*,
    and one for files to be deleted which is all but the final output

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
    zip_list : list (str)
        List of files to be compressed
    del_list : list (str)
        List of files to be deleted
    """

    # first get obsid array
    obsid_array = get_obsid_array(startdate=startdate, enddate=enddate)

    # then get initial path for each beam / obsid combination
    obs_beam_dir_list = []
    for obsid in obsid_array:
        for b in range(40):
            obdir = get_obsid_beam_dir(obsid, b, mode=mode)
            if os.path.isdir(obdir):
                obs_beam_dir_list.append(obdir)

    del_list = []
    zip_list = []
    for beamdir in obs_beam_dir_list:
        print(beamdir)
        # get all dirty beams
        beam_list = glob.glob(os.path.join(beamdir, "continuum/beam*_0[0-9]"))
        # get all first dirty images (maps)
        map_list = glob.glob(os.path.join(beamdir, "continuum/map*_0[0-9]"))
        # get images that aren't fits
        image_list = glob.glob(os.path.join(beamdir, "continuum/image_*_0[0-9]"))
        # Find NN to save; this if for mf plus chunks
        # do this by looking at the saved fits images
        fits_image_list = glob.glob(os.path.join(beamdir, "continuum/image_*fits"))
        fits_image_list.sort()
        # now iterate through patterns for each saved image
        # setup lists to hold things
        model_zip_list = []
        mask_zip_list = []
        residual_keep_list = []
        for image in fits_image_list:
            pattern = re.search('image_(.+?).fits', image).group(1)
            # now add the relevant things with that pattern to the right lists
            # make sure they exist first
            mask = os.path.join(beamdir, "continuum/mask_{}".format(pattern))
            model = os.path.join(beamdir, "continuum/model_{}".format(pattern))
            residual = os.path.join(beamdir, "continuum/residual_{}".format(pattern))
            if os.path.isdir(mask): mask_zip_list.append(mask)
            if os.path.isdir(model): model_zip_list.append(model)
            if os.path.isdir(residual): residual_keep_list.append(residual)
        # Find all models, masks and residuals which are not in zip/keep list
        # Do this by listing all and then checking against zip_list and keep_list
        # start with models
        model_del_list = glob.glob(os.path.join(beamdir, "continuum/model_*_0[0-9]"))
        model_del_list.sort()
        for model in model_zip_list:
            if model in model_del_list:
                model_del_list.remove(model)
        # now masks
        mask_del_list = glob.glob(os.path.join(beamdir, "continuum/mask_*_0[0-9]"))
        mask_del_list.sort()
        for mask in mask_zip_list:
            if mask in mask_del_list:
                mask_del_list.remove(mask)
        # now residuals
        residual_del_list = glob.glob(os.path.join(beamdir, "continuum/residual_*_0[0-9]"))
        residual_del_list.sort()
        for residual in residual_keep_list:
            if residual in residual_del_list:
                residual_del_list.remove(residual)

        # join everything w/ zip & delete list
        zip_list = zip_list + mask_zip_list + model_zip_list
        del_list = del_list + mask_del_list + model_del_list + residual_del_list + beam_list + map_list + image_list

    return zip_list, del_list


def cleanup_continuum_intermediates(startdate=None, enddate=None,
                                    mode='happili-01',
                                    run=False,
                                    verbose=True):
    """
    Cleanup intermediate continuum files :: Copied from delete_intermediate_scal_dirs

    Optionally do this for a range of dates
    Intermediate continuum directories are in
    /data/apertif/ObsID/BB/continuum

    Files from the non-final cycle are deleted.
    Those from the last cycle are saved, and zipped if they are models or masks
    This is applied to mf images, in addition to chunk images.

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
    # first get files for deletion and zipping, plus writing to fits
    zip_list, del_list = get_continuum_intermediates(startdate=startdate, enddate=enddate, mode=mode)

    # then iterate through each list
    # start with zip and fits, to avoid accidental deletion
    # but also clean those up as you go
    # print statement and delete, as set by flags
    # zip the directories to keep
    for contdir in zip_list:
        if run is True:
            # do a try/except
            # because of permission issues on happili
            try:
                shutil.make_archive(contdir, 'gztar', contdir)
                if verbose is True:
                    print('gztar for {}'.format(contdir))
            except:
                if verbose is True:
                    print('Unable to gztar file {}'.format(contdir))
            # then clean up files if they are zipped/tarred
            if os.path.exists(contdir+'.tar.gz'):
                try:
                    shutil.rmtree(contdir)
                    print('gztar file exists, clean up original directory {}'.format(contdir))
                except:
                    if verbose is True:
                        print('gztar file exists but unable to clean up original directory {}'.format(contdir))
        else:
            if verbose is True:
                print('practice run only; gztar and then try to clean up {}'.format(contdir))
    for contdir in del_list:
        if run is True:
            # do a try/except
            # because may not have permission to delete data
            try:
                shutil.rmtree(contdir)
                if verbose is True:
                    print('Deleting {}'.format(contdir))
            except:
                if verbose is True:
                    print('Unable to delete {}'.format(contdir))
        else:
            if verbose is True:
                print('Practice run only; deleting {}'.format(contdir))






