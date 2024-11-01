#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <sched.h>
#include <unistd.h>

std::vector<int> get_p_cores() {
    std::vector<int> p_cores;
    std::ifstream cpuinfo("/proc/cpuinfo");
    std::string line;
    
    // Read through /proc/cpuinfo
    while (std::getline(cpuinfo, line)) {
        if (line.find("core id") != std::string::npos) {
            std::istringstream iss(line);
            std::string key;
            int core_id;
            iss >> key >> key >> core_id;

            // Check for cache size or other identifiers to differentiate P-cores
            // Example for Raptor Cove
            std::getline(cpuinfo, line); // Move to the next line
            if (line.find("cache size") != std::string::npos && line.find("2 MB") != std::string::npos) {
                p_cores.push_back(core_id);
            }
        }
    }
    return p_cores;
}

void set_affinity(const std::vector<int>& p_cores) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);

    // Set affinity for P-cores
    for (int core : p_cores) {
        CPU_SET(core, &cpuset);
    }

    // Set the CPU affinity of the current thread
    if (sched_setaffinity(0, sizeof(cpu_set_t), &cpuset) == -1) {
        perror("sched_setaffinity");
    }
}

int main() {
    std::vector<int> p_cores = get_p_cores();
    
    if (p_cores.empty()) {
        std::cerr << "No Performance Cores found!" << std::endl;
        return 1;
    }

    set_affinity(p_cores);

    // Your matrix multiplication code here
    std::cout << "Running on Performance Cores!" << std::endl;

    return 0;
}
