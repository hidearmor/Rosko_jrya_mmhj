#include "rosko.h"
#include "cnpy.h"
#include <string>
#include <stdlib.h>
#include <stdio.h>
#include <cstring>
#include <vector>
#include <tuple>
#include <cmath>
#include <iostream>
#include <cstdlib>
#include <ctime>

// need to install this package: cnpy
// python file conversion part written with help from chat GPT
// https://github.com/rogersce/cnpy?tab=readme-ov-file
// note: make install step in instructions should be called in sudo mode
// then I've set this in my profile, (they are called in Makefil in this folder):
    // export CNPY_PATH=/usr/local/lib
    // export CNPY_INCLUDE_PATH=/usr/local/lib/include

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

float* numpy(float* A, float* B, int M, int N, int K) {
    float* C = (float*) calloc(M * N , sizeof( float ));
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
    return C;
}


float* rosko(float* A, float* B, int M, int N, int K, float density, int p, int alg) {
    float* C = (float*) calloc(M * N , sizeof( float ));
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
    return C;
}

float* naive(float* A, float* B, int M, int N, int K) {
    float* C = (float*) calloc(M * N , sizeof( float ));
    for (int m = 0; m < M;  m++) {
        for (int n = 0; n < N; n++) {
            for (int k = 0; k < K; k++){
                C[m*N + n] += A[m*K + k] * B[k*N + n];
            }
        }
	}
    return C;
}

using Triplet = std::tuple<int, int, int>;

std::vector<Triplet> generateShapes(int maxDimSize) {
    std::vector<Triplet> shapes;
    int minDimSize = 100;

    // Determine the number of shapes to generate (between 5 and 10)
    int numShapes = std::max(5, std::min(10, maxDimSize / minDimSize));

    // Generate evenly spaced values between minDimSize and maxDimSize
    int step = (maxDimSize - minDimSize) / numShapes;

    // Ensure step is at least 1 to avoid division by zero
    if (step < 1) step = 1;

    // Create a list of candidate sizes
    std::vector<int> sizes;
    for (int i = minDimSize; i <= maxDimSize; i += step) {
        sizes.push_back(i);
    }

    // Generate shapes using combinations of the candidate sizes
    for (int i = 0; i < numShapes; ++i) {
        int m = sizes[i % sizes.size()];
        int n = sizes[(i + 1) % sizes.size()];
        int k = sizes[(i + 2) % sizes.size()];

        // Alternate between square and non-square shapes
        if (i % 2 == 0) {
            m = n = k = sizes[i % sizes.size()];
        }

        shapes.emplace_back(m, n, k);
    }

    return shapes;
}

float* changeSingleElement(float* M, int size) {
    float* M_copy = (float*) malloc(size * sizeof(float));
    for (int i = 0; i < size; ++i) {
        M_copy[i] = M[i];
    }
    std::srand(std::time(nullptr));
    int randomIndex = std::rand() % size;
    M_copy[randomIndex] = 42.0f;

    return M_copy;
}

float* changeSingleRow(float* M, int rows, int cols) {
    float* M_copy = (float*) malloc(rows * cols * sizeof(float));
    for (int i = 0; i < rows * cols; ++i) {
        M_copy[i] = M[i];
    }
    std::srand(std::time(nullptr));
    int randomRow = std::rand() % rows;
    for (int j = 0; j < cols; ++j) {
        M_copy[randomRow * cols + j] = 42.0f;
    }

    return M_copy;
}

bool check_matrices_equal(float* C1, float* C2, int M, int N, const std::string& name1, const std::string& name2, std::string expected) {
    if (mat_equals_thesis(C1, C2, M, N) != 0) {
        std::cerr << "Error: Matrices " << name1 << " and " << name2 << " should be " << expected << std::endl;
        return false; // Error encountered, stop execution
    }
    return true;
}

void printSpecs(int M, int N, int K, float sp, std::string sp_pattern, int p) {
    printf("\nspecs: M %d, N %d,, K %d, sp %f, sp_pattern: %s, p %d\n", M, N, K, sp, sp_pattern.c_str(), p );
}

