#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from __future__ import absolute_import, unicode_literals, print_function

__doc__ = """
Plotting of posterior parameter marginal distributions

Author: Johannes Buchner (C) 2013-2019
"""
import matplotlib.pyplot as plt
import json
import corner
import numpy
import warnings

def marginal_plots(analyzer, minweight=1e-4, **kwargs):
	"""
	Create marginal plots
	
	* analyzer: A instance of pymultinest.Analyzer
	* d: if more than 20 dimensions, by default only 1d marginal distributions
	   are plotted. set d=2 if you want to force a 2d matrix plot
	
	"""
	prefix = analyzer.outputfiles_basename
	parameters = json.load(open(prefix + 'params.json'))
	
	data = analyzer.get_data()[:,2:]
	weights = analyzer.get_data()[:,0]

	mask = weights > minweight

	with warnings.catch_warnings():
		warnings.simplefilter("ignore")
		corner.corner(data[mask,:], weights=weights[mask], 
			labels=parameters, show_titles=True, **kwargs)
	
	plt.savefig(prefix + 'corner.pdf')
	plt.savefig(prefix + 'corner.png')
	plt.close()


