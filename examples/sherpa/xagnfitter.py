from __future__ import print_function
import os
import sys
import argparse
import numpy
import json
import traceback
import tqdm

from bxa.sherpa.background.models import ChandraBackground
from bxa.sherpa.background.pca import auto_background
from bxa.sherpa.background.fitters import SingleFitter
import bxa.sherpa.priors as priorfuncs
from bxa.sherpa.galabs import auto_galactic_absorption
from bxa.sherpa.solver import BXASolver

from sherpa.models.parameter import Parameter

import logging
logging.basicConfig(filename='bxa.log',level=logging.DEBUG)
logFormatter = logging.Formatter("[%(name)s %(levelname)s]: %(message)s")
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.INFO)
logging.getLogger().addHandler(consoleHandler)

parser = argparse.ArgumentParser()

#parser.add_argument('--reactive', action='store_true')
parser.add_argument('--energyrange', type=str, default='0.5:8')
parser.add_argument('--backgroundmodel', type=str, default='auto')
parser.add_argument('--num_live_points', type=int, default=400)

parser.add_argument('--withapec', action='store_true')
parser.add_argument('filenames', nargs='+', type=str, help="Spectra files (*.pi, *.pha)")

args = parser.parse_args()

from sherpa.astro.ui import load_pha, get_rmf, get_arf, get_fit_plot, load_table_model, set_xsabund, set_xsxsect, ignore, notice, set_xlog, set_ylog
from sherpa.astro.ui import xsapec, set_full_model, get_bkg_model, get_bkg_scale, set_stat, get_bkg, group_adapt, set_analysis, calc_stat, get_data, set_model, get_response, get_model, calc_energy_flux

id = 1
filename = args.filenames[0]
elo, ehi = args.energyrange.split(':')
elo, ehi = float(elo), float(ehi)
load_pha(id, filename)
try:
	assert get_rmf(id).energ_lo[0] > 0
	assert get_arf(id).energ_lo[0] > 0
	assert (get_bkg(id).counts > 0).sum() > 0
except:
	traceback.print_exc()
	sys.exit(0)

set_xlog()
set_ylog()
set_stat('cstat')
set_xsabund('wilm')
set_xsxsect('vern')
set_analysis(id, 'ener', 'counts')
ignore(None, elo)
ignore(ehi, None)
notice(elo, ehi)

prefix = filename + '_xagnfitter_out_'

#import json
#z = float(open(filename + '.z').read())
#galnh_value = float(open(filename + '.nh').read())

galabso = auto_galactic_absorption()
galabso.nH.freeze()

if args.backgroundmodel == 'chandra':
	print('calling singlefitter...')
	fitter = SingleFitter(id, filename, ChandraBackground)
	try:
		fitter.tryload()
	except IOError:
		fitter.fit(plot=False)


# Models available at https://doi.org/10.5281/zenodo.602282
#torus, scat = None, None
load_table_model("torus", '/home/user/Downloads/specmodels/uxclumpy-cutoff.fits')
load_table_model("scat", '/home/user/Downloads/specmodels/uxclumpy-cutoff-omni.fits')
# the limits correspond to fluxes between Sco X-1 and CDFS7Ms faintest fluxes
srclevel = Parameter('src', 'level', 0, -8, 3, -20, 20) 
print('combining components')
model = torus + scat
print('linking parameters')
torus.norm = 10**srclevel
srcnh = Parameter('src', 'nH', 22, 20, 26, 20, 26)
torus.nh = 10**(srcnh - 22)
scat.nh = torus.nh
scat.nh = torus.nh
print('setting redshift')
redshift = Parameter('src', 'z', 1, 0, 10, 0, 10) 
torus.redshift = redshift
scat.redshift = redshift
scat.phoindex = torus.phoindex

scat.ecut = torus.ecut
scat.theta_inc = torus.theta_inc
scat.torsigma = torus.torsigma
scat.ctkcover = torus.ctkcover
softscatnorm = Parameter('src', 'softscatnorm', -2, -7, -1, -7, -1)
scat.norm = 10**(srclevel + softscatnorm)




print('creating priors')
priors = []
parameters = [srclevel, torus.phoindex, srcnh, softscatnorm]
priors += [priorfuncs.create_uniform_prior_for(srclevel)]
priors += [priorfuncs.create_gaussian_prior_for(torus.phoindex, 1.95, 0.15)]
priors += [priorfuncs.create_uniform_prior_for(srcnh)]
priors += [priorfuncs.create_uniform_prior_for(softscatnorm)]

