#include "rosko.h"
#include <iostream>
#include <vector>
#include <algorithm>  // for std::random_shuffle or std::shuffle
#include <cstdlib>    // for rand()
#include <ctime>      // for seeding rand
#include <random>     // for std::shuffle (modern C++)


int run_tests_sparse() {

	// float *A, *B, *C;
	int M, K, N, m, k, n, max_threads,p;
	float *A, *B, *C;
	cake_cntx_t* cake_cntx = cake_query_cntx();
	max_threads = cake_cntx->ncores;
	int num_tests = 5;
	int Ms[5] = {10,96,111,960,2111};
	int Ks[5] = {10,96,111,960,2111};
	int Ns[5] = {10,96,111,960,2111};
	int cnt = 0;

	printf("starting spMM tests\n");

	for(p = 2; p <= max_threads; p++)  {
		for(m = 0; m < num_tests; m++) {
			for(k = 0; k < num_tests; k++) {
				for(n = 0; n < num_tests; n++) {
					



					M = Ms[m];
					K = Ks[k];
					N = Ns[n];

					A = (float*) malloc(M * K * sizeof( float ));
					B = (float*) malloc(K * N * sizeof( float ));
					C = (float*) calloc(M * N , sizeof( float ));
				    srand(time(NULL));

				    rand_sparse(A, M, K, 0.5);
					rand_init(B, K, N);

// printf("K-first p=%d M=%d K=%d N=%d\n",p,M,K,N);

					rosko_sgemm_online(A, B, C, M, N, K, p, cake_cntx, 0.5, NULL, 0, NULL, 0, 1, 0, KMN, 2);
					if(cake_sgemm_checker(A, B, C, N, M, K)) {
						printf("TESTS FAILED on K-first p=%d M=%d K=%d N=%d\n",p,M,K,N);
						cnt++;
					}

					free(A);
					free(B);
					free(C);





					M = Ms[m];
					K = Ks[k];
					N = Ns[n];

					A = (float*) malloc(M * K * sizeof( float ));
					B = (float*) malloc(K * N * sizeof( float ));
					C = (float*) calloc(M * N , sizeof( float ));
				    srand(time(NULL));

				    rand_sparse(A, M, K, 0.5);
					rand_init(B, K, N);

					rosko_sgemm(A, B, C, M, N, K, p, cake_cntx, 0.5);
					if(cake_sgemm_checker(A, B, C, N, M, K)) {
						printf("TESTS FAILED on M-first p=%d M=%d K=%d N=%d\n",p,M,K,N);
						cnt++;
					}

					free(A);
					free(B);
					free(C);


					// A = (float*) malloc(M * K * sizeof( float ));
					// B = (float*) malloc(K * N * sizeof( float ));
					// C = (float*) calloc(M * N , sizeof( float ));
				 //    srand(time(NULL));

				 //    rand_sparse(A, M, K, 0.5);
					// rand_init(B, K, N);

					// rosko_sgemm(A, B, C, M, N, K, p, cake_cntx, 0,0,1,0,KMN);
					// if(cake_sgemm_checker(A, B, C, N, M, K)) {
					// 	printf("TESTS FAILED on K-first p=%d M=%d K=%d N=%d\n",p,M,K,N);
					// 	cnt++;
					// }

					// free(A);
					// free(B);
					// free(C);


					// A = (float*) malloc(M * K * sizeof( float ));
					// B = (float*) malloc(K * N * sizeof( float ));
					// C = (float*) calloc(M * N , sizeof( float ));
				 //    srand(time(NULL));

				 //    rand_sparse(A, M, K, 0.5);
					// rand_init(B, K, N);

					// rosko_sgemm(A, B, C, M, N, K, p, cake_cntx, 0,0,1,0, NKM);
					// if(cake_sgemm_checker(A, B, C, N, M, K)) {
					// 	printf("TESTS FAILED on N-first p=%d M=%d K=%d N=%d\n",p,M,K,N);
					// 	cnt++;
					// }

					// free(A);
					// free(B);
					// free(C);
				}
			}
		}
	}

	if(cnt) {
		printf("FAILED\n");
	} else {
		printf("ALL SPARSE MM TESTS PASSED!\n");
	}

	return 0;
}




