#!/bin/bash

# Define the number of iterations
iterations=10

# Loop through the specified number of iterations
for ((i = 1; i <= iterations; i++)); do
	echo "Running iteration $i/$iterations"
	./run_tests.sh staging/fuzz-test /home/neo/.local/wayfire/debug-build/bin/wayfire -j 8
done

echo "All iterations completed."
