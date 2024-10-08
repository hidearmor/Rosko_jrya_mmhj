import os
import sys
import datetime

import numpy as np
from scipy.sparse import csr_matrix

########## BABY VERSION ################

# Define a dense matrix (3x3)
dense_matrix = np.array([[1, 2, 3],
                         [4, 5, 6],
                         [7, 8, 9]])

# Define a sparse matrix in CSR format (3x3)
# Only non-zero elements will be stored.
sparse_matrix = csr_matrix([[1, 0, 0],
                            [0, 0, 2],
                            [3, 0, 0]])

# Perform sparse-dense matrix multiplication
result = sparse_matrix.dot(dense_matrix)

# Display the result
print("Sparse Matrix:\n", sparse_matrix.toarray())  # Converts sparse to dense to display
print("\nDense Matrix:\n", dense_matrix)
print("\nResult of Sparse x Dense Multiplication:\n", result)

########################################

def SparseDenseMM(M, K, N, sp):
    # 2. build random sparse matrix A with sparsity sp
    # 3. build random dense matrix B
    # 4. (maybe) convert to correct formats
    # 5. if warmup: start time
    # 6. perform multiplications 
    # 7. if warmup: end time and return it
    return 0

def main(M, K, N, sp, ntrials, filename):
    warmups = 10
    for i in range(warmups):
        SparseDenseMM(M, K, N, sp)
    
    res = 0.0
    for i in range(ntrials):
        res += SparseDenseMM(M, K, N, sp)
    
    # run loop warmup many times
    # run loop ntrials many times
    # calculate avg
    # print to results_comp file
    
if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Format b like dis: numscipy_mm.py M K N s, ntrials filename")
        sys.exit(1)
    
    M = sys.argv[1]
    K = sys.argv[2]
    N = sys.argv[3]
    sp = sys.argv[4]
    ntrials = sys.argv[5]
    filename = sys.argv[6]
    main(M, K, N, sp, ntrials, filename)


# np.random.rand(3,2) https://numpy.org/doc/stable/reference/random/generated/numpy.random.rand.html
# scipy https://docs.scipy.org/doc/scipy/reference/sparse.html#
# scipy random matrix density, random   distribution: https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.random.html#scipy.sparse.random
# scipy random matrix density, uniform  distribution: https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.rand.html#scipy.sparse.rand