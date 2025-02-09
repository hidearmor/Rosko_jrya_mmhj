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

FILE="results_p_extensive"

# Check if the results file already exists
if [ -f "$FILE" ]; then
	rm -f $FILE
    echo "File '$FILE' exists. Removing..."
else
    echo "File '$FILE' does not exist."
fi

echo "algo,p,sp,M,K,N,sppattern,rosko-time,outer-time,ntrials,measure" >> $FILE

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
    
	declare -i trials=10
	declare -i warmups=5
	n_start=512
	n_end=2560
	n_step=512
	ps=(1 2 3 4 5 6 7 8 9 10 15 20 35 40 45 50 60 70 80 90 100)
	num_ps=${#ps[@]}
	sparsity_values=(50 60 70 85 95 97 98 99 99.9)
	num_sparsity_values=${#sparsity_values[@]} # the number of sparsity values used in this experiment
	measure="mm" # options: all, packing, mm

elif [ "$person" == "jrya" ]; then

    echo "Running as jrya - Setting specific experiment parameters for jrya computer"
    
	declare -i trials=30
	declare -i warmups=10
	n_start=512
	n_end=8192
	n_step=512
	ps=(1 2 3 4 5 6 10 14 20 40 43 46 50 75 100 125 150 175 200)
	num_ps=${#ps[@]}
	sparsity_values=(20 30 40 50 60 70 80 85 90 95 97 98 99 99.9)
	num_sparsity_values=${#sparsity_values[@]} # the number of sparsity values used in this experiment
	measure="mm" # options: all, packing, mm

else

    echo "Running as another user - Applying general settings"
	
	declare -i trials=1
	declare -i warmups=1
	n_start=512
	n_end=1536
	n_step=512
	ps=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20)
	num_ps=${#ps[@]}
	sparsity_values=(20 30 40 50 60 70 80 85 90 95 97 98 99)
	num_sparsity_values=${#sparsity_values[@]} # the number of sparsity values used in this experiment
	measure="mm" # options: all, packing, mm

fi

hyperthreading=$($ROSKO_HOME/thesis_utils/hyperthreading.sh)
sparsity_patterns=("random-uniform" "diagonal" "row-pattern" "column-pattern") # options: random-uniform, diagonal, row-pattern, column-pattern
num_sparsity_patterns=${#sparsity_patterns[@]}


for (( n=$n_start; n<=$n_end; n+=$n_step ));
do
	for sp in ${sparsity_values[@]};
	do
		for p in ${ps[@]};
		do
			for sparsity_pattern in ${sparsity_patterns[@]};
			do
				./rosko_sgemm_test $n $n $n $p $sp $trials $warmups $sparsity_pattern rosko $FILE $measure
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

cp $FILE $path$time$unscr$FILE$unscr$measure$nameHype

python3 plots_p_extensive.py $num_sparsity_patterns ${sparsity_patterns[@]} $num_sparsity_values ${sparsity_values[@]} $num_ps ${ps[@]} $n_start $n_end $n_step $FILE $nameHype

commit_hash=$(git rev-parse HEAD)
logName="commit_hash"
echo "$commit_hash" > $path$time$unscr$logName$unscr$FILE$nameHype

#####################