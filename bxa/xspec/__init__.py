#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
BXA (Bayesian X-ray Analysis) for Xspec

Copyright: Johannes Buchner (C) 2013-2014
"""

import pymultinest
import os
import json
from math import log10, isnan, isinf
import numpy

import plot
import qq
from sinning import binning

from xspec import Xset, AllModels, Fit, AllChains, Plot
import xspec
import matplotlib.pyplot as plt
import progressbar
from priors import *

def store_chain(chainfilename, transformations, posterior):
	"""
	Writes a MCMC chain file in the same format as the Xspec chain command
	"""
	import pyfits
	columns = [pyfits.Column(name='%s__%d' % (t['name'], t['index']), 
		format='D', array=t['aftertransform'](posterior[:,i]))
		for i, t in enumerate(transformations)]
	columns.append(pyfits.Column(name='FIT_STATISTIC', 
		format='D', array=posterior[:,-1]))
	table = pyfits.ColDefs(columns)
	header = pyfits.Header()
	header.add_comment("""Created by BXA (Bayesian X-ray spectal Analysis) for Xspec""")
	header.add_comment("""refer to https://github.com/JohannesBuchner/""")
	header.update('TEMPR001', 1.)
	header.update('STROW001', 1)
	tbhdu = pyfits.new_table(table, header = header)
	tbhdu.update_ext_name('CHAIN')
	tbhdu.writeto(chainfilename, clobber=True)

def set_parameters(transformations, values):
	"""
	Set current parameters.
	"""
	pars = []
	for i, t in enumerate(transformations):
		v = t['aftertransform'](values[i])
		assert not isnan(v) and not isinf(v), 'ERROR: parameter %d (index %d, %s) to be set to %f' % (
			i, t['index'], t['name'], v)
		pars += [t['model'], {t['index']:v}]
	AllModels.setPars(*pars)

def set_best_fit(analyzer, transformations):
	"""
	Set to best fit
	"""
	try:
		modes = analyzer.get_mode_stats()['modes']
		highestmode = sorted(modes, key=lambda x: x['local evidence'])[0]
		params = highestmode['maximum a posterior']
	except Exception as e:
		# modes were not described by MultiNest, last point instead
		pass
	params = analyzer.get_best_fit()['parameters']
	set_parameters(transformations=transformations, values=params)

def nested_run(transformations, prior_function = None, sampling_efficiency = 0.3, 
	n_live_points = 400, evidence_tolerance = 0.5,
	outputfiles_basename = 'chains/', verbose=True, **kwargs):
	"""
	Run the Bayesian analysis with specified parameters+transformations.

	If prior is None, uniform priors are used on the passed parameters.
	If parameters is also None, all thawed parameters are used.

	:param transformations: Parameter transformation definitions
	:param prior_function: set only if you want to specify a custom, non-separable prior
	:param outputfiles_basename: prefix for output filenames.
	The remainder are multinest arguments (see PyMultiNest and MultiNest documentation!)

	The remainder are multinest arguments (see PyMultiNest and MultiNest documentation!)
	n_live_points: 400 are often enough
	
	For quick results, use sampling_efficiency = 0.8, n_live_points = 50, 
	evidence_tolerance = 5.
	The real results must be estimated with sampling_efficiency = 0.3 
	and without using const_efficiency_mode, otherwise it is not reliable.
	"""
	
	# for convenience
	if outputfiles_basename.endswith('/'):
		if not os.path.exists(outputfiles_basename):
			os.mkdir(outputfiles_basename)
	
	if prior_function is None:
		prior_function = create_prior_function(transformations)
	oldchatter = Xset.chatter, Xset.logChatter
	Xset.chatter, Xset.logChatter = 0, 0
	def log_likelihood(cube, ndim, nparams):
		try:
			set_parameters(transformations=transformations, values=cube)
			l = -0.5*Fit.statistic
			#print "like = %.1f" % l
			return l
		except Exception as e:
			print 'Exception in log_likelihood function: ', e
			import sys
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
	json.dump(paramnames, file('%sparams.json' % outputfiles_basename, 'w'), indent=4)
	
	# store as chain too, and try to load it for error computations
	analyzer = pymultinest.Analyzer(n_params = len(transformations), 
		outputfiles_basename = outputfiles_basename)
	posterior = analyzer.get_equal_weighted_posterior()
	chainfilename = '%schain.fits' % outputfiles_basename
	store_chain(chainfilename, transformations, posterior)
	xspec.AllChains.clear()
	Xset.chatter, Xset.logChatter = oldchatter
	xspec.AllChains += chainfilename
	
	# set current parameters to best fit
	set_best_fit(analyzer, transformations)
	
	Xset.chatter, Xset.logChatter = oldchatter
	return analyzer

