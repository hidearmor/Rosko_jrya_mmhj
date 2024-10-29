The function `secret()` retrieves information about the system’s CPU configuration by running specific Linux commands. Here’s a step-by-step breakdown:

### Code Walkthrough

```python
def secret():
	ret1 = subprocess.check_output("grep -c ^processor /proc/cpuinfo", shell=True)
	ret2 = subprocess.check_output("lscpu | grep Thread -m 1 | tr -dc '0-9'", shell=True)
	ret3 = subprocess.check_output("lscpu | grep Socket -m 1 | tr -dc '0-9'", shell=True)
	return int(int(ret1) / (int(ret2)*int(ret3)))
```

#### Step-by-Step Explanation

1. **Imports**: 
   - This function likely assumes that `subprocess` has been imported earlier in the script. The `subprocess.check_output()` function allows it to run shell commands and capture their output as a byte string.

2. **Variable `ret1`**: 
   ```python
   ret1 = subprocess.check_output("grep -c ^processor /proc/cpuinfo", shell=True)
   ```
   - **Command**: `grep -c ^processor /proc/cpuinfo`
     - This command searches for lines starting with `processor` in the `/proc/cpuinfo` file, which provides CPU information on Linux systems.
     - The `-c` option counts the number of matches.
   - **Purpose**: The command counts the total number of logical CPU cores in the system.
   - **Output**: The result is a byte string representing the total logical cores, e.g., `b'16\n'` for a system with 16 logical cores.

3. **Variable `ret2`**:
   ```python
   ret2 = subprocess.check_output("lscpu | grep Thread -m 1 | tr -dc '0-9'", shell=True)
   ```
   - **Command**: `lscpu | grep Thread -m 1 | tr -dc '0-9'`
     - `lscpu` provides detailed CPU architecture information.
     - `grep Thread -m 1` searches for the first occurrence of "Thread" in the output, which typically appears in a line like `Thread(s) per core: 2`.
     - `tr -dc '0-9'` removes all non-numeric characters, leaving only the number (in this case, the threads per core count).
   - **Purpose**: This retrieves the number of threads per CPU core, which helps in identifying whether the CPU has hyper-threading or similar technologies enabled.
   - **Output**: This will be a byte string with the thread count, e.g., `b'2'` for two threads per core.

4. **Variable `ret3`**:
   ```python
   ret3 = subprocess.check_output("lscpu | grep Socket -m 1 | tr -dc '0-9'", shell=True)
   ```
   - **Command**: `lscpu | grep Socket -m 1 | tr -dc '0-9'`
     - `grep Socket -m 1` searches for the first occurrence of "Socket" in the output from `lscpu`, which typically appears in a line like `Socket(s): 1`.
     - `tr -dc '0-9'` removes all non-numeric characters, leaving only the number.
   - **Purpose**: This retrieves the number of CPU sockets, which helps determine the physical CPUs in a multi-socket system.
   - **Output**: The result is a byte string representing the socket count, e.g., `b'1'` for a single-socket system.

5. **Calculation**:
   ```python
   return int(int(ret1) / (int(ret2) * int(ret3)))
   ```
   - **Explanation**:
     - `int(ret1)`: Converts the byte string `ret1` to an integer, which is the total logical CPU core count.
     - `int(ret2)`: Converts `ret2` to an integer, representing threads per core.
     - `int(ret3)`: Converts `ret3` to an integer, representing the number of sockets.
   - **Formula**:
     - The formula calculates the number of physical CPU cores per socket as:
       \[
       \text{{physical cores per socket}} = \frac{{\text{{total logical cores}}}}{{\text{{threads per core}} \times \text{{sockets}}}}
       \]

#### Example

For a system with:
- **Total logical cores** (`ret1`) = 16
- **Threads per core** (`ret2`) = 2
- **Sockets** (`ret3`) = 1

The result would be:
\[
\frac{16}{2 \times 1} = 8
\]

So, the function would return `8`, indicating there are 8 physical cores per socket on this machine.