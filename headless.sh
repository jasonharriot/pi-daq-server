#!/bin/bash

echo "Pi DAQ Headless Plots @ $(date)"

cd $(dirname $0)

source venv/bin/activate

python3 headless_live.py

echo "Done @ $(date)"
