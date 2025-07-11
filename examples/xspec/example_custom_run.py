"""
Example of doing BXA in X-spec

Run with python example_advanced_priors.py example-file.fak absorbed-
"""
import sys
import scipy.stats
import bxa.xspec as bxa
from xspec import *

Fit.statMethod = 'cstat'
Plot.xAxis = 'keV'

# first program argument is spectrum file
s = Spectrum(sys.argv[1])
s.ignore("**"); s.notice("0.2-8.0")

# second program argument is output prefix
outputfiles_basename = sys.argv[2]

m = Model("wabs*pow + gauss")

# val, delta, min, bottom, top, max
m.wabs.nH.values = ",,0.01,0.01,1000,1000"
m.powerlaw.norm.values = ",,1e-10,1e-10,1e1,1e1"
m.gaussian.norm.values = ",,1e-10,1e-10,1e1,1e1"
m.gaussian.LineE.values = ",,6,6,8,8"
m.gaussian.Sigma.values = ",,0.001,0.001,1,1"

def my_custom_prior(u):
	# prior distributions transform from 0:1 to the parameter range
	# here: a gaussian prior distribution, cut below 1/above 3
	x = scipy.stats.norm(1.9, 0.15).ppf(u)
	if x < 1.:
		x = 1
	if x > 3:
		x = 3
	return x

# define prior
transformations = [
	# jeffreys prior for nH (but see below)
	bxa.create_jeffreys_prior_for(m, m.wabs.nH),
	# jeffreys prior for scale variable
	bxa.create_jeffreys_prior_for(m, m.powerlaw.norm),
	# custom gaussian prior function for photon index
	bxa.create_custom_prior_for(  m, m.powerlaw.PhoIndex, my_custom_prior),
	# and possibly many more
	# jeffreys prior for scale variable
	bxa.create_jeffreys_prior_for(m, m.gaussian.norm),
	# uniform prior for location variable
	bxa.create_uniform_prior_for(m, m.gaussian.LineE),
	# jeffreys prior for scale variable
	bxa.create_jeffreys_prior_for(m, m.gaussian.Sigma),
]

# we want nH to come out in logarithmic values, without offset of 22
# so we shift the existing jeffreys prior transformation:
# first get the old transformation
prevtransform = transformations[0]['transform']
# shift it for storage
transformations[0]['transform'] = lambda x: prevtransform(x) + 22
# before putting it into xspec, we have to shift back and exponentiate
transformations[0]['aftertransform'] = lambda x: 10**(x - 22)

print('running analysis ...')
# where to store intermediate and final results? this is the prefix used
solver = bxa.BXASolver(transformations=transformations, outputfiles_basename=outputfiles_basename)
results = solver.run(resume=True)
print('running analysis ... done!')


import matplotlib.pyplot as plt
print('creating plot of posterior predictions against data ...')
plt.figure()
data = solver.posterior_predictions_convolved(nsamples=100,
	component_names=['total', 'comp1', 'comp2', 'comp3'],
	plot_args=[dict(color='k'), dict(color='blue'), dict(color='navy'), dict(color='blue')])
# plot data
print('binning for plot...')
binned = bxa.binning(outputfiles_basename=outputfiles_basename,
	bins = data['bins'], widths = data['width'],
	data = data['data'], models = data['models'])
for point in binned['marked_binned']:
	plt.errorbar(marker='o', zorder=-1, **point)
plt.xlim(binned['xlim'])
plt.ylim(binned['ylim'][0], binned['ylim'][1]*2)
plt.gca().set_yscale('log')
if Plot.xAxis == 'keV':
	plt.xlabel('Energy [keV]')
elif Plot.xAxis == 'channel':
	plt.xlabel('Channel')
plt.ylabel(Plot.labels()[1])
print('saving plot...')
plt.legend()
plt.savefig(outputfiles_basename + 'convolved_posterior.pdf', bbox_inches='tight')
plt.close()




print('creating plot of posterior predictions ...')
plt.figure()
solver.posterior_predictions_unconvolved(nsamples=100,
	component_names=['total', 'comp1', 'comp2', 'comp3'],
	plot_args=[dict(color='k'), dict(color='blue'), dict(color='navy'), dict(color='blue')])
ylim = plt.ylim()
# 3 orders of magnitude at most
plt.ylim(max(ylim[0], ylim[1] / 1000), ylim[1])
plt.yscale('log')
plt.xscale('log')
if Plot.xAxis == 'keV':
	plt.xlabel('Energy [keV]')
elif Plot.xAxis == 'channel':
	plt.xlabel('Channel')
plt.ylabel('Energy flux density [erg/s/cm$^2$/keV]')
print('saving plot...')
plt.legend()
plt.savefig(outputfiles_basename + 'unconvolved_posterior.pdf', bbox_inches='tight')
plt.close()



print('creating quantile-quantile plot ...')
plt.figure(figsize=(7,7))
with bxa.XSilence():
	solver.set_best_fit()
	bxa.qq.qq(prefix=outputfiles_basename, markers=5, annotate=True)
print('saving plot...')
plt.savefig(outputfiles_basename + 'qq_model_deviations.pdf', bbox_inches='tight')
plt.close()


print("compute fluxes ...")
flux_hard = solver.create_flux_chain(s, "2.0 10.0")
flux_soft = solver.create_flux_chain(s, "0.5 2.0")
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.hist(flux_hard[:,0], label='hard', histtype='step')
plt.hist(flux_soft[:,0], label='soft', histtype='step')
plt.legend()
plt.xlabel("Photon flux [phot/s/cm$^2$]")
plt.subplot(1, 2, 2)
plt.hist(flux_hard[:,1], label='hard', histtype='step')
plt.hist(flux_soft[:,1], label='soft', histtype='step')
plt.legend()
plt.xlabel("Energy flux [erg/s/cm$^2$]")
plt.savefig(outputfiles_basename + 'flux_posterior.pdf', bbox_inches='tight')
plt.close()

# in case there are multiple spectra, you first have to get the right index:
from bxa.xspec.solver import get_isrc
i_src = get_isrc(ispectrum=1, isource=1)
flux_soft = solver.create_flux_chain(s, "0.5 2.0", i_src=i_src)
