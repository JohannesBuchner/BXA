from __future__ import print_function
import bxa.sherpa as bxa
print('loading background fitting module...')
from bxa.sherpa.background.models import ChandraBackground
from bxa.sherpa.background.fitters import SingleFitter

import logging
logging.basicConfig(filename='bxa.log',level=logging.DEBUG)
logFormatter = logging.Formatter("[%(name)s %(levelname)s]: %(message)s")
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.INFO)
logging.getLogger().addHandler(consoleHandler)

id = 1
load_pha(id, '179.pi')
if get_rmf(id).energ_lo[0] == 0: get_rmf(id).energ_lo[0] = 0.01
if get_arf(id).energ_lo[0] == 0: get_arf(id).energ_lo[0] = 0.01
set_xlog()
set_ylog()
set_stat('cstat')
set_xsabund('wilm')
ignore(None, 0.5)
ignore(8, None)
notice(0.5, 8)

print('calling singlefitter...')
fitter = SingleFitter(id, '179.pi', ChandraBackground)
try:
	fitter.tryload()
except IOError:
	fitter.fit(plot=False)

set_stat('cstat')
ignore(None, 0.3)
ignore(8, None)
notice(0.3, 8)

import json
z = float(open('179.pi.z').read())
galnh_value = float(open('179.pi.nh').read())

#from bxa.sherpa.rebinnedmodel import RebinnedModel
load_table_model('sphere', '/opt/models/sphere0708.fits')

srcmodel = sphere * xstbabs.galabso
set_model(id, srcmodel)
set_full_model(id, get_bkg_model(id) * get_bkg_scale(id) + get_response(id)(srcmodel))

sphere.phoindex.min = 1
sphere.phoindex.max = 3
sphere.phoindex.val = 2
sphere.norm.min = 1e-10
sphere.norm.max = 100
sphere.norm.val = 0.001
sphere.redshift.max = 10
from sherpa.models.parameter import Parameter
redshift = z
sphere.redshift = redshift
# assuming solar abundances ...
sphere.abund_.freeze()
sphere.fe_abund_.freeze()
sphere.redshift = redshift
sphere.nh.min = 1e20 / 1e22
sphere.nh.max = 1e26 / 1e22
sphere.nh.val = 1e22 / 1e22
galabso.nh.freeze()
galabso.nh.val = galnh_value / 1e22

print('freezing background params')
for p in get_bkg_model(id).pars: 
	p.freeze()
print(get_model(id))

print('creating prior functions...')
srclevel = Parameter('src', 'level', numpy.log10(sphere.norm.val), -8, 3, -8, 3)
srcnh = Parameter('src', 'nh', numpy.log10(sphere.nh.val)+22, 20, 26, 20, 26)
galnh = galabso.nH.val
sphere.norm = 10**srclevel
sphere.nh = 10**(srcnh - 22)
galabso.nH = 10**(galnh - 22)

priors = []
parameters = [srclevel, sphere.phoindex, srcnh]

import bxa.sherpa as bxa
priors += [bxa.create_uniform_prior_for(srclevel)]
priors += [bxa.create_gaussian_prior_for(sphere.phoindex, 1.95, 0.15)]
priors += [bxa.create_uniform_prior_for(srcnh)]
priorfunction = bxa.create_prior_function(priors = priors)
assert not numpy.isnan(calc_stat(id)), 'NaN on calc_stat, probably a bad RMF/ARF file for PC'
print('running BXA ...')
outputfiles_basename = 'spherefit_'

if not os.path.exists(outputfiles_basename + 'params.json'):
	bxa.nested_run(id, prior=priorfunction, parameters = parameters, 
		resume = True, verbose=True, n_live_points=400,
		outputfiles_basename = outputfiles_basename)



if os.environ.get('INTERACTIVE', '0') == '1':
	print('setting to best fit ...')
	bxa.set_best_fit(id, parameters = parameters, outputfiles_basename = outputfiles_basename)
	no_exit = True
else:
	import pymultinest
	a = pymultinest.analyse.Analyzer(n_params = len(parameters), outputfiles_basename = outputfiles_basename)
	if not os.path.exists('%sfit.json' % outputfiles_basename):
		print('collecting fit plot data')
		set_analysis(id, 'ener', 'counts')
		group_adapt(id, 30)
		set_stat('chi2gehrels')
		pl = get_fit_plot(id)
		myplot = dict(counts=int(get_data(id).counts.sum()), background_counts=int(get_bkg(id).counts.sum()),
			data=pl.dataplot.y.tolist(), dataerr=pl.dataplot.yerr.tolist(), 
			x=pl.dataplot.x.tolist(), xerr=pl.dataplot.xerr.tolist(),
			instances=[])
		for row in a.get_equal_weighted_posterior():
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

	print('done.')

