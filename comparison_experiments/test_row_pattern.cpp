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
	float sp = 50;
	float* A = (float*) malloc(N * N * sizeof( float )); // initalizes with garbage value

    float actual_sparsity = row_pattern_sparse(A, N, N, ((float) sp) / 100.0, -1); // init A with row pattern
    printf("row_pattern_sparse\nsparsity = %f\nactual_sparsity = %f\n", sp, (actual_sparsity*100));
	// rand_sparse(A, N, N, ((float) sp) / 100.0); // init A with random uniform sparsity
    // printf("rand_sparse\n");
	print_mat(A, N, N);
}

