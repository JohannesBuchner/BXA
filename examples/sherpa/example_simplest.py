"""
Example of doing BXA in X-spec

Run with "sherpa example_simplest.py"
"""
import bxa.sherpa as bxa

load_pha('example-file.fak')

set_stat('cstat')
ignore(None, 0.2)
ignore(8, None)
notice(0.2, 8.0)

# where to store intermediate and final results? 
# this is the prefix used
outputfiles_basename = 'simplest-'

set_model(xspowerlaw.mypow)

# set model parameters ranges
mypow.norm.min = 1e-10
mypow.norm.max = 10
mypow.PhoIndex.min = 1
mypow.PhoIndex.max = 3

# define prior
parameters = [mypow.PhoIndex, mypow.norm]
priors = [
	# uniform prior for Photon Index (see other example for 
	# something more advanced)
	bxa.create_uniform_prior_for(mypow.PhoIndex),
	# jeffreys prior for scale variable
	bxa.create_jeffreys_prior_for(mypow.norm),
	# and possibly many more parameters here
]
prior = bxa.create_prior_function(priors=priors)

# send it off!
bxa.nested_run(prior = prior, parameters = parameters,
	outputfiles_basename = outputfiles_basename,
	verbose=True, # show a bit of progress
	resume=True, # MultiNest supports resuming a crashed/aborted run
	)

exit()

