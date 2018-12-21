import os
import re
import sys

import h5py as h5
import numpy as np
import pandas as pd

from copy import copy, deepcopy

# Fetches the given variables from the given hdf5 file
# with a group and dataset storing all the variables data
def fetch_variables_hdf5(fn, group, dataset, variables):

    if not fn.endswith(".h5"):
        sys.exit("Error: File '{}' is not HDF5.".format(fn))

    # Open the h5py file stream
    with h5.File(fn, "r") as hf:

        # Get the group object unless failure
        try:
            gp = hf.get(group)
        except AttributeError:
            sys.stderr.write("'{}' has no group: {}.\n".format(fn, group))
            return -1

        # Get the dataset object unless failure

        try:
            ds = gp.get(dataset)
        except AttributeError:
            sys.stderr.write("'{}' has no dataset: {}.\n".format(fn, dataset))
            return -1

        # Go through the dataset and check what variables
        # are actually in the dataset
        data = dict()
        for variable in variables:
            if variable in ds.dtype.names:
                data[variable] = list()
            else:
                sys.stderr.write("'{}' was not found in the dataset.\n".format(variable))
                variables.remove(variable)

        # Find the location of all of the variables
        indices = list()
        for variable in variables:
            indices.append(ds.dtype.names.index(variable))

        # We must manipulate the values to be in an appropriate form
        # At the moment, it is 11x37 in which each column corresponds to
        # a single value for one of the 37 variables
        for variable, index in zip(variables, indices):
            for d in ds:
                data[variable].append(d[index])

    return data

# Extract time and pitch angles data from a text file
def get_pitch_data(fn):

    times = list()
    pitch_angles = list()

    with open(fn, 'r') as f:
        for line in f:
            time, pitch_angle = line.split()

            times.append(float(time))
            pitch_angles.append(float(pitch_angle))

    return (times, pitch_angles)

# Returns the appropriate indices for the times which match with one another
# (within a tolerance) for both list objects provided
def compare_times(egg_times, pitch_times):

    # Change numpy arrays to lists before computation
    if isinstance(egg_times, np.ndarray):
        egg_times = list(egg_times)

    if isinstance(pitch_times, np.ndarray):
        pitch_times = list(pitch_times)

    tol = 2e-4
    time_indices = list()
    ptch_indices = list()
    for et in egg_times:
        for pt in pitch_times:
            diff = abs(et - pt)
            if diff < tol:
                ptch_indices.append(pitch_times.index(pt))
                time_indices.append(egg_times.index(et))
                break

    return (time_indices, ptch_indices)

