#include "rosko.h"
#include <string>

double naive_mm(float* A, float* B, float* C, int M, int N, int K) {

    struct timespec start, end;
	long seconds, nanoseconds;
	double diff_t, times;
	
    clock_gettime(CLOCK_REALTIME, &start);

	// KMN order
	// for (int k = 0; k < K; k++){
	// 	for (int m = 0; m < M;  m++) {
	// 		for (int n = 0; n < N; n++) {
    //             C[m*N + n] += A[m*K + k] * B[k*N + n];
	// 		}
	// 	}
	// }

	// MNK order (the one we have known the best)
	for (int m = 0; m < M;  m++) {
		for (int n = 0; n < N; n++) {
			for (int k = 0; k < K; k++){
                C[m*N + n] += A[m*K + k] * B[k*N + n];
			}
		}
		// Check elapsed time after each outer loop iteration
        clock_gettime(CLOCK_REALTIME, &end);
        seconds = end.tv_sec - start.tv_sec;
        nanoseconds = end.tv_nsec - start.tv_nsec;
        diff_t = seconds + nanoseconds * 1e-9;

		// float limit = 40.0;

        // if (diff_t > limit) {
        //     return -1.0;  // Return -1.0 if time exceeds 40 seconds
        // }
	}


    clock_gettime(CLOCK_REALTIME, &end);
    seconds = end.tv_sec - start.tv_sec;
    nanoseconds = end.tv_nsec - start.tv_nsec;
    diff_t = seconds + nanoseconds*1e-9;
    return diff_t; 
}

int main( int argc, char** argv ) {

// exit(1);
	int M, K, N, p, nz, ntrials, alg, warmup; // alg is only for rosko use
	struct timespec start, end;
	double diff_t;
	float density, sp;
	std::string filename, algo;

	M = atoi(argv[1]); 
	K = atoi(argv[2]);
	N = atoi(argv[3]);
	p = 1;
	sp = atof(argv[4]);
	ntrials = atoi(argv[5]);
	warmup = atoi(argv[6]);
	algo = std::string(argv[7]);
	filename = std::string(argv[8]);

	// printf("M = %d, K = %d, N = %d, cores = %d, sparsity = %f, algorithm = %s\n", M,K,N,p, ((float) sp) / 100.0, algo.c_str());


	// ---------- Memory allocation for matrices --------------
	float* A = (float*) malloc(M * K * sizeof( float )); // initalizes with garbage value
	float* B = (float*) malloc(K * N * sizeof( float ));
	float* C = (float*) calloc(M * N , sizeof( float )); // intializes whith zero

	// ---------- Initialize A and B -------------------------
    srand(time(NULL)); 
	rand_sparse(A, M, K, ((float) sp) / 100.0); // init A with random uniform sparsity
	rand_init(B, K, N); // init B with random nnz

	// --------- Naive init -------------------
	density = (100.0 - sp) / 100.0;

	cake_cntx_t* cake_cntx = cake_query_cntx(); // just to have stats on this computer

	char fname[50];
	snprintf(fname, sizeof(fname), "%s", filename.c_str());
	FILE *fp;
	fp = fopen(fname, "a");

    float ressss;
    float tttmp[18];
    int flushsz = 2*cake_cntx->L3 / sizeof(float);
    diff_t = 0.0;

    
    // printf("alg = %d, flushsize = %d\n", alg, flushsz);

    // ------------- Performance experiment --------------
    for(int i = 0; i < (ntrials + warmup); i++) {
	// for(int i = 0; i < (1); i++) {

		memset(C, 0, M * N * sizeof(float));  // Reset C to zero

        float* dirty = (float *) malloc(flushsz * sizeof(float));
        #pragma omp parallel for // parallelizes for loop with OpenMP 
        for (int dirt = 0; dirt < flushsz; dirt++){
            dirty[dirt] += dirt%100;
            tttmp[dirt%18] += dirty[dirt];
        }

        for(int ii =0; ii<18;ii++){
            ressss+= tttmp[ii];
        }

		float y = 0.0;
		if(i < warmup) {
			y = naive_mm(A, B, C, M, N, K);
		} else {
			y = naive_mm(A, B, C, M, N, K);
			// printf("sss %f\n", y);
			diff_t += y;
		}

		// break if time limit exeeced
		if (y == -1.0) {
			diff_t = y*ntrials;
			break;
		}

        free(dirty);
    }

	printf("%s,%d,%f,%d,%d,%d,%f,%d\n", algo.c_str(), p, sp, M, K, N, diff_t / ntrials, ntrials);
	fprintf(fp, "%s,%d,%f,%d,%d,%d,%f,%d\n", algo.c_str(), p, sp, M, K, N, diff_t / ntrials, ntrials);
	fclose(fp);

	// cake_sgemm_checker(A, B, C, N, M, K);

	free(A);
	free(B);
	free(C);
	free(cake_cntx);

	return 0;
}
