from __future__ import print_function
from sherpa.astro.ui import *
import numpy as np
import os
import json
import numpy
import bxa.sherpa as bxa
print('loading background fitting module...')
from bxa.sherpa.background.models import SwiftXRTBackground
from bxa.sherpa.background.fitters import SingleFitter

import logging
logging.basicConfig(filename='bxa.log',level=logging.DEBUG)
logFormatter = logging.Formatter("[%(name)s %(levelname)s]: %(message)s")
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.INFO)
logging.getLogger().addHandler(consoleHandler)

id = 2
load_pha(id, 'interval0pc.pi')
nhgal = np.loadtxt('interval0pc.pi.nh')
set_xlog()
set_ylog()
set_stat('cstat')
set_xsabund('wilm')
ignore(None, 0.5)
ignore(5, None)
notice(0.5, 5)

print('calling singlefitter...')
fitter = SingleFitter(id, 'interval0pc', SwiftXRTBackground)
try:
	fitter.tryload()
except IOError:
	fitter.fit(plot=False)

id2 = 3
if os.path.exists('interval0wt.pi'):
	load_pha(id2, 'interval0wt.pi')
	if get_rmf(id2).energ_lo[0] == 0: get_rmf(id2).energ_lo[0] = 0.01
	if get_arf(id2).energ_lo[0] == 0: get_arf(id2).energ_lo[0] = 0.01
	ncounts = get_bkg(id2).counts.sum()
	if ncounts < 150:
		id2 = None
	else:
		set_stat('cstat')
		ignore(None, 0.5)
		ignore(5, None)
		notice(0.5, 5)

		print('calling singlefitter...')
		fitter = SingleFitter(id2, 'interval0wt3', SwiftXRTBackground)
		try:
			fitter.tryload()
		except IOError:
			fitter.fit(plot=False)
else:
	id2 = None

set_stat('cstat')
ignore(None, 0.5)
ignore(5, None)
notice(0.5, 5)

#from bxa.sherpa.rebinnedmodel import RebinnedModel
# sphere model of Brightman & Nandra (2011)
load_table_model('sphere', os.environ.get('MODELDIR', '.') + '/sphere0708.fits')
load_table_model('sphere2', os.environ.get('MODELDIR', '.') + '/sphere0708.fits')

srcmodel = sphere * xstbabs.galabso
srcmodel2 = sphere2 * xstbabs.galabso
set_model(id, srcmodel)
set_full_model(id, get_bkg_model(id) * get_bkg_scale(id) + get_response(id)(srcmodel))
if id2:
	set_model(id2, srcmodel2)
	set_full_model(id2, get_bkg_model(id2) * get_bkg_scale(id2) + get_response(id2)(srcmodel2))

sphere.phoindex.min = 1
sphere.phoindex.max = 3
sphere.phoindex.val = 2
sphere.norm.min = 1e-10
sphere.norm.max = 1000
sphere.norm.val = 0.001
sphere.redshift.max = 10
sphere2.phoindex.min = 1
sphere2.phoindex.max = 3
sphere2.phoindex.val = 2
sphere2.norm.min = 1e-10
sphere2.norm.max = 1000
sphere2.norm.val = 0.001
sphere2.redshift.max = 10
from sherpa.models.parameter import Parameter
redshift = 2.352
sphere.redshift = redshift
sphere2.redshift = sphere.redshift
# assuming solar abundances ...
sphere.abund_.freeze()
sphere.fe_abund_.freeze()
sphere.redshift = redshift
sphere.nh.min = 1e20 / 1e22
sphere.nh.max = 1e26 / 1e22
sphere.nh.val = 1e22 / 1e22
sphere2.abund_.freeze()
sphere2.fe_abund_.freeze()
sphere2.redshift = redshift
sphere2.nh.min = 1e20 / 1e22
sphere2.nh.max = 1e26 / 1e22
sphere2.nh.val = 1e22 / 1e22
galabso.nh.freeze()
galabso.nH.val = nhgal / 1e22

print('freezing background params')
for p in get_bkg_model(id).pars: 
	p.freeze()
print(get_model(id))
if id2:
	for p in get_bkg_model(id2).pars: 
		p.freeze()
	print(get_model(id2))

