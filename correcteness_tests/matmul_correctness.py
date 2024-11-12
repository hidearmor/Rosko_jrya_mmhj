import numpy as np
import sys

def numpyMM(matrix_A, matrix_B):
    return matrix_A @ matrix_B

def main(A_filename, B_filename, C_filename):
    # Load matrices A and B as float32 to match C++ float type
    matrix_A = np.load(A_filename).astype(np.float32)
    matrix_B = np.load(B_filename).astype(np.float32)

    # Perform matrix multiplication
    result = numpyMM(matrix_A, matrix_B)

    matrix_A = np.load(A_filename)
    matrix_B = np.load(B_filename)

    # Save the result with dtype float32
    np.save(C_filename, result.astype(np.float32))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python matrix_multiply.py <A.npy> <B.npy> <C.npy>")
        sys.exit(1)

    A_filename = sys.argv[1]
    B_filename = sys.argv[2]
    C_filename = sys.argv[3]
    main(A_filename, B_filename, C_filename)
