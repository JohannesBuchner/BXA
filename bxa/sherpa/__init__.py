# -*- coding: utf-8 -*-
"""
Bayesian inference using (Py)MultiNest
"""
import os
if 'MAKESPHINXDOC' not in os.environ:
	import sherpa.astro.ui as ui
	#from sherpa.utils import get_keyword_defaults, sao_fcmp
	from sherpa.stats import Cash, CStat

import pymultinest
import numpy
from math import log10, isnan

# prior
def create_uniform_prior_for(parameter):
	"""
	Use for location variables (position)
	The uniform prior gives equal weight in non-logarithmic scale.
	"""
	spread = (parameter.max - parameter.min)
	low = parameter.min
	return lambda x: x * spread + low

def create_jeffreys_prior_for(parameter):
	"""
	Use for scale variables (order of magnitude)
	The Jeffreys prior gives equal weight to each order of magnitude between the
	minimum and maximum value. Flat in logarithmic scale.

	It is usually easier to create a ancillary Parameter, and make the actual parameter
	a function of it, like so::

		from sherpa.models.parameter import Parameter
		lognorm = Parameter(modelname='mycomponent', name='lognorm', val=-5, min=-4*2, max=0)
		powerlaw.norm = 10**lognorm
	"""
	low = log10(parameter.min)
	spread = log10(parameter.max) - log10(parameter.min)
	return lambda x: 10**(x * spread + low)


def create_prior_function(id=None, otherids=(), priors = [], parameters = None):
	"""
	Combine the prior transformations into a single function for pymultinest.

	If priors is empty, uniform priors are used on all passed parameters
	"""

	functions = []
	if priors == []:
		assert parameters is not None, "you need to pass the parameters if you want automatic uniform priors"
		thawedparmins  = [p.min for p in parameters]
		thawedparmaxes = [p.max for p in parameters]
		for low, high, i in zip(thawedparmins, thawedparmaxes, range(ndim)):
			functions.append(lambda x: x * (high - low) + low)
	else:
		functions = priors
    
	def prior_function(cube, ndim, nparams):
		for i in range(ndim):
			cube[i] = functions[i](cube[i])

	return prior_function

plot_best = False

def nested_run(id=None, otherids=(), prior = None, parameters = None, sampling_efficiency = 0.8, 
	n_live_points = 1000, outputfiles_basename = 'chains/', **kwargs):
	"""
	Run the Bayesian analysis with specified prior. 
	If prior is None, uniform priors are used on the passed parameters.
	If parameters is also None, all thawed parameters are used.

	The remainder are multinest arguments (see PyMultiNest and MultiNest documentation!)
	outputfiles_basename: prefix to output files
	n_live_points: 400 are often enough
	"""
	fit = ui._session._get_fit(id=id, otherids=otherids)[1]

	if not isinstance(fit.stat, (Cash, CStat)):
		raise RuntimeError("Fit statistic must be cash or cstat, not %s" %
			fit.stat.name)
    
	if parameters is None:
		parameters = fit.model.thawedpars
	def log_likelihood(cube, ndim, nparams):
		try:
			for i, p in enumerate(parameters):
				assert not isnan(cube[i]), 'ERROR: parameter %d (%s) to be set to %f' % (i, p.fullname, cube[i])
				p.val = cube[i]
				#print "%s: %f" % (p.fullname,p.val),
			l = -0.5*fit.calc_stat()
			#print "%.1f" % l
			return l
		except Exception as e:
			print 'Exception in log_likelihood function: ', e
			for i, p in enumerate(parameters):
				print '    Parameter %10s: %f --> %f [%f..%f]' % (p.fullname, p.val, cube[i], p.min, p.max)
			import sys
			sys.exit(-127)
		return -1e300


	if prior is None:
		prior = create_prior_function(id=id, otherids=otherids, parameters = parameters)
	n_params = len(parameters)
	pymultinest.run(log_likelihood, prior, n_params, 
		sampling_efficiency = sampling_efficiency, n_live_points = n_live_points, 
		outputfiles_basename = outputfiles_basename, **kwargs)

	import json
	m = ui._session._get_model(id)
	paramnames = map(lambda x: x.fullname, parameters)
	json.dump(paramnames, file('%sparams.json' % outputfiles_basename, 'w'), indent=2)
def set_best_fit(id=None, otherids=(), parameters = None, outputfiles_basename = 'chains/'):
	"""
	Sets model to the best fit values
	"""
	fit = ui._session._get_fit(id, otherids)[1]
	if parameters is None:
		parameters = fit.model.thawedpars
	a = pymultinest.analyse.Analyzer(n_params = len(parameters), outputfiles_basename = outputfiles_basename)
	try:
		modes = a.get_mode_stats()['modes']
		highestmode = sorted(modes, key=lambda x: x['local evidence'])[0]
		params = highestmode['maximum a posterior']
	except Exception as e:
		print "WARNING: modes were not described by MultiNest:", e
		print "Using last point instead"
		params = a.get_best_fit()['parameters']
	for p,v in zip(parameters, params):
		p.val = v

def get_distribution_with_fluxes(id=None, otherids=(), lo=None, hi=None, parameters = None, outputfiles_basename = 'chains/'):
	"""
	Returns an array of equally weighted posterior samples (parameter values) with two 
	additional columns: the photon fluxes and the energy fluxes. 

	The values will be correctly distributed according to the
	analysis run before.
	"""

	fit = ui._session._get_fit(id, otherids)[1]
	if parameters is None:
		parameters = fit.model.thawedpars
	a = pymultinest.analyse.Analyzer(n_params = len(parameters), outputfiles_basename = outputfiles_basename)
	r = []
	for row in a.get_equal_weighted_posterior():
		for p, v in zip(parameters, row):
			p.val = v
        	r.append(list(row) + [ui._session.calc_photon_flux(lo=lo, hi=hi, id=id), ui._session.calc_energy_flux(lo=lo, hi=hi, id=id)])
	return numpy.array(r)

def get_solutions_plot(id=None, otherids=(), lo=None, hi=None, parameters = None, outputfiles_basename = 'chains/'):
	"""
	Returns a sequence of unfolded spectra plots (note: set xlog, ylog, etc. before calling)
	based on equally weighted posterior points (parameter values)
	"""
	fit = ui._session._get_fit(id, otherids)[1]
	if parameters is None:
		parameters = fit.model.thawedpars
	a = pymultinest.analyse.Analyzer(n_params = len(parameters), outputfiles_basename = outputfiles_basename)
	r = []
	for row in a.get_equal_weighted_posterior():
		for p, v in zip(parameters, row):
			p.val = v
		r.append()
	return numpy.array(r)

def distribution_stats(distribution):
	return flux_distribution.mean(axis=0), flux_distribution.std(axis=0)


def photon_flux_histogram(distribution, nbins = None):
	flux_distribution = distribution[:,-2]
	if nbins is None:
		nbins = len(distribution)**0.5
	x, y = numpy.histogram(flux_distribution, bins=nbins)
	return numpy.vstack([y[:-1], y[1:], x]).transpose()


def energy_flux_histogram(distribution, nbins = None):
	flux_distribution = distribution[:,-1]
	if nbins is None:
		nbins = len(flux_distribution)**0.5
	x, y = numpy.histogram(flux_distribution, bins=nbins)
	return numpy.vstack([y[:-1], y[1:], x]).transpose()



