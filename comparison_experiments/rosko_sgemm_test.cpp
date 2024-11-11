#include "rosko.h"
#include <string>

int main( int argc, char** argv ) {

// exit(1);
	int M, K, N, p, nz, mr, nr, ntrials, alg, warmup; // alg is only for rosko use
	struct timespec start, end;
	double diff_t;
	float density, sp, actual_sp;
	std::string filename, algo, sp_pattern;

	M = atoi(argv[1]); 
	K = atoi(argv[2]);
	N = atoi(argv[3]);
	p = atoi(argv[4]);
	sp = atof(argv[5]);
	ntrials = atoi(argv[6]);
	warmup = atoi(argv[7]);
	sp_pattern = std::string(argv[8]);
	algo = std::string(argv[9]);
	filename = std::string(argv[10]);


	// printf("M = %d, K = %d, N = %d, cores = %d, sparsity = %f, sparsity pattern = %s, algorithm = %s\n", M,K,N,p, ((float) sp) / 100.0, sp_pattern.c_str(), algo.c_str());

	// ---------- Memory allocation for matrices --------------
	float* A = (float*) malloc(M * K * sizeof( float )); // initalizes with garbage value
	float* B = (float*) malloc(K * N * sizeof( float ));
	float* C = (float*) calloc(M * N , sizeof( float )); // intializes whith zero

	// ---------- Initialize A and B -------------------------
    srand(time(NULL)); 
	rand_sparse(A, M, K, ((float) sp) / 100.0); // init A with random uniform sparsity

	if (sp_pattern == "random-uniform") {
		actual_sp = rand_sparse(A, M, K, ((float) sp) / 100.0); // init A with random uniform sparsity
	} else if (sp_pattern == "row-pattern") {
		actual_sp = row_pattern_sparse(A, M, K, ((float) sp) / 100.0, -1);
	} else if (sp_pattern == "column-pattern") {
		actual_sp = column_pattern_sparse(A, M, K, ((float) sp) / 100.0, -1);
	} else if (sp_pattern == "diagonal") {
		actual_sp = diagonal_pattern_sparse(A, M, K, ((float) sp) / 100.0);
	} else {
		printf("%s is not a valid sparsity pattern\n", sp_pattern.c_str());
		return -1;
	}

	sp = actual_sp *100.0;

	rand_init(B, K, N); // init B with random nnz

	// --------- Rosko init (begin) -------------------
	density = (100.0 - sp) / 100.0;

	cake_cntx_t* cake_cntx = cake_query_cntx();

	char fname[50];
	snprintf(fname, sizeof(fname), "%s", filename.c_str());
	FILE *fp;
	fp = fopen(fname, "a");

    float ressss;
    float tttmp[18];
    int flushsz = 2*cake_cntx->L3 / sizeof(float);
    diff_t = 0.0;

	// --------- Rosko init (end) -------------------
    
    // printf("alg = %d, flushsize = %d\n", alg, flushsz);

    for(int i = 0; i < (ntrials + warmup); i++) {
	// for(int i = 0; i < (1); i++) {

        float* dirty = (float *) malloc(flushsz * sizeof(float));
        #pragma omp parallel for
        for (int dirt = 0; dirt < flushsz; dirt++){
            dirty[dirt] += dirt%100;
            tttmp[dirt%18] += dirty[dirt];
        }

        for(int ii =0; ii<18;ii++){
            ressss+= tttmp[ii];
        }

		
		if(i < warmup) {
			float y = rosko_sgemm(A, B, C, M, N, K, p, cake_cntx, density, NULL, 0, NULL, 0, 1, 0, KMN, alg);
			// printf("sss %f\n", y);
		} else {
			float y = rosko_sgemm(A, B, C, M, N, K, p, cake_cntx, density, NULL, 0, NULL, 0, 1, 0, KMN, alg);
			// printf("sss %f\n", y);
			diff_t += y;
		}

        free(dirty);
    }

	printf("%s,%d,%f,%d,%d,%d,%s,%f,%d\n", algo.c_str(), p, sp, M, K, N, sp_pattern.c_str(), diff_t / ntrials, ntrials);
	fprintf(fp, "%s,%d,%f,%d,%d,%d,%s,%f,%d\n", algo.c_str(), p, sp, M, K, N, sp_pattern.c_str(), diff_t / ntrials, ntrials);
	fclose(fp);

	// cake_sgemm_checker(A, B, C, N, M, K);

	free(A); 
	free(B);
	free(C);
	free(cake_cntx);

	return 0;
}









