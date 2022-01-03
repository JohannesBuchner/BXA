# -*- coding: utf-8 -*-
"""

QQ plots and goodness of fit

"""
import os
if 'MAKESPHINXDOC' not in os.environ:
	import sherpa.astro.ui as ui
	from sherpa.stats import Cash, CStat

import numpy
import json
from math import log10, isnan
from numpy import logical_and

# KS-stat

def KSstat(data, model, staterror=None, syserror=None, weight=None):
	modelc = model.cumsum() / model.sum()
	datac = data.cumsum() / data.sum()
	ks = numpy.abs(modelc - datac).max()
	return ks, 0

def CvMstat(data, model, staterror=None, syserror=None, weight=None):
	modelc = model.cumsum()
	datac = data.cumsum()
	maxmodelc = modelc.max()
	cvm = ((modelc / maxmodelc - datac / datac.max())**2 * model / maxmodelc).sum()
	return cvm, 0

def ADstat(data, model, staterror=None, syserror=None, weight=None):
	modelc = model.cumsum()
	datac = data.cumsum()
	maxmodelc = modelc.max()
	valid = numpy.logical_and(modelc > 0, maxmodelc - modelc > 0)
	modelc = modelc[valid] / maxmodelc
	datac = datac[valid] / datac.max()
	model = model[valid] / maxmodelc
	assert (modelc > 0).all(), ['ADstat has zero cumulative denominator', modelc]
	assert (maxmodelc - modelc > 0).all(), ['ADstat has zero=1-1 cumulative denominator', maxmodelc - modelc]
	ad = ((modelc - datac)**2 / (modelc * (maxmodelc - modelc)) * model).sum()
	return ad, 0

def fake_staterr_func(data):
	return data**0.5

def qq_export(id=None, bkg=False, outfile='qq.txt', elow=None, ehigh=None):
	"""
	Export Q-Q plot into a file for plotting.

	:param id: spectrum id to use (see get_bkg_plot/get_data_plot)
	:param bkg: whether to use get_bkg_plot or get_data_plot
	:param outfile: filename to write results into
	:param elow: low energy limit
	:param ehigh: low energy limit

	Example::

		qq.qq_export('bg', outfile='my_bg_qq', elow=0.2, ehigh=10)

	"""
	# data
	d = ui.get_bkg_plot(id=id) if bkg else ui.get_data_plot(id=id)
	e = d.x
	mask = logical_and(e >= elow, e <= ehigh)
	data = d.y[mask].cumsum()
	d = ui.get_bkg_model_plot(id=id) if bkg else ui.get_model_plot(id=id)
	e = d.xlo
	mask = logical_and(e >= elow, e <= ehigh)
	e = e[mask]
	model = d.y[mask].cumsum()
	last_stat = ui.get_stat()
	ui.set_stat(ksstat)
	ks = ui.calc_stat()
	ui.set_stat(cvmstat)
	cvm = ui.calc_stat()
	ui.set_stat(adstat)
	ad = ui.calc_stat()
	ui.set_stat(last_stat)
	ad = ui.calc_stat()
	
	ui.set_stat('chi2gehrels')
	chi2 = ui.calc_stat()
	ui.set_stat('cstat')
	cstat = ui.calc_stat()
	ui.set_stat(last_stat)
	stats = dict(ks=ks, cvm=cvm, ad=ad, cstat=cstat, chi2=chi2)
	
	numpy.savetxt(outfile, numpy.transpose([e, data, model]))
	json.dump(stats, open(outfile + '.json', 'w'), indent=4)
	
if 'MAKESPHINXDOC' not in os.environ:
	ui.load_user_stat("ksstat", KSstat, fake_staterr_func)
	ui.load_user_stat("cvmstat", CvMstat, fake_staterr_func)
	ui.load_user_stat("adstat", ADstat, fake_staterr_func)
