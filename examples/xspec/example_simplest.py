"""
Example of doing BXA in X-spec
"""
import bxa.xspec as bxa
from xspec import *

Fit.statMethod = 'cstat'
Plot.xAxis = 'keV'

s = Spectrum('example-file.fak')
s.ignore("**"); s.notice("0.2-8.0")

# set model and parameters ranges
#                         val, delta, min, bottom, top, max
m = Model("pow")
m.powerlaw.norm.values = ",,1e-10,1e-10,1e1,1e1" # 10^-10 .. 10
m.powerlaw.PhoIndex.values = ",,1,1,3,3"         #     1 .. 3

# define prior
transformations = [
	# uniform prior for Photon Index (see other example for 
	# something more advanced)
	bxa.create_uniform_prior_for( m, m.powerlaw.PhoIndex),
	# jeffreys prior for scale variable
	bxa.create_jeffreys_prior_for(m, m.powerlaw.norm),
	# and possibly many more parameters here
]
print('running analysis ...')
# where to store intermediate and final results? this is the prefix used
outputfiles_basename = 'simplest/'
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
plt.figure(figsize=(7,7))
with bxa.XSilence():
	solver.set_best_fit()
	bxa.qq.qq(prefix=outputfiles_basename, markers=5, annotate=True)
print('saving plot...')
plt.savefig(outputfiles_basename + 'qq_model_deviations.pdf', bbox_inches='tight')
plt.close()
