#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
BXA (Bayesian X-ray Analysis) for Xspec

Copyright: Johannes Buchner (C) 2013-2025

"""
from ultranest.integrator import ReactiveNestedSampler, resume_from_similar_file
from ultranest.plot import PredictionBand
import ultranest.stepsampler
import os
from math import isnan, isinf
import warnings
import numpy
import tempfile

from . import qq
from .sinning import binning

from xspec import Xset, AllModels, Fit, Plot
import xspec
import matplotlib.pyplot as plt
from tqdm import tqdm  # if this fails --> pip install tqdm


class XSilence:
	"""Context for temporarily making xspec quiet."""
	def __init__(self, chatter=0, logChatter=0):
		self.chatter = chatter
		self.logChatter = logChatter
	
	def __enter__(self):
		self.oldchatter = Xset.chatter, Xset.logChatter
		Xset.chatter, Xset.logChatter = self.chatter, self.logChatter

	def __exit__(self, *args):
		Xset.chatter, Xset.logChatter = self.oldchatter


def create_prior_function(transformations):
	"""
	Create a single prior transformation function from a list of
	transformations for each parameter. This assumes the priors factorize.
	"""

	def prior(cube):
		params = cube.copy()
		for i, t in enumerate(transformations):
			transform = t['transform']
			params[i] = transform(cube[i])
		return params

	return prior


def store_chain(chainfilename, transformations, posterior, fit_statistic):
	"""Writes a MCMC chain file in the same format as the Xspec chain command."""
	import astropy.io.fits as pyfits

	group_index = 1
	index_offsets = {1: 0}
	old_model = transformations[0]['model']

	indices = [t["index"] for t in transformations]
	names = []
	for t in transformations:
		if t['model'] != old_model:
			# we are assuming that the next model is referring to the next group
			group_index += 1
			# the parameter index is offset by the number of model parameters
			index_offsets[group_index] = index_offsets[group_index - 1] + old_model.nParameters
		old_model = t['model']
		try:
			original_parname = AllModels(group_index)(t["index"]).name
		except:
			original_parname = AllModels(1)(t["index"]).name
		names.append('%s__%d' % (original_parname, t['index'] + index_offsets.get(group_index, 0)))

	columns = [pyfits.Column(
		name=name, format='D', unit=AllModels(1)(transformations[i]["index"]).unit, array=t['aftertransform'](posterior[:, i]))
		for i, name in enumerate(names)]
	columns = list(numpy.array(columns)[numpy.argsort(indices)])

	columns.append(pyfits.Column(name='FIT_STATISTIC', format='D', array=fit_statistic))
	table = pyfits.ColDefs(columns)
	header = pyfits.Header()
	header.add_comment("""Created by BXA (Bayesian X-ray spectal Analysis) for Xspec""")
	header.add_comment("""refer to https://github.com/JohannesBuchner/BXA/""")
	header['TEMPR001'] = 1.
	header['STROW001'] = 1
	header['EXTNAME'] = 'CHAIN'
	tbhdu = pyfits.BinTableHDU.from_columns(table, header=header)
	tbhdu.writeto(chainfilename, overwrite=True)


def set_parameters(transformations, values):
	"""Set current parameters."""
	assert len(values) == len(transformations)
	pars = []
	for i, t in enumerate(transformations):
		v = t['aftertransform'](values[i])
		assert not isnan(v) and not isinf(v), 'ERROR: parameter %d (index %d, %s) to be set to %f' % (
			i, t['index'], t['name'], v)
		pars += [t['model'], {t['index']:v}]
	AllModels.setPars(*pars)

def get_isrc(erange="2.0 10.0", ispectrum=1, isource=1):
	"""
	Returns the index of the source in flux calculation of Xspec. The
	returned index is to be used BXASolver.create_flux_chain for isource
	parameter. Relevant when multiple sources are loaded (e.g. for
	multiple responses). Needs to be used when multiple sources are
	defined because the fluxes listed by Xspec are not ordered by source
	number.
	
	:param erange: energy range as in create_flux_chain.
	:param ispectrum: index of spectrum if multiple spectra are loaded.
	:param isource: index of source. In most cases 1.
	"""
	src = xspec.AllData(ispectrum)
	try:
		src.multiresponse[1]
	except Exception:
		# only one response, so the index has to be zero
		return 0
	# otherwise, need to parse calcFlux output:
	with tempfile.NamedTemporaryFile(suffix=".log") as tmp_file:
		log_path = tmp_file.name
	with XSilence(0, 10):
		Xset.openLog(log_path)
		AllModels.calcFlux(erange)
		Xset.closeLog()
	loglines = {}
	with open(log_path, 'r') as f:
		for line in f.readlines():
			line_short = line.replace('\n', '').strip()
			if line_short.startswith('Spectrum Number: '):
				curr_spec = line_short[17:]
				loglines[curr_spec] = []
			elif line_short.startswith('Source '):
				loglines[curr_spec].append(line_short[7:])
	ispectrum_str = '%s' % (ispectrum)
	isource_str = '%s' % (isource)
	if ispectrum_str in loglines and isource_str in loglines[ispectrum_str]:
		return numpy.where(numpy.asarray(loglines[ispectrum_str]) == isource_str)[0][0]
	else:
		raise ValueError('Spectrum %s not loaded, have only: %s' % (ispectrum, loglines))

