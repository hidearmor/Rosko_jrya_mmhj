#include "rosko.h"


double rosko_sgemm_p_exploration(float* A, float* B, float* C, int M, int N, int K, int p, 
	cake_cntx_t* cake_cntx, float density, char* argv[], 
	bool packedA, sp_pack_t* sp_pack, bool packedB, 
	float alpha, float beta, enum sched sch, int alg, int measure, int mcu, int kcu, int ncu) {


	size_t A_sz, B_sz, C_sz;	
	struct timespec start, end, start1, end1;
	long seconds, nanoseconds;
	double diff_t, times;
	float *A_p, *B_p;

	sch = KMN;
	// sch = set_schedule(sch, M, N, K);

	// JOnas include almost all in time
	if (measure == 0) clock_gettime(CLOCK_REALTIME, &start1);

	if(cake_cntx == NULL) {
		printf("\nauto-calculating");
		cake_cntx = cake_query_cntx();
	}

	blk_dims_t* x = (blk_dims_t*) malloc(sizeof(blk_dims_t));



	init_sparse_block_dims(M, N, K, p, x, cake_cntx, sch, argv, density, 4, alg, mcu, kcu, ncu);
	omp_set_num_threads(p);
	// JONAS OMP
	printf("\nnumber of threads assigned OpenMP = %d", p);
	printf("\nnumber of threads from OpenMP = %d", omp_get_num_threads());
	printf("\nmax # of threads from OpenMP = %d", omp_get_max_threads());
	printf("\nthread number from OpenMP = %d", omp_get_thread_num());
	printf("\n");

	if(DEBUG) printf("m_r = %d, n_r = %d\n\n", cake_cntx->mr, cake_cntx->nr);
	if(DEBUG) printf("mc = %d, kc = %d, nc = %d, alpha_n = %f\n", x->m_c, x->k_c, x->n_c, cake_cntx->alpha_n);

	// // JOnas include packing in time
	if (measure == 1) clock_gettime(CLOCK_REALTIME, &start1);

	if(sp_pack == NULL) {

		clock_gettime(CLOCK_REALTIME, &start);

		A_sz = cake_sgemm_packed_A_size(M, K, p, x, cake_cntx, sch) / sizeof(float);
	    A_p = (float*) calloc(A_sz, sizeof(float));

		sp_pack = (sp_pack_t*) malloc(sizeof(sp_pack_t));

		pack_A_sp(A, A_p, M, K, p, sp_pack, x, cake_cntx, sch);

		clock_gettime(CLOCK_REALTIME, &end);
		seconds = end.tv_sec - start.tv_sec;
		nanoseconds = end.tv_nsec - start.tv_nsec;
		diff_t = seconds + nanoseconds*1e-9;
		if(DEBUG) printf("A sparse pack time: %f \n", diff_t ); 
	}

	// JONAS original position
	if (measure == 2) clock_gettime(CLOCK_REALTIME, &start1);



	if(packedB) {
		B_p = B;
	} else {

		clock_gettime(CLOCK_REALTIME, &start);

	    B_sz = cake_sgemm_packed_B_size(K, N, p, x, cake_cntx);
		if(posix_memalign((void**) &B_p, 64, B_sz)) {
			printf("posix memalign error\n");
			exit(1);
		}

		pack_B(B, B_p, K, N, p, x, cake_cntx, sch);

	    clock_gettime(CLOCK_REALTIME, &end);
	    seconds = end.tv_sec - start.tv_sec;
	    nanoseconds = end.tv_nsec - start.tv_nsec;
	    diff_t = seconds + nanoseconds*1e-9;
		if(DEBUG) printf("B pack time: %f \n", diff_t ); 
	}



	if(sch == KMN) {

		float *C_p[p];

		for(int i = 0; i < p; i++) {
			C_p[i] = (float*) calloc(x->m_c * x->n_c, sizeof(float));
		}

		clock_gettime(CLOCK_REALTIME, &start);

		// schedule_sp(sp_pack, B_p, C_p, M, N, K, p, cake_cntx, x, sch);
		schedule_KMN_sp(sp_pack, B_p, C, C_p, M, N, K, p, cake_cntx, x);

	    clock_gettime(CLOCK_REALTIME, &end);
	    seconds = end.tv_sec - start.tv_sec;
	    nanoseconds = end.tv_nsec - start.tv_nsec;
	    diff_t = seconds + nanoseconds*1e-9;
		if(DEBUG) printf("GEMM time: %f \n", diff_t); 	// exit(1);

		for(int i = 0; i < p; i++) {
			free(C_p[i]);
		}
	} else {

		float *C_p;
		// C = alpha*A*B + beta*C. If beta is !=0, we must explicitly pack C, 
		// otherwise just allocate an empty C_p buffer
		if(beta != 0) {

			clock_gettime(CLOCK_REALTIME, &start);

		    C_sz = cake_sgemm_packed_C_size(M, N, p, x, cake_cntx, sch);
			if(posix_memalign((void**) &C_p, 64, C_sz)) {
				printf("posix memalign error\n");
				exit(1);
			}

			pack_C(C, C_p, M, N, p, x, cake_cntx, sch);

		    clock_gettime(CLOCK_REALTIME, &end);
		    seconds = end.tv_sec - start.tv_sec;
		    nanoseconds = end.tv_nsec - start.tv_nsec;
		    diff_t = seconds + nanoseconds*1e-9;
			if(DEBUG) printf("C pack time: %f \n", diff_t ); 

		} else {
		    C_sz = cake_sgemm_packed_C_size(M, N, p, x, cake_cntx, sch) / sizeof(float);
		    C_p = (float*) calloc(C_sz, sizeof(float));

		}

		clock_gettime(CLOCK_REALTIME, &start);

		schedule_sp(sp_pack, B_p, C_p, M, N, K, p, cake_cntx, x, sch);

	    clock_gettime(CLOCK_REALTIME, &end);
	    seconds = end.tv_sec - start.tv_sec;
	    nanoseconds = end.tv_nsec - start.tv_nsec;
	    diff_t = seconds + nanoseconds*1e-9;
		if(DEBUG) printf("GEMM time: %f \n", diff_t); 	// exit(1);


		clock_gettime(CLOCK_REALTIME, &start);

		unpack_C(C, C_p, M, N, p, x, cake_cntx, sch); 

	    clock_gettime(CLOCK_REALTIME, &end);
	    seconds = end.tv_sec - start.tv_sec;
	    nanoseconds = end.tv_nsec - start.tv_nsec;
	    diff_t = seconds + nanoseconds*1e-9;
		if(DEBUG) printf("unpacking time: %f \n", diff_t); 	// exit(1);

		free(C_p);
	}


    clock_gettime(CLOCK_REALTIME, &end1);
    seconds = end1.tv_sec - start1.tv_sec;
    nanoseconds = end1.tv_nsec - start1.tv_nsec;
    diff_t = seconds + nanoseconds*1e-9;
	if(DEBUG) printf("full gemm time: %f \n", diff_t); 	// exit(1);

	// JONAS indside times
	printf("\ninside time: %f", diff_t);

	times = diff_t;

	if(!packedA) {
		free(sp_pack->loc); 
		free(sp_pack->nnz_outer); 
		free(sp_pack->k_inds); 
		free(sp_pack->mat_sp_p);
		free(sp_pack);
	}

	if(!packedB) free(B_p);
	free(x);

	return times;
}

