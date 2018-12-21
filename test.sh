#!/bin/bash

seed_vals=${@:-*}

declare -a seeds=()
for seed_val in ${seed_vals}; do
    seed="Seed${seed_val}"
    seeds+=(${seed})
done

echo ${seeds[@]}