class BXASolver(object):
	"""
	Run the Bayesian analysis.

	The nested sampling package `UltraNest <https://johannesbuchner.github.io/UltraNest/>`_ is used under the hood.

	If prior is None, uniform priors are used on the passed parameters.
	If parameters is also None, all thawed parameters are used.

	:param transformations: List of parameter transformation definitions
	:param prior_function: set only if you want to specify a custom, non-separable prior
	:param outputfiles_basename: prefix for output filenames.
	:param resume_from: prefix for output filenames of a previous run with similar posterior from which to resume

	More information on the concept of prior transformations is available at
	https://johannesbuchner.github.io/UltraNest/priors.html
	"""

	allowed_stats = ['cstat', 'cash', 'pstat']

	def __init__(
		self, transformations, prior_function=None, outputfiles_basename='chains/',
		resume_from=None
	):
		if prior_function is None:
			prior_function = create_prior_function(transformations)

		self.prior_function = prior_function
		self.transformations = transformations
		self.set_paramnames()
		self.vectorized = False

		# for convenience. Has to be a directory anyway for ultranest
		if not outputfiles_basename.endswith('/'):
			outputfiles_basename = outputfiles_basename + '/'

		if not os.path.exists(outputfiles_basename):
			os.mkdir(outputfiles_basename)

		self.outputfiles_basename = outputfiles_basename

		if resume_from is not None:
			self.paramnames, self.log_likelihood, self.prior_function, self.vectorized = resume_from_similar_file(
				os.path.join(resume_from, 'chains', 'weighted_post_untransformed.txt'),
				self.paramnames, loglike=self.log_likelihood, transform=self.prior_function,
				vectorized=False,
			)

	def set_paramnames(self, paramnames=None):
		if paramnames is None:
			self.paramnames = [str(t['name']) for t in self.transformations]
		else:
			self.paramnames = paramnames

	def set_best_fit(self):
		"""Sets model to the best fit values."""
		i = numpy.argmax(self.results['weighted_samples']['logl'])
		params = self.results['weighted_samples']['points'][i, :]
		set_parameters(transformations=self.transformations, values=params)

	def log_likelihood(self, params):
		""" returns -0.5 of the fit statistic."""
		set_parameters(transformations=self.transformations, values=params)
		like = -0.5 * Fit.statistic
		# print("like = %.1f" % like)
		if not numpy.isfinite(like):
			return -1e100
		return like

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

		# run nested sampling
		if Fit.statMethod.lower() not in BXASolver.allowed_stats:
			raise RuntimeError('ERROR: not using cash (Poisson likelihood) for Poisson data! set Fit.statMethod to cash before analysing (currently: %s)!' % Fit.statMethod)

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

		with XSilence():
			self.sampler = ReactiveNestedSampler(
				self.paramnames, self.log_likelihood, transform=self.prior_function,
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
			except Exception:
				import traceback
				traceback.print_exc()
				warnings.warn("plotting failed.")

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

	def create_flux_chain(self, spectrum, erange="2.0 10.0", nsamples=None, i_src=0):
		"""
		For each posterior sample, computes the flux in the given energy range.

		The so-created chain can be combined with redshift information to propagate
		the uncertainty. This is especially important if redshift is a variable
		parameter in the fit (with some prior).

		Returns erg/cm^2 energy flux (first column) and photon flux (second column)
		for each posterior sample.
		
		:param spectrum: spectrum to use for spectrum.flux
		:param erange: argument to AllModels.calcFlux, energy range
		:param nsamples: number of samples to consider (the default, None, means all)
		:param i_src: index of source in case multiple sources are defined. Can be obtained with function bxa.solver.get_isrc. 
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
				flux.append([f[6 * i_src + 0], f[6 * i_src + 3]])

			return numpy.array(flux)

	def posterior_predictions_convolved(
		self, component_names=None, plot_args=None, nsamples=400
	):
		"""Plot convolved model posterior predictions.

		Also returns data points for plotting.

		:param component_names: labels to use. Set to 'ignore' to skip plotting a component
		:param plot_args: matplotlib.pyplot.plot arguments for each component
		:param nsamples: number of posterior samples to use (lower is faster)
		"""
		# get data, binned to 10 counts
		# overplot models
		# can we do this component-wise?
		data = [None]  # bin, bin width, data and data error
		models = []    #
		if component_names is None:
			component_names = ['convolved model'] + ['component%d' for i in range(100-1)]
		if plot_args is None:
			plot_args = [{}] * 100
			for i, c in enumerate(plt.rcParams['axes.prop_cycle'].by_key()['color']):
				plot_args[i] = dict(color=c)
				del i, c
		bands = []
		Plot.background = True
		Plot.add = True

		for content in self.posterior_predictions_plot(plottype='counts', nsamples=nsamples):
			xmid = content[:, 0]
			ndata_columns = 6 if Plot.background else 4
			ncomponents = content.shape[1] - ndata_columns
			if data[0] is None:
				data[0] = content[:, 0:ndata_columns]
			model_contributions = []
			for component in range(ncomponents):
				y = content[:, ndata_columns + component]
				if component >= len(bands):
					bands.append(PredictionBand(xmid))
				bands[component].add(y)

				model_contributions.append(y)
			models.append(model_contributions)

		for band, label, component_plot_args in zip(bands, component_names, plot_args):
			if label == 'ignore': continue
			lineargs = dict(drawstyle='steps', color='k')
			lineargs.update(component_plot_args)
			shadeargs = dict(color=lineargs['color'])
			band.shade(alpha=0.5, **shadeargs)
			band.shade(q=0.495, alpha=0.1, **shadeargs)
			band.line(label=label, **lineargs)

		if Plot.background:
			results = dict(list(zip('bins,width,data,error,background,backgrounderr'.split(','), data[0].transpose())))
		else:
			results = dict(list(zip('bins,width,data,error'.split(','), data[0].transpose())))
		results['models'] = numpy.array(models)
		return results

	def posterior_predictions_unconvolved(
		self, component_names=None, plot_args=None, nsamples=400,
		plottype='model',
	):
		"""
		Plot unconvolved model posterior predictions.

		:param component_names: labels to use. Set to 'ignore' to skip plotting a component
		:param plot_args: list of matplotlib.pyplot.plot arguments for each component, e.g. [dict(color='r'), dict(color='g'), dict(color='b')]
		:param nsamples: number of posterior samples to use (lower is faster)
		:param plottype: type of plot string, passed to `xspec.Plot()`
		"""
		if component_names is None:
			component_names = ['model'] + ['component%d' for i in range(100-1)]
		if plot_args is None:
			plot_args = [{}] * 100
			for i, c in enumerate(plt.rcParams['axes.prop_cycle'].by_key()['color']):
				plot_args[i] = dict(color=c)
				del i, c
		Plot.add = True
		bands = []

		for content in self.posterior_predictions_plot(plottype=plottype, nsamples=nsamples):
			xmid = content[:, 0]
			ncomponents = content.shape[1] - 2
			for component in range(ncomponents):
				y = content[:, 2 + component]

				if component >= len(bands):
					bands.append(PredictionBand(xmid))
				bands[component].add(y)

		for band, label, component_plot_args in zip(bands, component_names, plot_args):
			if label == 'ignore': continue
			lineargs = dict(drawstyle='steps', color='k')
			lineargs.update(component_plot_args)
			shadeargs = dict(color=lineargs['color'])
			band.shade(alpha=0.5, **shadeargs)
			band.shade(q=0.495, alpha=0.1, **shadeargs)
			band.line(label=label, **lineargs)

	def posterior_predictions_plot(self, plottype, nsamples=None):
		"""
		Internal Routine used by posterior_predictions_unconvolved, posterior_predictions_convolved
		"""
		# for plotting, we don't need so many points, and especially the
		# points that barely made it into the analysis are not that interesting.
		# so pick a random subset of at least nsamples points
		posterior = self.posterior[:nsamples]

		with XSilence():
			olddevice = Plot.device
			Plot.device = '/null'

			# plot models
			maxncomp = 100 if Plot.add else 0
			for k, row in enumerate(tqdm(posterior, disable=None)):
				set_parameters(values=row, transformations=self.transformations)
				Plot(plottype)
				# get plot data
				if plottype == 'model':
					base_content = numpy.transpose([
						Plot.x(), Plot.xErr(), Plot.model()])
				elif Plot.background:
					base_content = numpy.transpose([
						Plot.x(), Plot.xErr(), Plot.y(), Plot.yErr(),
						Plot.backgroundVals(), numpy.zeros_like(Plot.backgroundVals()),
						Plot.model()])
				else:
					base_content = numpy.transpose([
						Plot.x(), Plot.xErr(), Plot.y(), Plot.yErr(),
						Plot.model()])
				# get additive components, if there are any
				comp = []
				for i in range(1, maxncomp):
					try:
						comp.append(Plot.addComp(i))
					except Exception:
						print('The error "***XSPEC Error: Requested array does not exist for this plot." can be ignored.')
						maxncomp = i
						break	
				content = numpy.hstack((base_content, numpy.transpose(comp).reshape((len(base_content), -1))))
				yield content
			Plot.device = olddevice
