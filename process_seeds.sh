#!/bin/bash

# Usage: ./process_seeds.sh <beg_seed_val> <end_seed_val>

if [[ ${1} = "help" ]]; then
    echo "Usage: ./process_seeds.sh <beg_seed_val> <end_seed_val>"
    echo "beg seed val: First seed value"
    echo "end seed val: Last seed value\n"
    echo "Processes all egg files in the given range using Katydid."
    exit 0
fi

beg_seed_val=${1}
end_seed_val=${2}

if [[ ${beg_seed_val} -gt ${end_seed_val} ]]; then
    echo "Error: Begining seed value must be greater than end seed value!"
    echo "./process_seeds.sh help -- for help."
    exit 0
fi

# Initiate an empty array for seed values
declare -a seed_vals=()

# Populate the seed value given the boundaries
for (( seed_val = ${beg_seed_val}; seed_val <= ${end_seed_val}; seed_val++ )); do
    seed_vals+=(${seed_val})
done


# Process all the seed values
echo "Processing Seeds: ${seed_vals[@]}"
./process.sh ${seed_vals[@]}