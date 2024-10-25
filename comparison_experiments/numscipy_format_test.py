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

def diagonals_with_density(N, d):
    nnz = int(d * (N * N))
    nnz_exact = 0
    acc1 = 0
    acc2 = N
    counter = 2
    num_diagonals = 1

    while(acc2 < nnz):
        acc1 = acc2
        acc2 += 2*(N-counter)
        counter += 2
        num_diagonals += 2

    if acc2-nnz <= nnz-acc1:
        nnz_exact = acc2
    else: 
        num_diagonals += -2
        nnz_exact = acc1

    # Ensure the number of diagonals does not exceed the matrix size
    if num_diagonals > 2 * (N - 1) + 1:
        num_diagonals = 2 * (N - 1) + 1  # Max number of diagonals is 2N-1

    half_diags = (num_diagonals - 1) // 2
    diags = list(range(-half_diags, half_diags + 1))

    exact_density = nnz_exact / (N * N)
    return diags, exact_density

    # missing warmup runs
def SparseDenseMM(N, d_org, format):
    diags, d = diagonals_with_density(N, d_org)    
    dense_matrix = np.random.rand(N,N)

    rng = np.random.default_rng()
    sparse_matrix = None
    if format == 'dia':
        data = rng.random((len(diags), N))
        sparse_matrix = sp.sparse.dia_array((data, diags), shape=(N, N))
    else:
        sparse_matrix = sp.sparse.random_array((N, N), density=d, random_state=rng, format = format)

    start = time.time()
    result = sparse_matrix @ dense_matrix
    end = time.time()

    return  end-start

formats = ['csr', 'bsr', 'coo', 'csc', 'dia']
formats = ['csr', 'dia']
densities = [0.01, 0.05, 0.1, 0.2, 0.3, 0.5]
headliner = 'format, N, density, time, runs, diagonals'
file = open('format_horse_race.txt', 'a')
file.write(headliner)
print(headliner)
for d in densities:
    for format in formats:
        res = 0
        runs = 4
        N = 4096
        N = 2048
        # d = 0.08
        diags, dens = diagonals_with_density(N, d)
        for i in range(0, runs):
            SparseDenseMM(N, d, format)
        for i in range(0, runs):
            res += SparseDenseMM(N, d, format)
        result = format + ', ' + str(N) + ', ' + str(round(dens, 2)) + ', ' + str(round((res/(runs)), 7)) + ', ' + str(runs) + ', ' + str(len(diags))
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