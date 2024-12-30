import sys
import time

import numpy as np
import scipy as scipy

DEBUG = False


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


def generateMatricesAB(M, N, K, sp, algo, sp_pattern):
    
    matrix_B = np.random.rand(K,N).astype(np.float32) # dense matrix 
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
        matrix_A = scipy.sparse.dia_array((data, diags), shape=(M, K), dtype=np.float32)
        
    elif sp_pattern == 'row-pattern':
        M_nz_rows = round(d * M)
        sp = 1.0 - (M_nz_rows / M)
        if algo == 'numpy_dense':
            matrix_A = np.random.rand(M_nz_rows, K).astype(np.float32)
        else:
            # make a sparse row pattern MxK matrix
            pass
            
        
    elif sp_pattern == 'random-uniform':
        matrix_A = scipy.sparse.random_array((N, N), density=d, random_state=rng, format = 'csr', dtype=np.float32)
        if algo == 'numpy_arr':
            matrix_A = matrix_A.toarray()
    else:
        print(sp_pattern + " is not a valid sparsity pattern")
        sys.exit()
    
    return matrix_A, matrix_B, sp

def mat_bit(matrix):
    """
    Checks the bit-width of the data type of elements in a NumPy matrix.
    Returns a string describing the data type and bit-width.
    """
    # Get the data type of the matrix
    dtype = matrix.dtype
    
    # Check the kind of the data type
    if np.issubdtype(dtype, np.integer):
        data_type = "Integer"
    elif np.issubdtype(dtype, np.floating):
        data_type = "Floating point"
    elif np.issubdtype(dtype, np.complexfloating):
        data_type = "Complex floating point"
    else:
        data_type = "Unknown or unsupported type"
    
    # Get the number of bits (itemsize gives bytes, so multiply by 8)
    bit_width = dtype.itemsize * 8

    return f"{data_type} ({bit_width}-bit)"

def printIt(algo, patter):
    N = 20
    M = N
    K = N
    sp = 0.8

    matrix_A, matrix_B, sp = generateMatricesAB(M, N, K, sp, algo, patter)
    result = matrix_A @ matrix_B

    print()
    print(algo + ' & ' + patter)
    print('A ' + mat_bit(matrix_A))
    print('B ' + mat_bit(matrix_B))
    print('C ' + mat_bit(result))

printIt('numpy_csr','random-uniform')
printIt('numpy_arr','random-uniform')
printIt('numpy_dia','diagonal')
# printIt('numpy_dense','column-pattern')
printIt('numpy_dense','row-pattern')
