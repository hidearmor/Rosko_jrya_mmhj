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

# Experiment parameters setup
declare -i trials=2
declare -i warmups=1
declare -i n=256
declare -i cores=4
# declare -i trials=10
# declare -i warmups=10
# declare -i n=5000
# declare -i cores=10
num_algorithms=3 # the number of algorithms used in this experiment
algorithms=("rosko" "numpy_csr" "numpy_arr")  # options: rosko, naive, numpy_csr, numpy_arr, numpy_dia, numpy_dense
sparsity_pattern="random-uniform"  # options: random-uniform, diagonal, row-pattern, column-pattern
num_sparsity_values=7 # the number of sparsity values used in this experiment
sparsity_values=(60 70 80 90 95 98 99)  # Define sparsity values as an array
# sparsity_values=(99 99.5 99.8 99.9)


# for sp in 70 75 80 85 90 95 98 99;
# for sp in 60 70 80 90 95 98 99;
for sp in ${sparsity_values[@]};
do
	./rosko_sgemm_test 	$n $n $n $cores $sp $trials $warmups $sparsity_pattern rosko $FILE
	python3 numscipy_mm_test.py $n $n $n $cores $sp $trials $warmups $sparsity_pattern numpy_csr $FILE
	python3 numscipy_mm_test.py $n $n $n $cores $sp $trials $warmups $sparsity_pattern numpy_arr $FILE

	# python3 numscipy_mm.py $n $n $n $cores $sp $trials $warmups random_csr numpy_csr $FILE
	# python3 numscipy_mm.py $n $n $n $cores $sp $trials $warmups random_arr numpy_arr $FILE
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

cp $FILE $path$time$underscore$FILE$underscore$sparsity_pattern

# Call the python plot script with inputs
python3 plots_comp.py $sparsity_pattern $num_algorithms ${algorithms[@]} $num_sparsity_values ${sparsity_values[@]} $FILE

commit_hash=$(git rev-parse HEAD)
logName="commit_hash.txt"
echo "$commit_hash" > $path$time$underscore$logName$underscore$FILE

#####################