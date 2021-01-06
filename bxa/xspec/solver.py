#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
BXA (Bayesian X-ray Analysis) for Xspec

Copyright: Johannes Buchner (C) 2013-2020

"""

from __future__ import print_function
from ultranest.solvecompat import pymultinest_solve_compat as solve
from ultranest.plot import PredictionBand
import os
from math import isnan, isinf
import numpy

from . import qq
from .sinning import binning

from xspec import Xset, AllModels, Fit, Plot
import xspec
import matplotlib.pyplot as plt
from tqdm import tqdm  # if this fails --> pip install tqdm
from .priors import *


class XSilence(object):
	"""Context for temporarily making xspec quiet."""
	def __enter__(self):
		self.oldchatter = Xset.chatter, Xset.logChatter
		Xset.chatter, Xset.logChatter = 0, 0

	def __exit__(self, *args):
		Xset.chatter, Xset.logChatter = self.oldchatter


def create_prior_function(transformations):
	"""
	Creates a single prior transformation function from parameter transformations
	"""

	def prior(cube):
		params = cube.copy()
		for i, t in enumerate(transformations):
			transform = t['transform']
			params[i] = transform(cube[i])
		return params

	return prior


def store_chain(chainfilename, transformations, posterior, fit_statistic):
	"""
	Writes a MCMC chain file in the same format as the Xspec chain command
	"""
	import astropy.io.fits as pyfits

	group_index = 1
	old_model = transformations[0]['model']
	names = []
	for t in transformations:
		if t['model'] != old_model:
			group_index += 1
		old_model = t['model']
		names.append('%s__%d' % (t['name'], t['index'] + (group_index - 1) * old_model.nParameters))

	columns = [pyfits.Column(
		name=name, format='D', array=t['aftertransform'](posterior[:, i]))
		for i, name in enumerate(names)]
	columns.append(pyfits.Column(name='FIT_STATISTIC', format='D', array=fit_statistic))
	table = pyfits.ColDefs(columns)
	header = pyfits.Header()
	header.add_comment("""Created by BXA (Bayesian X-ray spectal Analysis) for Xspec""")
	header.add_comment("""refer to https://github.com/JohannesBuchner/""")
	header['TEMPR001'] = 1.
	header['STROW001'] = 1
	header['EXTNAME'] = 'CHAIN'
	tbhdu = pyfits.BinTableHDU.from_columns(table, header=header)
	tbhdu.writeto(chainfilename, overwrite=True)


def set_parameters(transformations, values):
	"""
	Set current parameters.
	"""
	assert len(values) == len(transformations)
	pars = []
	for i, t in enumerate(transformations):
		v = t['aftertransform'](values[i])
		assert not isnan(v) and not isinf(v), 'ERROR: parameter %d (index %d, %s) to be set to %f' % (
			i, t['index'], t['name'], v)
		pars += [t['model'], {t['index']:v}]
	AllModels.setPars(*pars)


