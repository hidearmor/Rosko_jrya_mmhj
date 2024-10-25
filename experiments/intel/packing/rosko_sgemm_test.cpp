#include "rosko.h"
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <numeric>
#include <stdlib.h>

// Comparison function for qsort
int compare(const void *a, const void *b) {
	return (*(double*)a > *(double*)b) - (*(double*)a < *(double*)b);
}

double calculate_median(double* array, int runs) {
    qsort(array, runs, sizeof(double), compare);
    return (runs % 2 == 0) ?
		((array[runs / 2 - 1] + array[runs / 2]) / 2.0) :
		(array[runs / 2]);
}

double calculate_mean(double* array, int runs)
{
    return std::accumulate( array, array + runs, 0.0) / (double)(runs);
}

double calculate_mean(int* array, int runs)
{
    return std::accumulate( array, array + runs, 0.0) / (double)(runs);
}

int main( int argc, char** argv ) {

	int M, K, N, p, sp, nz, mr, nr, ntrials, store, runs, warmup = 3; // why segmentation fault at 4 and up? I think I have to free up the dirty space
	struct timespec start, end;
	long seconds, nanoseconds;
	int  rosko_byte_i, csr_byte_i;
	double rosko_time_i, rosko_bw_i, csr_time_i, csr_bw_i;
	float density;
	enum sched sch = KMN;
	// struct stat buffer;
	// csr_t* csr;

	M = atoi(argv[1]);
	K = atoi(argv[2]);
	N = 10000;
	p = atoi(argv[3]);
	sp = atoi(argv[4]);
	// argv[5] = csr_file
	// argv[6] = rosko_file
	store = atoi(argv[7]);
	runs = atoi(argv[8]);

	printf("M = %d, K = %d, N = %d, cores = %d, sparsity = %f, runs = %d\n", M,K,N,p, ((float) sp) / 100.0, runs);

	// // preparations/setup
	// float* A = (float*) malloc(M * K * sizeof( float ));
    // srand(time(NULL));
	// nz = rand_sparse(A, M, K, ((float) sp) / 100.0);
	// density = ((float) nz) / ((float) (((float) M) * ((float) K)));
	// cake_cntx_t* cake_cntx = cake_query_cntx();
	// update_mr_nr(cake_cntx, 30, 128);



	// --------------- NEW --------------------

	double csr_times[runs], csr_bws[runs], rosko_bws[runs], rosko_times[runs];
	int csr_bytes[runs], rosko_bytes[runs];

	// for (int i = 0; i < (runs); i++) {
	for (int i = 0; i < (runs + warmup); i++) {

		// declarations from top
		struct stat buffer;
		csr_t* csr;

		// preparations/setup
		float* A = (float*) malloc(M * K * sizeof( float ));
		srand(time(NULL));
		nz = rand_sparse(A, M, K, ((float) sp) / 100.0);
		density = ((float) nz) / ((float) (((float) M) * ((float) K)));
		cake_cntx_t* cake_cntx = cake_query_cntx();
		update_mr_nr(cake_cntx, 30, 128);

		// measure MKL-CSR packing DRAM bw
		// csr_times[i] = mat_to_csr_file(A, M, K, argv[5]);
		csr_time_i = mat_to_csr_file(A, M, K, argv[5]);
		stat(argv[5], &buffer);
		// csr_bytes[i] = buffer.st_size;
		csr_byte_i = buffer.st_size;
		csr = file_to_csr(argv[5]);
		// printf("csr pack time: %f \n", csr_times[i]); 
		// printf("csr bytes: %d \n", csr_bytes[i]); 

		// measure Rosko packing DRAM bw
		// is t his block supposed to be by itself ?
		// clock_gettime(CLOCK_REALTIME, &start); // Jonas this was moved
		blk_dims_t* x = (blk_dims_t*) malloc(sizeof(blk_dims_t));
		init_sparse_block_dims(M, N, K, p, x, cake_cntx, sch, NULL, density, 4, 0);
		size_t A_sz = cake_sgemm_packed_A_size(M, K, p, x, cake_cntx, sch) / sizeof(float);
		float* A_p = (float*) calloc(A_sz, sizeof(float));
		sp_pack_t* sp_pack = (sp_pack_t*) malloc(sizeof(sp_pack_t));

		clock_gettime(CLOCK_REALTIME, &start);
		pack_A_sp_k_first(A, A_p, M, K, p, sp_pack, x, cake_cntx);
		clock_gettime(CLOCK_REALTIME, &end);
		seconds = end.tv_sec - start.tv_sec;
		nanoseconds = end.tv_nsec - start.tv_nsec;

		// why M*K*4 here ?
		// csr_bws[i] = ((float) (csr_bytes[i] + M*K*4)) / csr_times[i] / 1e9;
		csr_bw_i = ((float) (csr_byte_i + M*K*4)) / csr_time_i / 1e9;

		// here below TIME's are set/calculated 
		// rosko_times[i] = seconds + nanoseconds*1e-9;
		rosko_time_i = seconds + nanoseconds*1e-9;
		// printf("rosko pack time: %f \n", rosko_time);

		sp_pack_t* sp_pack1 = malloc_sp_pack(M, K, nz, x, cake_cntx);
		pack_A_csr_to_sp_k_first(csr, M, K, nz, p, sp_pack1, x, cake_cntx);
		sp_pack_to_file(sp_pack1, argv[6]);
		stat(argv[6], &buffer);
		// rosko_bytes[i] = buffer.st_size;
		rosko_byte_i = buffer.st_size;
		// printf("rosko bytes: %d \n", rosko_bytes[i]); 

		// rosko_bws[i] = ((float) (rosko_bytes[i] + M*K*4)) / rosko_times[i] / 1e9;
		rosko_bw_i = ((float) (rosko_byte_i + M*K*4)) / rosko_time_i / 1e9;
		
		if (i >= warmup) { // don't count warmup runs in the recorded results
			rosko_times[i] = rosko_time_i;
			rosko_bws[i] = rosko_bw_i;
			rosko_bytes[i] = rosko_byte_i;

			csr_times[i] = csr_time_i;
			csr_bws[i] = csr_bw_i;
			csr_bytes[i] = csr_byte_i;
		}

		// free resources per run for cache
		free_sp_pack(sp_pack1);
		free(A_p);
		free(sp_pack);
		free(x);

		// fordi det er kopieret ind i loopet
		free_csr(csr);
		free(A);
	}
	
	// double csr_time 	= calculate_median(csr_times, runs);
	// double rosko_time 	= calculate_median(rosko_times, runs);
	// float csr_bw 		= calculate_median(csr_bws, runs);
	// float rosko_bw 		= calculate_median(rosko_bws, runs);

	double csr_time 		= calculate_mean(csr_times, runs);
	double rosko_time 		= calculate_mean(rosko_times, runs);
	float csr_bw 			= calculate_mean(csr_bws, runs);
	float rosko_bw 			= calculate_mean(rosko_bws, runs);
	float csr_bytes_agv		= calculate_mean(csr_bytes, runs); 
	float rosko_bytes_agv	= calculate_mean(rosko_bytes, runs); 

	printf("csr pack time: %f \n", csr_time); 
	printf("rosko pack time median: %f \n", rosko_time);

	printf("rosko bw = %f, csr bw = %f\n", rosko_bw, csr_bw);
	printf("runs %d", runs);


    char fname[50];
    snprintf(fname, sizeof(fname), "result_pack");
    FILE *fp;
    fp = fopen(fname, "a");
    fprintf(fp, "rosko bw,%d,%d,%d,%d,%d,%f,%d\n",store,M,K,N,sp,rosko_bw,runs);
    fprintf(fp, "mkl bw,%d,%d,%d,%d,%d,%f,%d\n",store,M,K,N,sp,csr_bw,runs);
    fprintf(fp, "rosko time,%d,%d,%d,%d,%d,%f,%d\n",store,M,K,N,sp,rosko_time,runs);
    fprintf(fp, "mkl time,%d,%d,%d,%d,%d,%f,%d\n",store,M,K,N,sp,csr_time,runs);

	// JONAS addition
    fprintf(fp, "rosko bytes,%d,%d,%d,%d,%d,%f,%d\n",store,M,K,N,sp,rosko_bytes_agv,runs);
    fprintf(fp, "mkl bytes,%d,%d,%d,%d,%d,%f,%d\n",store,M,K,N,sp,csr_bytes_agv,runs);


    fclose(fp);

	// fordi jeg har kopieret det ind i loopet	
	// free_csr(csr);
	// free(A);

	return 0;

// -------------- OLD ---------------------

	// // measure MKL-CSR packing DRAM bw

	// double csr_time = mat_to_csr_file(A, M, K, argv[5]);
	// stat(argv[5], &buffer);
	// int csr_bytes = buffer.st_size;
	// csr = file_to_csr(argv[5]);
	// // printf("csr pack time: %f \n", csr_time); 
	// // printf("csr bytes: %d \n", csr_bytes); 


	// // measure Rosko packing DRAM bw
	// blk_dims_t* x = (blk_dims_t*) malloc(sizeof(blk_dims_t));
	// init_sparse_block_dims(M, N, K, p, x, cake_cntx, sch, NULL, density, 4, 0);
	// size_t A_sz = cake_sgemm_packed_A_size(M, K, p, x, cake_cntx, sch) / sizeof(float);
    // float* A_p = (float*) calloc(A_sz, sizeof(float));
	// sp_pack_t* sp_pack = (sp_pack_t*) malloc(sizeof(sp_pack_t));

	// clock_gettime(CLOCK_REALTIME, &start);
	// pack_A_sp_k_first(A, A_p, M, K, p, sp_pack, x, cake_cntx);
	// clock_gettime(CLOCK_REALTIME, &end);
	// seconds = end.tv_sec - start.tv_sec;
	// nanoseconds = end.tv_nsec - start.tv_nsec;

	// float csr_bw = ((float) (csr_bytes + M*K*4)) / csr_time / 1e9;

	// // here below TIME's are set/calculated 
	// double rosko_time = seconds + nanoseconds*1e-9;
	// printf("rosko pack time: %f \n", rosko_time); 

	// sp_pack_t* sp_pack1 = malloc_sp_pack(M, K, nz, x, cake_cntx);
	// pack_A_csr_to_sp_k_first(csr, M, K, nz, p, sp_pack1, x, cake_cntx);
	// sp_pack_to_file(sp_pack1, argv[6]);
	// stat(argv[6], &buffer);
	// int rosko_bytes = buffer.st_size;
	// printf("rosko bytes: %d \n", rosko_bytes); 

	// float rosko_bw = ((float) (rosko_bytes + M*K*4)) / rosko_time / 1e9;



	// printf("rosko bw = %f, csr bw = %f\n", rosko_bw, csr_bw);


    // char fname[50];
    // snprintf(fname, sizeof(fname), "result_pack");
    // FILE *fp;
    // fp = fopen(fname, "a");
    // fprintf(fp, "rosko bw,%d,%d,%d,%d,%d,%f\n",store,M,K,N,sp,rosko_bw);
    // fprintf(fp, "mkl bw,%d,%d,%d,%d,%d,%f\n",store,M,K,N,sp,csr_bw);
    // fprintf(fp, "rosko time,%d,%d,%d,%d,%d,%f\n",store,M,K,N,sp,rosko_time);
    // fprintf(fp, "mkl time,%d,%d,%d,%d,%d,%f\n",store,M,K,N,sp,csr_time);

    // fclose(fp);
	
	// free_csr(csr);
	// free(A);

	// free_sp_pack(sp_pack1);
	// free(A_p);
	// free(sp_pack);
	// free(x);

	// return 0;

	// -----------------------------------
}


