#!/bin/bash

#
# -1- Create the test data
bash create_simdata.sh

#
# -2- Run the test script
python example_script.py > "example_output/example_script_run.log" 2>&1
