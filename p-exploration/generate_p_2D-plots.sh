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
FILE="results_p_extensive"

# Check if the "person" argument is provided
if [ -z "$1" ]; then
    echo "Error: No argument provided. Please specify who is running the experiment (e.g., mmhj or jrya)."
    exit 1  # Exit the script if no argument is provided
fi

# Set the "person" variable based on the first argument
person=$1

# Perform different actions based on the value of "person"
if [ "$person" == "mmhj" ]; then

    echo "Running as mmhj - Setting specific experiment parameters for mmhj computer"

	declare -i trials=15
	declare -i warmups=10
	declare -i n=4096
	ps=(4 5 6 7 8 9 10 12 14 16 18 20 25 30 35 40 50 75 100 125 150 175 200 300)
	num_ps=${#ps[@]}
	sparsity_values=(60 70 80 85 90 95 97 98 99 99.9)
	num_sparsity_values=${#sparsity_values[@]} # the number of sparsity values used in this experiment
	measure="mm" # options: all, packing, mm

elif [ "$person" == "jrya" ]; then

    echo "Running as jrya - Setting specific experiment parameters for jrya computer"

	declare -i trials=15
	declare -i warmups=10
	declare -i n=8192
	# ps=(6 7 8 9 10 12 14 16 18 20 25 30 35 40 50 75 100 125 150 175 200 300) # full range
	ps=(6 7 20 50 100)
	num_ps=${#ps[@]}
	sparsity_values=(60 70 80 85 90 95 97 98 99 99.9) # full range
	# sparsity_values=(90 95 97 98 99 99.9)
	# sparsity_values=(60 70 80 85 90 95 97 98 99)
	num_sparsity_values=${#sparsity_values[@]} # the number of sparsity values used in this experiment
	measure="mm" # options: all, packing, mm

else

    echo "Running as another user - Applying general settings"

	declare -i trials=1
	declare -i warmups=1
	declare -i n=500
	ps=(4 5 6 7 8 9 10 12 14 16 18 20 25 30 35 40 50 75 100 125 150 175 200 300)
	num_ps=${#ps[@]}
	sparsity_values=(60 70 80 85 90 95 97 98 99 99.9)
	num_sparsity_values=${#sparsity_values[@]} # the number of sparsity values used in this experiment
	measure="mm" # options: all, packing, mm

fi


hyperthreading=$($ROSKO_HOME/thesis_utils/hyperthreading.sh)
sparsity_pattern="random-uniform"  # options: random-uniform, diagonal, row-pattern, column-pattern

algorithms="rosko"
num_algorithms=${#algorithms[@]}  # the number of algorithms used in this experiment


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

# Call the python plot script with inputs
python3 plots_p_2D.py $sparsity_pattern $num_algorithms ${algorithms[@]} $num_sparsity_values ${sparsity_values[@]} $FILE $nameHype $num_ps ${ps[@]}

#####################