def create_flux_chain(analyzer, transformations, spectrum, erange = "2.0 10.0"):
	"""
	For each posterior sample, computes the flux in the given energy range.

	The so-created chain can be combined with redshift information to propagate
	the uncertainty. This is especially important if redshift is a variable
	parameter in the fit (with some prior).

	Returns erg/cm^2 energy flux (first column) and photon flux (second column)
	for each posterior sample.
	"""
	posterior = analyzer.get_equal_weighted_posterior()
	prefix = analyzer.outputfiles_basename
	modelnames = set([t['model'].name for t in transformations])

	oldchatter = Xset.chatter, Xset.logChatter
	Xset.chatter, Xset.logChatter = 0, 0
	# plot models
	flux = []
	pbar = progressbar.ProgressBar(
		widgets=[progressbar.Percentage(), progressbar.Counter('%5d'), 
		progressbar.Bar(), progressbar.ETA()],
		maxval=len(posterior)).start()
	for k, row in enumerate(posterior):
		set_parameters(parameters=row[:-1], transformations=transformations)
		AllModels.calcFlux(erange)
		f = spectrum.flux
		# compute flux in current energies
		f.append([f[0], f[3]])
		pbar.update(k)
	pbar.finish()
	
	Xset.chatter, Xset.logChatter = oldchatter		
	return numpy.array(flux)

def posterior_predictions_convolved(analyzer, transformations, 
	component_names = None, plot_args = None,
	nsamples = 400):
	"""
	Plot convolved model posterior predictions.
	Also returns data points for plotting.

	component_names: labels to use. Set to 'ignore' to skip plotting a component
	plot_args: matplotlib.pyplot.plot arguments for each component
	"""
	# get data, binned to 10 counts
	# overplot models
	# can we do this component-wise?
	data = [None] # bin, bin width, data and data error
	models = []    # 
	if component_names is None:
		component_names = [''] * 100
	if plot_args is None:
		plot_args = [{}] * 100

	def plot_convolved_components(content):
		xmid = content[:,0]
		ncomponents = content.shape[1] - 4
		if data[0] is None:
			data[0] = content[:,0:4]
		model_contributions = []
		for component in range(ncomponents):
			y = content[:, 4 + component]
			kwargs = dict(drawstyle='steps', alpha=0.1, color='k')
			kwargs.update(plot_args[component])
			
			label = component_names[component]
			# we only label the first time we enter here
			# otherwise we get lots of entries in the legend
			component_names[component] = ''
			if label != 'ignore':
				plt.plot(xmid, y, label=label, **kwargs)
			model_contributions.append(y)
		models.append(model_contributions)
	posterior_predictions_plot(plottype = 'counts', 
		callback = plot_convolved_components, 
		analyzer = analyzer, transformations = transformations,
		nsamples = nsamples)
	results = dict(zip('bins,width,data,error'.split(','), data[0].transpose()))
	results['models'] = numpy.array(models)
	return results


def posterior_predictions_unconvolved(analyzer, transformations, 
	component_names = None, plot_args = None,
	nsamples = 400):
	"""
	Plot unconvolved model posterior predictions.

	component_names: labels to use. Set to 'ignore' to skip plotting a component
	plot_args: matplotlib.pyplot.plot arguments for each component
	"""
	if component_names is None:
		component_names = [''] * 100
	if plot_args is None:
		plot_args = [{}] * 100
	def plot_unconvolved_components(content):
		xmid = content[:,0]
		ncomponents = content.shape[1] - 2
		for component in range(ncomponents):
			y = content[:, 2 + component]
			kwargs = dict(drawstyle='steps', alpha=0.1, color='k')
			kwargs.update(plot_args[component])
			
			label = component_names[component]
			# we only label the first time we enter here
			# otherwise we get lots of entries in the legend
			component_names[component] = ''
			if label != 'ignore':
				plt.plot(xmid, y, label=label, **kwargs)

	posterior_predictions_plot(plottype = 'model', 
		callback = plot_unconvolved_components, 
		analyzer = analyzer, transformations = transformations,
		nsamples = nsamples)


