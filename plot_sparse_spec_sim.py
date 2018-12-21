'''
Script to process root files with discrim points and event data and save images
of sparse specs with track and event data displayed. Made for (and for ROOT built with) python 2
Author: L. Saldana
11/27/18
'''

from __future__ import division
from __future__ import absolute_import

import os
import sys
import glob
import subprocess
import numpy as np
import matplotlib as mpl
mpl.use('pdf')
import matplotlib.pyplot as plt
mpl.rcParams['figure.figsize'] = (12,6) # figsize
mpl.rcParams['font.size'] = 15 # tick size
mpl.rcParams['axes.labelsize'] = 20 # axes label size
mpl.rcParams['axes.titlesize'] = 20 # title size

from itertools import izip

def plotSparseSpec(discrim_time,discrim_freq,spec_name,file_dest_dir=None,tracklabels_inrun=np.array([]),tracktimes_inrun=np.array([]),
                   trackfreqs_inrun=np.array([]),evtstarttimes_inrun=np.array([]),evtstartfreqs_inrun=np.array([]),flag_classified=False):
    u'''
    Plots (and saves) sparse spectrograms given the discriminated points in time and frequency; it can also overlay tracks and events
    By discriminated points we mean the values of the Katydid signal `discrim:disc-1d`. Usually we would have root or h5 files with this
    and we would process these file through the function processSparseSpec() which calls this function. However this
    function call also be called independently
    Required:
    discrim_time (1d arr): numpy array of discriminated points' times in seconds
    discrim_freq (1d arr): numpy array of discriminated points' frequencies in Hz
    spec_name (str): title for plot
    Optional:
    file_dest_dir (str): path to directory to save plots as png files to; no final forwardslash /
    tracktimes_inrun (2d arr of shape Nx2): numpy array where each row is [start_time,end_time] in seconds; N tracks gives N rows w/ 2 columns
    trackfreqs_inrun (2d arr of shape Nx2): numpy array where each row is [start_freq,end_freq] in Hz; N tracks gives N rows w/ 2 columns
    tracklabels_inrun (1d arr of shape N): numpy array where each entry is either 0, 1 or 2 following the Phase 1 classifier labels
    evtstarttimes_inrun (1d arr): numpy array of events' start times in seconds
    evtstartfreqs_inrun (1d arr): numpy array of events' start frequencies in Hz
    flag_classified (bool): True if plotting tracks which have been classified; used with processSparseSpec2() only
    '''

    handles = [] # for legend
   # min_freq = 1.64e9 # 17 keV for classifier paper events
   # min_freq = 1.04e9 # 30 keV for classifier paper events
   # min_freq = 9.65e8 # 32 keV for classifier paper events
    min_freq = 0

    # Plot discriminated points
    fig = plt.figure(figsize=(14,10))
    plt.clf()
    plt.scatter(discrim_time*1e3,(discrim_freq+min_freq)/1e6,s=7,color=u'k',alpha=0.4,lw=0.2,zorder=2) # discrim points
    plt.xlim(np.min(discrim_time)*1e3,np.max(discrim_time)*1e3)
    plt.ylim(np.min(discrim_freq+min_freq)/1e6,np.max(discrim_freq+min_freq)/1e6)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.xlabel('Time in Run (ms)',fontsize=18)
    plt.ylabel('Frequency (MHz)',fontsize=18)
    plt.title(spec_name,fontsize=14)

    # If the track (no classification label) info is present we plot it on top
    if tracktimes_inrun.size:
        spec_name += u"+Tracks"
        counter = 0
        for idx_track in xrange(len(tracktimes_inrun)): # there might be more than one track within the acquisition
            if counter != 0:
                plt.plot(tracktimes_inrun[idx_track]*1e3,trackfreqs_inrun[idx_track]/1e6,linewidth=4,color='red',zorder=1)
            else:
                plt.plot(tracktimes_inrun[idx_track]*1e3,trackfreqs_inrun[idx_track]/1e6,linewidth=4,color='red',zorder=1,label='Track')
                counter += 1

    # If the event info is present we plot it on top
    if evtstarttimes_inrun.size:
        spec_name += u"+Events"
        plt.scatter(evtstarttimes_inrun*1e3,evtstartfreqs_inrun/1e6,marker='o',s=30,edgecolors='darkgreen',facecolors='lightgreen',zorder=3,label='Event Start')

    # Saving the extra spectrogram
    if (file_dest_dir is not None):
        plt.legend(loc='upper right',fontsize=14)
        plt.title(spec_name,fontsize=18)
        file_dest = file_dest_dir + u"/" + spec_name + u".png"
        plt.savefig(file_dest,dpi=300,bbox_inches=u'tight')
        print u'\t\t{}'.format(spec_name)+u'.png'
        plt.close()

    return

