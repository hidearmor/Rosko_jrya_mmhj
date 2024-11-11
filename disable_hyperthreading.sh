# #!/bin/bash

#################################################
#Check if hyperthreading is on (it is on if output is 'on')
cat /sys/devices/system/cpu/smt/control

# Do this to disable hyperthreading:
sudo bash -c 'echo off > /sys/devices/system/cpu/smt/control'

# Do this to enable hyperthreading:
# sudo bash -c 'echo on > /sys/devices/system/cpu/smt/control'


#################################################
# DID NOT USE THIS, DON'T KNOW IF IT WORKS

# typeset -i core_id
# typeset -i sibling_id
# typeset -i state

# for i in /sys/devices/system/cpu/cpu[0-9]*; 
# do
#     core_id="${i##*cpu}"
#     sibling_id="-1"
    
#     if [ -f ${i}/topology/thread_siblings_list ]; then
#         sibling_id="$(cut -d',' -f1 ${i}/topology/thread_siblings_list)"
#     fi
    
#     if [ $core_id -ne $sibling_id ]; then
#         state="$(<${i}/online)"
#         echo -n "$((1-state))" > "${i}/online"
#         echo "switched ${i}/online to $((1-state))"
#     fi
# done