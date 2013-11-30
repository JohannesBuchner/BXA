"""
Example of doing BXA in X-spec

Run with python example1.py example-file.fak absorbed-
"""
import sys
import scipy.stats
import bxa_xspec as bxa
from xspec import *

Fit.statMethod = 'cstat'

# first program argument is spectrum file
s = Spectrum(sys.argv[1])
# second program argument is output prefix
outputfiles_basename = sys.argv[2]

m = Model("wabs*pow")

# val, delta, min, bottom, top, max
m.wabs.nH.values = ",,0.01,0.01,1000,1000"
m.powerlaw.norm.values = ",,1e-5,1e-5,1e5,1e5"

def my_custom_prior(u):
	# prior distributions transform from 0:1 to the parameter range
	# here: a gaussian prior distribution, cut below 1/above 3
	x = scipy.stats.norm(1.9, 0.15).ppf(u)
	if x < 1.:
		x = 1
	if x > 3:
		x = 3
	return x

# define prior
transformations = [
	# jeffreys prior for nH (but see below)
	bxa.create_jeffreys_prior_for(m, m.wabs.nH),
	# jeffreys prior for scale variable
	bxa.create_jeffreys_prior_for(m, m.powerlaw.norm),
	# custom gaussian prior function for photon index
	bxa.create_custom_prior_for(  m, m.powerlaw.PhoIndex, my_custom_prior),
	# and possibly many more
]

# we want nH to come out in logarithmic values, without offset of 22
# so we shift the existing jeffreys prior transformation:
# first get the old transformation
prevtransform = transformations[0]['transform']
# shift it for storage
transformations[0]['transform'] = lambda x: prevtransform(x) + 22
# before putting it into xspec, we have to shift back and exponentiate
transformations[0]['aftertransform'] = lambda x: 10**(x - 22)

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