"""
Finds the percentage of events successfully found through Katydid
    pitch_angles: Pitch angle file directory or list of pitch_angle files
        By default pitch_angles = "./data/pitch_angles/"
    egg: Processed egg file directory or list of egg files
        By default eggs = "./data/processed_eggs/(hdf5/root)"
        depending on the egg_type

    egg_type [string]: 'h5' or 'root'
        By default egg_type = 'h5'
"""
def test_event_processing(pitch_angles=None, eggs=None, egg_type='h5'):

    pitch_angle_dir = "./data/pitch_angles"

    h5_dir = "./data/processed_eggs/hdf5"
    root_dir = "./data/processed_eggs/root"
    if egg_type == 'h5':
        egg_dir = h5_dir
    else:
        egg_dir = root_dir

    # Default Parameter Handling --> extract entire default directory
    if pitch_angles is None:
        pitch_angles = [os.path.join(pitch_angle_dir, fn) for fn in os.listdir(pitch_angle_dir)]

    if eggs is None:
        eggs = [os.path.join(egg_dir, fn) for fn in os.listdir(egg_dir)]

    # Single File Parameter Handling --> turn string into list unless it's a dir
    if isinstance(pitch_angles, str):
        if os.path.isdir(pitch_angles):
            pitch_angles = [os.path.join(pitch_angles, fn) for fn in os.listdir(pitch_angles)]
        else:
            pitch_angles = [pitch_angles]

    if isinstance(eggs, str):
        if os.path.isdir(eggs):
            eggs = [os.path.join(eggs, fn) for fn in os.listdir(eggs)]
        else:
            eggs = [eggs]

    # Non-list Parameters Handling --> exit with error
    if not isinstance(pitch_angles, list):
        sys.stderr.write("Usage Error: pitch_angles must be a directory, file name, list of file names, or None.")
        sys.exit(0)

    if not isinstance(eggs, list):
        sys.stderr.write("Usage Error: pitch_angles must be a directory, file name, list of file names, or None.")
        sys.exit(0)

    # List Parameters Handling --> continue with execution, no more error handling

    # print('Testing Katydid processing on {} egg file(s) and {} pitch angle file(s).'.format(eggs, pitch_angles))

    single_file = False
    if len(pitch_angles) == 1:
        single_file = True

    # Iterate through the pitch angle seed values and look for egg
    # files that have the appropriate seed value
    total_events = 0
    total_events_detected = 0
    for pitch_angle in pitch_angles:
        pitch_seed = extract_seed(pitch_angle)

        for egg in eggs:
            # If a match is found then compared
            # the events and move on to the next seed
            egg_match = re.search(pitch_seed, egg)

            if egg_match is not None:
                # Note: variable 'angle_events' is actually time data
                # but the physicality of the data is completely irrelevant
                # and this nomeclature is better.

                # Read the angle file
                angle_events, __ = get_pitch_data(pitch_angle)

                # Read the egg file (depends on egg_type)
                egg_events = None
                if egg_type == 'h5':
                    group = "candidates"
                    dataset = "candidates_0"
                    variables = ["EventID"]
                    data = fetch_variables_hdf5(egg, group, dataset, variables)

                    if data == -1:
                        sys.stderr.write("Could not fetch {} from {}\n".format(variables, egg))
                        break

                    # If EventID not found variables will return as empty
                    if len(variables) > 0:
                        egg_events = data[variables[0]]
                    else:
                        sys.stderr.write('No EventID found in {}\n'.format(egg))
                else:
                    sys.stderr.write('Root implemetation not available\n')

                if egg_events is not None:
                    a = len(angle_events)
                    e = len(egg_events)
                    print("{}: {}/{} events detected ({}%).".format(pitch_seed, e, a, (e/a)*100))

                    total_events+=a
                    total_events_detected+=e

                # Remove the file name from the group of eggs
                eggs.remove(egg)

                # Found a valid egg file so leave regardless of outcome
                break

    if total_events > 0 and not single_file:
        event_detect_prcnt = (total_events_detected / total_events) * 100
        print("Total Events Detected: {}/{} ({}%)".format(total_events_detected, total_events, event_detect_prcnt))

# Given a string this method searches through the contents and extracts
# any string with a 'SeedXXX' in it and returns this as the result or None
# if no string can be found.
def extract_seed(string):
    # Parameter handling
    if not isinstance(string, str):

        if isinstance(string, list):
            sys.stderr.write('Usage error: Use extract_seeds for lists of strings.')

        sys.exit("Error: Argument 'string' must be a single string")

    # Regex to capture seed
    seed_regx = re.compile(r'.*(?P<seed>Seed\d{0,3}).*')

    match = seed_regx.search(string)

    # Add the captured named group ('seed') to the seeds list
    seed = None
    if match is not None:
            seed = match.group('seed')

    return seed

# Given a list of strings this method searches through the contents and extracts
# any string with a 'SeedXXX' in it and stores this in a list of results that are
# returned. If a 'SeedXXX' is not found in the string nothing is added to the list.
def extract_seeds(strings):
    # Parameter handling
    if not isinstance(strings, list):
        # If string then turn into a list with the string in it
        if isinstance(strings, str):
            sys.stderr.write('Usage error: Use extract_seed for a single string.')

        sys.exit("Error: Argument 'strings' must be a list of strings.")

    seeds = list()
    for string in strings:
        seed = extract_seed(string)

        if seed is not None:
            seeds.append(seed)

    return seeds

# Given a directory this method searches through the contents and extracts
# any file name with a 'SeedXXX' in it and stores this in a list which is
# returned.
def extract_dirSeeds(dir):
    if not os.path.isdir(dir):
        sys.exit("Error: {} is not a valid directory. Exiting.".format(dir))

    # Run through the directory and extract the seed value for each file
    seed_regx = re.compile(r'.*(?P<seed>Seed\d{0,3}).*') # Regex to capture seed

    # Gather the contents of the directory into a list
    files = os.listdir(dir)

    # Extract the SeedXXX from each file in the list
    seeds = extract_seeds(files)

    return seeds