# 
# apec with L(2-10keV) = 1e42 erg/s
# z      norm[kT=10keV] norm[kT=2keV]
# 0.1    40e-6          150e-6
# 0.5    2e-6           6e-6
# 1      0.7e-6         2e-6
# 3      0.15e-6        0.5e-6
# ================================
# z -->  0.5e-6/ z**2   2e-6/z**2
# 
if args.withapec:
	model = model + xsapec.apec
	apec = xsapec.apec
	apec.redshift = redshift
	apec.kT.max = 8
	apec.kT.min = 0.2
	# normalised so that its luminosity does not go above 1e42 erg/s
	apecnorm = Parameter('src', 'apecnorm', -2, -10, 0, -10, 0)
	apec.norm = 10**apecnorm * 0.5e-6 / apec.redshift**2
	prefix += 'withapec_'
	parameters += [apecnorm, apec.kT]
	priors += [priorfuncs.create_uniform_prior_for(apecnorm)]
	priors += [priorfuncs.create_jeffreys_prior_for(apec.kT)]

if os.path.exists(filename + '.z'):
	redshift, zparameters, zpriorfs = priorfuncs.prior_from_file(filename + '.z', redshift)
	priors += zpriorfs
	parameters += zparameters
else:
	prefix += 'zfree_'
	parameters += [redshift]
	priors += [priorfuncs.create_uniform_prior_for(redshift)]


assert len(priors) == len(parameters), 'priors: %d parameters: %d' % (len(priors), len(parameters))

################
# set model
#    find background automatically using PCA method

print('setting source and background model ...')
set_model(id, model * galabso)
convmodel = get_model(id)
bkg_model = auto_background(id)
set_full_model(id, get_response(id)(model) + bkg_model * get_bkg_scale(id))
#plot_bkg_fit(id)

## we allow the background normalisation to be a free fitting parameter
p = bkg_model.pars[0]
p.max = p.val + 2
p.min = p.val - 2
parameters.append(p)
priors += [priorfuncs.create_uniform_prior_for(p)]


priorfunction = priorfuncs.create_prior_function(priors = priors)
assert not numpy.isnan(calc_stat(id)), 'NaN on calc_stat, probably a bad RMF/ARF file for PC'

print('running BXA ...')

solver = BXASolver(id=id, prior=priorfunction, parameters=parameters)

solver.run(resume = True, verbose=True, n_live_points=args.num_live_points,
	outputfiles_basename = prefix, frac_remain=0.01, min_ess=1000)

if not os.path.exists('%sfit.json' % prefix):
	print('collecting fit plot data')
	set_analysis(id, 'ener', 'counts')
	group_adapt(id, 30)
	set_stat('chi2gehrels')
	pl = get_fit_plot(id)
	myplot = dict(counts=int(get_data(id).counts.sum()), background_counts=int(get_bkg(id).counts.sum()),
		data=pl.dataplot.y.tolist(), dataerr=pl.dataplot.yerr.tolist(), 
		x=pl.dataplot.x.tolist(), xerr=pl.dataplot.xerr.tolist(),
		instances=[])
	for row in tqdm.tqdm(solver.results['samples']):
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
	json.dump(myplot, open('%s/fit.json' % prefix, 'w'))
	print('stored fit plot data into fit.json')

# compute 2-10keV intrinsic luminosities?
# calculate restframe intrinsic flux
set_model(id, torus)

print("estimating intrinsic flux/luminosity ...")
r = []
for row in tqdm.tqdm(solver.results['samples']):
	z = redshift.val if hasattr(redshift, 'val') else redshift
	for p, v in zip(parameters, row):
		if p.name == 'redshift' or p.name == 'z':
			z = v
		p.val = v
	srcnh.val = 20
	r.append([z, 
		calc_energy_flux(id=id, lo=2/(1+z), hi=10/(1+z)),
		calc_energy_flux(id=id, lo=elo/(1+z), hi=ehi/(1+z))
	])

numpy.savetxt(prefix + "/intrinsic_photonflux.dist", r)
print("stored intrinsic flux/luminosity data in intrinsic_photonflux.dist")

