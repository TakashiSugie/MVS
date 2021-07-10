#!/bin/bash
set -e

python autoSaveAllDir.py
python myRun.py
python setData4Poisson.py

