import sys
import time

import numpy as np
import scipy as scipy

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

def SparseDenseMM(N, d, type):
    dense_matrix = np.random.rand(N,N)

    rng = np.random.default_rng()
    sparse_matrix = None
    if type == 'diagonal':
        diags, d = diagonals_with_density(N, d)
        data = rng.random((len(diags), N))
        sparse_matrix = scipy.sparse.dia_array((data, diags), shape=(N, N))
    elif type == 'random_csr':
        sparse_matrix = scipy.sparse.random_array((N, N), density=d, random_state=rng, format = 'csr')
    elif type == 'random_arr':
        sparse_matrix = scipy.sparse.random_array((N, N), density=d, random_state=rng, format = 'csr').toarray()
    else: return -1.0, -1.0

    start = time.perf_counter()
    result = sparse_matrix @ dense_matrix
    end = time.perf_counter()

    return  end-start, result

def DenseMM(M, N, K):
    matrix_A = np.random.rand(M,K)
    matrix_B = np.random.rand(K,N)

    start = time.perf_counter()
    result = matrix_A @ matrix_B
    end = time.perf_counter()

    return  end-start, result

def main(N, M, K, p, sp_raw, trials, warmups, type, algo, filename):
    sp = float(sp_raw)/100
    if type=='diagonal':
        _, sp = diagonals_with_density(N, (1.0-sp))
    d = 1.0-sp
    res_total = 0.0

    if type == 'row-pattern':
        M_temp = round((1.0 - sp) * M)
        sp = 1.0 - (M_temp / M)
        M = M_temp
    # MAYA: We should use a combo of algo and type to determine what type of data
    # should be run on which algorithm, instead of using type alone to indicate that.
    # Doing that, we won't need the type names: dense, random_csr, random_arr
    for i in range(warmups):
        (type == 'dense' or type == 'row-pattern') if DenseMM(M, N, K) else SparseDenseMM(N, d, type)

    for i in range(trials):
        res_part = 0.0
        if type == 'dense' or type == 'row-pattern':
            res_part, _ = DenseMM(M, N, K)
        else:
            res_part, _ = SparseDenseMM(N, d, type)
        res_total += res_part
    
    avg = round(res_total / trials, 6)
    file = open(filename, 'a')
    sp_print = round(sp*100, 2)
    print(f'{algo},{p},{sp_print},{M},{K},{N},{avg},{trials}')
    file.write(f'{algo},{p},{sp_print},{M},{K},{N},{avg},{trials}')
    file.write('\n')

if __name__ == "__main__":
    if len(sys.argv) != 11: # first argument is path for this script
        print("Format b like dis: numscipy_mm.py N sp trials warmups type filename")
        sys.exit(1)
    _, N, M, K, p, sp, trials, warmups, type, algo, filename = sys.argv
    main(int(N), int(M), int(K), int(p), float(sp), int(trials), int(warmups), type, algo, filename)

# np.random.rand(3,2) https://numpy.org/doc/stable/reference/random/generated/numpy.random.rand.html
# scipy https://docs.scipy.org/doc/scipy/reference/sparse.html#
# scipy random matrix density, random   distribution: https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.random.html#scipy.sparse.random
# scipy random matrix density, uniform  distribution: https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.rand.html#scipy.sparse.rand
# schipy same but array format: https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.random_array.html#scipy.sparse.random_array