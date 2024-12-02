#!/bin/bash

x=$PWD
cd ../CAKE_on_CPU;
source env.sh;
cd ..;
source env.sh;
cd $x;

echo $ROSKO_HOME;
echo $CAKE_HOME;

# check if results exists and if it does, move it
FILE="results_numpy"
# FILE="results_comp_numpy"

# Experiment parameters setup
# hyperthreading=$($ROSKO_HOME/thesis_utils/hyperthreading.sh)
hyperthreading=noHype
person=$1 # argument for who is doing dis

declare -i trials=30
declare -i warmups=10
declare -i n=4192
declare -i cores=6
algorithms=("numpy_csr")  # options: rosko, naive, numpy_csr, numpy_arr, numpy_dia, numpy_dense
num_algorithms=${#algorithms[@]} # the number of algorithms used in this experiment
sparsity_pattern="random-uniform"  # options: random-uniform, diagonal, row-pattern, column-pattern
sparsity_values=(60 70 80 90 95 98 99)  # Define sparsity values as an array
num_sparsity_values=${#sparsity_values[@]} # the number of sparsity values used in this experiment

# exit 0 # exit without errors

### PLOTS PART ####

PYTHON_SCRIPT_PATH="$ROSKO_HOME/plotslib/plot_utils.py"
FUNCTION_NAME="getPlotsDirectory"
cwd=$PWD
# Call the Python script with the function name as an argument
output=$(python3 "$PYTHON_SCRIPT_PATH" "$FUNCTION_NAME" "$cwd")

# Read the output values
path=$(echo "$output" | sed -n '1p')
time=$(echo "$output" | sed -n '2p')
unscr="_"
nameHype=$unscr$hyperthreading$unscr$person

# cp $FILE $path$time$unscr$FILE$unscr$sparsity_pattern$nameHype

# Call the python plot script with inputs
echo "calling python"
# python3 plots_comp.py $sparsity_pattern $num_algorithms ${algorithms[@]} $num_sparsity_values ${sparsity_values[@]} $FILE $nameHype
python3 plots_bits.py $sparsity_pattern $num_algorithms ${algorithms[@]} $num_sparsity_values ${sparsity_values[@]} $FILE $nameHype

# commit_hash=$(git rev-parse HEAD)
# logName="commit_hash"
# echo "$commit_hash" > $path$time$unscr$logName$unscr$FILE$nameHype

#####################