bool runAllTests(int M, int N, int K, float sp_init, std::string sp_pattern, int p)
{
    float actual_sp;
    int alg;
    bool result = 1;

    float* A1 = nullptr;
    float* B1 = nullptr;
    float* A1elem = nullptr;
    float* A1row = nullptr;
    float* A2 = nullptr;
    float* B2 = nullptr;

    initialize_matrices(A1, B1, M, K, N, sp_init, sp_pattern, actual_sp);
    initialize_matrices(A2, B2, M, K, N, sp_init, sp_pattern, actual_sp);

    int sizeA = M * K;
    A1elem = changeSingleElement(A1, sizeA);
    A1row = changeSingleRow(A1, M, K);

    float sp = actual_sp *100.0;
    float density = (100.0 - actual_sp * 100.0) / 100.0;
    
    float* C_1_rosko =       rosko(A1, B1, M, N, K, density, p, alg);
    float* C_1_numpy =       numpy(A1, B1, M, N, K);
    float* C_1_naive =       naive(A1, B1, M, N, K);
    
    float* C_1_rosko_copy =  rosko(A1, B1, M, N, K, density, p, alg);
    float* C_1_numpy_copy =  numpy(A1, B1, M, N, K);
    float* C_1_naive_copy =  naive(A1, B1, M, N, K);

    float* C_1row_rosko =    rosko(A1row, B1, M, N, K, density, p, alg);
    float* C_1row_numpy =    numpy(A1row, B1, M, N, K);
    float* C_1row_naive =    naive(A1row, B1, M, N, K);

    float* C_1elem_rosko =   rosko(A1elem, B1, M, N, K, density, p, alg);
    float* C_1elem_numpy =   numpy(A1elem, B1, M, N, K);
    float* C_1elem_naive =   naive(A1elem, B1, M, N, K);

    float* C_2_rosko =       rosko(A2, B2, M, N, K, density, p, alg);
    float* C_2_numpy =       numpy(A2, B2, M, N, K);
    float* C_2_naive =       naive(A2, B2, M, N, K);
    
    // to know where we are if it goes wrong
    printSpecs(M, N, K, sp, sp_pattern, p);

    // does it test with correct input?
    if (!check_matrices_equal(C_1_rosko, C_1_rosko, M, N, "C_1_rosko", "C_1_rosko", "identical")) return false;

    // Group 1: C_1_*
    if (!check_matrices_equal(C_1_rosko, C_1_numpy, M, N, "C_1_rosko", "C_1_numpy", "identical")) return false;
    if (!check_matrices_equal(C_1_rosko, C_1_naive, M, N, "C_1_rosko", "C_1_naive", "identical")) return false;
    if (!check_matrices_equal(C_1_numpy, C_1_naive, M, N, "C_1_numpy", "C_1_naive", "identical")) return false;

    // Group 2: Identical input, two processes
    if (!check_matrices_equal(C_1_rosko, C_1_rosko_copy, M, N, "C_1_rosko", "C_1_rosko_copy", "identical")) return false;
    if (!check_matrices_equal(C_1_numpy, C_1_numpy_copy, M, N, "C_1_numpy", "C_1_numpy_copy", "identical")) return false;
    if (!check_matrices_equal(C_1_naive, C_1_naive_copy, M, N, "C_1_naive", "C_1_naive_copy", "identical")) return false;

    // Group 5: C_2_*
    if (!check_matrices_equal(C_2_rosko, C_2_numpy, M, N, "C_2_rosko", "C_2_numpy", "identical")) return false;
    if (!check_matrices_equal(C_2_rosko, C_2_naive, M, N, "C_2_rosko", "C_2_naive", "identical")) return false;
    if (!check_matrices_equal(C_2_numpy, C_2_naive, M, N, "C_2_numpy", "C_2_naive", "identical")) return false;

    // // Group 3: change row, should be FALE
    // if (check_matrices_equal(C_1row_rosko, C_1_rosko, M, N, "C_1row_rosko", "C_1_rosko", "diffent")) return false;
    // if (check_matrices_equal(C_1row_naive, C_1_naive, M, N, "C_1row_naive", "C_1_naive", "diffent")) return false;
    // if (check_matrices_equal(C_1row_numpy, C_1_numpy, M, N, "C_1row_numpy", "C_1_numpy", "diffent")) return false;

    // // Group 4: changed element, should be diferent
    // if (check_matrices_equal(C_1elem_rosko, C_1_rosko, M, N, "C_1elem_rosko", "C_1_rosko", "different")) return false;
    // if (check_matrices_equal(C_1elem_naive, C_1_naive, M, N, "C_1elem_naive", "C_1_naive", "different")) return false;
    // if (check_matrices_equal(C_1elem_numpy, C_1_numpy, M, N, "C_1elem_numpy", "C_1_numpy", "different")) return false;

    // // Group 5: C_2_*
    // if (check_matrices_equal(C_2_rosko, C_1_numpy, M, N, "C_2_rosko", "C_1_numpy", "different")) return false;
    // if (check_matrices_equal(C_2_naive, C_1_rosko, M, N, "C_2_naive", "C_1_rosko", "different")) return false;
    // if (check_matrices_equal(C_2_numpy, C_1_naive, M, N, "C_2_numpy", "C_1_naive", "different")) return false;
    // if (check_matrices_equal(C_2_rosko, C_1_rosko, M, N, "C_2_rosko", "C_1_rosko", "different")) return false;
    // if (check_matrices_equal(C_2_naive, C_1_naive, M, N, "C_2_naive", "C_1_naive", "different")) return false;
    // if (check_matrices_equal(C_2_numpy, C_1_numpy, M, N, "C_2_numpy", "C_1_numpy", "different")) return false;

    free(A1);
    free(B1);
    free(A1elem);
    free(A1row);
    free(A2);
    free(B2);
    free(C_1_rosko);
    free(C_1_numpy);
    free(C_1_naive);
    free(C_1_rosko_copy);
    free(C_1_numpy_copy);
    free(C_1_naive_copy);
    free(C_1row_rosko);
    free(C_1row_numpy);
    free(C_1row_naive);
    free(C_1elem_rosko);
    free(C_1elem_numpy);
    free(C_1elem_naive);
    free(C_2_rosko);
    free(C_2_numpy);
    free(C_2_naive);

    return result;
}

