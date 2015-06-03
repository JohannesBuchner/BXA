#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
BXA (Bayesian X-ray Analysis) for Sherpa

Copyright: Johannes Buchner (C) 2013-2015
"""

import pymultinest
import os
from math import log10, isnan, isinf
if 'MAKESPHINXDOC' not in os.environ:
	import sherpa.astro.ui as ui
	from sherpa.stats import Cash, CStat

import numpy
from priors import *

plot_best = False

def nested_run(id=None, otherids=(), prior = None, parameters = None, 
	sampling_efficiency = 0.3, evidence_tolerance = 0.5,
	n_live_points = 400, outputfiles_basename = 'chains/', **kwargs):
	"""
	Run the Bayesian analysis with specified parameters+transformations.

	:param id: See the sherpa documentation of calc_stat.
	:param otherids: See the sherpa documentation of calc_stat.
	:param prior: prior function created with create_prior_function.
	:param parameters: List of parameters to analyse.
	:param outputfiles_basename: prefix for output filenames.
	
	If prior is None, uniform priors are used on the passed parameters.
	If parameters is also None, all thawed parameters are used.

	The remainder are multinest arguments (see PyMultiNest and MultiNest documentation!)
	n_live_points: 400 are often enough
	
	For quick results, use sampling_efficiency = 0.8, n_live_points = 50, 
	evidence_tolerance = 5. 
	The real results must be estimated with sampling_efficiency = 0.3,
	otherwise it is not reliable.
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
		outputfiles_basename = outputfiles_basename, evidence_tolerance=evidence_tolerance,
		**kwargs)

	import json
	m = ui._session._get_model(id)
	paramnames = map(lambda x: x.fullname, parameters)
	json.dump(paramnames, file('%sparams.json' % outputfiles_basename, 'w'), indent=2)

def set_best_fit(id=None, otherids=(), parameters = None, outputfiles_basename = 'chains/'):
	"""
	Sets model to the best fit values.
	"""
	fit = ui._session._get_fit(id, otherids)[1]
	if parameters is None:
		parameters = fit.model.thawedpars
	a = pymultinest.analyse.Analyzer(n_params = len(parameters), outputfiles_basename = outputfiles_basename)
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



