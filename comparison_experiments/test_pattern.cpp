#include "rosko.h"
#include <string>
#include <iostream>
#include <vector>
#include <algorithm>  // for std::random_shuffle or std::shuffle
#include <cstdlib>    // for rand()
#include <ctime>      // for seeding rand
#include <random>     // for std::shuffle (modern C++)



// int main(int argc, char *argv[]) {
int main( int argc, char** argv ) {
	int N = 10;
	float sp = 90;
	float* A = (float*) malloc(N * N * sizeof( float )); // initalizes with garbage value

    // float actual_sparsity = column_pattern_sparse(A, N, N, ((float) sp) / 100.0, -1); // init A with column pattern
    // printf("column_pattern_sparse\nsparsity = %f\nactual_sparsity = %f\n", sp, (actual_sparsity*100));

	// float actual_sparsity = row_pattern_sparse(A, N, N, ((float) sp) / 100.0, -1); // init A with row pattern
    // printf("row_pattern_sparse\nsparsity = %f\nactual_sparsity = %f\n", sp, (actual_sparsity*100));

	// int num_nnz = rand_sparse(A, N, N, ((float) sp) / 100.0); // init A with random uniform sparsity
	// printf("rand_sparse\nnnz in A = %d\n", num_nnz);
	// printf("input_sparsity = %f\n", ((float) sp) / 100.0);
    // printf("actual_sparsity = %f\n", (100.0 - ((float) num_nnz / (float) (N*N)) * 100.0));

	float actual_sparisty = rand_sparse_teamOtter(A, N, N, ((float) sp) / 100.0); // init A with random uniform sparsity
	printf("rand_sparse_teamOtter\n");
	printf("input_sparsity = %f\n", ((float) sp) / 100.0);
    printf("actual_sparsity = %f\n", (actual_sparisty));

	print_mat(A, N, N);
}

