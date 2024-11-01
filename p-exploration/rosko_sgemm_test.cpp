#include "rosko.h"
#include <string>

int main( int argc, char** argv ) {

// exit(1);
	int M, K, N, p, nz, mr, nr, ntrials, alg, warmup; // alg is only for rosko use
	struct timespec start, end;
	double diff_t;
	float density, sp;
	std::string filename, algo, measure_r;

	M = atoi(argv[1]); 
	K = atoi(argv[2]);
	N = atoi(argv[3]);
	p = atoi(argv[4]);
	sp = atof(argv[5]);
	ntrials = atoi(argv[6]);
	warmup = atoi(argv[7]);
	algo = std::string(argv[8]);
	filename = std::string(argv[9]);
	measure_r = std::string(argv[10]);
	int measure = 0;
	if (measure_r == "all") measure = 0;
	else if (measure_r == "packing") measure = 1;
	else if (measure_r == "mm") measure = 2;


	// printf("M = %d, K = %d, N = %d, cores = %d, sparsity = %f, algorithm = %s\n", M,K,N,p, ((float) sp) / 100.0, algo.c_str());


	// ---------- Memory allocation for matrices --------------
	float* A = (float*) malloc(M * K * sizeof( float )); // initalizes with garbage value
	float* B = (float*) malloc(K * N * sizeof( float ));
	float* C = (float*) calloc(M * N , sizeof( float )); // intializes whith zero

	// ---------- Initialize A and B -------------------------
    srand(time(NULL)); 
	rand_sparse(A, M, K, ((float) sp) / 100.0); // init A with random uniform sparsity
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
	double myDiff = 0.0;

	// --------- Rosko init (end) -------------------
    
    // printf("alg = %d, flushsize = %d\n", alg, flushsz);

    for(int i = 0; i < (ntrials + warmup); i++) {
        float* dirty = (float *) malloc(flushsz * sizeof(float));
		// should this run private ? like this example:
			// #pragma omp parallel for private(core,k)
			// for(core = 0; core < p_used; core++) {
        #pragma omp parallel for
        for (int dirt = 0; dirt < flushsz; dirt++){
            dirty[dirt] += dirt%100;
            tttmp[dirt%18] += dirty[dirt];
        }

        for(int ii =0; ii<18;ii++){
            ressss+= tttmp[ii];
        }

		
		if(i < warmup) {
			float y = rosko_sgemm(A, B, C, M, N, K, p, cake_cntx, density, NULL, 0, NULL, 0, 1, 0, KMN, alg, measure);
			// printf("sss %f\n", y);
		} else {
			clock_gettime(CLOCK_REALTIME, &start);
			float y = rosko_sgemm(A, B, C, M, N, K, p, cake_cntx, density, NULL, 0, NULL, 0, 1, 0, KMN, alg, measure);
			clock_gettime(CLOCK_REALTIME, &end);
			double seconds = end.tv_sec - start.tv_sec;
			double nanoseconds = end.tv_nsec - start.tv_nsec;
			myDiff += seconds + nanoseconds*1e-9;
			// printf("sss %f\n", y);
			diff_t += y;
		}

        free(dirty);
    }
	clock_gettime(CLOCK_REALTIME, &end);


	printf("\n------------------");
	printf("\nouter time: %f", myDiff / ntrials);
	printf("\nrosko Diff: %f", diff_t / ntrials);
	printf("\n%s,%d,%f,%d,%f,%f,%d,%s\n", algo.c_str(), p, sp, N, diff_t / ntrials, myDiff / ntrials, ntrials, measure_r.c_str());
	fprintf(fp, "%s,%d,%f,%d,%f,%f,%d,%s\n", algo.c_str(), p, sp, N, diff_t / ntrials, myDiff / ntrials, ntrials, measure_r.c_str());
	fclose(fp);

	// cake_sgemm_checker(A, B, C, N, M, K);

	free(A); 
	free(B);
	free(C);
	free(cake_cntx);

	return 0;
}









