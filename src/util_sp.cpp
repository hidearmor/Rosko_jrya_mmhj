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
					
// printf("density = %f, nnz = %d, max_threads = %d\n",density , csr->rowptr[M], max_threads);
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

// Thesis related

// randomized sparse matrix in range [-1,1] 
// with sparsity % of values that are zero
// i.e., threshold pruning
float rand_sparse_teamOtter(float* mat, int r, int c, float sparsity) {
	float density = 1.0f - sparsity;
	int total_nz = (int) round(r*c * density);
	float actual_sparsity = 1.0 - ((float) total_nz / (float) (r*c));
	// printf("density from utils: %f", density);
	// printf("actual_sparsity from utils: %f", actual_sparsity);
	// printf("total_nz from utils: %d", total_nz);
	
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

    
    // Pick the first nz index in the shuffled matrix indices and fill it with nz
	int nz_range = total_nz;
    for (int i = 0; i < total_nz; i++) {
		if (nz_range != 0) {
			float rand_val = (float) rand() / (float) RAND_MAX;
			int index = shuffled_matrix_indices[i];
			mat[index] = rand_val * 2.0f - 1.0f;  // Random value between -1 and 1
			nz_range--;
		} else {
			break;
		}
    }

	return actual_sparsity;
}


// randomized sparse matrix in range [-1,1] 
// with sparsity % of values that are zero
// i.e., threshold pruning
float rand_sparse(float* mat, int r, int c, float sparsity) {
	
	int nnz = 0;

	for(int i = 0; i < r*c; i++) {
		int x = rand();
		if(x <= ((float) RAND_MAX)*sparsity) {
			mat[i] = 0;
		} else {
			mat[i] =  (float) x / ((float) RAND_MAX)*2.0 - 1.0;
			nnz++;
		}
	}

	float actual_sparsity = 1.0 - ((float) nnz / (float) (r*c));

	return actual_sparsity;	
}

