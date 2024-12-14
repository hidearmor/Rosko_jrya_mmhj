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

FILE="results_cache_p"

# Check if the results file already exists
if [ -f "$FILE" ]; then
	rm -f $FILE
    echo "File '$FILE' exists. Removing..."
else
    echo "File '$FILE' does not exist."
fi

echo "algo,p,sp,M,K,N,sppattern,rosko-time,ntrials,L3_factor,L3_size" >> $FILE

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
	n=8192
	ps=(4 5 6 7 14 30 50 75 100 125 150 175 200 300)
	measure="mm" # options: all, packing, mm

elif [ "$person" == "jrya" ]; then

    echo "Running as jrya - Setting specific experiment parameters for jrya computer"
    
	declare -i trials=15
	declare -i warmups=10
	n=8192
	ps=(6 7 14 30 50 75 100 125 150 175 200 300)
	measure="mm" # options: all, packing, mm

else

    echo "Running as another user - Applying general settings"
	
	declare -i trials=2
	declare -i warmups=1
	n=2000
	ps=(6 7 14 30 50 75 100 125 150 175 200 300)
	measure="mm" # options: all, packing, mm

fi

hyperthreading=$($ROSKO_HOME/thesis_utils/hyperthreading.sh)
sparsity_patterns=("random-uniform" "diagonal" "row-pattern" "column-pattern") # options: random-uniform, diagonal, row-pattern, column-pattern
num_sparsity_patterns=${#sparsity_patterns[@]}
L3_factors=(0.1 0.175 0.25 0.5 0.75 1.0 1.1 1.25 1.5 1.75 2.0)
sparsity_values=(90)
num_L3_factors=${#L3_factors[@]}
num_ps=${#ps[@]}
num_sparsity_values=${#sparsity_values[@]} # the number of sparsity values used in this experiment


for sp in ${sparsity_values[@]};
do
	for p in ${ps[@]};
	do
		for sparsity_pattern in ${sparsity_patterns[@]};
		do
			for L3_factor in ${L3_factors[@]}
			do
				# echo $n $p $sp $sparsity_pattern $L3_factor
				./rosko_sgemm_test 	$n $n $n $p $sp $trials $warmups $sparsity_pattern rosko $FILE $L3_factor
			done
		done
	done
done	



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

plot_type="p"

cp $FILE $path$time$unscr$FILE$unscr$measure$nameHype

# python3 plots_cache_3D.py $num_sparsity_patterns ${sparsity_patterns[@]} $num_sparsity_values ${sparsity_values[@]} $num_ps ${ps[@]} $n $n 1 $FILE $nameHype $num_L3_factors ${L3_factors[@]} $plot_type

commit_hash=$(git rev-parse HEAD)
logName="commit_hash"
echo "$commit_hash" > $path$time$unscr$logName$unscr$FILE$nameHype

#####################