#!/bin/bash

# start from scratch
rm -rf simplest/ absorbed/ line/

# slow generating, to let us see what we did
cat gen.xspec | { 
	while read line; do echo "$line"; sleep 0.1; done; sleep 10;
} | xspec

mkdir -p reference-output
mv example-file.gif_2 reference-output/data.gif

# run the three models
coverage run -p example_simplest.py || exit 1
coverage run -p example_advanced_priors.py example-file.fak absorbed/  || exit 1
coverage run -p example_custom_run.py example-file.fak line/  || exit 1

# compare the evidences
coverage run -p model_compare.py absorbed simplest line || exit 1

for prefix in absorbed simplest line
do
	convert -density 100 ${prefix}/plots/corner.pdf reference-output/${prefix}-corner.png
	convert -density 100 ${prefix}/convolved_posterior.pdf reference-output/${prefix}-convolved_posterior.png
	convert -density 100 ${prefix}/unconvolved_posterior.pdf reference-output/${prefix}-unconvolved_posterior.png
	convert -density 100 ${prefix}/qq_model_deviations.pdf reference-output/${prefix}-qq_model_deviations.png
	cp ${prefix}/plots/corner.pdf reference-output/${prefix}-corner.pdf
	cp ${prefix}/convolved_posterior.pdf reference-output/${prefix}-convolved_posterior.pdf
	cp ${prefix}/unconvolved_posterior.pdf reference-output/${prefix}-unconvolved_posterior.pdf
	cp ${prefix}/qq_model_deviations.pdf reference-output/${prefix}-qq_model_deviations.pdf
done

exit 0