// Sparse matrix with row pattern generator
// Either sparsity should be given as argument or num_nz_rows (call with -1 to disregard a parameter). 
// returns the actual sparsity of matrix A from 0.0-1.0
float row_pattern_sparse(float* mat, int r, int c, float sparsity, int num_nz_rows) {

	// Calculate number of non-zero rows based on sparsity if num_nz_row is not provided
    if (num_nz_rows >= 0) { // we have a num_nz_rows argument
        if (num_nz_rows > r) {
            printf("num_nz_rows cannot exceed the total number of rows");
            return -1;
        }

    } else { // we don't have a num_nz_rows argument but must have a sparsity argument
        if (sparsity < 0.0f || sparsity > 1.0f) {
            printf("Sparsity must be between 0 and 1");
            return -1;
        }
        // Calculate number of non-zero rows based on sparsity
        num_nz_rows = (int) round((1.0f - sparsity) * r);

		// Should we make it so, that if num_nz_rows == 0 and sparsity < 100, then we set num_nz_cols to 1?
    }
		float actual_sparsity = 1.0f - ((float) num_nz_rows / (float) r); 


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

    
    // Pick the first nz row in the shuffled rows and fill them with nz values
    for (int i = 0; i < num_nz_rows; i++) {
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
// Either sparsity should be given as argument or num_nz_rows (call with -1 to disregard a parameter). 
// returns the actual sparsity of matrix A from 0.0-1.0
float column_pattern_sparse(float* mat, int r, int c, float sparsity, int num_nz_cols) {

	// Calculate number of non-zero columns based on sparsity if num_nz_cols is not provided
    if (num_nz_cols >= 0) { // we have a num_nz_cols argument
        if (num_nz_cols > c) {
            printf("num_nz_cols cannot exceed the total number of columns");
            return -1;
        }

    } else { // we don't have a num_nz_cols argument but must have a sparsity argument
        if (sparsity < 0.0f || sparsity > 1.0f) {
            printf("Sparsity must be between 0 and 1");
            return -1;
        }
        // Calculate number of non-zero columns based on sparsity
        num_nz_cols = (int) round((1.0f - sparsity) * c);

		// Should we make it so, that if num_nz_cols == 0 and sparsity < 100, then we set num_nz_cols to 1?
    }
		float actual_sparsity = 1.0f - ((float) num_nz_cols / (float) c); 


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

    // Pick the first nz column in the shuffled columns and fill them with nz values
    for (int i = 0; i < num_nz_cols; i++) {
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

// CAN NEVER GO TO 0% SPARSITY AKA 100% DENSITY - JUST A FLAW
float diagonal_pattern_sparse(float* mat, int r, int c, float sparsity) {
	
	// Validate sparsity and calculate number of diagonals
	if (sparsity < 0.0f || sparsity > 1.0f) {
		std::cerr << "Sparsity must be between 0 and 1" << std::endl;
		return -1;
	}

	float density = 1.0f - sparsity;
	int total_elements = r * c;
	int target_num_nz = (int) round(total_elements * density);

    // Zero out the matrix
    for (int i = 0; i < r * c; i++) {
        mat[i] = 0;
    }

	if (target_num_nz == 0) {
		return 1.0f;  // Sparsity of 100%
	}

	// Calculate the diagonal "band width" based on the target number of non-zero elements
	// This is the width of the band of diagonals: an approximation of how many diagonals we are going to need (a maximum) 
	int band_width = std::max(1, (int) (std::ceil(target_num_nz / (float) (std::min(r, c)))));

    int nz = 0;  // Count non-zero elements
	bool stop = false;

    // Fill the matrix along the diagonals within the calculated band width
    for (int diag = -band_width / 2; diag <= band_width / 2; ++diag) {
        int row_start = std::max(0, -diag);
        int col_start = std::max(0, diag);

        // Populate the current diagonal fully
        for (int i = 0; i < std::min(r - row_start, c - col_start); ++i) {

			// Make it known, that after this diagonal is populated it stops populating any more diagonals 
            if (nz >= target_num_nz) {
				stop = true;
			}

            // Random value between -1 and 1
            float rand_val = (float) (rand()) / (float) (RAND_MAX) * 2.0f - 1.0f;
            mat[(row_start + i) * c + (col_start + i)] = rand_val;

            nz++;  // Increment non-zero element count
        }

		if (stop == true) break;
        // if (nz >= target_num_nz) break;  // Stop if we reach the target non-zero count
    }

    // Calculate the actual sparsity achieved
    float actual_sparsity = 1.0f - ((float) (nz) / total_elements);

    return actual_sparsity;
}

// create matrices given pointers for A-sparse and B-dense
void initialize_matrices(float*& A, float*& B, int M, int K, int N, float sp, const std::string& sp_pattern, float& actual_sp) {
    // Allocate memory for matrices A and B
    A = (float*) malloc(M * K * sizeof(float));
    B = (float*) malloc(K * N * sizeof(float));

    // Check if allocation was successful
    if (A == nullptr || B == nullptr) {
        fprintf(stderr, "Memory allocation failed\n");
        exit(1);
    }

    // Initialize matrix A based on sparsity pattern
    if (sp_pattern == "random-uniform") {
        actual_sp = rand_sparse(A, M, K, sp / 100.0);
    } else if (sp_pattern == "row-pattern") {
        actual_sp = row_pattern_sparse(A, M, K, sp / 100.0, -1);
    } else if (sp_pattern == "column-pattern") {
        actual_sp = column_pattern_sparse(A, M, K, sp / 100.0, -1);
    } else if (sp_pattern == "diagonal") {
        actual_sp = diagonal_pattern_sparse(A, M, K, sp / 100.0);
    } else {
        printf("%s is not a valid sparsity pattern\n", sp_pattern.c_str());
        free(A);
        free(B);
        exit(-1);
    }

    // Initialize matrix B with random values
    rand_init(B, K, N);
}

bool mat_equals_thesis(float* C, float* C_check, int M, int N) {

    int CORRECT = 1;
    int cnt = 0;
    int ind1 = 0;
    float eps = 1e-3; // machine precision level

	for(int m = 0; m < M; m++) {
	    for(int n = 0; n < N; n++) {
	        if(fabs(C_check[ind1] - C[ind1]) > eps) {
	            cnt++;
	            CORRECT = 0;
	        }
			// printf("%f\t%f\n", C_check[ind1], C[ind1]);
	        ind1++; 
      	}
    }

	if(CORRECT) {
		// printf("CORRECT!\n");
		return 0;
	} else {
		// printf("WRONG!\n");
		// printf("%d\n", cnt);
		return 1;
	}
}