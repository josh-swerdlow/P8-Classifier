#!/bin/sh

# Usage: ./move_egg.sh <local_dir> [seed_val(s)]
# Moves processed egg files from the respective directory on Wright to a local directory
# using scp repeatedly.

if [[ ${1} = "help" ]]; then
    echo "Usage ./move_pitch_angle.sh <local_dir> [seeds]"
    echo "local_dir: A path to a local directory"
    echo "seeds: seed values to be moved"
    exit 0
fi

WRIGHT_ACCOUNT="jswerdlow@wright.physics.yale.edu" # account on Wright
METHOD="scp"
NUMB_ARGS=${#}

# Create the local directory to recv the files
RECV_DIR=${1}

# If the local directory doesn't exit use the default
if [[ ! -d  "${RECV_DIR}" ]]; then
    RECV_DIR="~/Documents/College/Senior_Year/thesis/classifier/data/pitch_angles"
fi

# The remote hdf5/root file dir
hdf5_dir="/home/jswerdlow/classifier/data/processed_eggs/hdf5"

for seed_val in "${@:2:${NUMB_ARGS}}"; do
    seed="Seed${seed_val}"
    hdf5_file="${seed}.h5"

    # scp hdf5/root file from wright to local dir
    ${METHOD} ${WRIGHT_ACCOUNT}:${hdf5_dir}/${hdf5_file} ${RECV_DIR}/
done