"""
Converts an h5 file, or list or dict of h5 files to
a python dictionary object.
    - If a file name is given then a base level dictionary
        will be returned
    - If a list is given then the SeedXXX value from the file
        names will be used to key each file as would be in the
        previous case
    - If a dict is given the then keys for each file name will
        be used as the key for the dictionary
"""
def h5todict(h5files):

    # If the argument is a string convert to list
    if isinstance(h5files, str):
        h5files = [h5files]

    keys = list()
    # If the argument is a dictionary take the keys out
    # and use the items as the h5files
    if isinstance(h5files, dict):
        keys = list(h5files.keys())

        # Check if each val is a string (realistically it could be a list or dict
        # but we would have to recurse on this function itself)
        for val in h5files.values():
            if not isinstance(val, str):
                sys.exit("Error: Each value of the dictionary should be a string.")

        h5files = list(h5files.values())
    else:
        keys = extract_seeds(h5files)


    # Check the size of h5files and keys (they must be the same)
    if len(h5files) != len(keys):
        sys.exit("Error: The number of files and the keys found or given must be the same.")


    h5dict = dict()
    for h5file, key in zip(h5files, keys):
        h5fdict = dict()

        # Open the h5 file and store the contents into a dictionary for the h5 file
        with h5.File(h5file, 'r') as h5f:
            for name, h5_obj in h5f.items():

                # Recurse on Groups
                if isinstance(h5_obj, h5.Group):
                    h5fdict.update({name: _h5grp2dct(h5_obj)})
                # Update on Datasets
                elif isinstance(h5_obj, h5.Dataset):
                    ds = np.array(h5_obj.get(name))
                    h5fdict.update({name:ds})

        # Update the master dictionary with the h5 files dictionary
        h5dict.update({key: h5fdict})

    return h5dict

# Helper function for recrusion to be called from h5todct
def _h5grp2dct(h5grp_obj):
    h5dict = dict()

    for name, h5_obj in h5grp_obj.items():
        if isinstance(h5_obj, h5.Group):
            h5grp2dct(h5grp_obj)
        elif isinstance(h5_obj, h5.Dataset):
            ds = np.array(h5grp_obj.get(name))
            h5dict.update({name:ds})

    return h5dict

"""
Processes all the data for the list of h5/pitch seed values
or the entire h5/pitch angle directory.
    h5_seeds [default: entire h5_dir]:
        A list of seed values (i.e. ['100', '110'])

    pitch_seeds [default: entire pitch_angle_dir]:
        A list of seed values (i.e. ['100', '110'])

    pitch_angle_dir [default: "./data/pitch_angles/"]
        A string directory path the pitch angle directory

    h5_dir [default: "./data/processed_eggs/hdf5/"]
        A string directory path to h5 directory

    test [default: False]
        A boolean to decide whether or not to run the method
        test_event_processing on the files found during processing.

    Returns: (seeds, files, data)
        seeds: A list of seed values processed from the two directories
        files: A list of tuples of (h5_files, pitch_files) processed from the two directories
        data: A dictionary result from calling h5todict on the h5_files used
"""
def process_files(h5_seeds=None, pitch_seeds=None, pitch_angle_dir=None, h5_dir=None, test=False):
    # Set all the parameter values

    # Use the default directories
    if pitch_angle_dir is None:
        pitch_angle_dir = "./data/pitch_angles"

    if h5_dir is None:
        h5_dir = "./data/processed_eggs/hdf5"

    # Check assumptions for the given files (assumes directories are given rather than seeds)
    # Any and all herecy is punished with removal from the directory!
    check_assumptions(hdf5_dir=h5_dir, pitch_dir=pitch_angle_dir)

    if h5_seeds is None:
        h5_seeds = extract_dirSeeds(h5_dir)

    if pitch_seeds is None:
        pitch_seeds = extract_dirSeeds(pitch_angle_dir)

    print('Processing files in {} and {}'.format(h5_dir, pitch_angle_dir))


    # Construct a list of seed values found ONLY in both directories
    seeds = list(set(h5_seeds + pitch_seeds))
    for pitch_seed in pitch_seeds:
        if pitch_seed not in h5_seeds:
            print("Warning: {} found in {}, but not found {}".format(pitch_seed, pitch_angle_dir, h5_dir))

            if pitch_seed in seeds:
                print("Error: {} found in seeds.".format(pitch_seed))

    # Construct a list of tuples called files to store the h5 and pitch files
    # which will be used to generate the data
    files = list()
    for seed in seeds:
        h5_fmt = os.path.join(h5_dir, "{}.h5".format(seed))
        pitch_angl_fmt = os.path.join(pitch_angle_dir, "pitchangles_{}.txt".format(seed))

        files.append((h5_fmt, pitch_angl_fmt))

    h5_files = [file[0] for file in files]
    pitch_files = [file[1] for file in files]

    # Test the Katydid processing
    if test:
        test_event_processing(copy(pitch_files), copy(h5_files))

    # Generate the unfiltered data from the h5_files
    data = h5todict(h5_files)

    # Add the pitch angle data
    for pitch_file in pitch_files:
        pitch_seed = extract_seed(pitch_file)

        times, pitch_angles = get_pitch_data(pitch_file)

        data[pitch_seed].update({'pitch times': times, 'pitch angles': pitch_angles})

    # Filter the data with standard filters (i.e. time matching). One can add custom
    # filters or filter the data at any point using the method filter_data and creating
    # an appropriate filter method
    data = filter_data(data)

    return (seeds, files, data)

