#include "common_sp.h"
#include <string>


// sparse utils
int run_tests_sparse();

int run_tests_sparse_test();

void rand_sparse_gaussian(float* mat, int r, int c, float mu, float sigma);

// thesis utils
float rand_sparse_teamOtter(float* mat, int r, int c, float sparsity);

// we didn't write this, just changed it
float rand_sparse(float* mat, int r, int c, float sparsity);

float row_pattern_sparse(float* mat, int r, int c, float sparsity, int num_nz_rows);

float column_pattern_sparse(float* mat, int r, int c, float sparsity, int num_nz_cols);

float diagonal_pattern_sparse(float* mat, int r, int c, float sparsity);

void initialize_matrices(float*& A, float*& B, int M, int K,
    int N, float sp, const std::string& sp_pattern, float& actual_sp);

bool mat_equals_thesis(float* C, float* C_check, int M, int N);