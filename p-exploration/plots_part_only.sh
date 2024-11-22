#!/bin/bash

x=$PWD
cd ../CAKE_on_CPU;
source env.sh;
cd ..;
source env.sh;
cd $x;

echo $ROSKO_HOME;
echo $CAKE_HOME;

# Set the "person" variable based on the first argument
person=$1
FILE="results_p_extensive"
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

cp $FILE $path$time$unscr$FILE$unscr$measure$nameHype

python3 plots_p_extensive.py $num_sparsity_patterns ${sparsity_patterns[@]} $num_sparsity_values ${sparsity_values[@]} $num_ps ${ps[@]} $n_start $n_end $n_step $FILE $nameHype

commit_hash=$(git rev-parse HEAD)
logName="commit_hash"
echo "$commit_hash" > $path$time$unscr$logName$unscr$FILE$nameHype

#####################