"""

Fits potentially obscured AGN automatically

How to run this script:

1) create filenames.txt:

	contains 3 space-separated columns, giving .pha/.pi filename, lower and upper energy range
	for example:
	
	acis.pi  0.5 8
	nu_A.fits 5 77
	nu_B.fits 5 77

2) for each spectral file, create .nh foreground absorbing column density file::

	for example, acis.pi.nh could contain (in units of 1/cm^2)::

		2e20

	You can create this file automatically by using::
	
		BXA/gal.py acis.pi

3) for each spectral file, create .z redshift information file

	for example, acis.pi.z could contain::
	
		2.001
	
	If the redshift is known spectroscopically. If you have a redshift
	probability distribution (for example from photo-z or because of other prior information),
	use two columns::
	
		0.0  0
		0.2  0
		0.3  0.1
		0.4  0.4
		0.5  0.6
		0.6  0.8
		0.7  1
	
	where the first column gives the cumulative probability distribution, and the second column gives 
	the redshift.
	
	If you do not need to create this file, a flat redshift prior distribution is assumed.
	This is the XZ method of Simmonds+18.

4) verify that the source and background spectral files, and the ARF, RMF files are correctly linked.

	You can do this automatically with::

		BXA/fixkeywords.py chandra.pi chandra_bkg.pi chandra.rmf chandra.arf
	
	This will fix the fits header keywords.

5) load ciao (source path/to/ciao/bin/ciao.sh). You installed ciao and bxa, right?

6) set the environment variable MODELDIR:

	It should point to the directory containing the UXCLUMPY table model files,
	namely uxclumpy-cutoff.fits and uxclumpy-cutoff-omni.fits, which you can
	download from https://zenodo.org/record/1169181
	
	for example (in bash)::
	
		export MODELDIR=$HOME/Downloads/specmodels/

7) Optional: decide if you want to include a apec component:

	If yes, set the environment variable WITHAPEC=1 (default)
	If no, set the environment variable WITHAPEC=0 
	
	This will model contamination from stars in the soft energies at
	the source redshift.

	The normalisation is limited to not exceed 1e42 erg/s.

8) run:

	$ python3 BXA/examples/sherpa/xagnfitter.py

9) analyse results:

	This will create a bunch of output files starting with multiple_out_*.
	
	intrinsic_photonflux.dist.gz contains the posterior samples as rows 
	(each row is a equally probable solution). 
	
	The columns are:
	
	* redshift 
	* rest-frame intrinsic (unabsorbed) flux in the 2-10keV band
	* absorbed flux in the observed band 2-8keV
	* source normalisation (log)
	* photon index: Prior is 1.95 +- 0.15, so check if it differs from that.
	* log(NH): absorbing column density (from 20 to 26)
	* f_scat: normalisation of soft, unobscured powerlaw
	* apec norm (if did not set WITHAPEC=0)
	* apec temperature (if did not set WITHAPEC=0)
	* redshift (if not fixed to a single value)
	* and one background normalisation parameter for each spectrum
	
	You can use cosmolopy to convert each flux and redshifts to a luminosity.

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

if not os.path.exists('filenames.txt'):
	print("ERROR: No filenames.txt found.")
	print()
	print(__doc__)

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
load_table_model("torus", os.environ['MODELDIR'] + '/uxclumpy-cutoff.fits')
load_table_model("scat", os.environ['MODELDIR'] + '/uxclumpy-cutoff-omni.fits')
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
torus.redshift.max = 10
scat.redshift = redshift
scat.redshift.max = 10
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

solver = bxa.BXASolver(id = ids[0], otherids = tuple(ids[1:]),
	prior = priorfunction, parameters = parameters, 
	outputfiles_basename = prefix)
results = solver.run(resume=True, n_live_points = os.environ.get('NLIVEPOINTS', 400))

try:
	from mpi4py import MPI
	if MPI.COMM_WORLD.Get_rank() > 0:
		sys.exit(0)
except Exception as e:
	pass

outputfiles_basename = prefix
rows = results['samples']

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
		for p, v in zip(parameters, row):
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
	for p, v in zip(parameters, row):
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

set_full_model(id, get_response(id)(model) + bkg_model * get_bkg_scale(id))
solver.set_best_fit()

import sys; sys.exit()
exit()
