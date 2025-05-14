#!/bin/bash

echo "Pi-DAQ @ $(date)"

cd $(dirname $0)

source venv/bin/activate

python3 pidaq_server.py

e=$?

echo "Python exited with code $e."

echo "Pi-DAQ exiting @ $(date)"