"""
Filters the data dictionary given by the list of methods provided.
    data: A dictionary of data created using h5todict() method
    filters: A list of function that operate on the data dictionary
        and return an updated data dictionary without altering the
        original data found in the dictionary.

        Note: All functions should only take the data dictionary
        as a parameter and should return an updated dictionary.
        The updated dictionary should be keyed however the user
        designates in their filter functions, but standard syntax
        will be to use the lowest level unfiltered key and append
        an '_' to the end of if.
"""
def filter_data(data, filters=None):

    # Default filters
    if filters is None:
        filters = [filter_times]

    for filter in filters:
        data = filter(data)

    return data

def filter_times(data):

    # Highest level of data dict is always SeedXXX keys
    seeds = data.keys();
    for seed in seeds:
        # Get the current seeds data
        seed_data = data[seed]

        # Get the relevant time information from the h5 section of the data
        group = "candidates"
        dataset = "candidates_0"
        h5_candidates_0 = seed_data[group][dataset]

        egg_time_name = "StartTimeInAcq"
        egg_times = h5_candidates_0[egg_time_name] # Create function to fetch data safely

        # Get the pitch times
        pitch_times = seed_data['pitch times']

        # Get the matched indices for the data
        egg_indices, pitch_indices = compare_times(egg_times, pitch_times)

        # Filter the data and update the dictionary to only have values at the appropriate
        # egg and pitch indices
        filtered_extension = "_"

        # All pitch angle data should be filtered by pitch indices
        items = list(seed_data.items())
        for key, item in items:
            if key == 'pitch times' or key == 'pitch angles':
                new_key = key + filtered_extension
                seed_data[new_key] = [item[p] for p in pitch_indices]

        # All hdf5 data should be filtered by egg indices
        # Note: This only filters data in data hierarchy:
        #       ... > candidates > candidates_0 > ...
        #       Also note, that hdf5_data is a np.ndarray object, not a dictionary

        # Get all the names of data in the np.ndarray object
        dt = h5_candidates_0.dtype
        names = dt.names
        shape = h5_candidates_0.shape

        # Copy the attributes of the unfiltered ndarray
        dt_fltrd = deepcopy(dt)
        shape_fltrd = (len(egg_indices),)

        # Rename the names
        dt_fltrd.names = [name + filtered_extension for name in dt_fltrd.names]
        names_fltrd = dt_fltrd.names

        # Instantiate a zeroed ndarry for filtered data
        filtered_ndarray = np.zeros(shape_fltrd, dt_fltrd)

        # Populate the filtered ndarray
        for name, new_name in zip(names, names_fltrd):
            values = h5_candidates_0[name]
            filtered_ndarray[new_name] = [values[e] for e in egg_indices]

        # In case one wishes to see the new time data
        # print(filtered_ndarray[egg_time_name + '_'])
        # print(seed_data['pitch times_'])

        # Rename the dataset and update the seed_data with the filtered array
        new_dataset = dataset + filtered_extension
        seed_data[group][new_dataset] = filtered_ndarray

        # Update the data with the new seed data
        data.update({seed: seed_data})

    return data

