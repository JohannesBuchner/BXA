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


def create_prior_function(id=None, otherids=(), priors = [], parameters = None):
    
    functions = []
    if priors == []:
        assert parameters is not None, "you need to pass the parameters if you want automatic priors"
        thawedparmins  = [p.min for p in parameters]
        thawedparmaxes = [p.max for p in parameters]
        for low, high, i in zip(thawedparmins, thawedparmaxes, range(ndim)):
            functions.append(lambda x: x * (high - low) + low)
    else:
        functions = priors
    
    def prior_function(cube, ndim, nparams):
        for i in range(ndim):
            cube[i] = functions[i](cube[i])

    return prior_function

plot_best = False

def nested_run(id=None, otherids=(), prior = None, parameters = None, sampling_efficiency = 0.8, 
    n_live_points = 1000, outputfiles_basename = 'chains/', **kwargs):
    fit = ui._session._get_fit(id, otherids)[1]

    if not isinstance(fit.stat, (Cash, CStat)):
        raise RuntimeError("Fit statistic must be cash or cstat, not %s" %
                           fit.stat.name)
    
    if parameters is None:
	parameters = fit.model.thawedpars
    def log_likelihood(cube, ndim, nparams):
        try:
          for i, p in enumerate(parameters):
            assert not math.isnan(cube[i]), 'ERROR: parameter %d (%s) to be set to %f' % (i, p.fullname, cube[i])
            p.val = cube[i]
          l = -0.5*fit.calc_stat()
          return l
        except Exception as e:
          print 'Exception in log_likelihood function: ', e
          import sys
          sys.exit(-127)
          return -1e300
          
    
    if prior is None:
        prior = create_prior_function(id=id, otherids=otherids, parameters = parameters)
    n_params = len(parameters)
    pymultinest.run(log_likelihood, prior, n_params, 
        sampling_efficiency = sampling_efficiency, n_live_points = n_live_points, 
        outputfiles_basename = outputfiles_basename, **kwargs)
    
    import json
    m = ui._session._get_model(id)
    paramnames = map(lambda x: x.fullname, parameters)
    json.dump(paramnames, file('%sparams.json' % outputfiles_basename, 'w'), indent=2)

def plot_best_fit(id=None, otherids=(), parameters = None, outputfiles_basename = 'chains/'):
    fit = ui._session._get_fit(id, otherids)[1]
    if parameters is None:
	parameters = fit.model.thawedpars
    a = pymultinest.analyse.Analyzer(n_params = len(parameters), outputfiles_basename = outputfiles_basename)
    for p,v in zip(parameters, a.get_best_fit()['parameters']):
       p.val = v
    
    ui.plot_fit_resid()


