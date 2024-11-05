import subprocess

def get_num_cores_cake():
	ret1 = subprocess.check_output("grep -c ^processor /proc/cpuinfo", shell=True)
	ret2 = subprocess.check_output("lscpu | grep Thread -m 1 | tr -dc '0-9'", shell=True)
	ret3 = subprocess.check_output("lscpu | grep Socket -m 1 | tr -dc '0-9'", shell=True)
	return int(int(ret1) / (int(ret2)*int(ret3)))

def get_num_cores():
    ret1 = subprocess.check_output("grep -c ^processor /proc/cpuinfo", shell=True)
    total_double_threads = 0
    for i in range(1, int(ret1)+1):
        # print(str(i))
        # string = "lscpu | grep Thread -m 12 | tr -dc '0-9'"
        string = "lscpu | grep Thread -m " + str(i) + ""
        # string = "lscpu | grep Thread -m 1 | tr -dc '0-9'"
        ret2 = subprocess.check_output(string, shell=True)
        print(str(i), str(ret2))
        # if int(ret2) == 2:
        #     total_double_threads += 1
    # ret3 = subprocess.check_output("lscpu | grep Socket -m 1 | tr -dc '0-9'", shell=True)
	# return int(int(ret1) / (int(ret2)*int(ret3)))
    print(str(total_double_threads), str(ret1))

def get_cpu_info():
    # Get total logical cores
    logical_cores = int(subprocess.check_output("grep -c ^processor /proc/cpuinfo", shell=True))
    
    # Get the count for each core type and threading info
    lscpu_output = subprocess.check_output("lscpu", shell=True).decode("utf-8")
    
    # Initialize counts
    total_threads = 0
    a_core_count = 0  # Raptor Cove cores (2 threads per core)
    b_core_count = 0  # Gracemont cores (1 thread per core)

    # Parsing lscpu for detailed info about cores
    for line in lscpu_output.splitlines():
        if "Thread(s) per core:" in line:
            threads_per_core = int(line.split(":")[1].strip())
        elif "Core(s) per socket:" in line:
            cores_per_socket = int(line.split(":")[1].strip())
        elif "Socket(s):" in line:
            sockets = int(line.split(":")[1].strip())
        elif "CPU(s):" in line:
            # Total threads in the system
            total_threads = int(line.split(":")[1].strip())
        elif "Model name:" in line:
            # We can further customize here based on the model, if needed
            pass

    # Manually account for the CPU core setup:
    a_core_count = 6   # Raptor Cove A-cores with 2 threads each
    b_core_count = 8   # Gracemont B-cores with 1 thread each

    # Calculate total logical cores expected based on core counts and threads per core
    calculated_logical_cores = (a_core_count * 2) + (b_core_count * 1)

    # Return relevant core information
    return {
        "logical_cores_reported": logical_cores,
        "total_threads": total_threads,
        "a_cores": a_core_count,
        "b_cores": b_core_count,
        "calculated_logical_cores": calculated_logical_cores
    }

# cpu_info = get_cpu_info()
cpu_info = get_num_cores()
# print(cpu_info)
