#include "rosko.h"
// #include "cnpy.h"
#include <string>
#include <stdlib.h>
#include <stdio.h>

// void save_matrix_to_npy(const std::string& filename, float* matrix, int rows, int cols) {
//     cnpy::npy_save(filename, matrix, {rows, cols}, "w");
// }

void rosko(float* A, float* B, float* C, int M, int N, int K, float density, int p, int alg) {
	cake_cntx_t* cake_cntx = cake_query_cntx();
    float ressss;
    float tttmp[18];
    int flushsz = 2*cake_cntx->L3 / sizeof(float);

    float* dirty = (float *) malloc(flushsz * sizeof(float));
    #pragma omp parallel for
    for (int dirt = 0; dirt < flushsz; dirt++){
        dirty[dirt] += dirt%100;
        tttmp[dirt%18] += dirty[dirt];
    }

    for(int ii =0; ii<18;ii++){
        ressss+= tttmp[ii];
    }

    rosko_sgemm(A, B, C, M, N, K, p, cake_cntx, density, NULL, 0, NULL, 0, 1, 0, KMN, alg);
    
    free(dirty);
}

void naive(float* A, float* B, float* C, int M, int N, int K) {
    for (int m = 0; m < M;  m++) {
        for (int n = 0; n < N; n++) {
            for (int k = 0; k < K; k++){
                C[m*N + n] += A[m*K + k] * B[k*N + n];
            }
        }
	}
}

// need to install this: sudo apt install libcnpy-dev
// need to install this: conda install conda-forge::libcnpy
// float* python() {

// }

int main(int argc, char** argv) {
    int M, K, N, p, alg;
    float sp, actual_sp;
    std::string sp_pattern;

    if (argc < 7) {
        printf("Usage: %s <M> <K> <N> <sparsity> <pattern>\n", argv[0]);
        return -1;
    }

    M = atoi(argv[1]);
    K = atoi(argv[2]);
    N = atoi(argv[3]);
    sp = atof(argv[4]);
    sp_pattern = std::string(argv[5]);
    p = atof(argv[6]);

    // Variables to hold matrices A and B
    float* A = nullptr;
    float* B = nullptr;

    // Initialize the matrices
    initialize_matrices(A, B, M, K, N, sp, sp_pattern, actual_sp);

    float* C_rosko = (float*) calloc(M * N , sizeof( float ));
    float* C_naive = (float*) calloc(M * N , sizeof( float ));
    float* C_numpy = (float*) calloc(M * N , sizeof( float ));

    // Calculate the density
    sp = actual_sp *100.0;
    float density = (100.0 - actual_sp * 100.0) / 100.0;

    naive(A, B, C_naive, M, N, K);
    rosko(A, B, C_rosko, M, N, K, density, p, alg);
    // numpy(A, B, C_numpy); // maybe other parameters

    mat_equals(C_rosko, C_naive, M, N);
    // mat_equals(C_numpy, C_naive, M, N);
    // Clean up allocated memory
    free(A);
    free(B);

    return 0;
}