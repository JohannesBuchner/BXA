#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
BXA (Bayesian X-ray Analysis) for Xspec

Copyright: Johannes Buchner (C) 2013-2020
"""

from __future__ import print_function

from . import qq
from .sinning import binning

from xspec import Plot
import matplotlib.pyplot as plt
from .priors import *
from .solver import BXASolver, XSilence, create_prior_function


def nested_run(
	transformations, prior_function=None,
	n_live_points=400, evidence_tolerance=0.5,
	outputfiles_basename='chains/', verbose=True, **kwargs
):
	"""
	Run the Bayesian analysis with specified parameters+transformations.

	If prior is None, uniform priors are used on the passed parameters.
	If parameters is also None, all thawed parameters are used.

	:param transformations: Parameter transformation definitions
	:param prior_function: set only if you want to specify a custom, non-separable prior
	:param outputfiles_basename: prefix for output filenames.

	The remainder are multinest arguments (see PyMultiNest and MultiNest documentation!)

	n_live_points=400 (default) is often enough.
	
	For quick results, use sampling_efficiency = 0.8, n_live_points = 50, 
	evidence_tolerance = 5.
	The real results must be estimated with sampling_efficiency = 0.3 
	and without using const_efficiency_mode, otherwise it is not reliable.
	"""
	solver = BXASolver(
		transformations=transformations, prior_function=prior_function, 
		outputfiles_basename=outputfiles_basename)
	return solver.run(n_live_points=n_live_points, evidence_tolerance=evidence_tolerance, **kwargs)


def standard_analysis(
	transformations, outputfiles_basename, 
	prior_function=None,
	skipsteps=[], **kwargs
):
	"""
	Default analysis which produces nice plots:
	
	* runs nested sampling analysis, creates MCMC chain file
	* marginal probabilities (1d and 2d)
	* model posterior predictions + data overplotted, convolved
	* model posterior predictions unconvolved
	* quantile-quantile plot with statistics
	* prints out summary of parameters
	* prints out model evidence
	
	Look at the source of this function to figure out how to do
	the individual parts. 
	Copy them to your scripts and adapt them to your needs.
	"""

	#   run multinest
	print('running analysis ...')
	solver = BXASolver(
		transformations=transformations, prior_function=prior_function, 
		outputfiles_basename=outputfiles_basename)
	solver.run(**kwargs)
	print('running analysis ... done')

	print('creating plot of posterior predictions ...')
	plt.figure()
	solver.posterior_predictions_unconvolved(transformations, nsamples=100)
	ylim = plt.ylim()
	# 3 orders of magnitude at most
	plt.ylim(max(ylim[0], ylim[1] / 1000), ylim[1])
	plt.gca().set_yscale('log')
	if Plot.xAxis == 'keV':
		plt.xlabel('Energy [keV]')
	elif Plot.xAxis == 'channel':
		plt.xlabel('Channel')
	plt.ylabel('Counts/s/cm$^2$')
	print('saving plot...')
	plt.savefig(outputfiles_basename + 'unconvolved_posterior.pdf', bbox_inches='tight')
	plt.close()

	print('creating plot of posterior predictions against data ...')
	plt.figure()
	data = solver.posterior_predictions_convolved(outputfiles_basename, transformations, nsamples=100)
	# plot data
	# plt.errorbar(x=data['bins'], xerr=data['width'], y=data['data'], yerr=data['error'],
	# 	label='data', marker='o', color='green')
	#  bin data for plotting
	print('binning for plot...')
	binned = binning(
		outputfiles_basename=outputfiles_basename, 
		bins=data['bins'], widths=data['width'], 
		data=data['data'], models=data['models'])
	for point in binned['marked_binned']:
		plt.errorbar(marker='o', zorder=-1, **point)
	plt.xlim(binned['xlim'])
	plt.ylim(binned['ylim'][0], binned['ylim'][1] * 2)
	plt.gca().set_yscale('log')
	if Plot.xAxis == 'keV':
		plt.xlabel('Energy [keV]')
	elif Plot.xAxis == 'channel':
		plt.xlabel('Channel')
	plt.ylabel('Counts/s/cm$^2$')
	print('saving plot...')
	plt.savefig(outputfiles_basename + 'convolved_posterior.pdf', bbox_inches='tight')
	plt.close()
	
	print('creating quantile-quantile plot ...')
	solver.set_best_fit()
	plt.figure(figsize=(7, 7))
	qq.qq(prefix=outputfiles_basename, markers=5, annotate=True)
	print('saving plot...')
	plt.savefig(outputfiles_basename + 'qq_model_deviations.pdf', bbox_inches='tight')
	plt.close()
	
	return solver
