#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
BXA (Bayesian X-ray Analysis) for Sherpa

Copyright: Johannes Buchner (C) 2013-2020
"""

from __future__ import print_function
import os
import numpy
from math import isnan
from ultranest.integrator import ReactiveNestedSampler, resume_from_similar_file
import ultranest.stepsampler
import warnings
from .priors import create_prior_function

if 'MAKESPHINXDOC' not in os.environ:
	import sherpa.astro.ui as ui
	from sherpa.stats import Cash, CStat


def default_logging():
	import logging
	logging.basicConfig(filename='bxa.log', level=logging.DEBUG)
	logFormatter = logging.Formatter("[%(name)s %(levelname)s]: %(message)s")
	consoleHandler = logging.StreamHandler()
	consoleHandler.setFormatter(logFormatter)
	consoleHandler.setLevel(logging.INFO)
	logging.getLogger().addHandler(consoleHandler)


def distribution_stats(distribution):
	return distribution.mean(axis=0), distribution.std(axis=0)


def photon_flux_histogram(distribution, nbins=None):
	flux_distribution = distribution[:, -2]
	if nbins is None:
		nbins = len(distribution)**0.5
	x, y = numpy.histogram(flux_distribution, bins=nbins)
	return numpy.vstack([y[:-1], y[1:], x]).transpose()


def energy_flux_histogram(distribution, nbins=None):
	flux_distribution = distribution[:, -1]
	if nbins is None:
		nbins = len(flux_distribution)**0.5
	x, y = numpy.histogram(flux_distribution, bins=nbins)
	return numpy.vstack([y[:-1], y[1:], x]).transpose()


class BXASolver(object):
	def __init__(
		self, id=None, otherids=(), prior=None, parameters=None,
		outputfiles_basename='chains/',
		resume_from=None
	):
		"""
		Set up Bayesian analysis with specified parameters+transformations.

		:param id: See the sherpa documentation of calc_stat.
		:param otherids: See the sherpa documentation of calc_stat.
		:param prior: prior function created with create_prior_function.
		:param parameters: List of parameters to analyse.
		:param outputfiles_basename: prefix for output filenames.
		:param resume_from: prefix for output filenames of a previous run with similar posterior from which to resume

		If prior is None, uniform priors are used on the passed parameters.
		If parameters is also None, all thawed parameters are used.
		"""

		self.id = id
		self.otherids = otherids

		self.fit = ui._session._get_fit(self.id, self.otherids)[1]
		if parameters is None:
			parameters = self.fit.model.thawedpars
		if prior is None:
			prior = create_prior_function(id=id, otherids=otherids, parameters=parameters)

		self.prior = prior
		self.parameters = parameters
		self.outputfiles_basename = outputfiles_basename
		self.set_paramnames()
		self.allowed_stats = (Cash, CStat)
		self.ndims = len(parameters)
		self.vectorized = False

		if resume_from is not None:
			self.paramnames, self.log_likelihood, self.prior_transform, self.vectorized = resume_from_similar_file(
				os.path.join(resume_from, 'chains', 'weighted_post_untransformed.txt'),
				self.paramnames, loglike=self.log_likelihood, transform=self.prior_transform,
				vectorized=False,
			)

	def set_paramnames(self, paramnames=None):
		if paramnames is None:
			self.paramnames = [p.fullname for p in self.parameters]
		else:
			self.paramnames = paramnames

	def get_fit(self):
		return self.fit

	def prior_transform(self, cube):
		"""unit cube transformation.

		see https://johannesbuchner.github.io/UltraNest/priors.html#Dependent-priors
		"""
		params = cube.copy()
		self.prior(params, self.ndims, self.ndims)
		return params

	def log_likelihood(self, cube):
		""" returns -0.5 of the fit statistic."""
		try:
			for i, p in enumerate(self.parameters):
				assert not isnan(cube[i]), 'ERROR: parameter %d (%s) to be set to %f' % (i, p.fullname, cube[i])
				p.val = cube[i]
				# print "%s: %f" % (p.fullname,p.val),
			return -0.5 * self.fit.calc_stat()
		except Exception as e:
			print('Exception in log_likelihood function: ', e)
			for i, p in enumerate(self.parameters):
				print('    Parameter %10s: %f --> %f [%f..%f]' % (p.fullname, p.val, cube[i], p.min, p.max))
			raise e

	def run(
		self, sampler_kwargs={'resume': 'overwrite'}, run_kwargs={'Lepsilon': 0.1},
		speed="safe", resume=None, n_live_points=None,
		frac_remain=None, Lepsilon=0.1, evidence_tolerance=None
	):
		"""Run nested sampling with ultranest.

		:sampler_kwargs: arguments passed to ReactiveNestedSampler (see ultranest documentation)
		:run_kwargs: arguments passed to ReactiveNestedSampler.run() (see ultranest documentation)

		The following arguments are also available directly for backward compatibility:

		:param resume: sets sampler_kwargs['resume']='resume' if True, otherwise 'overwrite'
		:param n_live_points: sets run_kwargs['min_num_live_points']
		:param evidence_tolerance: sets run_kwargs['dlogz']
		:param Lepsilon: sets run_kwargs['Lepsilon']
		:param frac_remain: sets run_kwargs['frac_remain']
		"""

		fit = self.fit
		if False and not isinstance(fit.stat, self.allowed_stats):
			raise RuntimeError("Fit statistic must be cash or cstat, not %s" % fit.stat.name)

		if resume is not None:
			sampler_kwargs['resume'] = 'resume' if resume else 'overwrite'
		run_kwargs['Lepsilon'] = run_kwargs.pop('Lepsilon', Lepsilon)
		del Lepsilon
		if evidence_tolerance is not None:
			run_kwargs['dlogz'] = run_kwargs.pop('dlogz', evidence_tolerance)
		del evidence_tolerance
		if frac_remain is not None:
			run_kwargs['frac_remain'] = run_kwargs.pop('frac_remain', frac_remain)
		del frac_remain
		if n_live_points is not None:
			run_kwargs['min_num_live_points'] = run_kwargs.pop('min_num_live_points', n_live_points)
		del n_live_points

		self.sampler = ReactiveNestedSampler(
			self.paramnames, self.log_likelihood, transform=self.prior_transform,
			log_dir=self.outputfiles_basename,
			vectorized=self.vectorized, **sampler_kwargs)

		if speed == "safe":
			pass
		elif speed == "auto":
			region_filter = run_kwargs.pop('region_filter', True)
			self.sampler.run(max_ncalls=40000, **run_kwargs)

			self.sampler.stepsampler = ultranest.stepsampler.SliceSampler(
				nsteps=1000,
				generate_direction=ultranest.stepsampler.generate_mixture_random_direction,
				adaptive_nsteps='move-distance', region_filter=region_filter
			)
		else:
			self.sampler.stepsampler = ultranest.stepsampler.SliceSampler(
				generate_direction=ultranest.stepsampler.generate_mixture_random_direction,
				nsteps=speed,
				adaptive_nsteps=False,
				region_filter=False)

		self.sampler.run(**run_kwargs)
		self.sampler.print_results()
		self.results = self.sampler.results
		try:
			self.sampler.plot()
		except Exception as e:
			import traceback
			traceback.print_exc()
			warnings.warn("plotting failed.")

		self.set_best_fit()
		return self.results

	def set_best_fit(self):
		"""Sets model to the best fit values."""
		i = numpy.argmax(self.results['weighted_samples']['logl'])
		for p, v in zip(self.parameters, self.results['weighted_samples']['points'][i, :]):
			p.val = v

	def get_distribution_with_fluxes(self, elo=None, ehi=None):
		"""Computes flux posterior samples.

		Returns an array of equally weighted posterior samples (parameter values) with two
		additional columns: the photon fluxes and the energy fluxes.

		The values will be correctly distributed according to the
		analysis run before.
		"""

		r = []
		for row in self.results['samples']:
			for p, v in zip(self.parameters, row):
				p.val = v
			r.append(
				list(row) + [
					ui._session.calc_photon_flux(lo=elo, hi=ehi, id=self.id),
					ui._session.calc_energy_flux(lo=elo, hi=ehi, id=self.id)])
		return numpy.array(r)
