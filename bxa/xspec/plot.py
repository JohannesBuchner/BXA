#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
Plotting of posterior parameter marginal distributions
"""

import numpy
from numpy import exp, log
import matplotlib.pyplot as plt
import json
import pymultinest

def marginal_plots(analyzer, d=None):
	"""
	Create marginal plots
	
	* analyzer: A instance of pymultinest.Analyzer
	* d: if more than 20 dimensions, by default only 1d marginal distributions
	   are plotted. set d=2 if you want to force a 2d matrix plot
	
	"""
	prefix = analyzer.outputfiles_basename
	n_params = analyzer.n_params
	parameters = json.load(file(prefix + 'params.json'))
	a = analyzer
	s = a.get_stats()

	p = pymultinest.PlotMarginal(a)

	values = a.get_equal_weighted_posterior()
	assert n_params == len(s['marginals'])
	modes = s['modes']
	dim2 = ((1 if n_params > 20 else 2) if d is None else d) == 2

	if dim2:
		plt.figure(figsize=(5*n_params, 5*n_params))
		for i in range(n_params):
			plt.subplot(n_params, n_params, i + 1)
			plt.xlabel(parameters[i])
	
			m = s['marginals'][i]
			plt.xlim(m['5sigma'])
	
			oldax = plt.gca()
			x,w,patches = oldax.hist(values[:,i], bins=20, edgecolor='grey', color='grey', histtype='stepfilled', alpha=0.2)
			oldax.set_ylim(0, x.max())
	
			newax = plt.gcf().add_axes(oldax.get_position(), sharex=oldax, frameon=False)
			p.plot_marginal(i, ls='-', color='blue', linewidth=3)
			newax.set_ylim(0, 1)
	
			ylim = newax.get_ylim()
			y = ylim[0] + 0.05*(ylim[1] - ylim[0])
			center = m['median']
			low1, high1 = m['1sigma']
			#print center, low1, high1
			newax.errorbar(x=center, y=y,
				xerr=numpy.transpose([[center - low1, high1 - center]]), 
				color='blue', linewidth=2, marker='s')
			oldax.set_yticks([])
			#newax.set_yticks([])
			newax.set_ylabel("Probability")
			ylim = oldax.get_ylim()
			newax.set_xlim(m['5sigma'])
			oldax.set_xlim(m['5sigma'])
			#plt.close()
	
			for j in range(i):
				plt.subplot(n_params, n_params, n_params * (j + 1) + i + 1)
				p.plot_conditional(i, j, bins=20, cmap = plt.cm.gray_r)
				for m in modes:
					plt.errorbar(x=m['mean'][i], y=m['mean'][j], xerr=m['sigma'][i], yerr=m['sigma'][j])
				plt.xlabel(parameters[i])
				plt.ylabel(parameters[j])
				plt.xlim(s['marginals'][i]['5sigma'])
				plt.ylim(s['marginals'][j]['5sigma'])
				#plt.savefig('cond_%s_%s.pdf' % (params[i], params[j]), bbox_tight=True)
				#plt.close()

		plt.savefig(prefix + 'marg.pdf')
		plt.savefig(prefix + 'marg.png')
		plt.close()
	else:
		from matplotlib.backends.backend_pdf import PdfPages
		print '1dimensional only. Set the D environment variable D=2 to force'
		print '2d marginal plots.'
		pp = PdfPages(prefix + 'marg1d.pdf')
	
		for i in range(n_params):
			plt.figure(figsize=(5, 5))
			plt.xlabel(parameters[i])
		
			m = s['marginals'][i]
			plt.xlim(m['5sigma'])
	
			oldax = plt.gca()
			x,w,patches = oldax.hist(values[:,i], bins=20, edgecolor='grey', color='grey', histtype='stepfilled', alpha=0.2)
			oldax.set_ylim(0, x.max())
	
			newax = plt.gcf().add_axes(oldax.get_position(), sharex=oldax, frameon=False)
			p.plot_marginal(i, ls='-', color='blue', linewidth=3)
			newax.set_ylim(0, 1)
	
			ylim = newax.get_ylim()
			y = ylim[0] + 0.05*(ylim[1] - ylim[0])
			center = m['median']
			low1, high1 = m['1sigma']
			print center, low1, high1
			newax.errorbar(x=center, y=y,
				xerr=numpy.transpose([[center - low1, high1 - center]]), 
				color='blue', linewidth=2, marker='s')
			oldax.set_yticks([])
			newax.set_ylabel("Probability")
			ylim = oldax.get_ylim()
			newax.set_xlim(m['5sigma'])
			oldax.set_xlim(m['5sigma'])
			plt.savefig(pp, format='pdf', bbox_inches='tight')
			plt.close()
		pp.close()



