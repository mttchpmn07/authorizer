#!/bin/bash

# Get the list of Python processes
python_processes=$(tasklist | grep python)

# Check if there are any Python processes running
if [ -z "$python_processes" ]; then
    echo "No Python processes found."
    exit 0
fi

# Extract PIDs and kill the processes
while read -r line; do
    pid=$(echo "$line" | awk '{print $2}')
    taskkill -f -pid "$pid"
done <<< "$python_processes"

echo "All Python processes have been terminated."