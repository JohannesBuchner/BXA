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

m = Model("wabs*pow")

# val, delta, min, bottom, top, max
m.wabs.nH.values = ",,0.01,0.01,1000,1000"
m.powerlaw.norm.values = ",,1e-10,1e-10,1e1,1e1"

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
]

# we want nH to come out in logarithmic values, without offset of 22
# so we shift the existing jeffreys prior transformation:
# first get the old transformation
prevtransform = transformations[0]['transform']
# shift it for storage
transformations[0]['transform'] = lambda x: prevtransform(x) + 22
# before putting it into xspec, we have to shift back and exponentiate
transformations[0]['aftertransform'] = lambda x: 10**(x - 22)

# send it off!
print('running analysis ...')
# where to store intermediate and final results? this is the prefix used
solver = bxa.BXASolver(transformations=transformations, outputfiles_basename=outputfiles_basename)
results = solver.run(resume=True)
print('running analysis ... done!')


import matplotlib.pyplot as plt
print('creating plot of posterior predictions against data ...')
plt.figure()
data = solver.posterior_predictions_convolved(nsamples=100)
# plot data
#plt.errorbar(x=data['bins'], xerr=data['width'], y=data['data'], yerr=data['error'],
#	label='data', marker='o', color='green')
# bin data for plotting
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
plt.ylabel('Counts/s/cm$^2$')
print('saving plot...')
plt.savefig(outputfiles_basename + 'convolved_posterior.pdf', bbox_inches='tight')
plt.close()




print('creating plot of posterior predictions ...')
plt.figure()
solver.posterior_predictions_unconvolved(nsamples=100)
ylim = plt.ylim()
# 3 orders of magnitude at most
plt.ylim(max(ylim[0], ylim[1] / 1000), ylim[1])
plt.gca().set_yscale('log')
if Plot.xAxis == 'keV':
	plt.xlabel('Energy [keV]')
elif Plot.xAxis == 'channel':
	plt.xlabel('Channel')
plt.ylabel('Counts/s/cm$^2$')
print('saving plot...')
plt.savefig(outputfiles_basename + 'unconvolved_posterior.pdf', bbox_inches='tight')
plt.close()



print('creating quantile-quantile plot ...')
solver.set_best_fit()
plt.figure(figsize=(7,7))
with bxa.XSilence():
	bxa.qq.qq(prefix=outputfiles_basename, markers=5, annotate=True)
print('saving plot...')
plt.savefig(outputfiles_basename + 'qq_model_deviations.pdf', bbox_inches='tight')
plt.close()