void correctnessSuite(int maxDimSize)
{
    float sparsities[7] = {0.0f, 30.0f, 50.0f, 70.0f, 90.0f, 99.0f, 100.0f};
    // float sparsities[2] = {70.0f, 90.0f};
    // int pRange[5] = {1, 4, 6, 49, 231};
    int pRange[2] = {6, 49};
    std::string sp_patterns[1] = {"diagonal"};
    // std::string sp_patterns[1] = {"column-pattern"};
    // std::string sp_patterns[1] = {"row-pattern"};
    // std::string sp_patterns[1] = {"random-uniform"};
    // std::string sp_patterns[4] = {"random-uniform", "row-pattern", "column-pattern", "diagonal"};
    // std::string sp_patterns[3] = {"random-uniform", "row-pattern", "column-pattern"};
    // std::string sp_patterns[1] = {"column-pattern"};
    // std::string sp_patterns[1] = {"row-pattern"};
    std::vector<Triplet> shapes = generateShapes(maxDimSize);

    bool result = 1;

    for (const auto& [M, N, K] : shapes) {
        printf("\nm %d, n %d, k %d\n", M, N, K);
    }

    for (const auto& [M, N, K] : shapes) {
        for (const int& p : pRange) {
            for (const float& sp_init : sparsities) {
                for (const std::string sp_pattern : sp_patterns) {
                    // some of our matrix building can't handle 100% sparsity
                    if (
                        sp_init >= 100.0f &&
                        (sp_pattern == "diagonal"
                        || sp_pattern == "column-pattern"
                        || sp_pattern == "row-pattern")
                        ) continue;
                    result = runAllTests(M, N, K, sp_init, sp_pattern, p);
                    if (result = false) return;
                }
            }
        }
    }

    printf("\n\nTest succesful! No errors encountered!\n");
}

