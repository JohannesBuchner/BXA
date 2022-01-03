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
	deprecated. Use BXASolver instead.
	"""
	solver = BXASolver(
		transformations=transformations, prior_function=prior_function, 
		outputfiles_basename=outputfiles_basename)
	return solver.run(n_live_points=n_live_points, evidence_tolerance=evidence_tolerance, **kwargs)