# Given any file name (pitch angle, root, or hdf5) extract the seed
# and remove or label the corresponding files in the other directories
#
# i.e.) Given Seed100.h5, Seed100.txt and Seed100.root would be removed
# or labeled.
def punish_invalid_files(file, remove=True, label=False):
    home_dir = "/Users/josh_swerdlow/Documents/College/Senior_Year/First_Semester/thesis/classifier"

    hdf5_dir = os.path.join(home_dir, "data/processed_eggs/hdf5")
    root_dir = os.path.join(home_dir, "data/processed_eggs/root")
    pitch_dir = os.path.join(home_dir, "data/pitch_angles")

    file_type = None

    if file.endswith(".h5"):
        file_type = "h5"
    elif file.endswith(".root"):
        file_type = "root"
    elif file.endswith(".txt"):
        file_type = "pitch"
    else:
        sys.stderr.write("Error: File must be .h5, .root, or .txt not '{}'.\n".format(file))
        sys.exit("Could not punish the invalid file for its herecy.")

    seed = extract_seed(file)

    # Make sure we received a seed
    if seed is None:
        sys.stderr.write("Error: Could not find seed in '{}'.\n".format(file))
        sys.exit()


    # Use the seed to construct the pitch file, root file, or hdf5 file
    hdf5_file = os.path.join(hdf5_dir, "{}.h5".format(seed))
    root_file = os.path.join(root_dir, "{}.root".format(seed))
    pitch_file = os.path.join(pitch_dir, "pitchangles_{}.txt".format(seed))

    if file_type == "h5":
        hdf5_file = file
    elif file_type == "root":
        root_file = file
    elif file_type == "pitch":
        pitch_file = file

    # Punish the files
    if remove:
        print("Removing files with '{}' for crimes against my thesis.\n".format(seed))
        os.remove(hdf5_file)
        os.remove(root_file)
        os.remove(pitch_file)
    elif label:
        print("Label is currently not implented, sorry!")
    #     os.rename(hdf5_file, dst)
    #     os.rename(root_file, dst)
    #     os.rename(pitch_file, dst)
    else:
        sys.stderr.write("Removal and Label are false and no punishments will be brought down on the heretic files.\n")
        sys.exit()

# Ensures any assumptions made through the analysis process
# do not propogate through the data
def check_assumptions(hdf5_dir=None, root_dir=None, pitch_dir=None):
    home_dir = "/Users/josh_swerdlow/Documents/College/Senior_Year/First_Semester/thesis/classifier"

    if hdf5_dir is None:
        hdf5_dir = os.path.join(home_dir, "data/processed_eggs/hdf5")

    if root_dir is None:
        root_dir = os.path.join(home_dir, "data/processed_eggs/root")

    if pitch_dir is None:
        pitch_dir = os.path.join(home_dir, "data/pitch_angles")

    # C H E C K  H D F 5  F I L E S
    hdf5_files = [os.path.join(hdf5_dir, fn) for fn in os.listdir(hdf5_dir)]

    for hdf5_file in hdf5_files:
        if not validate_hdf5(hdf5_file):
            punish_invalid_files(hdf5_file, remove=True)


    # C H E C K  R O O T  F I L E S

    # C H E C K  P I T C H  A N G L E  F I L E S

# Validate an hdf5 file to ensure it has the necessary data hierarchy
# and the necessary variables
def validate_hdf5(hf):

    group1 = "candidates"
    dataset1 = "candidates_0"
    variables1 = ['StartTimeInAcq'] # Add more as appropriate

    group2 = "candidate_tracks"
    dataset2 = "candidate_tracks_0"
    variables2 = ['StartTimeInAcq'] # Add more as appropriate

    # Populate iterators
    groups = [group1, group2]
    datasets = [dataset1, dataset2]
    variables = [variables1, variables2]

    # Iterate through the data hierarchy to check for all the variables
    # If this fails anywhere break and return False else return True
    valid = True
    for grp, ds, var in zip(groups, datasets, variables):
        data = fetch_variables_hdf5(hf, grp, ds, var)

        if data == -1:
            valid = False
            break

    return valid

if __name__ == "__main__":
    # check_assumptions()
    seeds, files, data = process_files(test=True)