int main(int argc, char** argv) {
    if (argc < 2) {
        printf("Takes int maxDimensions as argument! \n");
        return -1;
    }
    int maxDims = atoi(argv[1]);
    correctnessSuite(maxDims);

    return 0;
}

// void manual_test(int M, int N, int K, int p, int alg, std::string sp_pattern, float sp, float actual_sp) {
    
//     printf("\nn = %d, p = %d, sp = %f, sp_pattern: %s\n", N, p, sp, sp_pattern.c_str());

//     // Variables to hold matrices A and B
//     float* A = nullptr;
//     float* B = nullptr;

//     // Initialize the matrices
//     initialize_matrices(A, B, M, K, N, sp, sp_pattern, actual_sp);

//     // Calculate the density
//     sp = actual_sp *100.0;
//     float density = (100.0 - actual_sp * 100.0) / 100.0;

//     float* C_rosko = rosko(A, B, M, N, K, density, p, alg);
//     float* C_naive = naive(A, B, M, N, K);
//     float* C_naive_copy = naive(A, B, M, N, K);
//     float* C_numpy = numpy(A, B, M, N, K);

//     // standard tests
//     printf("\nstright up rosko naive, CORRECT; same input\n");
//     mat_equals_thesis(C_rosko, C_naive, M, N);

//     printf("\nCORRECT; same input, naive naive\n");
//     mat_equals_thesis(C_naive_copy, C_naive, M, N);

//     printf("\nCORRECT; same input, naive numpy\n");
//     mat_equals_thesis(C_naive, C_numpy, M, N);
//     printf("\nCORRECT; same input, rosko numpy\n");
//     mat_equals_thesis(C_rosko, C_numpy, M, N);


//     // // Wrongness tests
//     float* A_2 = nullptr;
//     float* B_2 = nullptr;
//     initialize_matrices(A_2, B_2, M, K, N, sp, sp_pattern, actual_sp);
//     float* C_naive2 = naive(A_2, B_2, M, N, K);
//     float* C_rosko2 = rosko(A_2, B_2, M, N, K, density, p, alg);
//     float* C_numpy2 = numpy(A_2, B_2, M, N, K);
    
//     printf("\nWRONG; different input, naive naive2\n");
//     mat_equals_thesis(C_naive, C_naive2, M, N);

//     printf("\nWRONG; different input, rosko & naive2 2\n");
//     mat_equals_thesis(C_rosko, C_naive2, M, N);
 
//     printf("\nWRONG; different input, rosko & rosko2 2\n");
//     mat_equals_thesis(C_rosko, C_rosko2, M, N);
 
//     printf("\nWRONG; different input, numpy & numpy2 2\n");
//     mat_equals_thesis(C_numpy, C_numpy2, M, N);
 
//     printf("\nCORRECT; same input, rosko2 & numpy2\n");
//     mat_equals_thesis(C_rosko2, C_numpy2, M, N);
 
//     free(A_2);
//     free(B_2);
//     free(C_naive2);
//     free(C_rosko2);
//     free(C_numpy2);


//     // Clean up allocated memory from standard
//     free(A);
//     free(B);
//     free(C_rosko);
//     free(C_naive);
//     free(C_naive_copy);
//     free(C_numpy);
// }

// int old_main(int argc, char** argv) {
//     int M, K, N, p, alg;
//     float sp, actual_sp;
//     std::string sp_pattern;

//     if (argc < 7) {
//         printf("Usage: %s <M> <K> <N> <sparsity> <pattern>\n", argv[0]);
//         return -1;
//     }

//     M = atoi(argv[1]);
//     K = atoi(argv[2]);
//     N = atoi(argv[3]);
//     sp = atof(argv[4]);
//     sp_pattern = std::string(argv[5]);
//     p = atof(argv[6]);

//     manual_test(M, N, K, p, alg, sp_pattern, sp, actual_sp);

//     return 0;
// }