def processSparseSpec(file_loc,file_type=u'root',file_dest_dir=None,acq_length=0.02,flag_plot_tracks=False,flag_plot_evts=False):
    u'''
    Processes a directory where root or h5 (not yet implemented) files sit which have sparse spectrogram data and optionally track and event data
    The files must at least contain discriminated-points data to make plots. Plots can be saved if a destination directory is provided
    By discriminated points we mean the values of the Katydid signal `discrim:disc-1d`

    Required:
    file_loc (str): path to directory where source root or h5 (not yet implemented) files sit; no final forwardslash /
    file_type (str) root or h5 (not yet implemented)

    Optional:
    file_dest_dir (str): path to directory to save plots as png files to; no final forwardslash /
    acq_length (double): acquisition length of data. Defaults to 10 ms which is our usual acquisition length
    flag_plot_tracks (bool): if True then we plot tracks on top of sparse spectrogram
    flag_plot_evts (bool): if True then we plit events on top of sparse spectrogram
    '''

    import ROOT # only need ROOT for this function

    if file_type==u"root":
        filelist = glob.glob(file_loc+u'/*.root')
    elif file_type==u"h5": # not yet implemented
        filelist = glob.glob(file_loc+u'/*.h5')

    if not filelist:
        raise Exception(u"No files found in {}. Aborting.".format(file_loc))

    for idx_file, ii_file in enumerate(filelist):

        # Getting name for spectrogram from filename
        filename = os.path.split(ii_file)[1] # splits path and keeps file name
        print u'Source file: {}'.format(filename)
        filename = os.path.splitext(filename)[0] # removes extension
        # Load file
        file = ROOT.TFile(ii_file)
        print 'ii_file: {}'.format(ii_file)

        try:
            disc = file.Get("discPoints1D") # Discrim points
            NPoints = disc.GetEntries()
        except AttributeError:
            print u"\tNo discPoints1D data found. Skipping..."
            continue # next file since without discrim points we don't care for tracks/events

        else: # if there's no exception execute this block

            # LOADING DATA

            freq = np.zeros(NPoints) # allocate space
            time = np.zeros(NPoints)
            # Collect frequencies and times in run
            for ii_point in xrange(NPoints):
                disc.GetEntry(ii_point)
                freq[ii_point] = disc.fAbscissa
                time[ii_point] = disc.fTimeInRunC

            if (flag_plot_tracks) or (flag_plot_evts):
                try:
                    mtevents = file.Get('multiTrackEvents')
                except Exception as e:
                    print '\tNo multiTrackEvents data found. Skipping...'
                else:
                    event = mtevents.FindBranch('Event')
                    NEvents = mtevents.GetEntries()

            # Plot tracks?
            if flag_plot_tracks:
                try:
                    tracks = event.FindBranch('fTracks')
                    NTracks = tracks.GetEntries()
                except AttributeError:
                    print u'\tNo procTracks data found. Skipping...'
                    continue
                else:
                    trackfreqs = np.zeros((2*NTracks,2)) # To plot lines we need pairs of freqs (start/end) which set the y limits of the line
                    tracktimes = np.zeros((2*NTracks,2)) # To plot lines we need pairs of times (start/end) which set the x limits of the line
                    for ii_point in np.arange(0,NTracks): # collect data points, each is a 2-element tuple
                        tracks.GetEntry(ii_point) # gets 2-element tuple (don't know why it's formatted this way)
                        branch1 = tracks.FindBranch('fTracks.fStartFrequency')
                        leaf1 = branch1.FindLeaf('fTracks.fStartFrequency')
                        branch2 = tracks.FindBranch('fTracks.fEndFrequency')
                        leaf2 = branch2.FindLeaf('fTracks.fEndFrequency')
                        branch3 = tracks.FindBranch('fTracks.fStartTimeInRunC')
                        leaf3 = branch3.FindLeaf('fTracks.fStartTimeInRunC')
                        branch4 = tracks.FindBranch('fTracks.fEndTimeInRunC')
                        leaf4 = branch4.FindLeaf('fTracks.fEndTimeInRunC')
                        for jj_point in range(2): # we need both
                            trackfreqs[2*ii_point+jj_point] = np.array([leaf1.GetValue(jj_point),leaf2.GetValue(jj_point)])
                            tracktimes[2*ii_point+jj_point] = np.array([leaf3.GetValue(jj_point),leaf4.GetValue(jj_point)])

            # Plot events?
            if flag_plot_evts:
                evtstartfreqs = np.zeros(NEvents) # allocate space
                evtstarttimes = np.zeros(NEvents)
                for ii_point in xrange(NEvents): # collect data points
                    mtevents.GetEntry(ii_point)
                    leaf1 = mtevents.FindLeaf(u"fStartFrequency")
                    leaf2 = mtevents.FindLeaf(u"fStartTimeInRunC")
                    evtstartfreqs[ii_point] = leaf1.GetValue()
                    evtstarttimes[ii_point] = leaf2.GetValue()

            # PLOTTING

            # Data files (h5/root) come from concatenated mat files and thus have huge time gaps
            # We want to get spectrograms from separate acquisitions
            # So we find the time gaps in the data set and save them for later use in the plots
            time_sorted = np.sort(time)
            time_diff = np.diff(time_sorted) # misses the last time limit
            time_upperlim = time_sorted[np.where(time_diff>0.1)[0]]
            time_upperlim = np.append(time_upperlim,time[-1]) # include the last time limit

            if file_dest_dir is not None:
                print u'\tSaving files to: {}'.format(file_dest_dir)
            for idx_timelim,ii_timelim in enumerate(time_upperlim): # loop through acquistions in file
                acq_time_start = ii_timelim-acq_length # start time of this acqusition
                spec_name = filename+u"_{}".format(idx_timelim)
                kwargs = {u'spec_name':spec_name,u'file_dest_dir':file_dest_dir} # we'll pas in a kwarg dict for convenience instead of passing in every kwarg argument to plot function
                if flag_plot_tracks: # if so add track information to kwargs
                    acq_cut = (tracktimes[:,0]>=acq_time_start) & (tracktimes[:,1]<=ii_timelim) # cut for tracks within this acquistion only
                    tracktimes_inrun = tracktimes[acq_cut] # track start and end times in this acqusition
                    trackfreqs_inrun = trackfreqs[acq_cut] # track start and end frequencies in this acquisition
                    kwargs[u'tracktimes_inrun'] = tracktimes_inrun # to send to plotSparseSpec
                    kwargs[u'trackfreqs_inrun'] = trackfreqs_inrun
                if flag_plot_evts: # if so add event information to kwargs
                    acq_cut = (evtstarttimes>=acq_time_start) & (evtstarttimes<=ii_timelim) # cut for events within this acquistion only
                    evtstarttimes_inrun = evtstarttimes[acq_cut] # event start times in this acqusition
                    evtstartfreqs_inrun = evtstartfreqs[acq_cut] # events start frequencies in this acqusition
                    kwargs[u'evtstarttimes_inrun'] = evtstarttimes_inrun # to send to plotSparseSpec
                    kwargs[u'evtstartfreqs_inrun'] = evtstartfreqs_inrun
                acq_cut = (time>=acq_time_start) & (time<=ii_timelim) # time cut for a single acqusition
                plotSparseSpec(time[acq_cut],freq[acq_cut],**kwargs)
                plt.pause(0.05)
    return


if __name__ == '__main__':
    dest_dir1 = "/home/jswerdlow/classifier/figures/tracks_found"
    dest_dir2 = "/home/jswerdlow/classifier/figures/tracks_unfound"


    if len(sys.argv) == 2:
        root_fn = sys.argv[1]

        if not os.path.isdir(root_fn):
            sys.exit("Error: '{}' is not a valid directory.".format(root_fn))
    else:
        root_fn = "./data/processed_eggs/root"

    processSparseSpec(root_fn, file_dest_dir=dest_dir1,flag_plot_tracks=True,flag_plot_evts=True)
    # processSparseSpec(root_fn, file_dest_dir=dest_dir2,flag_plot_tracks=False,flag_plot_evts=False)
