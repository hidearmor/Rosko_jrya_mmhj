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
sparsity_patterns=("random-uniform" "row-pattern" "column-pattern" "diagonal")
p_values=(6, 40, 200)
sparsity_values=(0 30 60 90 99.9 100)
# sparsity_patterns=("row-pattern")
# p_values=(6)
# sparsity_values=(50)

for pattern in ${sparsity_patterns[@]}
do
    for p in ${p_values[@]}
    do
        for sp in ${sparsity_values[@]}
        do
            echo "running for: pattern ${pattern} p ${p} sp ${sp}"
            ./correctness_test $maxDims $pattern $p $sp
        done
    done
done

echo "Only showing shapes and errors, so if no errors, all passed!"