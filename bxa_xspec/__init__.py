import sys
import pymultinest
import os
import json
from math import log10, isnan, isinf

from xspec import Xset, AllModels, Fit

# priors
"""
Use for location variables (position)
The uniform prior gives equal weight in non-logarithmic scale.
"""
def create_uniform_prior_for(model, par):
	pval, pdelta, pmin, pbottom, ptop, pmax = par.values
	print '  uniform prior for %s between %f and %f ' % (par.name, pmin, pmax)
	# TODO: should we use min/max or bottom/top?
	low = float(pmin)
	spread = float(pmax - pmin)
	def uniform_transform(x): return x * spread + low
	return dict(model=model, index=par._Parameter__index, name=par.name, 
		transform=uniform_transform, aftertransform=lambda x: x)
"""
Use for scale variables (order of magnitude)
The Jeffreys prior gives equal weight to each order of magnitude between the
minimum and maximum value. Flat in logarithmic scale
"""
def create_jeffreys_prior_for(model, par):
	pval, pdelta, pmin, pbottom, ptop, pmax = par.values
	# TODO: should we use min/max or bottom/top?
	#print '  ', par.values
	print '  jeffreys prior for %s between %e and %e ' % (par.name, pmin, pmax)
	low = log10(pmin)
	spread = log10(pmax) - log10(pmin)
	def log_transform(x): return x * spread + low
	def log_after_transform(x): return 10**x
	return dict(model=model, index=par._Parameter__index, name=par.name, 
		transform=log_transform, aftertransform=log_after_transform)

"""
Pass your own prior weighting transformation
"""
def create_custom_prior_for(model, par, transform, aftertransform = lambda x: x):
	print '  custom prior for %s' % (par.name)
	return dict(model=model, index=par._Parameter__index, name=par.name, 
		transform=transform, aftertransform=aftertransform)

def create_prior_function(transformations):
	def prior(cube, ndim, nparams):
		try:
			for i, t in enumerate(transformations):
				transform = t['transform']
				cube[i] = transform(cube[i])
		except Exception as e:
			print 'ERROR: Exception in prior function. Faulty transformations specified!'
			print 'ERROR:', e
			print i, transformations[i]
			import sys
			sys.exit(-126)

	return prior

"""
Run the Bayesian analysis with specified parameters+transformations.

transformations: Parameter transformation definitions
prior_function: if you want to specify a custom (non-independent) prior
The remainder are multinest arguments (see PyMultiNest and MultiNest documentation!)
	outputfiles_basename: prefix to output files
		by default, chains/
	n_live_points: 400 are often enough
"""
def nested_run(transformations, prior_function = None, sampling_efficiency = 'model', 
	n_live_points = 1000, outputfiles_basename = 'chains/', 
	verbose=True, **kwargs):
	
	# for convenience
	if outputfiles_basename.endswith('/'):
		if not os.path.exists(outputfiles_basename):
			os.mkdir(outputfiles_basename)
	
	if prior_function is None:
		prior_function = create_prior_function(transformations)
	oldchatter = Xset.chatter, Xset.logChatter
	Xset.chatter = 0
	Xset.logChatter = 0
	print Xset.chatter, Xset.logChatter
	def log_likelihood(cube, ndim, nparams):
		try:
			pars = []
			for i, t in enumerate(transformations):
				v = t['aftertransform'](cube[i])
				assert not isnan(v) and not isinf(v), 'ERROR: parameter %d (index %d, %s) to be set to %f' % (
					i, j, t['name'], v)
				#print 'setting parameter %s to %f (transformed: %f)' % (t['name'], v, cube[i])
				pars += [t['model'], {t['index']:v}]
			AllModels.setPars(*pars)
			l = -0.5*Fit.statistic
			#print "like = %.1f" % l
			return l
		except Exception as e:
			print 'Exception in log_likelihood function: ', e
			sys.exit(-127)
		return -1e300
	# run multinest
	if Fit.statMethod.lower() not in ['cstat', 'cash']:
		raise RuntimeError('ERROR: not using cash (Poisson likelihood) for Poisson data! set Fit.statMethod to cash before analysing (currently: %s)!' % Fit.statMethod)
	
	n_params = len(transformations)
	pymultinest.run(log_likelihood, prior_function, n_params, 
		sampling_efficiency = sampling_efficiency, n_live_points = n_live_points, 
		outputfiles_basename = outputfiles_basename, 
		verbose=verbose, **kwargs)
	
	paramnames = [str(t['name']) for t in transformations]
	json.dump(paramnames, file('%sparams.json' % outputfiles_basename, 'w'), indent=2)
	Xset.chatter, Xset.logChatter = oldchatter

