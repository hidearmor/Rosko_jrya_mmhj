#include <iostream>
#include <cstdio>
#include <cstdlib>
#include <cstring>

int get_num_physical_cores() {

	FILE *fp;
	char ret1[16];
	char command1[128];

	sprintf(command1, "grep -c ^processor /proc/cpuinfo");
	fp = popen(command1, "r");

	if (fp == NULL) {
		printf("Failed to run proc/cpuinfo command\n" );
		exit(1);
	}

	if(fgets(ret1, sizeof(ret1), fp) == NULL) {
		printf("cpuinfo error\n");
	}
	

	char ret2[16];
	char command2[128];

	sprintf(command2, "lscpu | grep Thread -m 1 | tr -dc '0-9'");
	fp = popen(command2, "r");

	if (fp == NULL) {
		printf("Failed to run lscpu | grep Thread command\n" );
		exit(1);
	}

	if(fgets(ret2, sizeof(ret2), fp) == NULL) {
		printf("lscpu error\n");
	}
	

	char ret3[16];
	char command3[128];

	sprintf(command3, "lscpu | grep Socket -m 1 | tr -dc '0-9'");
	fp = popen(command3, "r");

	if (fp == NULL) {
		printf("Failed to run lscpu | grep Socket command\n" );
		exit(1);
	}

	if(fgets(ret3, sizeof(ret3), fp) == NULL) {
		printf("lscpu error\n");
	}

	pclose(fp);
	return atoi(ret1) / (atoi(ret2)*atoi(ret3));
}



// find cache size at levels L1d,L1i,L2,and L3 using lscpu
int get_cache_size(int level) {

	int model_id, len, size = 0;
	FILE *fp;
	char ret[16];
	char command[128];

	sprintf(command, "lscpu | grep Model \
					| head -1 \
					| tr -dc '0-9'");
	fp = popen(command, "r");

	if (fp == NULL) {
		printf("Failed to run lscpu | grep Model command\n" );
		exit(1);
	}

	if(fgets(ret, sizeof(ret), fp) == NULL) {
		printf("lscpu error\n");
	}
	
	pclose(fp);
	model_id = atoi(ret);

	if(level == 1) {
		switch(model_id) {
			case 1:
				return (32 * (1 << 10));
			case 3:
				return (32 * (1 << 10));
			case 4:
				return (16 * (1 << 10));
			case 17:
				return (32 * (1 << 10));
			case 33:
				return (32 * (1 << 10));
			case 49:
				return (32 * (1 << 10));
			case 69:
				return (32 * (1 << 10));
			case 85:
				return (32 * (1 << 10));
			case 142:
				return (32 * (1 << 10));
			case 165:
				return (32 * (1 << 10));
			default:
				break;
		}
	}

	else if(level == 2) {
		switch(model_id) {
			case 1:
				return (512 * (1 << 10));
			case 3:
				return (32 * (1 << 10));
			case 4:
				return (16 * (1 << 10));
			case 17:
				return (512 * (1 << 10));
			case 33:
				return (512 * (1 << 10));
			case 49:
				return (512 * (1 << 10));
			case 69:
				return (256 * (1 << 10));
			case 85:
				return (1024 * (1 << 10));
			case 142:
				return (256 * (1 << 10));
			case 165:
				return (256 * (1 << 10));
			default:
				break;
		}
	}

	else if(level == 3) {
		switch(model_id) {
			case 1:
				return (64 * (1 << 20));
			case 3:
				return (1 * (1 << 20));
			case 4:
				return (512 * (1 << 10));
			case 17:
				return (4 * (1 << 20));
			case 33:
				return (64 * (1 << 20));
			case 49:
				return (128 * (1 << 20));
			case 69:
				return (4 * (1 << 20));
			case 85:
				return (36608 * (1 << 10));
			case 142:
				return (8 * (1 << 20));
			case 165:
				return (20 * (1 << 20));
			default:
				break;
		}
	}


	if(level < 3) {
		sprintf(command, "lscpu --caches=NAME,ONE-SIZE \
						| grep L%d \
						| grep -Eo '[0-9]*M|[0-9]*K|0-9*G' \
						| tr -d '\n'", level);
		fp = popen(command, "r");
	} else {
		sprintf(command, "lscpu --caches=NAME,ALL-SIZE \
						| grep L%d \
						| grep -Eo '[0-9]*M|[0-9]*K|0-9*G' \
						| tr -d '\n'", level);
		fp = popen(command, "r");
	}

	if (fp == NULL) {
		printf("Failed to run lscpu --caches command\n" );
		exit(1);
	}

	if(fgets(ret, sizeof(ret), fp) == NULL) {
		printf("lscpu error\n");
		// quick hack for raspberry pi 3 cache sizes (32 KiB L1, 512 KiB L2 shared)
		if(level == 2) {
			return (32 * (1 << 10));
		} else if(level == 3) {
			return (512 * (1 << 10));
		}
	}

	len = strlen(ret) - 1;

	// set cache size variables
	if(ret[len] == 'K') {
		ret[len] = '\0';
		size = atoi(ret) * (1 << 10);
	} else if(ret[len] == 'M') {
		ret[len] = '\0';
		size = atoi(ret) * (1 << 20);
	} else if(ret[len] == 'G') {
		ret[len] = '\0';
		size = atoi(ret) * (1 << 30);
	}

	return size;
}

