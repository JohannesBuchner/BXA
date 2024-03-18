"""
Example of doing BXA in X-spec
"""
import bxa.xspec as bxa
from xspec import Fit, Plot, Model, AllData, AllModels
import scipy.stats
from numpy import log10

def concatenate_transformations(list_of_transformations, list_of_prior_functions):
	"""
	Concatenates transformation functions and prior functions.
	"""
	def combined_prior(cube):
		params = cube.copy()
		i = 0
		for transformations, prior in zip(list_of_transformations, list_of_prior_functions):
			# transform the first block, which has this many parameters:
			nparams = len(transformations)
			# apply the responsible prior to these:
			params[i:i+nparams] = prior(cube[i:i+nparams])
			i += nparams
		return params

	# return the combined function and full list of transform functions
	combined_transformations = []
	for transformations in list_of_transformations:
		combined_transformations += transformations
	return combined_prior, combined_transformations

def create_gaussian_hierarchical_prior_function(mean_min, mean_max, sigma_max, participating_parameters, sigma_min=0, name='hierarchical'):
	"""Hierarchical Gaussian prior.
	
	Flat priors on the hyper-parameters: mean and sigma.
	This avoids a strong funnel (compared to a log-uniform sigma prior)
	and is recommended by Gelman et al.
	"""
	
	upper_transformations = [
		dict(skip_setting=True, name='mean-%s' % name),
		dict(skip_setting=True, name='sigma-%s' % name),
	]
	lower_transformations = [bxa.create_uniform_prior_for(m, par) for m, par in participating_parameters]
	
	def gaussian_hierarchical_prior(cube):
		params = cube.copy()
		mean = params[0] = (mean_max - mean_min) * cube[0] + mean_min
		sigma = params[1] = (sigma_max - sigma_min) * cube[1] + sigma_min

		rv = scipy.stats.norm(mean, sigma)
		for i, (_, par) in enumerate(participating_parameters, start=2):
			pval, pdelta, pmin, pbottom, ptop, pmax = par.values
			params[i] = max(pmin, min(pmax, rv.ppf(cube[i])))
		return params

	return gaussian_hierarchical_prior, upper_transformations + lower_transformations

def create_loggaussian_hierarchical_prior_function(log_mean_min, log_mean_max, sigma_max, participating_parameters, sigma_min=0, name='hierarchical'):
	"""Hierarchical Gaussian prior on the log of parameters.
	
	Flat priors on the hyper-parameters: mean and sigma.
	This avoids a strong funnel (compared to a log-uniform sigma prior)
	and is recommended by Gelman et al.
	"""
	upper_transformations = [
		dict(skip_setting=True, name='log_mean-%s' % name),
		dict(skip_setting=True, name='sigma-%s' % name),
	]
	lower_transformations = [bxa.create_loguniform_prior_for(m, par) for m, par in participating_parameters]

	def loggaussian_hierarchical_prior(cube):
		params = cube.copy()
		log_mean = params[0] = (log_mean_max - log_mean_min) * cube[0] + log_mean_min
		sigma = params[1] = (sigma_max - sigma_min) * cube[1] + sigma_min

		rv = scipy.stats.norm(log_mean, sigma)
		for i, (_, par) in enumerate(participating_parameters, start=2):
			pval, pdelta, pmin, pbottom, ptop, pmax = par.values
			params[i] = max(log10(pmin), min(log10(pmax), rv.ppf(cube[i])))
		return params

	return loggaussian_hierarchical_prior, upper_transformations + lower_transformations

Fit.statMethod = 'cstat'
Plot.xAxis = 'keV'

Model("wabs*pow")
transformations = []
participating_parameters = []

for i, filename in enumerate(['sim1.fak', 'sim2.fak', 'sim3.fak'], start=1):
	AllData("%d:%d %s" % (i, i, filename))
	s1 = AllData(i)
	s1.ignore("**-0.2, 8.0-**")
	print("setting up model")
	m1 = AllModels(i)
	m1.wabs.nH.values = ",,0.01,0.01,1000,1000"
	m1.powerlaw.norm.values = ",,1e-10,1e-10,1e1,1e1"
	#m1.powerlaw.norm.values = ",,1e-10,1e-10,1e1,1e1"
	#m1.powerlaw.PhoIndex.values = ",,1,1,3,3"
	if i != 1:
		m1.powerlaw.PhoIndex.link = '=%d' % AllModels(1).powerlaw.PhoIndex.index
	if i != 1:
		m1.powerlaw.norm.link = '=%d' % AllModels(1).powerlaw.norm.index
	transformations += [
		bxa.create_uniform_prior_for( m1, m1.wabs.nH),
	]

	participating_parameters += [
		(m1, m1.wabs.nH),
	]

# define multi-level prior for communicating parameters
hierarchical_prior, hierarchical_transformations = create_loggaussian_hierarchical_prior_function(-2, 2, 2, participating_parameters)

# set parameters on non-communicating parameters
mref = AllModels(1)
mref.powerlaw.norm.values = ",,1e-10,1e-10,1e1,1e1"
mref.powerlaw.PhoIndex.values = ",,1,1,3,3"
transformations = [
	bxa.create_gaussian_prior_for(mref, mref.powerlaw.PhoIndex, 1.95, 0.15),
	bxa.create_jeffreys_prior_for(mref, mref.powerlaw.norm),
]
AllModels.show()
AllData.show()

plain_prior = bxa.create_prior_function(transformations)

combined_prior, combined_transformations = concatenate_transformations([transformations, hierarchical_transformations], [plain_prior, hierarchical_prior])

print('running analysis ...')
# where to store intermediate and final results? this is the prefix used
solver = bxa.BXASolver(
	transformations=combined_transformations,
	prior_function=combined_prior,
	outputfiles_basename='hierarchical3/',
)
import ultranest.stepsampler
results = solver.run(resume=True,
	run_kwargs=dict(frac_remain=0.5),
	stepsampler_kwargs=dict(
		generate_direction=ultranest.stepsampler.generate_mixture_random_direction,
		initial_max_ncalls=100000, nsteps=100))
print('running analysis ... done!')
