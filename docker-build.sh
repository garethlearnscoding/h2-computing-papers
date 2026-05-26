#!/bin/bash
set -e

echo "Building Docker image..."
docker build -t nj67-testcases:latest .

echo "Running tests..."
docker run --rm \
  --read-only \
  --tmpfs /tmp \
  --cap-drop=ALL \
  nj67-testcases:latest

docker run \
  --cpus 1 \
  --memory 256m \
  --pids-limit 50 \
  --read-only \
  --tmpfs \
  /tmp:size=64m \
  --security-opt no-new-privileges \
  --cap-drop=ALL \
  --user appuser \
  nj67-testcases:latest \

echo "✓ Build and tests passed!"