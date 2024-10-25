import os
import sys
import datetime
import time

import numpy as np
import scipy as sp

def print_matrices(sparse_matrix, dense_matrix, result):
    print("Sparse Matrix:\n", sparse_matrix.toarray().round(2))  # Converts sparse to dense to display
    print("\nDense Matrix:\n", dense_matrix.round(2))
    print("\nResult of Sparse x Dense Multiplication:\n", result.round(2))

# does NOT work properly
def diagonals_with_density(N, d):
    # 1. Calculate the number of non-zero elements (nnz) based on the density
    total_elements = N * N
    nnz = int(d * total_elements)
    
    # 2. Estimate the number of diagonals
    # We want an uneven number of diagonals that is close to the nnz we need
    num_diagonals = 2 * (nnz // N) + 1  # Closest odd number of diagonals
    
    # Ensure the number of diagonals does not exceed the matrix size
    if num_diagonals > 2 * (N - 1) + 1:
        num_diagonals = 2 * (N - 1) + 1  # Max number of diagonals is 2N-1
    
    # 3. Create the diagonal list centered around 0 (evenly distributed)
    half_diags = (num_diagonals - 1) // 2
    diags = list(range(-half_diags, half_diags + 1))
    
    # 4. Calculate the exact number of non-zero values based on the diagonals
    nnz_exact = sum(N - abs(diag) for diag in diags)
    exact_density = nnz_exact / total_elements
    
    return diags, exact_density

# def SparseDenseMM(M, K, N, sp):
def SparseDenseMM(N, d_org, format):
    # 2. build random sparse matrix A with sparsity sp
    # 3. build random dense matrix B
    # 4. (maybe) convert to correct formats
    # 5. if warmup: start time
    # 6. perform multiplications
    # 7. if warmup: end time and return it

    diags, d = diagonals_with_density(N, d_org)
    print(d, d_org)
    
    dense_matrix = np.random.rand(N,N)

    rng = np.random.default_rng()
    sparse_matrix = None
    # sparse_matrix = sp.sparse.random(N, N, density=d, random_state=rng, format='csr')
    if format == 'dia':
        # diags = [0]
        data = rng.random((len(diags), N))
        sparse_matrix = sp.sparse.dia_array((data, diags), shape=(N, N))
    else:
        sparse_matrix = sp.sparse.random_array((N, N), density=d, random_state=rng, format = format)

    start = time.time()
    result = sparse_matrix @ dense_matrix
    end = time.time()

    # print(format + str(sparse_matrix.toarray().round(2)))
    return  end-start

# formats = ['csr']
formats = ['csr', 'bsr', 'coo', 'csc', 'dia']
file = open('format_horse_race.txt', 'a')
file.write('format, N, density, time, runs')
for format in formats:
    res = 0
    loops = 10
    N = 4096
    N = 100
    d = 0.3
    for i in range(0, loops):
        SparseDenseMM(N, d, format)
    for i in range(0, loops):
        res += SparseDenseMM(N, d, format)
    result = format + ', ' + str(N) + ', ' + str(d) + ', ' + str(round((res/(loops)), 7)) + ', ' + str(loops)
    file.write('\n')
    file.write(result)
    print(result)



# structure to link to experiments:

# def main(M, K, N, sp, ntrials, filename):
#     warmups = 10
#     for i in range(warmups):
#         SparseDenseMM(M, K, N, sp)
    
#     res = 0.0
#     for i in range(ntrials):
#         res += SparseDenseMM(M, K, N, sp)
    
#     # run loop warmup many times
#     # run loop ntrials many times
#     # calculate avg
#     # print to results_comp file
    
# if __name__ == "__main__":
#     if len(sys.argv) != 6:
#         print("Format b like dis: numscipy_mm.py M K N s, ntrials filename")
#         sys.exit(1)
    
#     M = sys.argv[1]
#     K = sys.argv[2]
#     N = sys.argv[3]
#     sp = sys.argv[4]
#     ntrials = sys.argv[5]
#     filename = sys.argv[6]
#     main(M, K, N, sp, ntrials, filename)


# np.random.rand(3,2) https://numpy.org/doc/stable/reference/random/generated/numpy.random.rand.html
# scipy https://docs.scipy.org/doc/scipy/reference/sparse.html#
# scipy random matrix density, random   distribution: https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.random.html#scipy.sparse.random
# scipy random matrix density, uniform  distribution: https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.rand.html#scipy.sparse.rand
# schipy same but array format: https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.random_array.html#scipy.sparse.random_array