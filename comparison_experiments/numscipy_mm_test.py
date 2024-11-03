import sys
import time

import numpy as np
import scipy as scipy

DEBUG = False

def print_matrices(sparse_matrix, dense_matrix, result, algo):
    if algo == 'numpy_arr' or algo == 'numpy_dense':
             print("Sparse Matrix:\n", sparse_matrix.round(2))  # Converts sparse to dense to display
    else:
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

def numpyMM(matrix_A, matrix_B):
   
    start = time.perf_counter()
    result = matrix_A @ matrix_B
    end = time.perf_counter()

    return  end-start, result

def generateMatricesAB(M, N, K, sp, algo, sp_pattern):
    
    matrix_B = np.random.rand(K,N) # dense matrix 
    matrix_A = None # sparse matrix
    
    d = 1.0-sp
    rng = np.random.default_rng()
     
    if sp_pattern=='diagonal': # diagonal sparisty pattern only allows square NxN matrix
        if M != K:
            print(sp_pattern + " sparsity pattern only works on square matrices, i.e M is equal to K")
            sys.exit()
        diags, d = diagonals_with_density(M, d) 
        sp = 1.0-d
        data = rng.random((len(diags), M))
        matrix_A = scipy.sparse.dia_array((data, diags), shape=(M, K))
        
    elif sp_pattern == 'row-pattern':
        M_nz_rows = round(d * M)
        sp = 1.0 - (M_nz_rows / M)
        if algo == 'numpy_dense':
            matrix_A = np.random.rand(M_nz_rows, K)
        else:
            # make a sparse row pattern MxK matrix
            pass
            
    
    # DOES NOT WORK - dimensions af matrices in MM don't align    
    # elif sp_pattern == 'column-pattern':
    #     K_nz_cols = round(d * K)
    #     sp = 1.0 - (K_nz_cols / K)
    #     matrix_A = np.random.rand(M, K_nz_cols)
        
    elif sp_pattern == 'random-uniform':
        matrix_A = scipy.sparse.random_array((N, N), density=d, random_state=rng, format = 'csr')
        if algo == 'numpy_arr':
            matrix_A = matrix_A.toarray()
    else:
        print(sp_pattern + " is not a valid sparsity pattern")
        sys.exit()
    
    return matrix_A, matrix_B, sp


def main(N, M, K, p, sp_raw, trials, warmups, sp_pattern, algo, filename):
    
    # Allow only below combinations of sparsity pattern and algorithm, otherwise, it breaks the code
    if  not \
        ((algo == 'numpy_csr' and sp_pattern == 'random-uniform') or \
        (algo == 'numpy_arr' and sp_pattern == 'random-uniform') or \
        (algo == 'numpy_dia' and sp_pattern == 'diagonal') or \
        # (algo == 'numpy_dense' and sp_pattern == 'column-pattern') or \
        (algo == 'numpy_dense' and sp_pattern == 'row-pattern')):

        print("The combination of algorithm " + algo + " and sparsity pattern " + sp_pattern + " is not valid")
        sys.exit()
       
    sp = float(sp_raw)/100
    matrix_A, matrix_B, sp = generateMatricesAB(M, N, K, sp, algo, sp_pattern)
   
    res_total = 0.0
    result = None
    
    for i in range(warmups):
        _, result = numpyMM(matrix_A, matrix_B)

    for i in range(trials):
        res_part = 0.0
        res_part, result_matrix = numpyMM(matrix_A, matrix_B)
        if DEBUG: print_matrices(matrix_A, matrix_B, result_matrix, algo)
        res_total += res_part
    
    avg = round(res_total / trials, 6)
    file = open(filename, 'a')
    sp_print = round(sp*100, 2)
    print(f'{algo},{p},{sp_print},{M},{K},{N},{avg},{trials}')
    file.write(f'{algo},{p},{sp_print},{M},{K},{N},{avg},{trials}')
    file.write('\n')

if __name__ == "__main__":
    if DEBUG: print(sys.argv, len(sys.argv))
    if len(sys.argv) != 11: # first argument is path for this script
        print("Format like dis: numscipy_mm_test.py N M K p sp trials warmups sp_pattern algo filename")
        sys.exit(1)
    _, N, M, K, p, sp, trials, warmups, sp_pattern, algo, filename = sys.argv
    main(int(N), int(M), int(K), int(p), float(sp), int(trials), int(warmups), sp_pattern, algo, filename)

# np.random.rand(3,2) https://numpy.org/doc/stable/reference/random/generated/numpy.random.rand.html
# scipy https://docs.scipy.org/doc/scipy/reference/sparse.html#
# scipy random matrix density, random   distribution: https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.random.html#scipy.sparse.random
# scipy random matrix density, uniform  distribution: https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.rand.html#scipy.sparse.rand
# schipy same but array format: https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.random_array.html#scipy.sparse.random_array