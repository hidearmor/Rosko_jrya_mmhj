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
declare -i maxDims=10000
sparsity_patterns=("random-uniform" "row-pattern" "column-pattern" "diagonal")
p_values=(1, 6, 40, 200)
sparsity_values=(0 60 70 80 90 95 98 99 99.9)
# sparsity_patterns=("row-pattern")
# p_values=(6)
# sparsity_values=(50)

for pattern in ${sparsity_patterns[@]}
do
    for p in ${p_values[@]}
    do
        for sp in ${sparsity_values[@]}
        do
            ./correctness_test $maxDims $pattern $p $sp
        done
    done
done

echo "Only showing shapes and errors, so if no errors, all passed!"