print('creating prior functions...')
srclevel = Parameter('src', 'level', numpy.log10(sphere.norm.val), -8, 3, -8, 3)
srclevel2 = Parameter('src2', 'level', numpy.log10(sphere2.norm.val), -8, 3, -8, 3)
srcnh = Parameter('src', 'nh', numpy.log10(sphere.nh.val)+22, 20, 26, 20, 26)
galnh = galabso.nH.val

sphere.norm = 10**srclevel
sphere2.norm = 10**srclevel2
sphere.nh = 10**(srcnh - 22)
sphere2.nh = 10**(srcnh - 22)
galabso.nH = 10**(galnh - 22)

priors = []
parameters = [srclevel, sphere.phoindex, srcnh]

import bxa.sherpa as bxa
priors += [bxa.create_uniform_prior_for(srclevel)]
priors += [bxa.create_gaussian_prior_for(sphere.phoindex, 1.95, 0.15)]
priors += [bxa.create_uniform_prior_for(srcnh)]
if id2:
	priors += [bxa.create_uniform_prior_for(srclevel2)]
	parameters.append(srclevel2)
	priors += [bxa.create_uniform_prior_for(sphere2.phoindex)]
	parameters.append(sphere2.phoindex)
if id2:
	otherids = (id2,)
else:
	otherids = tuple()
#if redshift_uncertain:
#	priors.append(limited_0_10)
#	parameters.append(redshift)
priorfunction = bxa.create_prior_function(priors = priors)

outputfiles_basename = 'spherefit3'
solver = bxa.BXASolver(
	id, otherids=otherids, prior=priorfunction, parameters = parameters, 
	outputfiles_basename = outputfiles_basename)

results = solver.run(resume = True, verbose=True, n_live_points=400)

print('collecting fit plot data')
set_analysis(id, 'ener', 'counts')
group_counts(id, 40)
set_stat('chi2gehrels')
pl = get_fit_plot(id)
myplot = dict(counts=int(get_data(id).counts.sum()), background_counts=int(get_bkg(id).counts.sum()),
	data=pl.dataplot.y.tolist(), dataerr=pl.dataplot.yerr.tolist(), 
	x=pl.dataplot.x.tolist(), xerr=pl.dataplot.xerr.tolist(),
	instances=[])
for row in results['samples']:
	for p, v in zip(parameters, row):
		p.val = v
	pl = get_fit_plot(id)
	myplot['instances'].append(pl.modelplot.y.tolist())

srcnh.val = 20
pl = get_fit_plot(id)
myplot['unabsorbed'] = pl.modelplot.y.tolist()

galabso.nH = 0
pl = get_fit_plot(id)
myplot['nogal'] = pl.modelplot.y.tolist()

set_full_model(id, get_bkg_model(id) * get_bkg_scale(id))
pl = get_fit_plot(id)
myplot['background'] = pl.modelplot.y.tolist()
set_stat('cstat')
json.dump(myplot, open('%sfit.json' % outputfiles_basename, 'w'))


if id2:
	print('collecting fit2 plot data')
	set_analysis(id2, 'ener', 'counts')
	set_stat('chi2xspecvar')
	group_counts(id2, 20)
	pl = get_fit_plot(id2)
	myplot = dict(counts=int(get_data(id2).counts.sum()), background_counts=int(get_bkg(id2).counts.sum()),
		data=pl.dataplot.y.tolist(), dataerr=pl.dataplot.yerr.tolist(), 
		x=pl.dataplot.x.tolist(), xerr=pl.dataplot.xerr.tolist(),
		instances=[])
	for row in results['samples']:
		for p, v in zip(parameters, row):
			p.val = v
		pl = get_fit_plot(id2)
		myplot['instances'].append(pl.modelplot.y.tolist())

	srcnh.val = 20
	pl = get_fit_plot(id2)
	myplot['unabsorbed'] = pl.modelplot.y.tolist()

	galabso.nH = 0
	pl = get_fit_plot(id2)
	myplot['nogal'] = pl.modelplot.y.tolist()

	set_full_model(id2, get_bkg_model(id2) * get_bkg_scale(id2))
	pl = get_fit_plot(id2)
	myplot['background'] = pl.modelplot.y.tolist()

	set_stat('cstat')
	json.dump(myplot, open('%sfit2.json' % outputfiles_basename, 'w'))

print('done.')
