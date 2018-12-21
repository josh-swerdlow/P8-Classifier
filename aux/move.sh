#!/bin/sh

# Usage: ./move.sh <seed_val(s)>

if [[ ${1} = "help" ]]; then
    echo "Usage ./move.sh [seed_val(s)]"
    echo "\tseed_val: Seed Values"
    exit 0
fi

# Creat the local directory to recv the files
CLASSIFIER="/Users/josh_swerdlow/Documents/College/Senior_Year/First_Semester/thesis/classifier"
HDF5_DIR="${CLASSIFIER}/data/processed_eggs/hdf5"
ROOT_DIR="${CLASSIFIER}/data/processed_eggs/root"
PITCH_DIR="${CLASSIFIER}/data/pitch_angles"

# All seed values given as command line arguments
seeds_vals=$@

# Move all relevant data
./move_pitch_angle.sh ${PITCH_DIR} ${seeds_vals}
./move_hdf5.sh ${HDF5_DIR} ${seeds_vals}
./move_root.sh ${ROOT_DIR} ${seeds_vals}