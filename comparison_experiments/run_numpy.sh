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

# x=$PWD
# sudo cp mkl_sparse_gemm.cpp /opt/intel/oneapi/mkl/2021.1.1/examples/sycl/spblas
# cd /opt/intel/oneapi/mkl/2021.1.1/examples/sycl
# make sointel64 examples="spblas/mkl_sparse_gemm" sycl_devices=cpu
# cp _results/intel64_so_tbb/spblas/mkl_sparse_gemm.out $x
# cd $x



make;

# filename="results" #Mayas imp

# check if results exists and if it does, move it
FILE="results_comp_numpy"

# Check if the results file already exists
if [ -f "$FILE" ]; then
	rm -f $FILE
    echo "File '$FILE' exists. Removing..."
else
    echo "File '$FILE' does not exist."
fi


echo "algo,p,sp,M,K,N,time,ntrials" >> $FILE

declare -i trials=10
declare -i warmups=10
declare -i n=5000
declare -i cores=10
type="random" # options: random, diagonal

# algo might not be a relevenat parameter

# for sp in 70 75 80 85 90 95 98 99;
for sp in 60 70 80 90 95 98 99;
do
	./rosko_sgemm_test 	$n $n $n $cores $sp $trials $warmups rosko $FILE
	python3 numscipy_mm.py $n $n $n $cores $sp $trials $warmups $type python_sparse $FILE
	python3 numscipy_mm.py $n $n $n $cores $sp $trials $warmups $type python_dense $FILE
done

# exit 0 # exit without errors

### PLOTS PART ####

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