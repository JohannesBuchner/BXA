#!/bin/bash

# start from scratch
rm -f simplest-resume.dat absorbed-resume.dat line-resume.dat

# slow generating, to let us see what we did
cat gen.xspec | { 
	while read line; do echo "$line"; sleep 0.1; done; sleep 10;
} | xspec

# run the three models in parallel (&)
python3 example_simplest.py &
python3 example_advanced_priors.py example-file.fak absorbed/ &
python3 example_custom_run.py example-file.fak line/ &

# wait until they are done
wait

# compare the evidences
python3 model_compare.py absorbed simplest line
