#!/bin/bash

x=$PWD
cd ../CAKE_on_CPU;
source env.sh;
cd ..;
source env.sh;
cd $x;

echo $ROSKO_HOME;
echo $CAKE_HOME;

# Check if the "person" argument is provided
if [ -z "$1" ]; then
    echo "Error: No argument provided. Please specify who is running the experiment (e.g., mmhj or jrya)."
    exit 1  # Exit the script if no argument is provided
fi

# Set the "person" variable based on the first argument
person=$1

FILE="results_p_extensive"

n_start=512
# n_end=4096
n_end=2560
n_step=512
# ps=(1 2 3 4 5 6 7 8 9 10 15 20 35 40 45 50 60 70 80 90 100) # maya base
# ps=(4 5 6 7 8 9 10 15 20 35 40 45 50 60 70 80 90 100) # maya
ps=(4 5 6 7 8 9 10 15 20 35 40) # maya
# ps=(6 10 14 20 40 43 46 50 75 100 125 150 175 200)
# ps=(1 2 3 4 5 6 10 14 20 40 43 46 50 75 100 125 150 175 200) # jonas base
num_ps=${#ps[@]}
# sparsity_values=(20 30 40 50 60 70 80 85 90 95 97 98 99 99.9) # jonas base
# sparsity_values=(50 60 70 85 95 97 98 99 99.9) # maya base
sparsity_values=(85 95 97 98 99 99.9) # maya
# sparsity_values=(50 60 70) # maya
num_sparsity_values=${#sparsity_values[@]} # the number of sparsity values used in this experiment
measure="mm" # options: all, packing, mm
sparsity_patterns=("random-uniform" "diagonal" "row-pattern" "column-pattern") # options: random-uniform, diagonal, row-pattern, column-pattern
num_sparsity_patterns=${#sparsity_patterns[@]}

hyperthreading=$($ROSKO_HOME/thesis_utils/hyperthreading.sh)


### PLOTS PART ####
# exit 0 # exit without plots and files errors

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

python3 plots_p_extensive.py $num_sparsity_patterns ${sparsity_patterns[@]} $num_sparsity_values ${sparsity_values[@]} $num_ps ${ps[@]} $n_start $n_end $n_step $FILE $nameHype


#####################