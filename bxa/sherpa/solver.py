#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
BXA (Bayesian X-ray Analysis) for Sherpa

Copyright: Johannes Buchner (C) 2013-2019
"""

from __future__ import print_function
import os
from math import isnan
import matplotlib
matplotlib.use('Agg')
from ultranest.solvecompat import pymultinest_solve_compat as solve

if 'MAKESPHINXDOC' not in os.environ:
	import sherpa.astro.ui as ui
	from sherpa.stats import Cash, CStat

import numpy

from .priors import create_prior_function

def default_logging():
	import logging
	logging.basicConfig(filename='bxa.log',level=logging.DEBUG)
	logFormatter = logging.Formatter("[%(name)s %(levelname)s]: %(message)s")
	consoleHandler = logging.StreamHandler()
	consoleHandler.setFormatter(logFormatter)
	consoleHandler.setLevel(logging.INFO)
	logging.getLogger().addHandler(consoleHandler)

def distribution_stats(distribution):
	return distribution.mean(axis=0), distribution.std(axis=0)


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


plot_best = False

class BXASolver(object):
	def __init__(self, id, otherids=(), prior = None, parameters = None,
		outputfiles_basename = 'chains/'):
		self.id = id
		self.otherids = otherids

		fit = self.get_fit()
		if parameters is None:
			parameters = fit.model.thawedpars
		if prior is None:
			prior = create_prior_function(id=id, otherids=otherids, parameters = parameters)
		
		self.prior = prior
		self.parameters = parameters
		self.outputfiles_basename = outputfiles_basename
		self.set_paramnames()
		self.allowed_stats = (Cash, CStat)
	
	def set_paramnames(self, paramnames=None):
		if paramnames is None:
			self.paramnames = [p.fullname for p in self.parameters]
		else:
			self.paramnames = paramnames

	
	def get_fit(self):
		return ui._session._get_fit(self.id, self.otherids)[1]
	
	def run(self,
		evidence_tolerance = 0.5,
		n_live_points = 400,
		wrapped_params = None, **kwargs):
		
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

		fit = self.get_fit()
		if False and not isinstance(fit.stat, self.allowed_stats):
			raise RuntimeError("Fit statistic must be cash or cstat, not %s" %
				fit.stat.name)
		
		def prior_transform(cube):
			params = cube.copy()
			self.prior(params, n_dims, n_dims)
			return params
		
		def log_likelihood(cube):
			try:
				for i, p in enumerate(self.parameters):
					assert not isnan(cube[i]), 'ERROR: parameter %d (%s) to be set to %f' % (i, p.fullname, cube[i])
					p.val = cube[i]
					#print "%s: %f" % (p.fullname,p.val),
				l = -0.5 * fit.calc_stat()
				#print "%.1f" % l
				return l
			except Exception as e:
				print('Exception in log_likelihood function: ', e)
				for i, p in enumerate(self.parameters):
					print('    Parameter %10s: %f --> %f [%f..%f]' % (p.fullname, p.val, cube[i], p.min, p.max))
				#import sys
				#sys.exit(-127)
				raise Exception("Model evaluation problem") from e
			return -1e300
		
		n_dims = len(self.parameters)
		resume = kwargs.pop('resume', False)
		Lepsilon = kwargs.pop('Lepsilon', 0.1)

		self.results = solve(log_likelihood, prior_transform, n_dims,
			paramnames=self.paramnames,
			outputfiles_basename=self.outputfiles_basename,
			resume=resume, Lepsilon=Lepsilon,
			n_live_points=n_live_points, evidence_tolerance=evidence_tolerance,
			seed=-1, max_iter=0, wrapped_params=wrapped_params, **kwargs
		)
		self.set_best_fit()
		return self.results

	def set_best_fit(self):
		"""
		Sets model to the best fit values.
		"""
		i = numpy.argmax(self.results['weighted_samples']['L'])
		for p, v in zip(self.parameters, self.results['weighted_samples']['v'][i,:]):
			p.val = v

	def get_distribution_with_fluxes(self, elo=None, ehi=None):
		"""
		Returns an array of equally weighted posterior samples (parameter values) with two 
		additional columns: the photon fluxes and the energy fluxes. 

		The values will be correctly distributed according to the
		analysis run before.
		"""

		r = []
		for row in self.results['samples']:
			for p, v in zip(self.parameters, row):
				p.val = v
			r.append(list(row) + [ui._session.calc_photon_flux(lo=elo, hi=ehi, id=self.id), 
				ui._session.calc_energy_flux(lo=elo, hi=ehi, id=self.id)])
		return numpy.array(r)

