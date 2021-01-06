#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
BXA (Bayesian X-ray Analysis) for Sherpa

Copyright: Johannes Buchner (C) 2013-2019
"""

from __future__ import print_function
import os
from math import log10, isnan, isinf
if 'MAKESPHINXDOC' not in os.environ:
	import sherpa.astro.ui as ui
	from sherpa.stats import Cash, CStat

import numpy
from .priors import *
from .galabs import auto_galactic_absorption
from .solver import BXASolver, default_logging


def nested_run(
	id=None, otherids=(), prior=None, parameters=None,
	sampling_efficiency=0.3, evidence_tolerance=0.5,
	n_live_points=400, outputfiles_basename='chains/', **kwargs
):
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
	solver = BXASolver(
		id=id, otherids=otherids, prior=prior, parameters=parameters,
		outputfiles_basename=outputfiles_basename)
	return solver.run(
		evidence_tolerance=evidence_tolerance,
		n_live_points=n_live_points, **kwargs)
