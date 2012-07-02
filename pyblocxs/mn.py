# -*- coding: utf-8 -*-
"""

Bayesian inference using (Py)MultiNest

"""
import sherpa.astro.ui as ui
#from sherpa.utils import get_keyword_defaults, sao_fcmp
from sherpa.stats import Cash, CStat

import pymultinest
from math import log10

# prior
def create_uniform_prior_for(par):
    spread = (par.max - par.min)
    low = par.min
    return lambda x: x * spread + low
def create_jeffreys_prior_for(par):
    low = log10(par.min)
    spread = log10(par.max) - log10(par.min)
    return lambda x: 10**(x * spread + low)


def create_prior_function(id=None, otherids=(), priors = []):
    fit = ui._session._get_fit(id, otherids)[1]

    if not isinstance(fit.stat, (Cash, CStat)):
        raise RuntimeError("Fit statistic must be cash or cstat, not %s" %
                           fit.stat.name)

    thawedparmins  = fit.model.thawedparmins
    thawedparmaxes = fit.model.thawedparmaxes
    
    functions = []
    if priors == []:
        for low, high, i in zip(thawedparmins, thawedparmaxes, range(ndim)):
            functions.append(lambda x: x * (high-low) + low)
    else:
        functions = priors
    
    def prior_function(cube, ndim, nparams):
	for i in range(ndim):
	    cube[i] = functions[i](cube[i])
    return prior_function

def nested_run(id=None, otherids=(), prior = None, sampling_efficiency = 0.8, 
    n_live_points = 1000, outputfiles_basename = 'chains/', **kwargs):
    fit = ui._session._get_fit(id, otherids)[1]

    if not isinstance(fit.stat, (Cash, CStat)):
        raise RuntimeError("Fit statistic must be cash or cstat, not %s" %
                           fit.stat.name)
    
    def log_likelihood(cube, ndim, nparams):
        params = [cube[i] for i in range(ndim)]
        fit.model.thawedpars = params
        l = -0.5*fit.calc_stat()
        #print "%.2e " * ndim % tuple([float(p) for p in fit.model.thawedpars]), "%.0f" % l
        return l
    
    if prior is None:
        prior = create_prior_function(id, otherids)
    
    n_params = len(fit.model.thawedpars)
    pymultinest.run(log_likelihood, prior, n_params, 
        sampling_efficiency = sampling_efficiency, n_live_points = n_live_points, 
        outputfiles_basename = outputfiles_basename, **kwargs)
    
    import json
    m = ui._session._get_model(id)
    paramnames = map(lambda x: x.name, filter(lambda x: not x.frozen, m.pars))
    json.dump(paramnames, file('%sparams.json' % outputfiles_basename, 'w'), indent=2)




