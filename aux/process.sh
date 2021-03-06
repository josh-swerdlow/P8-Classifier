#!/bin/bash

# Usage: ./process.sh <seed_val0> <seed_val1> ... <seed_valn>

if [[ ${1} = "help" ]]; then
    echo "Usage: ./process.sh <seed_val0> <seed_val1> ... <seed_valn>"
    echo "seed_val: A seed value to process"
    echo "Processes all egg files for the given seeds using Katydid and copy the initial pitch angles."
    exit 0
fi

katydid=/cmn/p8/katydid/cbuild/bin/Katydid
config=/home/jswerdlow/classifier/simulation_phase1_classify.yaml # Point to your config file

pitchangles=/home/jswerdlow/classifier/data/pitch_angles # A designated folder to store pitch angles

for seed_val in "$@"; do
	seed="Seed${seed_val}"

    egg=/projects/p8/Phase1Sim/locust_mc_${seed}_LO25.3106G.egg

    # Edit the output path for your directories
    h5out=/home/jswerdlow/classifier/data/processed_eggs/hdf5/${seed}.h5
    rootout=/home/jswerdlow/classifier/data/processed_eggs/root/${seed}.root

    angles=/projects/p8/Phase1Sim/pitchangles_${seed}.txt

    echo "                              S E E D ${seed_val}                              "
	${katydid} -c ${config} -e ${egg} --h5w.output-file=${h5out} --rootw.output-file=${rootout} > /dev/null

	cp ${angles} ${pitchangles}

    sleep 2s
done
