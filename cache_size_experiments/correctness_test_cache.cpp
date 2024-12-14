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


float* rosko(float* A, float* B, int M, int N, int K, float density, int p, int alg, float L3_factor) {
    float* C = (float*) calloc(M * N , sizeof( float ));
	cake_cntx_t* cake_cntx = cake_query_cntx();

	int L3 = (cake_cntx->L3);
	cake_cntx->L3 = static_cast<int>(round(L3 * L3_factor));
    // printf("\n%f", (float(cake_cntx->L3)/1000000.0f));

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

struct Triplet {
    int M, N, K;
    Triplet(int m, int n, int k) : M(m), N(n), K(k) {}
};

std::vector<Triplet> generateShapes(int maxDimSize) {
    std::vector<Triplet> shapes;
    int minDimSize = 200;

    // Determine the number of shapes to generate (between 5 and 10)
    int numShapes = std::max(5, std::min(8, maxDimSize / minDimSize));

    // Create a non-linear distribution for sizes
    std::vector<int> sizes;
    for (int i = 0; i < numShapes; ++i) {
        // Use quadratic scaling to distribute sizes more densely at the lower range
        float factor = static_cast<float>(i) / (numShapes - 1); // range from 0 to 1
        int size = minDimSize + static_cast<int>((maxDimSize - minDimSize) * (factor * factor));
        sizes.push_back(size);
    }

    // Generate shapes using combinations of the non-linearly distributed sizes
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
    bool res = mat_equals_thesis(C1, C2, M, N);
    if ((res == 1 && expected == "identical") || (res == 0 && expected == "different")) {
        std::cerr << "Error: Matrices " << name1 << " and " << name2 << " should be " << expected << std::endl;
        return false;
    }
    return true;
}

void printSpecs(int M, int N, int K, float sp, std::string sp_pattern, int p) {
    printf("\nspecs: M %d, N %d, K %d, sp %f, sp_pattern: %s, p %d", M, N, K, sp, sp_pattern.c_str(), p );
}


bool runAllTestsWihtouNaive(int M, int N, int K, float sp_init, std::string sp_pattern, int p, float L3_factor)
{
    bool debugPrint = false;
    float actual_sp;
    int alg;
    bool result = false; // set to true after all checks

    float* A1 = nullptr;
    float* B1 = nullptr;
    float* A1elem = nullptr;
    float* A1row = nullptr;
    float* A2 = nullptr;
    float* B2 = nullptr;

    initialize_matrices(A1, B1, M, K, N, sp_init, sp_pattern, actual_sp);
    initialize_matrices(A2, B2, M, K, N, sp_init, sp_pattern, actual_sp);

    if (debugPrint) printf("\ninit normals");

    int sizeA = M * K;
    A1elem = changeSingleElement(A1, sizeA);
    A1row = changeSingleRow(A1, M, K);
    
    if (debugPrint) printf("\ninit copies");

    float sp = actual_sp *100.0;
    float density = (100.0 - actual_sp * 100.0) / 100.0;
    
    float* C_1_rosko =       rosko(A1, B1, M, N, K, density, p, alg, L3_factor);
    float* C_1_numpy =       numpy(A1, B1, M, N, K);
    
    float* C_1_rosko_copy =  rosko(A1, B1, M, N, K, density, p, alg, L3_factor);
    float* C_1_numpy_copy =  numpy(A1, B1, M, N, K);

    float* C_1row_rosko =    rosko(A1row, B1, M, N, K, density, p, alg, L3_factor);
    float* C_1row_numpy =    numpy(A1row, B1, M, N, K);

    float* C_1elem_rosko =   rosko(A1elem, B1, M, N, K, density, p, alg, L3_factor);
    float* C_1elem_numpy =   numpy(A1elem, B1, M, N, K);

    float* C_2_rosko =       rosko(A2, B2, M, N, K, density, p, alg, L3_factor);
    float* C_2_numpy =       numpy(A2, B2, M, N, K);
    
    if (debugPrint) printf("\ndid mm");

    while (result == false)
    {
        // does it test with correct input?
        if (!check_matrices_equal(C_1_rosko, C_1_rosko, M, N, "C_1_rosko", "C_1_rosko", "identical")) break;
        if (!check_matrices_equal(C_1_numpy, C_1_numpy, M, N, "C_1_numpy", "C_1_numpy", "identical")) break;

        // Group 1: C_1_*
        if (!check_matrices_equal(C_1_rosko, C_1_numpy, M, N, "C_1_rosko", "C_1_numpy", "identical")) break;

        // Group 2: Identical input, two different variables and MM processes
        if (!check_matrices_equal(C_1_rosko, C_1_rosko_copy, M, N, "C_1_rosko", "C_1_rosko_copy", "identical")) break;
        if (!check_matrices_equal(C_1_numpy, C_1_numpy_copy, M, N, "C_1_numpy", "C_1_numpy_copy", "identical")) break;

        // Group 5: Identical input, are 2's also identical?
        if (!check_matrices_equal(C_2_rosko, C_2_numpy, M, N, "C_2_rosko", "C_2_numpy", "identical")) break;

        // // Group 3: change row, should be different
        if (!check_matrices_equal(C_1row_rosko, C_1_rosko, M, N, "C_1row_rosko", "C_1_rosko", "different")) break;
        if (!check_matrices_equal(C_1row_numpy, C_1_numpy, M, N, "C_1row_numpy", "C_1_numpy", "different")) break;

        // // Group 4: changed element, should be different
        if (!check_matrices_equal(C_1elem_rosko, C_1_rosko, M, N, "C_1elem_rosko", "C_1_rosko", "different")) break;
        if (!check_matrices_equal(C_1elem_numpy, C_1_numpy, M, N, "C_1elem_numpy", "C_1_numpy", "different")) break;

        // // Group 5: plain different, should be different
        if (!check_matrices_equal(C_2_rosko, C_1_numpy, M, N, "C_2_rosko", "C_1_numpy", "different")) break;
        if (!check_matrices_equal(C_2_rosko, C_1_rosko, M, N, "C_2_rosko", "C_1_rosko", "different")) break;
        if (!check_matrices_equal(C_2_numpy, C_1_numpy, M, N, "C_2_numpy", "C_1_numpy", "different")) break;

        result = true;
    }

    if (debugPrint) printf("\nchecked");

    free(A1);
    free(B1);
    free(A1elem);
    free(A1row);
    free(A2);
    free(B2);
    free(C_1_rosko);
    free(C_1_numpy);
    free(C_1_rosko_copy);
    free(C_1_numpy_copy);
    free(C_1row_rosko);
    free(C_1row_numpy);
    free(C_1elem_rosko);
    free(C_1elem_numpy);
    free(C_2_rosko);
    free(C_2_numpy);

    if (debugPrint) printf("\nfreed\n");

    return result;
}

void correctnessSuite(int maxDimSize, float sp_init, std::string sp_pattern, int p, float L3_factor)
{
    std::vector<Triplet> shapes = generateShapes(maxDimSize);
    bool result = false;

    for (const auto& [M, N, K] : shapes) {
        printf("shape: M %d, K %d, N %d\n", M, K, N);
        if ((sp_init >= 100.0f)
            || (sp_init > 99.5f && (sp_pattern == "column-pattern" || sp_pattern == "row-pattern")))
            {
                // printf("\nsparsity too high for pattern continuing, pattern %s, sp %f", sp_pattern.c_str(), sp_init);
                continue;
            }
        result = runAllTestsWihtouNaive(M, N, K, sp_init, sp_pattern, p, L3_factor);
        if (result == false)
        {
            printf("\n");
            printSpecs(M, N, K, sp_init, sp_pattern, p);
            printf("\nERROR somewhere here\n");
            return;
        }
    }

    // printf("\np %d, sp %f, maxDim %d, pattern %s", p, sp_init, maxDimSize, sp_pattern.c_str());
    // printf("\nTest succesful! No errors encountered!");
}

void printCustomL3(float L3_factor) {
    cake_cntx_t* cake_cntx = cake_query_cntx();

	int L3 = (cake_cntx->L3);
	cake_cntx->L3 = static_cast<int>(round(L3 * L3_factor));
    printf("\nL3 custom: %f\n", (float(cake_cntx->L3)/1000000.0f));
    free(cake_cntx);
}


int main(int argc, char** argv) {
    if (argc < 5) {
        printf("Params: maxDims, sp, sp_pattern, p \n");
        return -1;
    }
    int maxDims = atoi(argv[1]);
    std::string sp_pattern = std::string(argv[2]);
    int p = atof(argv[3]);
    float sp_init = atof(argv[4]);
    float L3_factor = atof(argv[5]);
    printCustomL3(L3_factor);
    correctnessSuite(maxDims, sp_init, sp_pattern, p, L3_factor);

    return 0;
}