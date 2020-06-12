"""

Fit a X-ray point source (e.g. AGN), potentially obscured with BXA


How to run this script:

1) enter the docker container:

$ xhost +local:`docker inspect --format='{{ .Config.Hostname }}' johannesbuchner/bxa_absorbed`
$ docker run -v  /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY -v $PWD:/opt/example/ -ti johannesbuchner/bxa_absorbed bash

2) load ciao and run the script:

root@7082a4c30d82:/opt/example# . /opt/ciao-4.8/bin/ciao.sh
root@7082a4c30d82:/opt/example# FILENAME=combined_src.pi ELO=0.5 EHI=8 sherpa fitagn.py

"""
from sherpa.astro.ui import *
import os
import sys
import numpy

import bxa.sherpa as bxa
from bxa.sherpa.background.pca import auto_background
from sherpa.models.parameter import Parameter

import logging
logging.basicConfig(filename='bxa.log',level=logging.DEBUG)
logFormatter = logging.Formatter("[%(name)s %(levelname)s]: %(message)s")
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.INFO)
logging.getLogger().addHandler(consoleHandler)
import warnings
logging.getLogger('sherpa.plot').setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message='displayed errorbars')

ids = []

prefix = 'multiple_out_'
for id, line in enumerate(open('filenames.txt'), start=1):
	filename, elo, ehi = line.strip().split()
	elo, ehi = float(elo), float(ehi)
	load_pha(id, filename)
	ignore_id(id, None, None)
	notice_id(id, elo,  ehi)
	ids.append(id)

	set_analysis(id, 'ener', 'counts')

set_xlog()
set_ylog()
set_stat('cstat')
set_xsabund('wilm')
set_xsxsect('vern')


id = ids[0]
galabso = bxa.auto_galactic_absorption(id)
galabso.nH.freeze()

# Models available at https://doi.org/10.5281/zenodo.602282
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
priors += [bxa.create_uniform_prior_for(srclevel)]
priors += [bxa.create_gaussian_prior_for(torus.phoindex, 1.95, 0.15)]
priors += [bxa.create_uniform_prior_for(srcnh)]
priors += [bxa.create_uniform_prior_for(softscatnorm)]

# 
# apec with L(2-10keV) = 1e42 erg/s
# z      norm 10keV    norm 2keV
# 0.1    40e-6         150e-6
# 0.5    2e-6          6e-6
# 1      0.7e-6        2e-6
# 3      0.15e-6       0.5e-6
# ================================
# z -->  0.5e-6/ z**2  2e-6/z**2
# 
if os.environ.get('WITHAPEC', '1') == '1':
	model = model + xsapec.apec
	apec.redshift = redshift
	apec.kT.max = 8
	apec.kT.min = 0.2
	# normalised so that its luminosity does not go above 1e42 erg/s
	apecnorm = Parameter('src', 'apecnorm', -2, -10, 0, -10, 0)
	apec.norm = 10**apecnorm * 0.5e-6 / apec.redshift**2
	prefix += 'withapec_'
	parameters += [apecnorm, apec.kT]
	priors += [bxa.create_uniform_prior_for(apecnorm)]
	priors += [bxa.create_jeffreys_prior_for(apec.kT)]

if os.path.exists(filename + '.z'):
	redshift, zparameters, zpriorfs = bxa.prior_from_file(filename + '.z', redshift)
	if len(zparameters) > 0:
		prefix += 'zphot_'
	else:
		prefix += 'zspec_'
	priors += zpriorfs
	parameters += zparameters
else:
	prefix += 'zfree_'
	parameters += [redshift]
	priors += [bxa.create_uniform_prior_for(redshift)]


assert len(priors) == len(parameters), 'priors: %d parameters: %d' % (len(priors), len(parameters))

################
# set model
#    find background automatically using PCA method

print('setting source and background model ...')
for id in ids:
	set_model(id, model * galabso)
	convmodel = get_model(id)
	bkg_model = auto_background(id)
	set_full_model(id, get_response(id)(model) + bkg_model * get_bkg_scale(id))

	## we allow the background normalisation to be a free fitting parameter
	p = bkg_model.pars[0]
	p.max = p.val + 2
	p.min = p.val - 2
	parameters.append(p)
	priors += [bxa.create_uniform_prior_for(p)]

#################
# BXA run
priorfunction = bxa.create_prior_function(priors = priors)
print('running BXA ...')