def posterior_predictions_plot(plottype, callback, analyzer, transformations,
	nsamples = None):
	"""
	Internal Routine used by posterior_predictions_unconvolved, posterior_predictions_convolved
	"""
	posterior = analyzer.get_equal_weighted_posterior()
	# for plotting, we don't need so many points, and especially the 
	# points that barely made it into the analysis are not that interesting.
	# so pick a random subset of at least nsamples points
	if nsamples is not None and len(posterior) > nsamples:
		if hasattr(numpy.random, 'choice'):
			chosen = numpy.random.choice(
				numpy.arange(len(posterior)), 
				replace=False, size=nsamples)
		else:
			chosen = list(set(numpy.random.randint(0, len(posterior),
				size=10*nsamples)))[:nsamples]
		posterior = posterior[chosen,:]
		assert len(posterior) == nsamples
	prefix = analyzer.outputfiles_basename
	tmpfilename = '%s-wdatatmp.qdp' % prefix
	
	olddevice = Plot.device
	Plot.device = '/null'
	modelnames = set([t['model'].name for t in transformations])
	
	while len(Plot.commands) > 0:
		Plot.delCommand(1)
	Plot.addCommand('wdata "%s"' % tmpfilename.replace('.qdp', ''))
	
	oldchatter = Xset.chatter, Xset.logChatter
	Xset.chatter, Xset.logChatter = 0, 0
	# plot models
	widgets = [progressbar.Percentage()]
	if hasattr(progressbar, 'Counter'):
		widgets += [progressbar.Counter('%5d')]
	widgets += [progressbar.Bar(), progressbar.ETA()]
	pbar = progressbar.ProgressBar(widgets=widgets, maxval=len(posterior)).start()
	for k, row in enumerate(posterior):
		set_parameters(values=row[:-1], transformations=transformations)
		if os.path.exists(tmpfilename):
			os.remove(tmpfilename)
		xspec.Plot(plottype)
		content = numpy.genfromtxt(tmpfilename, skip_header=3)
		os.remove(tmpfilename)
		callback(content)
		pbar.update(k)
	pbar.finish()
	Xset.chatter, Xset.logChatter = oldchatter
	xspec.Plot.device = olddevice


def standard_analysis(transformations, outputfiles_basename, 
	skipsteps = [], **kwargs):
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
	print 'running analysis ...'
	nested_run(transformations = transformations,
		outputfiles_basename = outputfiles_basename,
		**kwargs
		)
	print 'running analysis ... done'

	# analyse results
	print 'analysing results...'
	analyzer = pymultinest.Analyzer(n_params = len(transformations), 
		outputfiles_basename = outputfiles_basename)
	s = analyzer.get_stats()
	# store information in readable, hierarchical format
	json.dump(s, open(outputfiles_basename + 'stats.json', 'w'), indent=4)
	
	#   make marginal plots
	if 'marginals' not in skipsteps:
		print 'creating marginal plots...'
		plot.marginal_plots(analyzer)
	if 'unconvolved' not in skipsteps:
		print 'creating plot of posterior predictions ...'
		plt.figure()
		posterior_predictions_unconvolved(analyzer, transformations, nsamples = 100)
		ylim = plt.ylim()
		# 3 orders of magnitude at most
		plt.ylim(max(ylim[0], ylim[1] / 1000), ylim[1])
		plt.gca().set_yscale('log')
		if Plot.xAxis == 'keV':
			plt.xlabel('Energy [keV]')
		elif Plot.xAxis == 'channel':
			plt.xlabel('Channel')
		plt.ylabel('Counts/s/cm$^2$')
		print 'saving plot...'
		plt.savefig(outputfiles_basename + 'unconvolved_posterior.pdf', bbox_inches='tight')
		plt.close()
	if 'convolved' not in skipsteps:
		print 'creating plot of posterior predictions against data ...'
		plt.figure()
		data = posterior_predictions_convolved(analyzer, transformations, nsamples = 100)
		# plot data
		#plt.errorbar(x=data['bins'], xerr=data['width'], y=data['data'], yerr=data['error'],
		#	label='data', marker='o', color='green')
		# bin data for plotting
		binned = binning(outputfiles_basename = analyzer.outputfiles_basename, 
			bins = data['bins'], widths = data['width'], 
			data = data['data'], models = data['models'])
		for point in binned['marked_binned']:
			plt.errorbar(marker='o', **point)
		plt.xlim(binned['xlim'])
		plt.ylim(binned['ylim'][0], binned['ylim'][1]*2)
		plt.gca().set_yscale('log')
		if Plot.xAxis == 'keV':
			plt.xlabel('Energy [keV]')
		elif Plot.xAxis == 'channel':
			plt.xlabel('Channel')
		plt.ylabel('Counts/s/cm$^2$')
		print 'saving plot...'
		plt.savefig(outputfiles_basename + 'convolved_posterior.pdf', bbox_inches='tight')
		plt.close()
	
	if 'qq' not in skipsteps:
		print 'creating quantile-quantile plot ...'
		set_best_fit(analyzer, transformations)
		plt.figure(figsize=(7,7))
		qq.qq(analyzer = analyzer, markers = 5, annotate = True)
		print 'saving plot...'
		plt.savefig(outputfiles_basename + 'qq_model_deviations.pdf', bbox_inches='tight')
		plt.close()
	
	if 'summary' not in skipsteps:
		#   print out summary
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
	
	return analyzer





