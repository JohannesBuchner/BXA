"""
Example of doing BXA in X-spec

Run with "INFILE=example-file.fak OUTPUT=absorbed- sherpa example_advanced_priors.py"
"""
import os
import bxa.sherpa as bxa

# environment variable INFILE is spectrum file
load_pha(os.environ['INFILE'])

set_stat('cstat')
ignore(None, 0.2)
ignore(8, None)
notice(0.2, 8.0)

# environment variable OUTPUT is output prefix
outputfiles_basename = os.environ['OUTPUT']

set_model(xswabs.myabs*xspowerlaw.mypow)

myabs.nH.min = 0.01
myabs.nH.max = 1000
mypow.norm.min = 1e-10
mypow.norm.max = 10
mypow.PhoIndex.min = 1
mypow.PhoIndex.max = 3

# add ancillary parameter for NH, so we can work in nice logarithmic units
from sherpa.models.parameter import Parameter
lognH = Parameter(modelname='myabs', name='logNH', val=22, min=20, max=24)
myabs.nH = 10**(lognH - 22)

# define prior
parameters = [lognH, mypow.norm, mypow.PhoIndex]
priors = [
	# jeffreys prior for nH -- is uniform in lognH
	bxa.create_uniform_prior_for(lognH),
	# jeffreys prior for scale variable
	bxa.create_jeffreys_prior_for(mypow.norm),
	# custom gaussian prior function for photon index
	bxa.create_gaussian_prior_for(mypow.PhoIndex, 1.9, 0.15),
	# and possibly many more
]
prior = bxa.create_prior_function(priors=priors)

# send it off!
bxa.nested_run(prior = prior, parameters = parameters,
	outputfiles_basename = outputfiles_basename,
	verbose=True, # show a bit of progress
	resume=True, # MultiNest supports resuming a crashed/aborted run
	)

exit()

