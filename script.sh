#!/bin/bash

pip install selenium
pip install twilio

python tsa_data.py

sleep 30 &
process_id=$!
echo "PID: $process_id"
wait $process_id
echo "Exit status: $?"

dbxcli put throughput.csv throughput/throughput.csv