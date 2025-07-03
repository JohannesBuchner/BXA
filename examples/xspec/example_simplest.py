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

from xspec import Plot
from bxa.xspec.solver import set_parameters, XSilence
from ultranest.plot import PredictionBand

band = None
Plot.background = True

with XSilence():
	Plot.device = '/null'
	# plot models
	for row in solver.posterior[:400]:
		set_parameters(values=row, transformations=solver.transformations)
		Plot('counts')
		if band is None:
			band = PredictionBand(Plot.x())
		band.add(Plot.model())

band.shade(alpha=0.5, color='blue')
band.shade(q=0.495, alpha=0.1, color='blue')
band.line(color='blue', label='convolved model')

plt.scatter(Plot.x(), Plot.y(), label='data')
#plt.errorbar(
#	x=Plot.x(), xerr=Plot.xErr(), y=Plot.y(), yerr=Plot.yErr(), 
#	marker='o', label='data')

if Plot.xAxis == 'keV':
	plt.xlabel('Energy [keV]')
elif Plot.xAxis == 'channel':
	plt.xlabel('Channel')
plt.ylabel('Counts/s/cm$^2$')
plt.savefig(outputfiles_basename + 'convolved_posterior_direct.pdf', bbox_inches='tight')
plt.close()



print('creating a rebinned plot to check the model ...')
plt.figure()
data = solver.posterior_predictions_convolved(nsamples=100)
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
plt.legend()
plt.savefig(outputfiles_basename + 'convolved_posterior.pdf', bbox_inches='tight')
plt.close()




print('creating plot of posterior predictions ...')
plt.figure()
solver.posterior_predictions_unconvolved(nsamples=100)
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
