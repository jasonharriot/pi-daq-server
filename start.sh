#!/bin/bash

echo "Pi-DAQ @ $(date)"

cd $(dirname $0)

sudo ifconfig eth0 192.168.1.2

e=$?

if [ $e -eq "0" ]; then
	echo "Set an ipv4 address on the interface."
else
	echo "Failed to set an ipv4 address. ($e)"
fi

source venv/bin/activate

python3 -u pi_daq_server.py	# -u for unbuffered, so output appears in the journal without delay.

e=$?

echo "Python exited with code $e."

echo "Pi-DAQ exiting @ $(date)"
