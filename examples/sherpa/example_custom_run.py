"""
Example of doing BXA in X-spec

Run with python example_advanced_priors.py example-file.fak absorbed-
"""
from __future__ import print_function
import sys
import scipy.stats
import bxa.xspec as bxa
from xspec import *

Fit.statMethod = 'cstat'
Plot.xAxis = 'keV'

# first program argument is spectrum file
s = Spectrum(sys.argv[1])
s.ignore("**"); s.notice("0.2-8.0")

# second program argument is output prefix
outputfiles_basename = sys.argv[2]

m = Model("wabs*pow + gauss")

# val, delta, min, bottom, top, max
m.wabs.nH.values = ",,0.01,0.01,1000,1000"
m.powerlaw.norm.values = ",,1e-10,1e-10,1e1,1e1"
m.gaussian.norm.values = ",,1e-10,1e-10,1e1,1e1"
m.gaussian.LineE.values = ",,6,6,8,8"
m.gaussian.Sigma.values = ",,0.001,0.001,1,1"

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
	# jeffreys prior for scale variable
	bxa.create_jeffreys_prior_for(m, m.gaussian.norm),
	# uniform prior for location variable
	bxa.create_uniform_prior_for(m, m.gaussian.LineE),
	# jeffreys prior for scale variable
	bxa.create_jeffreys_prior_for(m, m.gaussian.Sigma),
]

# we want nH to come out in logarithmic values, without offset of 22
# so we shift the existing jeffreys prior transformation:
# first get the old transformation
prevtransform = transformations[0]['transform']
# shift it for storage
transformations[0]['transform'] = lambda x: prevtransform(x) + 22
# before putting it into xspec, we have to shift back and exponentiate
transformations[0]['aftertransform'] = lambda x: 10**(x - 22)

# send it off manually: do the analysis
bxa.nested_run(transformations = transformations,
	outputfiles_basename = outputfiles_basename,
	verbose = True,
	resume = True,
	)
import pymultinest
# get the results
analyzer = pymultinest.Analyzer(n_params = len(transformations), 
		outputfiles_basename = outputfiles_basename)
# make marginal plots
bxa.plot.marginal_plots(analyzer)
# print out evidence
s = analyzer.get_stats()
print('Model evidence: ln(Z) = %.2f +- %.2f' % (s['global evidence'], s['global evidence error']))
# store stats
import json
json.dump(s, open(outputfiles_basename + 'stats.json', 'w'), indent=4)





