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
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo " "
    echo "ERROR: No argument provided. Please specify who is running the experiment (e.g., mmhj or jrya)."
    echo "and the filename, like so: results_p_extensive"
    echo "and the directory path from rosko home like so: p-exploration"
    echo " "
    exit 1  # Exit the script if no argument is provided
fi

# Set the "person" variable based on the first argument
person=$1
FILE=$2
slash="/"
dir=$3
cwd=$ROSKO_HOME$slash$dir
hyperthreading=$($ROSKO_HOME/thesis_utils/hyperthreading.sh)

PYTHON_SCRIPT_PATH="$ROSKO_HOME/plotslib/plot_utils.py"
FUNCTION_NAME="getPlotsDirectory"
output=$(python3 "$PYTHON_SCRIPT_PATH" "$FUNCTION_NAME" "$cwd")

# Read the output values
path=$(echo "$output" | sed -n '1p')
time=$(echo "$output" | sed -n '2p')
unscr="_"
nameHype=$unscr$hyperthreading$unscr$person

cp $cwd$slash$FILE $path$time$unscr$FILE$unscr$measure$nameHype

commit_hash=$(git rev-parse HEAD)
logName="commit_hash"
echo "$commit_hash" > $path$time$unscr$logName$unscr$FILE$nameHype

#####################
