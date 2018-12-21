#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 19:23:38 2018

@author: josh_swerdlow

Create some random data and plot it!
"""

import os
import re
import sys
import math

import h5py as h5
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import stable_matching as sm
from process import *

# Creates a histgram of the start times from the given data
def start_time_hist(data, binwidth=0.025e-3, filtered=False, save_dir=None, show=False):
    """
    start_times (s)
    """
    seeds = data.keys()

    group = 'candidate_tracks'
    dataset = 'candidate_tracks_0'
    start_time = 'StartTimeInAcq'
    title = 'Histogram of Start Time in Acquisition'
    # If we are looking at the filtered data then append the filtered
    # extension to the appropriate values
    if filtered:
        dataset += "_"
        start_time += "_"

    egg_times = list()

    for seed in seeds:
        egg_times += list(data[seed][group][dataset][start_time])

    egg_bins = np.arange(min(egg_times), max(egg_times) + binwidth, binwidth)
    plt.figure('Start Time Hist')
    plt.hist(egg_times, bins=egg_bins, color='b')

    # S E T T T I N G S
    plt.xlabel('Start Time [S]')
    plt.ylabel('Counts')
    plt.ylim((0,20))
    plt.title(title)
    plt.grid()

    if save_dir is not None:
        if os.path.isdir(save_dir):
            fn = "startTimeHistogram.png"
            plt.savefig(os.path.join(save_dir, fn))

    if show:
        plt.show()

def start_freq_hist(data, binwidth=0.1, filtered=False, save_dir=None, show=False, pitch_times=None, pitch_angls=None):
    """
    start_freqs (MHz)
    binwidth (MHz)
    """
    hz_to_Mhz = 1e-6
    title = "Histogram of Start Frequency"

    group = 'candidate_tracks'
    dataset = 'candidate_tracks_0'
    freq = 'StartFrequency'

    # If we are looking at the filtered data then append the filtered
    # extension to the appropriate values
    if filtered:
        dataset += "_"
        freq += "_"

    seeds = data.keys()
    egg_freqs = list()
    for seed in seeds:
        egg_freqs += list(data[seed][group][dataset][freq] * hz_to_Mhz)

    egg_bins = np.arange(min(egg_freqs), max(egg_freqs) + binwidth, binwidth)
    plt.figure('Start Freq Hist')
    plt.hist(egg_freqs, bins=egg_bins)

    # S E T T T I N G S
    plt.title(title)
    plt.ylabel("Counts")
    plt.ylim((0,20))
    plt.xlabel("Frequency [MHz]")
    plt.grid()

    if save_dir is not None:
        if os.path.isdir(save_dir):
            fn = "startFreqHist.png"
            plt.savefig(os.path.join(save_dir, fn))

    if show:
        plt.show()

# Scatterpolot of startfreq vs slope
def start_freq_v_slope(data, filtered=False, save_dir=None, show=False):
    hz_to_Mhz = 1e-6 # hertz to megahertz
    s_to_ms = 1e3 # seconds to milliseconds
    hzPs_to_MHzPms = 1e-9 # hz/s to MHz/ms

    title = "Slope vs Start Frequency"

    group = 'candidate_tracks'
    dataset = 'candidate_tracks_0'
    freq = 'StartFrequency'
    slope = 'Slope'

    if filtered:
        dataset += "_"
        freq += "_"

    seeds = data.keys()
    startFreqs = list()
    slopes = list()
    for seed in seeds:
        startFreqs += list(data[seed][group][dataset][freq] * hz_to_Mhz)
        slopes += list(data[seed][group][dataset][slope])

    # Plot in range 1049.5 to 1053 MHz on x-axis and 0.2 to 0.95 MHz/ms on y-axis.
    plt.figure('Start Freq v Slope')
    plt.scatter(startFreqs, slopes, facecolors='none', edgecolors='b', alpha=0.5,)

    plt.title(title)
    plt.xlabel("Start Frequency [MHz]")
    plt.ylabel("Slope [MHz/ms]")
    plt.grid()
    plt.xlim((105,118))
    # plt.xlim((1049.5, 1053))
    # plt.ylim(0.2, 0.95)

    if save_dir is not None:
        if os.path.isdir(save_dir):
            fn = 'startFreq_v_slope.png'
            plt.savefig(os.path.join(save_dir, fn))

    if show:
        plt.show()

def power_v_slope(data, filtered=False, save_dir=None, show=False):
    hz_to_Mhz = 1e-6 # hertz to megahertz
    s_to_ms = 1e3 # seconds to milliseconds
    hzPs_to_MHzPms = 1e-9 # hz/s to MHz/ms

    title = "Slope vs Start Frequency"

    group = 'candidate_tracks'
    dataset = 'candidate_tracks_0'
    totPower = 'TotalPower'
    slope = 'Slope'

    if filtered:
        dataset += "_"
        freq += "_"

    power = list()
    slopes = list()
    seeds = data.keys()
    for seed in seeds:
        power += list(data[seed][group][dataset][totPower])
        slopes += list(data[seed][group][dataset][slope])

    # Plot in range 1049.5 to 1053 MHz on x-axis and 0.2 to 0.95 MHz/ms on y-axis.
    plt.figure('Power v Slope')
    plt.scatter(slopes, power, facecolors='none', edgecolors='b', alpha=0.5,)

    plt.title(title)
    plt.xlabel("Slope [Hz/s]")
    plt.ylabel("Power [W/Hz]")
    plt.grid()

    plt.xlim((200e6, 800e6))
    plt.ylim((0, 50e-18))

    if save_dir is not None:
        if os.path.isdir(save_dir):
            fn = 'power_v_slope.png'
            plt.savefig(os.path.join(save_dir, fn))

    if show:
        plt.show()

# Implements Gale-Shapley (Asymmetric) Stable Match Algorithm
# The preference matrices (propPref, acptPref) are constructed
# by sort the different of proposer_i with all acceptors and vice versa
# NOTE: Proposers must always be the smaller set
def stable_matching(proposers, acceptors, tol):
    if not isinstance(proposers, np.ndarray) or not isinstance(acceptors, np.ndarray):
        sys.exit("Stable-Matching Error: proposers and acceptors must be numpy arrays.")

    P = proposers.size
    A = acceptors.size
    data_format = {'names': ['difference', 'values'],
                   'formats': [np.float32, np.float32]}

    # Instantiate the proposers and acceptors preference matrices
    propPref = np.zeros(shape=(P, A), dtype=data_format)
    acptPref = np.zeros(shape=(A, P), dtype=data_format)

    # Construct the difference matrix by doing the element-wise subtraction
    # shape = (P, A)
    diff = np.absolute(np.subtract(proposers[:, None], acceptors))

    # Then filter the diff matrix by the tolerance
    np.putmask(diff, diff > tol, 0)

    # Initialize the proposer and acceptor preference matrices
    propPref['difference'] = diff
    propPref['values'] = acceptors

    acptPref['difference'] = np.transpose(diff)
    acptPref['values'] = proposers

    # Sort (small to large) the prefence matrices by row
    # on the difference component
    np.ndarray.sort(propPref, axis=1, order='difference', kind='mergesort')
    np.ndarray.sort(acptPref, axis=1, order='difference', kind='mergesort')

    print("Proposer Preferences: \n{}".format(propPref))
    print("Acceptor Preferences: \n{}".format(acptPref))

    # Initialize a custom object for both proposers and acceptors
    # I should fina  way to make these iterable
    Proposers = sm.ElementArray(proposers)
    Acceptors = sm.ElementArray(acceptors)

    # Initialize a custom object for matches
    Matches = sm.Matches()

    # Initialize a custom object for proposer and acceptor preferences
    # PropPref = sm.PreferenceMatrix(Proposers, propPref['values'])
    # AcptPref = sm.PreferenceMatrix(Acceptors, acptPref['values'])


if __name__ == "__main__":
    # REMINDER: MAKE HISTOGRAM OF PITCH ANGLES SIMULATED

    # Process all the data in default directories
    seeds, files, data = process_files()
    save_dir = "./figures/test_properties/"
    # start_time_hist(data, save_dir=save_dir)
    # start_freq_hist(data, save_dir=save_dir)
    # start_freq_v_slope(data, save_dir=save_dir)
    power_v_slope(data, show=True)


    # Run through the files and construct the necessary plots
    # time_fig, time_ax = plt.subplots()
    # title = "Histogram of Start Time in Acquisition with associated pitch angles"
    # time_ax.set_title(title)
    # time_ax.set_ylabel("Counts")
    # time_ax.set_xlabel("Start Time [s]")
    # time_ax.grid()
    # unfiltered_dfs = dict()
    # filtered_dfs = dict()
    # for i, file in enumerate(files):
    #     h5_file = h5_dir + file[0]
    #     pitch_file = pitch_angl_dir + file[1]

    #     # Get the selected variables from the h5 file
    #     # in candidates/candidates_0
    #     # Return the variable data as a dictionary
    #     group = "candidates"
    #     dataset = "candidates_0"
    #     variables = ["StartTimeInAcq", "StartFrequency"]
    #     var_info = fetch_variables_hdf5(h5_file, group, dataset, variables)


    #     # Extracting info from hdf5 file
    #     start_times = var_info[variables[0]]
    #     start_freqs = var_info[variables[1]]

    #     # Get the pitch times and pitch angles
    #     pitch_times, pitch_angles = get_pitch_angles(pitch_file)
    #     var_info.update({'pitch times': pitch_times, 'pitch angles': pitch_angles})

    #     # Create an unfiltered data dataframe
    #     var_info.update({'Seed': [seeds[i] for _ in range(len(start_times))]})
    #     print(var_info)
    #     unfiltered_dfs[seeds[i]] = pd.DataFrame(var_info)

    #     # Find number of events found vs simulated
    #     test_event_processing(pitch_file, h5_file)

    #     # Get the matched indices for the data
    #     time_indices, ptch_indices = compare_times(start_times, pitch_times)

    #     # Filter the data and update the dictionary
    #     pitch_times_adj = [pitch_times[p] for p in ptch_indices]
    #     pitch_angles_adj = [pitch_angles[p] for p in ptch_indices]

    #     start_times_adj = [start_times[t] for t in time_indices]
    #     start_freqs_adj = [start_freqs[t] for t in time_indices]

    #     # Construct a dictionary of data that was filtered for event matching
    #     dic = dict()
    #     dic['pitch times adj'] = pitch_times_adj
    #     dic['pitch angles adj'] = pitch_angles_adj
    #     dic['start times adj'] = start_times_adj
    #     dic['start freqs adj'] = start_freqs_adj
    #     dic['Seed'] = [seeds[i] for _ in time_indices]

    #     filtered_dfs[seeds[i]] = pd.DataFrame(dic)

    #     ## MAKE A DATEFRAME OF DATAFRAMES!!

    #     # start_time_hist(time_ax, start_times, 0.025e-3, pitch_times=pitch_times_adj, pitch_angls=pitch_angles_adj)

    #     # start_freq_hist(np.array(start_freqs) * Hz_to_MHz, 0.1, show=False)

    # filtered_data = pd.concat(filtered_dfs)
    # unfiltrd_data = pd.concat(unfiltered_dfs)
    # # df['pitch times'].plot.hist()
    # # print(df.loc['Seed100', :])
    # print(filtered_data)
    # print(unfiltrd_data)
    # # time_ax.legend()
    # # plt.show()


def test_stable_matching():
    A = np.random.random(5)
    B = np.random.random(5)
    A = np.array([5, 0, 5, 10])
    B = np.array([3, 6])
    stable_matching(A, B, 2)