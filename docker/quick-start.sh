#!/bin/bash
set -e

# docker pull colmap/colmap:latest
docker build -t colmap/colmap:latest .
docker run --gpus all -w /working -v $1:/working -it colmap/colmap:latest;
