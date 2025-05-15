#!/bin/bash

echo "Pi-DAQ @ $(date)"

cd $(dirname $0)

source venv/bin/activate

python3 -u pidaq_server.py	# -u for unbuffered, so output appears in the journal without delay.

e=$?

echo "Python exited with code $e."

echo "Pi-DAQ exiting @ $(date)"
