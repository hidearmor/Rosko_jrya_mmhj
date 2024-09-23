#!/bin/bash
x=$PWD
cd ../../../CAKE_on_CPU;
source env.sh;
cd ..;
source env.sh;
cd $x;

echo $ROSKO_HOME;
echo $CAKE_HOME;

# compile mkl_sparse gemm test with Intel MKL
# cd /opt/intel/oneapi/mkl/2021.1.1/examples/sycl
# make sointel64 examples="spblas/sparse_gemm" sycl_devices=cpu
# cp _results/intel64_so_tbb/spblas/sparse_gemm.out $x
# cd $x


# compile rosko
make;

# check if result_pack exists and if it does, move it
FILE="result_pack"

# Check if the result_pack file already exists
if [ -f "$FILE" ]; then
	rm -f $FILE
    echo "File '$FILE' exists. Removing..."
else
    echo "File '$FILE' does not exist."
fi

# result pack is created and gets headers
# echo "algo,store,M,K,N,sp,bw" >> result_pack
echo "algo,store,M,K,N,sp,bw,runs" >> result_pack

declare -i runs=10
echo "runs $runs"

# exit;

# for i in 80 82 85 87 90 92 95 97 99
for i in 80 87 95 # this one
# for i in 80 87
do
	for n in {256..10240..512} # this one
	# for n in {256..2533..512}
	do
		#  it uses only 1 core
		./rosko_sgemm_test $n $n 1 $i csr_file rosko_file 0 $runs;
		./rosko_sgemm_test $n $n 1 $i csr_file rosko_file 1 $runs;

	done
done

PYTHON_SCRIPT_PATH="$ROSKO_HOME/plotslib/plot_utils.py"
FUNCTION_NAME="getPlotsDirectory"
cwd=$PWD
# Call the Python script with the function name as an argument
output=$(python3 "$PYTHON_SCRIPT_PATH" "$FUNCTION_NAME" "$cwd")

# Read the output values
path=$(echo "$output" | sed -n '1p')
time=$(echo "$output" | sed -n '2p')
underscore="_"

cp $FILE $path$time$underscore$FILE
