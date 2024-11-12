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

FILE="results_p"

# Check if the results file already exists
if [ -f "$FILE" ]; then
	rm -f $FILE
    echo "File '$FILE' exists. Removing..."
else
    echo "File '$FILE' does not exist."
fi

echo "algo,p,sp,N,rosko-time,outer-time,ntrials, measured" >> $FILE

# hyperthreading=$($ROSKO_HOME/thesis_utils/hyperthreading.sh)
hyperthreading="yesHype"
person=$1 # argument for who is doing dis
declare -i trials=15
declare -i warmups=5
declare -i n=4000
type="random" # options: random_csr, random_arr, diagonal

# not sure if this one makes any difference
# export GOMP_CPU_AFFINITY="0 1 2 3 4 5 6 7 8 9";

for measure in all packing mm;
do
	for p in 1 2 3 4 5 6 10 14 20 40 50 75 100 125 150 175 200 225 250 275 300 350 600 1000 10000;
	# for p in 225 230 235 240 245 250 255 260 265 270;
	# for p in 100000;
	do
		./rosko_sgemm_test 	$n $n $n $p 80 $trials $warmups rosko $FILE $measure
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

cp $FILE $path$time$unscr$FILE$unscr$type$nameHype

# python3 plots.py

commit_hash=$(git rev-parse HEAD)
logName="commit_hash"
echo "$commit_hash" > $path$time$unscr$logName$unscr$FILE$nameHype

#####################