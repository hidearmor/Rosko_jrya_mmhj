#!/bin/bash

x=$PWD
cd ../CAKE_on_CPU;
source env.sh;
cd ..;
source env.sh;
cd $x;

echo $ROSKO_HOME;
echo $CAKE_HOME;

make clean;
make;

# Set the "person" variable based on the first argument
person=$1

# variables
declare -i maxDims=8000
p_values=(6 40 100)
sparsity_values=(0 60 90 100)
sparsity_patterns=("random-uniform" "row-pattern" "column-pattern" "diagonal")
L3_factors=(0.1 0.5 1.0 1.5 2.0 10.0 22.0)

for pattern in ${sparsity_patterns[@]}
do
    for p in ${p_values[@]}
    do
        for sp in ${sparsity_values[@]}
        do
            for L3_factor in ${L3_factors[@]}
            do
                echo "running for: pattern ${pattern} p ${p} sp ${sp} L3_factor ${L3_factor}"
                ./correctness_test_cache $maxDims $pattern $p $sp $L3_factor
            done
        done
    done
done

echo "Only showing shapes and errors, so if no errors, all passed!"