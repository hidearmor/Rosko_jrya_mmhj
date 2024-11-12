#!/bin/bash

# Get the number of physical cores
physical_cores=$(lscpu | grep "^Core(s) per socket:" | awk '{print $4}')
sockets=$(lscpu | grep "^Socket(s):" | awk '{print $2}')
total_physical_cores=$((physical_cores * sockets))

# Get the number of logical processors
threads_per_core=$(lscpu | grep "^Thread(s) per core:" | awk '{print $4}')
logical_processors=$((total_physical_cores * threads_per_core))

# Determine if Hyperthreading is enabled
if [ "$logical_processors" -gt "$total_physical_cores" ]; then
    echo "yesHype"
else
    echo "noHype"
fi

