#!/bin/sh

# Usage: ./move.sh <method> <file_type>

if [[ ${1} = "help" ]]; then
    echo "Usage ./move.sh <data_type> <method>"
    echo "data_type: 'hdf5' or 'root'"
    echo "method: 'scp' or default to rsync"
    exit 0
fi

DATA_TYPE=${1} # hdf5 or root
METHOD=${2:-rsync} # either scp or rsync by default
seed="153"

# Creat the local directory to recv the files
HOME_DIR="/Users/josh_swerdlow/Documents/College/Senior_Year/First_Semester/thesis/classifier"
EGG_RECV_DIR="${HOME_DIR}/data/processed_eggs/${DATA_TYPE}"
PITCH_RECV_DIR="${HOME_DIR}/data/pitch_angles"

# Construct the remote egg file path
egg_file="locust_mc_Seed${seed}_LO25.3106G.egg"
EGG_DIR="/projects/p8/Phase1Sim/${egg_file}"

# Construct the remote pitch file path
pitch_file="pitchangles_Seed${seed}"
PITCH_DIR="/projects/p8/${pitch_file}"

WRIGHT_ACCOUNT="jswerdlow@wright.physics.yale.edu" # account on Wright

if [[ ${DATA_TYPE} = "hdf5" ]]; then
    echo "Moving all hdf5 files from ${EGG_DIR} to ${EGG_RECV_DIR}.\n"
elif [[ ${DATA_TYPE} = "root" ]]; then
    echo "Moving all root files from ${EGG_DIR} to ${EGG_RECV_DIR}.\n"
else
    echo "Error: Incorrect file type must be 'hdf5' or 'root' not '${DATA_TYPE}'!"
    exit 0
fi

if [[ ${METHOD} = "scp" ]]; then
    scp ${WRIGHT_ACCOUNT}:${EGG_DIR}/ ${EGG_RECV_DIR}/ # && makes sure this command runs successfully before executing the next
else
    # -r: recursive; -P: progress and partial; --remove-source-files: removes source files only if entire operation is successful
    # rsync --remove-source-files -rP ${LOCAL_DIR}/*.$DATA_TYPE ${WRIGHT_ACCOUNT}:$DESTINATION_DIR
    rsync ${WRIGHT_ACCOUNT}:${EGG_DIR}/ ${EGG_RECV_DIR}/
    # rsync ${WRIGHT_ACCOUNT}:${PITCH_DIR} ${PITCH_RECV_DIR}
fi
