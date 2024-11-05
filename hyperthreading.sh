#!/bin/bash

# Get the number of physical cores
physical_cores=$(lscpu | grep "^Core(s) per socket:" | awk '{print $4}')
sockets=$(lscpu | grep "^Socket(s):" | awk '{print $2}')
total_physical_cores=$((physical_cores * sockets))

# Get the number of logical processors
logical_processors=$(lscpu | grep "^CPU(s):" | awk '{print $2}')

# Determine if Hyperthreading is enabled
if [ "$logical_processors" -gt "$total_physical_cores" ]; then
    echo "yesHype"
else
    echo "noHype"
fi
