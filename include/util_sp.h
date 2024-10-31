#include "common_sp.h"



// sparse utils
int run_tests_sparse();

int run_tests_sparse_test();

float rand_sparse_teamOtter(float* mat, int r, int c, float sparsity);

int rand_sparse(float* mat, int r, int c, float sparsity);

float row_pattern_sparse(float* mat, int r, int c, float sparsity, int num_nnz_rows);

float column_pattern_sparse(float* mat, int r, int c, float sparsity, int num_nnz_cols);

void rand_sparse_gaussian(float* mat, int r, int c, float mu, float sigma);