bxa.nested_run(id = ids[0], otherids = tuple(ids[1:]),
	prior = priorfunction, parameters = parameters, 
	resume = True, verbose = True,
	outputfiles_basename = prefix, n_live_points = os.environ.get('NLIVEPOINTS', 400),
	importance_nested_sampling = False)

try:
	from mpi4py import MPI
	if MPI.COMM_WORLD.Get_rank() > 0:
		sys.exit(0)
except Exception as e:
	pass

outputfiles_basename = prefix
print('getting best-fit ...')
bxa.set_best_fit(parameters=parameters, outputfiles_basename=outputfiles_basename)

import pymultinest
thawedpars = parameters
a = pymultinest.analyse.Analyzer(n_params = len(thawedpars),
	outputfiles_basename = prefix)
rows = a.get_equal_weighted_posterior()

for id in ids:
	print('plotting spectrum ...')
	set_analysis(id,'ener','counts')
	b = get_bkg_fit_plot(id)
	numpy.savetxt(prefix + 'bkg_'+str(id)+'.txt.gz', numpy.transpose([b.dataplot.x, b.dataplot.y, b.modelplot.x, b.modelplot.y]))
	m = get_fit_plot(id)
	numpy.savetxt(prefix + 'src_'+str(id)+'.txt.gz', numpy.transpose([m.dataplot.x, m.dataplot.y, m.modelplot.x, m.modelplot.y]))
	
	ypreds = []
	for i, row in enumerate(rows):
		sys.stdout.write("%d/%d (%.2f%%)\r" % (i, len(rows), (i + 1)*100./ len(rows)))
		sys.stdout.flush()
		for p, v in zip(thawedpars, row):
			p.val = v
		
		m = get_fit_plot(id)
		ypreds.append(m.modelplot.y)
	
	ylo, ymid, yhi = numpy.percentile(ypreds, [15.87, 50, 84.13], axis=0)
	numpy.savetxt(prefix + 'src_'+str(id)+'.txt.gz', numpy.transpose([m.dataplot.x, m.dataplot.y, m.dataplot.yerr, m.modelplot.x, ylo, ymid, yhi]))


# compute 2-10keV intrinsic luminosities?
print("calculating intrinsic fluxes and distribution of model spectra")
# calculate restframe intrinsic flux
id = ids[0]
set_model(id, torus)

r = []
for i, row in enumerate(rows):
	sys.stdout.write("%d/%d (%.2f%%)\r" % (i, len(rows), (i + 1)*100./ len(rows)))
	sys.stdout.flush()
	z = redshift.val if hasattr(redshift, 'val') else redshift
	for p, v in zip(thawedpars, row):
		if p.name == 'redshift' or p.name == 'z':
			z = v
		p.val = v

	absflux = calc_energy_flux(id=id, lo=2, hi=8)
	srcnh.val = 20
	unabsflux = calc_energy_flux(id=id, lo=2/(1+z), hi=10/(1+z))
	r.append([z, unabsflux, absflux] + list(row))

print("saving distribution plot data")
r = numpy.asarray(r)
assert len(rows) == len(r)
numpy.savetxt(prefix + "intrinsic_photonflux.dist.gz", r)


rows = a.get_data()[:,2:]
r = []
for i, row in enumerate(rows):
	sys.stdout.write("%d/%d (%.2f%%)\r" % (i, len(rows), (i + 1)*100./ len(rows)))
	sys.stdout.flush()
	z = redshift.val if hasattr(redshift, 'val') else redshift
	for p, v in zip(thawedpars, row):
		if p.name == 'redshift' or p.name == 'z':
			z = v
		p.val = v

	srcnh.val = 20
	r.append([z, 
		calc_energy_flux(id=id, lo=2/(1+z), hi=10/(1+z)),
		calc_energy_flux(id=id, lo=0.5/(1+z), hi=8/(1+z))
	] + list(row))

print("saving distribution plot data")
r = numpy.asarray(r)
assert len(rows) == len(r)
numpy.savetxt(prefix + "intrinsic_photonflux_weighted.dist.gz", r)

set_full_model(id, get_response(id)(model) + bkg_model * get_bkg_scale(id))
bxa.set_best_fit(parameters=parameters, outputfiles_basename=outputfiles_basename)

import sys; sys.exit()
exit()


