"""
Example of doing BXA in X-spec
"""
import bxa.xspec as bxa
from xspec import Fit, Plot, Model, AllData, AllModels
import scipy.stats
from numpy import log10

Fit.statMethod = 'cstat'
Plot.xAxis = 'keV'

print("setting up main model")
Model("wabs*pow")
transformations = []
parameters = []

for i, filename in enumerate(['sim1.fak', 'sim2.fak', 'sim3.fak'], start=1):
	print("loading..", filename)
	AllData("%d:%d %s" % (i, i, filename))
	s1 = AllData(i)
	s1.ignore("**-0.2, 8.0-**")
	print("setting up model")
	m1 = AllModels(i)
	m1.wabs.nH.values = ",,0.01,0.01,1000,1000"
	m1.powerlaw.norm.values = ",,1e-10,1e-10,1e1,1e1"
	#m1.powerlaw.norm.values = ",,1e-10,1e-10,1e1,1e1"
	if i != 1:
		m1.powerlaw.PhoIndex.link = '=%d' % AllModels(1).powerlaw.PhoIndex.index
	transformations += [
		bxa.create_loguniform_prior_for(m1, m1.wabs.nH),
		bxa.create_loguniform_prior_for(m1, m1.powerlaw.norm)]
	parameters += [
		(m1, m1.wabs.nH), 
		(m1, m1.powerlaw.norm)]

# set parameters on non-communicating parameters
print("setting up non-communicating parameters")
mref = AllModels(1)
mref.powerlaw.PhoIndex.values = ",,1,1,3,3"
transformations += [
	bxa.create_gaussian_prior_for(mref, mref.powerlaw.PhoIndex, 1.95, 0.15),
]
AllModels.show()
AllData.show()

prior = bxa.create_prior_function(transformations)

print('running analysis ...')
# where to store intermediate and final results? this is the prefix used
solver = bxa.BXASolver(
	transformations=transformations,
	prior_function=prior,
	outputfiles_basename='independent/',
)
import ultranest.stepsampler
results = solver.run(resume=True,
	run_kwargs=dict(frac_remain=0.5),
	stepsampler_kwargs=dict(
		generate_direction=ultranest.stepsampler.generate_mixture_random_direction,
		initial_max_ncalls=200000, nsteps=100))

#results = solver.run(resume=True, speed='auto', 
#	stepsampler_kwargs=dict(
#		generate_direction=ultranest.stepsampler.generate_mixture_random_direction,
#		initial_max_ncalls=40000, nsteps=1000, max_nsteps=1000, adaptive_nsteps='move-distance'))

print('running analysis ... done!')
