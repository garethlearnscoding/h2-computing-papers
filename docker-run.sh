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
echo "docker compose woah, $OUTPUT_DIR"
docker compose up