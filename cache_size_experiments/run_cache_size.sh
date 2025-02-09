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

# check if results exists and if it does, move it
FILE="results_cache_sizes"

# Check if the results file already exists
if [ -f "$FILE" ]; then
	rm -f $FILE
    echo "File '$FILE' exists. Removing..."
else
    echo "File '$FILE' does not exist."
fi


echo "algo,p,sp,M,K,N,sppattern,time,ntrials,L3_size" >> $FILE

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
    
	declare -i trials=30
	declare -i warmups=10
	# declare -i n=4096
	# declare -i n=5120
	declare -i n=6144
	declare -i cores=4

elif [ "$person" == "jrya" ]; then

    echo "Running as jrya - Setting specific experiment parameters for jrya computer"
    
	declare -i trials=2
	declare -i warmups=1
	# declare -i trials=30
	# declare -i warmups=10
	declare -i n=8192
	declare -i cores=6
	# Rosko's measured L3: 25165824

else

    echo "Running as another user - Applying general settings"
	
	declare -i trials=1
	declare -i warmups=1
	declare -i n=512
	declare -i cores=1

fi


hyperthreading=$($ROSKO_HOME/thesis_utils/hyperthreading.sh)
algorithms=("rosko")  # options: rosko, naive, numpy_csr, numpy_arr, numpy_dia, numpy_dense
num_algorithms=${#algorithms[@]} # the number of algorithms used in this experiment
sparsity_pattern="random-uniform"  # options: random-uniform, diagonal, row-pattern, column-pattern
sparsity_values=(90)  # Define sparsity values as an array
# sparsity_values=(60 70 80 90 95 98 99 99.5 99.7 99.9)  # Define sparsity values as an array
num_sparsity_values=${#sparsity_values[@]} # the number of sparsity values used in this experiment
L3_factors=(0.1 0.25 0.5 1.0 1.1 1.5 2.0)
num_L3_factors=${#L3_factors[@]}


for sp in ${sparsity_values[@]};
do
	for L3_factor in ${L3_factors[@]}
	do
		./rosko_sgemm_test 	$n $n $n $cores $sp $trials $warmups $sparsity_pattern rosko $FILE $L3_factor
	done
done

exit 0 # exit without errors

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

cp $FILE $path$time$unscr$FILE$unscr$sparsity_pattern$nameHype

# Call the python plot script with inputs
python3 plots_cache_sizes.py $sparsity_pattern $num_algorithms ${algorithms[@]} $num_sparsity_values ${sparsity_values[@]} $FILE $nameHype $num_L3_factors $L3_factors

commit_hash=$(git rev-parse HEAD)
logName="commit_hash"
echo "$commit_hash" > $path$time$unscr$logName$unscr$FILE$nameHype

#####################