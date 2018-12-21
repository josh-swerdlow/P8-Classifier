#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 19:23:38 2018

@author: josh_swerdlow

Create some random data and plot it!
"""

def direct_concat(arg1, arg2):
    return arg1 + "/" + arg2


import h5py as h5
import numpy as np
import matplotlib.pyplot as plt

fn = "events_177_222_236_248.h5"

hf = h5.File(fn, "r")

group_1 = "candidate_tracks"
datasets_1 = ["StartTimeInAcq", "StartFrequency", "Slope"]

g1 = hf.get(group_1)
startTime = np.array(g1.get(datasets_1[0]))
startFreq = np.array(g1.get(datasets_1[1]))
slope = np.array(g1.get(datasets_1[2]))


group_2 = "egg-header"
datasets_2 = "minimum_frequency"

g2 = hf.get(group_2)
min_freq = np.array(g2.get(datasets_2))

adj_startFreq = startFreq + min_freq[0]

############ HISTOGRAMS ################

# Create a histogram of the StartTimeInAcq with bin width 0.025 ms. 
binwidth = 0.025e-3
print("histogram of start time...")
plt.figure(1)
plt.hist(startTime, bins=np.arange(min(startTime), max(startTime) + binwidth, binwidth))
plt.title("Histogram of Start Time in Acquisition with bin width of 0.025 ms")
plt.ylabel("Counts")
plt.xlabel("Start Time [ms]")

# Create a histogram of the Start Frequency adjusted for the minimum frequency
# Bin width is 0.1 MHZ with plot range of 1005 - 1105 MHz
binwidth = 0.1e6
print("historgram of start freq...")
plt.figure(2)
plt.hist(adj_startFreq, bins=np.arange(min(adj_startFreq), max(adj_startFreq) + binwidth, binwidth))
plt.title("Histogram of Start Frequency with bindwidth of 0.1 MHz")
plt.ylabel("Counts")
plt.xlabel("Frequency adjusted for minimum frequency [MHz]")
#plt.xlim(1005e6, 1105e6)


## FILTER DATA between 0.9 and 1.2 ms startingTime
condition = np.logical_and(startTime >= 0.9e-3, startTime <= 1.2e-3)
filtered_startTime = np.extract(condition, startTime)
filtered_startFreq = np.extract(condition, adj_startFreq)
filtered_slope = np.extract(condition, slope)


# Repeat plot #2 but this time only for tracks whose 'StartTimeInAcq' are between 0.9 and 1.2 ms.
binwidth = 0.1e6
print("filtered start frequncy histogram...")
plt.figure(4)
plt.hist(filtered_startFreq, bins=np.arange(min(filtered_startFreq), max(filtered_startFreq) + binwidth, binwidth))
plt.title("Filtered Historgram of Start Time In Acquisition with bindwidth 0.025 ms")
plt.ylabel("Counts")
plt.xlabel("Filtered Start Frequency [Hz]")

# Combine startTime histograms
# Create a histogram of the StartTimeInAcq with bin width 0.025 ms. 
# These are the start times of each track.
binwidth = 0.025e-3
print("histogram of start time...")
plt.figure(6)
plt.hist(startTime, bins=np.arange(min(startTime), max(startTime) + binwidth, binwidth))
plt.hist(filtered_startTime, bins=np.arange(min(filtered_startTime), max(filtered_startTime) + binwidth, binwidth))
plt.title("Combined (un)Filtered Historgram of Start Time In Acquisition with bindwidth 0.025 ms")
plt.ylabel("Counts")
plt.xlabel("(un)Filtered Start Time [ms]")

############ SCATTER PLOTS ################
print("SCATTER PLOTS....")

# Scatterpolot of startfreq vs slope
# Plot in range 1049.5 to 1053 MHz on x-axis and 0.2 to 0.95 MHz/ms on y-axis.
print("scatter plot of startfreq vs slope...")
plt.figure(3)
plt.scatter(adj_startFreq, slope)
plt.title("Start Frequency vs Slope")
plt.ylabel("Start Frequency [Hz]")
plt.xlabel("Slope [Hz/s]")
#plt.xlim((1049.5e6, 1053e6))
#plt.ylim(0.2e9, 0.95e9)

# Repeat plot #3 but this time only for tracks whose 'StartTimeInAcq' are between 0.9 and 1.2 ms
print("Filtered Start Frequency...")
plt.figure(5)
plt.scatter(filtered_startFreq, filtered_slope)
plt.title("Filtered Start Frequency vs Slope")
plt.ylabel("Filtered Start Frequency [Hz]")
plt.xlabel("Slope [Hz/s]")
#plt.xlim((1049.5e6, 1053e6))
#plt.ylim(0.2e9, 0.95e9)

# Combine startFreq scatter plots
print("Combined startFreq Scatter plots...")
plt.figure(7)
plt.scatter(adj_startFreq, slope)
plt.scatter(filtered_startFreq, filtered_slope)
plt.title("Combined (un)Filtered Start Frequency vs Slope")
plt.ylabel("(un)Filtered Start Frequency [Hz]")
plt.xlabel("Slope [Hz/s]")
plt.show()


# Close the hdf5 file
hf.close()
