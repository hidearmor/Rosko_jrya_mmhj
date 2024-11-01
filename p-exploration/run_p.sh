#!/bin/bash

x=$PWD
cd ../CAKE_on_CPU;
source env.sh;
cd ..;
source env.sh;
cd $x;

echo $ROSKO_HOME;
echo $CAKE_HOME;

make;

FILE="results_p"

# Check if the results file already exists
if [ -f "$FILE" ]; then
	rm -f $FILE
    echo "File '$FILE' exists. Removing..."
else
    echo "File '$FILE' does not exist."
fi

echo "algo,p,sp,N,rosko-time,outer-time,ntrials, measured" >> $FILE

declare -i trials=10
declare -i warmups=5
declare -i n=6000
type="random" # options: random_csr, random_arr, diagonal

# not sure if this one makes any difference
# export GOMP_CPU_AFFINITY="0 1 2 3 4 5 6 7 8 9";

for measure in all packing mm;
do
	for p in 5 10 14 20 40 50 100 300 600 1000 10000;
	# for p in 5;
	# for p in 100000;
	do
		./rosko_sgemm_test 	$n $n $n $p 75 $trials $warmups rosko $FILE $measure
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
underscore="_"

cp $FILE $path$time$underscore$FILE$underscore$type

# python3 plots.py

commit_hash=$(git rev-parse HEAD)
logName="commit_hash.txt"
echo "$commit_hash" > $path$time$underscore$logName$underscore$FILE

#####################