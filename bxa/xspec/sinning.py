#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
Binning routines for plotting
"""

from __future__ import print_function
import numpy
import scipy.special, scipy.stats
from . import gof
import tqdm


def group_adapt(xdata, ydata, xlo, xhi, nmin = 20):
	"""
	Adaptive grouping into nmin count bins
	"""
	i = 0
	while i < len(xlo):
		for j in range(i, len(xlo)):
			# [i:j] (with j)
			xmask = numpy.logical_and(xdata >= xlo[i], xdata < xhi[j])
			
			if ydata[xmask].sum() >= nmin or j + 1 >= len(xlo):
				yield (xlo[i], xhi[j], ydata[xmask].sum())
				#print '  groups', i,j
				break
		i = j + 1


def binning(outputfiles_basename, bins, widths, data, models):
	"""
	Bins the data for plotting.
	Using the gof module, computes a Poisson goodness-of-fit range,
	i.e. ranges where the model must lie. This is done for multiple
	binning sizes simultaneously.
	
	Returns:
	
	* marked_binned: data points binned to contain 10 counts
	  a sequence ready to be passed to matplotlib.pyplot.errorbar
	* modelrange: range allowed by the data
	  ready to be passed to matplotlib.pyplot.fill_between
	* and statistics (GoF measure)
	
	outputfiles_basename is not used.
	"""
	
	xdata = bins
	xlo = bins - widths
	xhi = bins + widths
	# convert from densities to counts
	ydata = numpy.rint(data * widths * 2)
	models = models * widths * 2
	
	best_gof = None
	best_gof_stats = None
	data = None
	
	grouped_data = list(group_adapt(xdata, ydata, xlo, xhi))
	data = numpy.array([ydata[numpy.logical_and(xdata >= i, xdata < j)].sum() for i, j in zip(xlo, xhi)])
	
	for icomponent in range(models.shape[1]):
		component = models[:,icomponent,:]
		for i, counts_predicted in enumerate(tqdm.tqdm(component)):
			modelrange_low, modelrange_high = gof.calc_models_range(data)
		
			stats = gof.calc_multigof(data, counts_predicted)
			curgof = -numpy.log10(
				numpy.min([stats[stats[:,0] == n][:,2].min() * (stats[:,0] == n).sum() 
					for n in sorted(set(stats[:,0]))]) + 1e-300)
			
			if best_gof is None or curgof < best_gof:
				best_gof = curgof
				best_gof_stats = stats
			if i > 100:
				break

	# check if we can reproduce the data
	curgof = best_gof
	stats = best_gof_stats
	
	data_gofp = [numpy.nan] * len(grouped_data)
	for n in numpy.unique(stats[:,0].astype(int)):
		# find the worst case for this level and each datapoint
		#exp(numpy.log(stats[stats[:,0] == n][:,2]).sum()) * (stats[:,0] == n).sum() 
		#		for n in sorted(set(stats[:,0]))]))
		nstats = stats[stats[:,0] == n]
		pxlo = xlo[(nstats[:,1] * n).astype(numpy.int)]
		pxhi = numpy.asarray(pxlo[1:].tolist() + [xdata.max()])
	
		# so far so good.
		# mark data points that have not been achieved
		#print zip(pxlo, chi2min)
		for i, (xloi, xhii, ydatai) in enumerate(grouped_data):
			# select p values that intersect
			mask = numpy.logical_and(pxlo < xhii, xloi < pxhi)
			if mask.any():
				data_gofp[i] = numpy.nanmin([data_gofp[i], (nstats[mask][:,2]).min() * len(nstats)])
	
	gof_avg = curgof
	gof_total = gof_avg * len(data)
	
	# return data, marked
	marked_binned = []
	# plot data
	ymin = 1e300
	ymax = 0
	for (xloi, xhii, ydatai), gofpi in zip(grouped_data, data_gofp):
		best_gof = -numpy.log10(gofpi + 1e-300)
		# 1e3 and 1e6 correspond roughly to 3 sigma and 5 sigma
		c = 'green' if best_gof < 2 else 'orange' if best_gof < 6. else 'red'
		f = 1. / (xhii-xloi) #* deltax
		y = ydatai * f
		modelrange_low  = scipy.special.gammaincinv(ydatai + 1, 0.1) * f
		modelrange_high = scipy.special.gammaincinv(ydatai + 1, 0.9) * f
		marked_binned.append(
			dict(x=(xloi+xhii)/2., xerr=(-xloi+xhii)/2.,
			y = y,
			yerr = [[modelrange_high - y], [y - modelrange_low]],
			color=c)
		)
		ymin = min(ymin, modelrange_low)
		ymax = max(ymax, modelrange_high)
	
	return dict(marked_binned = marked_binned, 
		gof_avg=gof_avg, gof_total=gof_total, stats=stats,
		xlim = (xlo[0], xhi[-1]),
		ylim = (ymin, ymax),
	)
