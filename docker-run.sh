#!/bin/sh
echo "Running docker image..."
if [ $# -eq 0 ]
    then
        echo "Pls provide user directory"
        exit 1
elif [ -d $1 ]
    then
        echo "Got user directory $1"
else 
    echo "Directory $1 invalid"
    exit 1
fi
OUTPUT_DIR=$(cd $1; pwd)
export OUTPUT_DIR

# Optional second argument for testcases directory
if [ $# -ge 2 ] && [ -d $2 ]; then
    TESTCASES_DIR=$(cd $2; pwd)
    export TESTCASES_DIR
    echo "Using testcases directory: $TESTCASES_DIR"
fi

echo "Running docker compose, OUTPUT_DIR=$OUTPUT_DIR"
docker compose up