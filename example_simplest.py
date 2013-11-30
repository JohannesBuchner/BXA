"""
Example of doing BXA in X-spec
"""
import bxa_xspec as bxa
from xspec import *

Fit.statMethod = 'cstat'

s = Spectrum('example-file.fak')
m = Model("pow")

# set model parameters ranges
#                         val, delta, min, bottom, top, max
m.powerlaw.norm.values = ",,1e-5,1e-5,1e5,1e5" # 10^-5 .. 10^5
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
bxa.nested_run(transformations,
	outputfiles_basename = outputfiles_basename,
	verbose=True, # show a bit of progress
	resume=True, # MultiNest supports resuming a crashed/aborted run
	)

# analyse results
import pymultinest
import json
a = pymultinest.Analyzer(n_params = len(transformations), 
	outputfiles_basename = outputfiles_basename)
s = a.get_stats()
# store information in readable, hierarchical format
json.dump(s, open(outputfiles_basename + 'stats.json', 'w'))

print 
print 
print 'Parameter estimation summary'
print '****************************'
print 
print ' %20s: median, 10%%, q90%% quantile' % ('parameter name')
print ' ', '-'*20
for t, m in zip(transformations, s['marginals']):
	print ' %20s: %.3f  %.3f %.3f ' % (t['name'], m['median'], m['q10%'], m['q90%'])
print 
print ' (for pretty plots, run "multinest_marginals.py %s")' % outputfiles_basename
print 
print 'Model evidence: ln(Z) = %.2f +- %.2f' % (s['global evidence'], s['global evidence error'])
print 


