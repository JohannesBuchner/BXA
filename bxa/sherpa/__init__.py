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
	deprecated, use BXASolver instead.
	"""
	solver = BXASolver(
		id=id, otherids=otherids, prior=prior, parameters=parameters,
		outputfiles_basename=outputfiles_basename)
	return solver.run(
		evidence_tolerance=evidence_tolerance,
		n_live_points=n_live_points, **kwargs)
