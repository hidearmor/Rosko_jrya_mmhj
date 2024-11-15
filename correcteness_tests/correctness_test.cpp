#include "rosko.h"
#include "cnpy.h"
#include <string>
#include <stdlib.h>
#include <stdio.h>
#include <cstring>

// need to install this package: cnpy
// python file conversion part written with help from chat GPT
// https://github.com/rogersce/cnpy?tab=readme-ov-file
// note: make install step in instructions should be called in sudo mode

void save_matrix_to_npy(const std::string& filename, float* matrix, unsigned long rows, unsigned long cols) {
    cnpy::npy_save(filename, matrix, {rows, cols}, "w");
}

void call_python_script(const std::string& A_filename, const std::string& B_filename, const std::string& C_filename) {
    std::string command = "python3 matmul_correctness.py " + A_filename + " " + B_filename + " " + C_filename;
    int status = system(command.c_str());
    if (status != 0) {
        std::cerr << "Python script failed!" << std::endl;
        exit(1);
    }
}

void python(float* A, float* B, float* C, int M, int N, int K) {
    save_matrix_to_npy("A.npy", A, M, K);
    save_matrix_to_npy("B.npy", B, K, N);

    call_python_script("A.npy", "B.npy", "C.npy");

    // Load the result matrix C into the existing C buffer
    cnpy::NpyArray arr = cnpy::npy_load("C.npy");
    if (arr.shape.size() == 0) {
        std::cerr << "Failed to load matrix C from C.npy!" << std::endl;
        exit(1);
    }

    float* data = arr.data<float>();

    // Copy data from the loaded result into the original C buffer
    std::memcpy(C, data, M * N * sizeof(float));
}


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

void manual_test(int M, int N, int K, int p, int alg, std::string sp_pattern, float sp, float actual_sp) {
    
    printf("\nn = %d, p = %d, sp = %f, sp_pattern: %s\n", N, p, sp, sp_pattern.c_str());

    // Variables to hold matrices A and B
    float* A = nullptr;
    float* B = nullptr;

    // Initialize the matrices
    initialize_matrices(A, B, M, K, N, sp, sp_pattern, actual_sp);

    float* C_rosko = (float*) calloc(M * N , sizeof( float ));
    float* C_naive = (float*) calloc(M * N , sizeof( float ));
    float* C_naive_copy = (float*) calloc(M * N , sizeof( float ));
    float* C_numpy = (float*) calloc(M * N , sizeof( float ));

    // Calculate the density
    sp = actual_sp *100.0;
    float density = (100.0 - actual_sp * 100.0) / 100.0;

    // naive(A, B, C_naive, M, N, K);
    rosko(A, B, C_rosko, M, N, K, density, p, alg);
    python(A, B, C_numpy, M, N, K);
    naive(A, B, C_naive, M, N, K);
    naive(A, B, C_naive_copy, M, N, K);

    // standard tests
    printf("\nstright up rosko naive, CORRECT; same input\n");
    mat_equals_thesis(C_rosko, C_naive, M, N);

    printf("\nCORRECT; same input, naive naive\n");
    mat_equals_thesis(C_naive_copy, C_naive, M, N);

    printf("\nCORRECT; same input, naive numpy\n");
    mat_equals_thesis(C_naive, C_numpy, M, N);
    printf("\nCORRECT; same input, rosko numpy\n");
    mat_equals_thesis(C_rosko, C_numpy, M, N);


    // // Wrongness tests
    float* A_2 = nullptr;
    float* B_2 = nullptr;
    initialize_matrices(A_2, B_2, M, K, N, sp, sp_pattern, actual_sp);
    float* C_naive2 = (float*) calloc(M * N , sizeof( float ));
    float* C_rosko2 = (float*) calloc(M * N , sizeof( float ));
    float* C_numpy2 = (float*) calloc(M * N , sizeof( float ));
    naive(A_2, B_2, C_naive2, M, N, K);
    rosko(A_2, B_2, C_rosko2, M, N, K, density, p, alg);
    python(A_2, B_2, C_numpy2, M, N, K);

    printf("\nWRONG; different input, naive naive2\n");
    mat_equals_thesis(C_naive, C_naive2, M, N);

    printf("\nWRONG; different input, rosko & naive2 2\n");
    mat_equals_thesis(C_rosko, C_naive2, M, N);
 
    printf("\nWRONG; different input, rosko & rosko2 2\n");
    mat_equals_thesis(C_rosko, C_rosko2, M, N);
 
    printf("\nWRONG; different input, numpy & numpy2 2\n");
    mat_equals_thesis(C_numpy, C_numpy2, M, N);
 
    printf("\nCORRECT; same input, rosko2 & numpy2\n");
    mat_equals_thesis(C_rosko2, C_numpy2, M, N);
 
    free(A_2);
    free(B_2);
    free(C_naive2);
    free(C_rosko2);
    free(C_numpy2);


    // Clean up allocated memory from standard
    free(A);
    free(B);
    free(C_rosko);
    free(C_naive);
    free(C_naive_copy);
    free(C_numpy);
}

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

    manual_test(M, N, K, p, alg, sp_pattern, sp, actual_sp);

    return 0;
}