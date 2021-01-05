#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from __future__ import print_function

"""
BXA (Bayesian X-ray Analysis) for Sherpa

Copyright: Johannes Buchner (C) 2013-2015

Priors
"""
from math import log10
import numpy
from . import invgauss

def create_uniform_prior_for(parameter):
	"""
	Use for location variables (position)
	The uniform prior gives equal weight in non-logarithmic scale.
	
	:param parameter: Parameter to create a prior for. E.g. xspowerlaw.mypowerlaw.PhoIndex
	"""
	spread = (parameter.max - parameter.min)
	low = parameter.min
	return lambda x: x * spread + low

def create_jeffreys_prior_for(parameter):
	"""deprecated name for create_loguniform_prior_for"""
	return create_loguniform_prior_for(parameter)

def create_loguniform_prior_for(parameter):
	"""
	Use for scale variables (order of magnitude)
	The Jeffreys prior gives equal weight to each order of magnitude between the
	minimum and maximum value. Flat in logarithmic scale.
	
	:param parameter: Parameter to create a prior for. E.g. xspowerlaw.mypowerlaw.norm

	It is usually easier to create an ancillary parameter, and link the 
	actual parameter, like so::

		from sherpa.models.parameter import Parameter
		lognorm = Parameter(modelname='mycomponent', name='lognorm', val=-5, min=-4*2, max=0)
		powerlaw.norm = 10**lognorm

	"""
	low = log10(parameter.min)
	spread = log10(parameter.max) - log10(parameter.min)
	return lambda x: 10**(x * spread + low)


def create_gaussian_prior_for(parameter, mean, std):
	"""
	Use for informed variables.
	The Gaussian prior weights by a Gaussian in the parameter. If you 
	would like the logarithm of the parameter to be weighted by
	a Gaussian, create a ancillary parameter (see create_jeffreys_prior_for).
	
	:param parameter: Parameter to create a prior for. E.g. xspowerlaw.mypowerlaw.PhoIndex

	"""
	lo = parameter.min
	hi = parameter.max
	f = invgauss.get_invgauss_func(mean, std)
	return lambda x: max(lo, min(hi, f(x)))

def prior_from_file(filename, parameter):
	"""
	Read a custom prior distribution from a file.
	The file should have two columns: cumulative probability
	and value, in ascii format. The cumulative probability
	has to be equally spaced and should exclude 0 and 1.
	
	Returns a sherpa parameter, a list with that parameter inside,
	and the prior function.
	
	If the file only constains a single value, that value is returned
	along with two empty lists.
	"""
	dist = numpy.loadtxt(filename)
	if numpy.shape(dist) == ():
		parameter.val = float(dist)
		return float(dist), [], []
	distz = numpy.array(list(dist[:, 1]) + [dist[-1,1]]*2)
	#deltax = dist[1,0] - dist[0,0]
	n = len(dist)
	def custom_priorf(x):
		assert x >= 0
		assert x <= 1
		i = int(numpy.floor(x*n))
		r = distz[i] + (distz[i + 1] - distz[i]) * (x * n - i)
		return r
	return parameter, [parameter], [custom_priorf]

def create_prior_function(priors = [], parameters = None):
	"""
	Combine the prior transformations into a single function for pymultinest.

	:param priors: individual prior transforms to combine into one function.
		If priors is empty, uniform priors are used on all passed parameters
	:param parameters: If priors is empty, specify the list of parameters.
		Uniform priors will be created for them.
	"""

	if priors == []:
		functions = []
		assert parameters is not None, "you need to pass the parameters if you want automatic uniform priors"
		thawedparmins  = [p.min for p in parameters]
		thawedparmaxes = [p.max for p in parameters]
		for low, high in zip(thawedparmins, thawedparmaxes):
			functions.append(lambda x: x * (high - low) + low)
	else:
		functions = priors
    
	def prior_function(cube, ndim, nparams):
		for i in range(ndim):
			cube[i] = functions[i](cube[i])

	return prior_function
