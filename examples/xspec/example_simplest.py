"""
Example of doing BXA in X-spec
"""
import bxa.xspec as bxa
from xspec import *

Fit.statMethod = 'cstat'
Plot.xAxis = 'keV'

s = Spectrum('example-file.fak')
s.ignore("**"); s.notice("0.2-8.0")
m = Model("pow")

# set model parameters ranges
#                         val, delta, min, bottom, top, max
m.powerlaw.norm.values = ",,1e-10,1e-10,1e1,1e1" # 10^-10 .. 10
m.powerlaw.PhoIndex.values = ",,1,1,3,3"       #     1 .. 3

# define prior
transformations = [
	# uniform prior for Photon Index (see other example for 
	# something more advanced)
	bxa.create_uniform_prior_for( m, m.powerlaw.PhoIndex),
	# jeffreys prior for scale variable
	bxa.create_jeffreys_prior_for(m, m.powerlaw.norm),
	# and possibly many more parameters here
]
# where to store intermediate and final results? this is the prefix used
outputfiles_basename = 'simplest-'

# send it off!
bxa.standard_analysis(transformations,
	outputfiles_basename = outputfiles_basename,
	verbose=True, # show a bit of progress
	resume=True, # MultiNest supports resuming a crashed/aborted run
	)

