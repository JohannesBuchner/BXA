"""
Example of doing BXA in sherpa

Run with "sherpa example_simplest.py" or "python3 example_simplest.py"
"""
from sherpa.astro.ui import *
import bxa.sherpa as bxa

load_pha('example-file.fak')

set_stat('cstat')
ignore(None, 0.2)
ignore(8, None)
notice(0.2, 8.0)

# where to store intermediate and final results? 
# this is the prefix used
outputfiles_basename = 'simplest'

set_model(powlaw1d.mypow)

# set model parameters ranges
mypow.ampl.min = 1e-10
mypow.ampl.max = 10
mypow.gamma.min = 1
mypow.gamma.max = 3

# define prior
parameters = [mypow.gamma, mypow.ampl]
priors = [
	# uniform prior for Photon Index (see other example for 
	# something more advanced)
	bxa.create_uniform_prior_for(mypow.gamma),
	# jeffreys prior for scale variable
	bxa.create_jeffreys_prior_for(mypow.ampl),
	# and possibly many more parameters here
]
prior = bxa.create_prior_function(priors=priors)

# send it off!
solver = bxa.BXASolver(prior = prior, parameters = parameters,
	outputfiles_basename = outputfiles_basename)
results = solver.run(
	resume=True, # UltraNest supports resuming a crashed/aborted run
	)

exit()