class BXASolver(object):
	"""
	Run the Bayesian analysis with specified parameters+transformations.

	If prior is None, uniform priors are used on the passed parameters.
	If parameters is also None, all thawed parameters are used.

	:param transformations: Parameter transformation definitions
	:param prior_function: set only if you want to specify a custom, non-separable prior
	:param outputfiles_basename: prefix for output filenames.
	"""

	allowed_stats = ['cstat', 'cash', 'pstat']

	def __init__(
		self, transformations, prior_function=None, outputfiles_basename='chains/'
	):
		if prior_function is None:
			prior_function = create_prior_function(transformations)

		self.prior_function = prior_function
		self.transformations = transformations
		self.set_paramnames()

		# for convenience. Has to be a directory anyway for ultranest
		if not outputfiles_basename.endswith('/'):
			outputfiles_basename = outputfiles_basename + '/'

		if not os.path.exists(outputfiles_basename):
			os.mkdir(outputfiles_basename)

		self.outputfiles_basename = outputfiles_basename

	def set_paramnames(self, paramnames=None):
		if paramnames is None:
			self.paramnames = [str(t['name']) for t in self.transformations]
		else:
			self.paramnames = paramnames

	def set_best_fit(self):
		"""
		Sets model to the best fit values.
		"""
		i = numpy.argmax(self.results['weighted_samples']['logl'])
		params = self.results['weighted_samples']['points'][i, :]
		set_parameters(transformations=self.transformations, values=params)

	def run(
		self, evidence_tolerance=0.5, n_live_points=400,
		wrapped_params=None, **kwargs
	):
		"""
		Run nested sampling with ultranest.

		:param n_live_points: number of live points (400 to 1000 is recommended).
		:param evidence_tolerance: uncertainty on the evidence to achieve
		:param resume: uncertainty on the evidence to achieve
		:param Lepsilon: numerical model inaccuracies in the statistic (default: 0.1).
			Increase if run is not finishing because it is trying too hard to resolve
			unimportant details caused e.g., by atable interpolations.
		:param frac_remain: fraction of the integration remainder allowed in the live points.
			Setting to 0.5 in mono-modal problems can be acceptable and faster.
			The default is 0.01 (safer).

		These are ultranest parameters (see ultranest.solve documentation!)
		"""

		def log_likelihood(params):
			set_parameters(transformations=self.transformations, values=params)
			like = -0.5 * Fit.statistic
			# print("like = %.1f" % like)
			if not numpy.isfinite(like):
				return -1e100
			return like

		# run multinest
		if Fit.statMethod.lower() not in BXASolver.allowed_stats:
			raise RuntimeError('ERROR: not using cash (Poisson likelihood) for Poisson data! set Fit.statMethod to cash before analysing (currently: %s)!' % Fit.statMethod)

		n_dims = len(self.paramnames)
		resume = kwargs.pop('resume', False)
		Lepsilon = kwargs.pop('Lepsilon', 0.1)

		with XSilence():
			self.results = solve(
				log_likelihood, self.prior_function, n_dims,
				paramnames=self.paramnames,
				outputfiles_basename=self.outputfiles_basename,
				resume=resume, Lepsilon=Lepsilon,
				n_live_points=n_live_points, evidence_tolerance=evidence_tolerance,
				seed=-1, max_iter=0, wrapped_params=wrapped_params, **kwargs
			)
			logls = [self.results['weighted_samples']['logl'][
				numpy.where(self.results['weighted_samples']['points'] == sample)[0][0]]
				for sample in self.results['samples']]
			self.posterior = self.results['samples']

			chainfilename = '%schain.fits' % self.outputfiles_basename
			store_chain(chainfilename, self.transformations, self.posterior, -2 * logls)
			xspec.AllChains.clear()
			xspec.AllChains += chainfilename

			# set current parameters to best fit
			self.set_best_fit()

		return self.results

	def create_flux_chain(self, spectrum, erange="2.0 10.0", nsamples=None):
		"""
		For each posterior sample, computes the flux in the given energy range.

		The so-created chain can be combined with redshift information to propagate
		the uncertainty. This is especially important if redshift is a variable
		parameter in the fit (with some prior).

		Returns erg/cm^2 energy flux (first column) and photon flux (second column)
		for each posterior sample.
		"""
		# prefix = analyzer.outputfiles_basename
		# modelnames = set([t['model'].name for t in transformations])

		with XSilence():
			# plot models
			flux = []
			for k, row in enumerate(tqdm(self.posterior[:nsamples], disable=None)):
				set_parameters(values=row, transformations=self.transformations)
				AllModels.calcFlux(erange)
				f = spectrum.flux
				# compute flux in current energies
				flux.append([f[0], f[3]])

			return numpy.array(flux)

	def posterior_predictions_convolved(
		self, component_names=None, plot_args=None, nsamples=400
	):
		"""
		Plot convolved model posterior predictions.
		Also returns data points for plotting.

		component_names: labels to use. Set to 'ignore' to skip plotting a component
		plot_args: matplotlib.pyplot.plot arguments for each component
		"""
		# get data, binned to 10 counts
		# overplot models
		# can we do this component-wise?
		data = [None]  # bin, bin width, data and data error
		models = []    #
		if component_names is None:
			component_names = [''] * 100
		if plot_args is None:
			plot_args = [{}] * 100
		bands = []
		Plot.background = True

		def plot_convolved_components(content):
			xmid = content[:, 0]
			ndata_columns = 6 if Plot.background else 4
			ncomponents = content.shape[1] - ndata_columns
			if data[0] is None:
				data[0] = content[:, 0:ndata_columns]
			model_contributions = []
			for component in range(ncomponents):
				y = content[:, ndata_columns + component]
				kwargs = dict(drawstyle='steps', alpha=0.1, color='k')
				kwargs.update(plot_args[component])

				label = component_names[component]
				# we only label the first time we enter here
				# otherwise we get lots of entries in the legend
				component_names[component] = ''
				if component >= len(bands):
					bands.append(PredictionBand(
						xmid,
						shadeargs=dict(color=kwargs['color']),
						lineargs=dict(color=kwargs['color'])))
				if label != 'ignore':
					# plt.plot(xmid, y, label=label, **kwargs)
					bands[component].add(y)

				model_contributions.append(y)
			models.append(model_contributions)

		self.posterior_predictions_plot(
			plottype='counts',
			callback=plot_convolved_components,
			nsamples=nsamples)

		for band, label in zip(bands, component_names):
			band.shade(alpha=0.5, label=label)
			band.shade(q=0.495, alpha=0.1)
			band.line()

		if Plot.background:
			results = dict(list(zip('bins,width,data,error,background,backgrounderr'.split(','), data[0].transpose())))
		else:
			results = dict(list(zip('bins,width,data,error'.split(','), data[0].transpose())))
		results['models'] = numpy.array(models)
		return results

	def posterior_predictions_unconvolved(
		self, component_names=None, plot_args=None, nsamples=400
	):
		"""
		Plot unconvolved model posterior predictions.

		:param component_names: labels to use. Set to 'ignore' to skip plotting a component
		:param plot_args: matplotlib.pyplot.plot arguments for each component
		:param nsamples: number of posterior samples to use
		"""
		if component_names is None:
			component_names = [''] * 100
		if plot_args is None:
			plot_args = [{}] * 100
		bands = []

		def plot_unconvolved_components(content):
			xmid = content[:, 0]
			ncomponents = content.shape[1] - 2
			for component in range(ncomponents):
				y = content[:, 2 + component]
				kwargs = dict(drawstyle='steps', alpha=0.1, color='k')
				kwargs.update(plot_args[component])

				label = component_names[component]
				# we only label the first time we enter here
				# otherwise we get lots of entries in the legend
				component_names[component] = ''
				if component >= len(bands):
					bands.append(PredictionBand(
						xmid,
						shadeargs=dict(color=kwargs['color']),
						lineargs=dict(color=kwargs['color'])))
				if label != 'ignore':
					# plt.plot(xmid, y, label=label, **kwargs)
					bands[component].add(y)

		self.posterior_predictions_plot(
			plottype='model',
			callback=plot_unconvolved_components,
			nsamples=nsamples)
		for band, label in zip(bands, component_names):
			band.shade(alpha=0.5, label=label)
			band.shade(q=0.495, alpha=0.1)
			band.line()

	def posterior_predictions_plot(self, plottype, callback, nsamples=None):
		"""
		Internal Routine used by posterior_predictions_unconvolved, posterior_predictions_convolved
		"""
		posterior = self.posterior
		# for plotting, we don't need so many points, and especially the
		# points that barely made it into the analysis are not that interesting.
		# so pick a random subset of at least nsamples points
		if nsamples is not None and len(posterior) > nsamples:
			if hasattr(numpy.random, 'choice'):
				chosen = numpy.random.choice(
					numpy.arange(len(posterior)),
					replace=False, size=nsamples)
			else:
				chosen = list(set(numpy.random.randint(
					0, len(posterior), size=10 * nsamples)))[:nsamples]
			posterior = posterior[chosen, :]
			assert len(posterior) == nsamples
		prefix = self.outputfiles_basename
		tmpfilename = os.path.join(os.path.dirname(prefix), os.path.basename(prefix).replace('.', '_') + '-wdatatmp.qdp')
		if os.path.exists(tmpfilename):
			os.remove(tmpfilename)

		with XSilence():
			olddevice = Plot.device
			Plot.device = '/null'
			# modelnames = set([t['model'].name for t in transformations])

			while len(Plot.commands) > 0:
				Plot.delCommand(1)
			Plot.addCommand('wdata "%s"' % tmpfilename.replace('.qdp', ''))

			# plot models
			for k, row in enumerate(tqdm(posterior, disable=None)):
				set_parameters(values=row, transformations=self.transformations)
				if os.path.exists(tmpfilename):
					os.remove(tmpfilename)
				xspec.Plot(plottype)
				content = numpy.genfromtxt(tmpfilename, skip_header=3)
				os.remove(tmpfilename)
				callback(content)
			xspec.Plot.device = olddevice
			while len(Plot.commands) > 0:
				Plot.delCommand(1)
			if os.path.exists(tmpfilename):
				os.remove(tmpfilename)


def standard_analysis(
	transformations, outputfiles_basename,
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
		transformations=transformations,
		outputfiles_basename=outputfiles_basename)
	solver.run(**kwargs)
	print('running analysis ... done')

	# analyse results
	print('analysing results...')
	if 'unconvolved' not in skipsteps:
		print('creating plot of posterior predictions ...')
		plt.figure()
		solver.posterior_predictions_unconvolved(nsamples=100)
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

	if 'convolved' not in skipsteps:
		print('creating plot of posterior predictions against data ...')
		plt.figure()
		data = solver.posterior_predictions_convolved(nsamples=100)
		# plot data
		# plt.errorbar(x=data['bins'], xerr=data['width'], y=data['data'], yerr=data['error'],
		# 	label='data', marker='o', color='green')
		# bin data for plotting
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

	if 'qq' not in skipsteps:
		print('creating quantile-quantile plot ...')
		solver.set_best_fit()
		plt.figure(figsize=(7, 7))
		qq.qq(outputfiles_basename, markers=5, annotate=True)
		print('saving plot...')
		plt.savefig(outputfiles_basename + 'qq_model_deviations.pdf', bbox_inches='tight')
		plt.close()

	return solver