// #include <iostream>
// #include <cstdio>
// #include <cstdlib>
// #include <cstring>

// int get_num_physical_cores() {
//     FILE *fp;
//     char ret1[16], ret2[16], ret3[16];

//     // Get total logical processors
//     fp = popen("grep -c ^processor /proc/cpuinfo", "r");
//     if (fp == NULL) {
//         std::cerr << "Failed to run proc/cpuinfo command\n";
//         exit(1);
//     }
//     if (fgets(ret1, sizeof(ret1), fp) == NULL) {
//         std::cerr << "cpuinfo error\n";
//     }
//     pclose(fp);

//     // Get threads per core
//     fp = popen("lscpu | grep Thread -m 1 | tr -dc '0-9'", "r");
//     if (fp == NULL) {
//         std::cerr << "Failed to run lscpu | grep Thread command\n";
//         exit(1);
//     }
//     if (fgets(ret2, sizeof(ret2), fp) == NULL) {
//         std::cerr << "lscpu error\n";
//     }
//     pclose(fp);

//     // Get number of sockets
//     fp = popen("lscpu | grep Socket -m 1 | tr -dc '0-9'", "r");
//     if (fp == NULL) {
//         std::cerr << "Failed to run lscpu | grep Socket command\n";
//         exit(1);
//     }
//     if (fgets(ret3, sizeof(ret3), fp) == NULL) {
//         std::cerr << "lscpu error\n";
//     }
//     pclose(fp);

//     return atoi(ret1) / (atoi(ret2) * atoi(ret3));
// }

// int get_cache_size(int level) {
//     int model_id, size = 0;
//     FILE *fp;
//     char ret[16], command[128];

//     fp = popen("lscpu | grep Model | head -1 | tr -dc '0-9'", "r");
//     if (fp == NULL) {
//         std::cerr << "Failed to run lscpu | grep Model command\n";
//         exit(1);
//     }
//     if (fgets(ret, sizeof(ret), fp) == NULL) {
//         std::cerr << "lscpu error\n";
//     }
//     pclose(fp);
//     model_id = atoi(ret);

//     if(level == 1) {
//         switch(model_id) {
//             case 1: case 3: case 17: case 33: case 49: case 69: case 85: case 142: case 165:
//                 return (32 * (1 << 10));
//             case 4:
//                 return (16 * (1 << 10));
//             default: break;
//         }
//     }
//     else if(level == 2) {
//         switch(model_id) {
//             case 1: case 17: case 33: case 49:
//                 return (512 * (1 << 10));
//             case 3: case 4:
//                 return (32 * (1 << 10));
//             case 69: case 142: case 165:
//                 return (256 * (1 << 10));
//             case 85:
//                 return (1024 * (1 << 10));
//             default: break;
//         }
//     }
//     else if(level == 3) {
//         switch(model_id) {
//             case 1: case 33:
//                 return (64 * (1 << 20));
//             case 3:
//                 return (1 * (1 << 20));
//             case 4:
//                 return (512 * (1 << 10));
//             case 17:
//                 return (4 * (1 << 20));
//             case 49:
//                 return (128 * (1 << 20));
//             case 69:
//                 return (4 * (1 << 20));
//             case 85:
//                 return (36608 * (1 << 10));
//             case 142:
//                 return (8 * (1 << 20));
//             case 165:
//                 return (20 * (1 << 20));
//             default: break;
//         }
//     }

//     // Command to retrieve cache size for unsupported model_ids
//     if(level < 3) {
//         sprintf(command, "lscpu --caches=NAME,ONE-SIZE | grep L%d | grep -Eo '[0-9]*M|[0-9]*K|0-9*G' | tr -d '\\n'", level);
//     } else {
//         sprintf(command, "lscpu --caches=NAME,ALL-SIZE | grep L%d | grep -Eo '[0-9]*M|[0-9]*K|0-9*G' | tr -d '\\n'", level);
//     }
    
//     fp = popen(command, "r");
//     if (fp == NULL) {
//         std::cerr << "Failed to run lscpu --caches command\n";
//         exit(1);
//     }

//     if (fgets(ret, sizeof(ret), fp) != NULL) {
//         int len = strlen(ret) - 1;
//         ret[len] = '\0';  // Remove last character for unit parsing
//         if(ret[len] == 'K') size = atoi(ret) * (1 << 10);
//         else if(ret[len] == 'M') size = atoi(ret) * (1 << 20);
//         else if(ret[len] == 'G') size = atoi(ret) * (1 << 30);
//     }
//     pclose(fp);
//     return size;
// }

int main() {
    int physical_cores = get_num_physical_cores();
    std::cout << "Physical cores: " << physical_cores << std::endl;

    for(int level = 1; level <= 3; ++level) {
        int cache_size = get_cache_size(level);
        std::cout << "Cache size at level L" << level << ": " << cache_size << " bytes" << std::endl;
    }

    return 0;
}
