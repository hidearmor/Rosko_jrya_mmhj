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
	int N = 2048;
	float sps[] = {0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 97, 98, 99, 100};
	int num_sps = sizeof(sps) / sizeof(sps[0]);
	float* A = (float*) malloc(N * N * sizeof( float )); // initalizes with garbage value
	int sp;

	for (int i = 0; i < num_sps; i++) {
		sp = sps[i];

		// float actual_sparsity = column_pattern_sparse(A, N, N, ((float) sp) / 100.0, -1); // init A with column pattern
		// printf("column_pattern_sparse\nsparsity = %f\nactual_sparsity = %f\n", sp, (actual_sparsity*100));

		// float actual_sparsity = row_pattern_sparse(A, N, N, ((float) sp) / 100.0, -1); // init A with row pattern
		// printf("row_pattern_sparse\nsparsity = %f\nactual_sparsity = %f\n", sp, (actual_sparsity*100));

		float actual_sparsity = rand_sparse(A, N, N, ((float) sp) / 100.0); // init A with random uniform sparsity
		printf("rand_sparse\n");
		printf("input_sparsity = %f\n", ((float) sp) / 100.0);
		printf("actual_sparsity = %f\n", actual_sparsity);

		// float actual_sparisty = rand_sparse_teamOtter(A, N, N, ((float) sp) / 100.0); // init A with random uniform sparsity
		// printf("rand_sparse_teamOtter\n");
		// printf("input_sparsity = %f\n", ((float) sp) / 100.0);
		// printf("actual_sparsity = %f\n", (actual_sparisty));

		// test return of rand_sparse OG and 
		// float actual_sparisty = diagonal_pattern_sparse(A, N, N, ((float) sp) / 100.0); // init A with random uniform sparsity
		// printf("diagonal_pattern_sparse\n");
		// printf("input_sparsity = %f\n", ((float) sp) / 100.0);
		// printf("actual_sparsity = %f\n", (actual_sparisty));

		// print_mat(A, N, N);
	}
}