int run_tests_sparse_test() {

	// float *A, *B, *C;
	int M, K, N, m, k, n, max_threads,p;
	float *A, *B, *C;
	cake_cntx_t* cake_cntx = cake_query_cntx();
	max_threads = cake_cntx->ncores;
	int num_tests = 5;
	int Ms[5] = {10,96,111,960,2111};
	int Ks[5] = {10,96,111,960,2111};
	int Ns[5] = {10,96,111,960,2111};
	int cnt = 0;

	printf("starting spMM tests\n");

	for(p = 2; p <= max_threads; p++)  {
		for(m = 0; m < num_tests; m++) {
			for(k = 0; k < num_tests; k++) {
				for(n = 0; n < num_tests; n++) {
					
					M = Ms[m];
					K = Ks[k];
					N = Ns[n];

					A = (float*) malloc(M * K * sizeof( float ));
					B = (float*) malloc(K * N * sizeof( float ));
					C = (float*) calloc(M * N , sizeof( float ));
				    srand(time(NULL));

				    rand_sparse(A, M, K, 0.5);
					rand_init(B, K, N);


					char fname[50];
					snprintf(fname, sizeof(fname), "convert_test");
					mat_to_csr_file(A, M, K, fname);
					
					csr_t* csr = file_to_csr(fname);
					float density = ((float) csr->rowptr[M]) / ((float) (((float) M) * ((float) K)));
					
// printf("density = %f, nz = %d, max_threads = %d\n",density , csr->rowptr[M], max_threads);
					blk_dims_t* x = (blk_dims_t*) malloc(sizeof(blk_dims_t));
					cake_cntx_t* cake_cntx = cake_query_cntx();
					init_sparse_block_dims(M, N, K, p, x, cake_cntx, KMN, NULL, density);
					sp_pack_t* sp_pack = malloc_sp_pack(M, K, csr->rowptr[M], x, cake_cntx);
					pack_A_csr_to_sp_k_first(csr, M, K, csr->rowptr[M], p, sp_pack, x, cake_cntx);

					// printf("heyyyyy\n");
					rosko_sgemm_compressed(fname, B, C, M, N, K, p, cake_cntx, density, NULL, sp_pack, 1, 0, 1, 0, KMN, 2);
					
					free_csr(csr);
					free_sp_pack(sp_pack);

					if(cake_sgemm_checker(A, B, C, N, M, K)) {
						printf("TESTS FAILED on M-first p=%d M=%d K=%d N=%d\n",p,M,K,N);
						cnt++;
					}

					free(A);
					free(B);
					free(C);
					free(cake_cntx);

				}
			}
		}
	}

	if(cnt) {
		printf("FAILED\n");
	} else {
		printf("ALL SPARSE MM TESTS PASSED!\n");
	}

	return 0;
}


// randomized sparse matrix in range [-1,1] 
// with sparsity % of values that are zero
// i.e., threshold pruning
float rand_sparse_teamOtter(float* mat, int r, int c, float sparsity) {
	float density = 1.0f - sparsity;
	int total_nnz = (int) round(r*c * density);
	float actual_sparsity = 1.0 - ((float) total_nnz / (float) (r*c));
	// printf("density from utils: %f", density);
	// printf("actual_sparsity from utils: %f", actual_sparsity);
	// printf("total_nnz from utils: %d", total_nnz);
	
	// Zero out the matrix
    for (int i = 0; i < r * c; i++) {
        mat[i] = 0;
    }

    // Create a vector of matrix indices
    std::vector<int> shuffled_matrix_indices(r*c);
    for (int i = 0; i < r*c; i++) {
        shuffled_matrix_indices[i] = i;
    }

    // Shuffle the vector of matrix indices (C++11 or later)
    std::random_device rd;   // Seed for randomness
    std::mt19937 g(rd());    // Mersenne Twister engine for randomness
    std::shuffle(shuffled_matrix_indices.begin(), shuffled_matrix_indices.end(), g);  // Modern C++ shuffle

    
    // Pick the first nnz index in the shuffled matrix indices and fill it with nnz
	int nnz_range = total_nnz;
    for (int i = 0; i < total_nnz; i++) {
		if (nnz_range != 0) {
			float rand_val = (float) rand() / (float) RAND_MAX;
			int index = shuffled_matrix_indices[i];
			mat[index] = rand_val * 2.0f - 1.0f;  // Random value between -1 and 1
			nnz_range--;
		} else {
			break;
		}
    }

	return actual_sparsity;
}


// randomized sparse matrix in range [-1,1] 
// with sparsity % of values that are zero
// i.e., threshold pruning
int rand_sparse(float* mat, int r, int c, float sparsity) {
	
	int nz = 0;

	for(int i = 0; i < r*c; i++) {
		int x = rand();
		if(x <= ((float) RAND_MAX)*sparsity) {
			mat[i] = 0;
		} else {
			mat[i] =  (float) x / ((float) RAND_MAX)*2.0 - 1.0;
			nz++;
		}
	}

	return nz;	
}

