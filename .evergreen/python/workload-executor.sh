#!/bin/sh
set -o errexit  # Exit the script with error if any of the commands fail

"$PYMONGO_PYTHON_RUNTIME" "$TARGET_DRIVER_SCRIPTS_DIRECTORY/workload-executor.py" "$1" "$2"
