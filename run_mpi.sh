#!/bin/bash

# Set the number of processes
num_processes=5

# Specify the MPI command
mpi_cmd="mpiexec"

# Add any additional MPI options or arguments here
# For example, if you're using Open MPI:
# mpi_cmd+=" --hostfile hostfile.txt"  # Specify the hostfile if needed
# mpi_cmd+=" -np $num_processes"       # Specify the number of processes

# Add the Python script and its arguments here
# For example:
# mpi_cmd+=" python processing_node.py"

# Run the MPI command
$mpi_cmd python processing_node.py