// Sparse matrix with row pattern generator
// Either sparsity should be given as argument or num_nnz_rows (call with -1 to disregard a parameter). 
// returns the actual sparsity of matrix A from 0.0-1.0
float row_pattern_sparse(float* mat, int r, int c, float sparsity, int num_nnz_rows) {

	// Calculate number of non-zero rows based on sparsity if num_nnz_row is not provided
    if (num_nnz_rows >= 0) { // we have a num_nnz_rows argument
        if (num_nnz_rows > r) {
            printf("num_nnz_rows cannot exceed the total number of rows");
            return -1;
        }

    } else { // we don't have a num_nnz_rows argument but must have a sparsity argument
        if (sparsity < 0.0f || sparsity > 1.0f) {
            printf("Sparsity must be between 0 and 1");
            return -1;
        }
        // Calculate number of non-zero rows based on sparsity
        num_nnz_rows = (int) round((1.0f - sparsity) * r);

		// Should we make it so, that if num_nnz_rows == 0 and sparsity < 100, then we set num_nnz_cols to 1?
    }
		float actual_sparsity = 1.0f - ((float) num_nnz_rows / (float) r); 


    int nz = 0;  // count of non-zero entries

    // Zero out the matrix
    for (int i = 0; i < r * c; i++) {
        mat[i] = 0;
    }

    // Create a vector of row indices
    std::vector<int> row_indices(r);
    for (int i = 0; i < r; i++) {
        row_indices[i] = i;
    }

    // Shuffle the vector of row indices (C++11 or later)
    std::random_device rd;   // Seed for randomness
    std::mt19937 g(rd());    // Mersenne Twister engine for randomness
    std::shuffle(row_indices.begin(), row_indices.end(), g);  // Modern C++ shuffle

    
    // Pick the first nnz row in the shuffled rows and fill them with nnz values
    for (int i = 0; i < num_nnz_rows; i++) {
        int row = row_indices[i];  // Select a unique row from the shuffled list

        // Fill the selected row with random values
        for (int j = 0; j < c; j++) {
            float rand_val = (float) rand() / (float) RAND_MAX;
            mat[row * c + j] = rand_val * 2.0f - 1.0f;  // Random value between -1 and 1
            nz++;
        }
    }

    return actual_sparsity;
}



// Sparse matrix with column pattern generator
// Either sparsity should be given as argument or num_nnz_rows (call with -1 to disregard a parameter). 
// returns the actual sparsity of matrix A from 0.0-1.0
float column_pattern_sparse(float* mat, int r, int c, float sparsity, int num_nnz_cols) {

	// Calculate number of non-zero columns based on sparsity if num_nnz_cols is not provided
    if (num_nnz_cols >= 0) { // we have a num_nnz_cols argument
        if (num_nnz_cols > c) {
            printf("num_nnz_cols cannot exceed the total number of columns");
            return -1;
        }

    } else { // we don't have a num_nnz_cols argument but must have a sparsity argument
        if (sparsity < 0.0f || sparsity > 1.0f) {
            printf("Sparsity must be between 0 and 1");
            return -1;
        }
        // Calculate number of non-zero columns based on sparsity
        num_nnz_cols = (int) round((1.0f - sparsity) * c);

		// Should we make it so, that if num_nnz_cols == 0 and sparsity < 100, then we set num_nnz_cols to 1?
    }
		float actual_sparsity = 1.0f - ((float) num_nnz_cols / (float) c); 


    int nz = 0;  // count of non-zero entries

    // Zero out the matrix
    for (int i = 0; i < r * c; i++) {
        mat[i] = 0;
    }

    // Create a vector of column indices
    std::vector<int> col_indices(c);
    for (int i = 0; i < c; i++) {
        col_indices[i] = i;
    }

    // Shuffle the vector of column indices (C++11 or later)
    std::random_device rd;   // Seed for randomness
    std::mt19937 g(rd());    // Mersenne Twister engine for randomness
    std::shuffle(col_indices.begin(), col_indices.end(), g);  // Modern C++ shuffle

    // Pick the first nnz column in the shuffled columns and fill them with nnz values
    for (int i = 0; i < num_nnz_cols; i++) {
        int col = col_indices[i];  // Select a unique column from the shuffled list

        // Fill the selected column with random values
        for (int j = 0; j < r; j++) {
            float rand_val = (float) rand() / (float) RAND_MAX;
			mat[j * c + col] = rand_val * 2.0f - 1.0f;  // Random value between -1 and 1
            nz++;
        }
    }

    return actual_sparsity; 
}




// randomized sparse Normal(0,1) matrix with sparsity % of values determined by sigma (std dev)
void rand_sparse_gaussian(float* mat, int r, int c, float mu, float sigma) {
	int nnz = 0;
	for(int i = 0; i < r*c; i++) {
		float x = normalRandom()*sigma+mu;
		if(fabs(x) <= 2) { // 2 sigmas i.e. 95% sparse
			mat[i] = 0;
		} else {
			mat[i] =  x;
			nnz++;
		}
	}	
	printf("nnz = %d\n", nnz);
}

