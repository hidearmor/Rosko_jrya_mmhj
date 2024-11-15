#!/bin/bash

x=$PWD
cd ../CAKE_on_CPU;
source env.sh;
cd ..;
source env.sh;
cd $x;

echo $ROSKO_HOME;
echo $CAKE_HOME;

# export GOMP_CPU_AFFINITY="0 1 2 3 4 5 6 7 8 9";
make clean;
make;

# Set the "person" variable based on the first argument
person=$1

hyperthreading=$($ROSKO_HOME/thesis_utils/hyperthreading.sh)

# Perform different actions based on the value of "person"
if [ "$person" == "mmhj" ]; then

    echo "Running as mmhj - Setting specific experiment parameters for mmhj computer"
    
	declare -i trials=10
	declare -i warmups=10
	declare -i n=2000
	declare -i cores=4

elif [ "$person" == "jrya" ]; then

    echo "Running as jrya - Setting specific experiment parameters for jrya computer"
    
	declare -i trials=10
	declare -i warmups=10
	declare -i n=1000
	declare -i cores=6

elif [ "$person" == "guest" ]; then

    echo "Running as jrya - Setting specific experiment parameters for jrya computer"
    
	declare -i trials=1
	declare -i warmups=1
	declare -i n=100
	declare -i cores=6

else
	$ROSKO_HOME/thesis_utils/wrong_user.sh
	exit 2;
fi

# algorithms=("rosko" "naive")  # options: rosko, naive, numpy_csr, numpy_arr, numpy_dia, numpy_dense
# num_algorithms=${#algorithms[@]} # the number of algorithms used in this experiment
sparsity_pattern="random-uniform"  # options: random-uniform, diagonal, row-pattern, column-pattern
sparsity_values=(60 70 80 90 95 98 99)  # Define sparsity values as an array
num_sparsity_values=${#sparsity_values[@]} # the number of sparsity values used in this experiment

./correctness_test $n $n $n 80 $sparsity_pattern $cores

exit 0; ## all below is old



# check if results exists and if it does, move it
FILE="results_corr"

# Check if the results file already exists
if [ -f "$FILE" ]; then
	rm -f $FILE
    echo "File '$FILE' exists. Removing..."
else
    echo "File '$FILE' does not exist."
fi

echo "algo,p,sp,M,K,N,sppattern,time,ntrials" >> $FILE

## RUN
# for sp in 70 75 80 85 90 95 98 99;
for sp in ${sparsity_values[@]};
do
	./rosko_sgemm_test 	$n $n $n $cores $sp $trials $warmups $sparsity_pattern rosko $FILE
	./naive_mm_test 	$n $n $n $sp $trials $warmups $sparsity_pattern naive $FILE
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
python3 plots_comp.py $sparsity_pattern $num_algorithms ${algorithms[@]} $num_sparsity_values ${sparsity_values[@]} $FILE $nameHype

commit_hash=$(git rev-parse HEAD)
logName="commit_hash"
echo "$commit_hash" > $path$time$unscr$logName$unscr$FILE$nameHype

#####################