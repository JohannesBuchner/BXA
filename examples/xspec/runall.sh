#!/bin/bash

# start from scratch
rm -rf simplest/ absorbed/ line/

# slow generating, to let us see what we did
cat gen.xspec | { 
	while read line; do echo "$line"; sleep 0.1; done; sleep 10;
} | xspec

# run the three models
coverage run -p example_simplest.py || exit 1
coverage run -p example_advanced_priors.py example-file.fak absorbed/  || exit 1
coverage run -p example_custom_run.py example-file.fak line/  || exit 1

# compare the evidences
coverage run -p model_compare.py absorbed simplest line || exit 1
