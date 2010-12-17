#!/usr/bin/env python

from mh import *
from stats import *
from utils import quantile, flat, inverse, inverse2
from sherpa.utils import get_keyword_defaults
import sherpa.astro.ui as ui
import numpy
import logging
info = logging.getLogger("sherpa").info



__version__ = "0.0.4"


###############################################################################
#
# Session
#
###############################################################################


class Session(object):
    """
    Session maintains the collection of configuration options accessable
    by the high level user interface.
    """

    def __init__(self):

        self.priors = {}

        # default sampler
        self.sampler = 'MetropolisMH'
        self.samplers = {
            'MH' : {
                'class' : MH,
                'opts' : get_keyword_defaults(MH.init)
                },

            'MetropolisMH' : {
                'class' : MetropolisMH,
                'opts' : get_keyword_defaults(MetropolisMH.init)
                }
            }




_session = Session()


###############################################################################
#
# High-level utilities
#
###############################################################################


__all__=['get_draws', 'get_error_estimates',

         'list_priors', 'set_prior', 'get_prior',

         'set_sampler', 'get_sampler', 'get_sampler_name', 'set_sampler_opt',
         'get_sampler_opt',

         'quantile', 'flat', 'inverse', 'inverse2', 'plot_pdf', 'plot_cdf',
         'plot_trace']


def list_priors():
    """
    List the dictionary of currently set prior functions for the set
    of thawed Sherpa model parameters

    """
    return str(_session.priors)


def get_prior(par):
    """
    Get the prior function set for the input Sherpa parameter

    `par`    Sherpa model parameter

    returns associated prior function

    """
    prior = _session.priors.get(par.fullname, None)
    if prior is None:
        raise ValueError("prior function has not been set for '%s'" %
                         par.fullname)
    return prior


def set_prior(par, prior):
    """
    Set the prior function for an associated input Sherpa parameter

    `par`    Sherpa model parameter
    `prior`  function pointer to run as prior on associated parameter

    returns None

    Example:
    
    set_prior(abs1.nh, inverse2)

    """
    _session.priors[par.fullname] = prior


def set_sampler(sampler):
    """
    Set the sampler type for use within pyblocxs

    `sampler`   String indicating sampler type, default="MetropolisMH"

    returns None

    Example:

    set_sampler("MH")

    """
    if sampler not in _session.samplers:
        raise TypeError("unknown sampler '%s'" % sampler)
    _session.sampler = sampler
    

def get_sampler_name():
    """
    Return the current sampler type 

    returns a string indicating the current sampler type

    """
    return _session.sampler


def get_sampler():
    """
    Return the current sampler's dictionary of configuration options

    returns a dictionary of configuration options

    """
    return _session.samplers[_session.sampler]['opts']


def set_sampler_opt(opt, value):
    """
    Set the sampler configuration option for use within pyblocxs

    `opt`     String indicating option
    `value`   Option value

    returns None

    Example:

    set_sampler_opt("log", True)

    """
    _session.samplers[_session.sampler]['opts'][opt] = value


def get_sampler_opt(opt):
    """
    Return the value of an input sampler configuration option

    `opt`     String indicating option

    returns option value

    Example:

    get_sampler_opt("log")
    True

    """
    return _session.samplers[_session.sampler]['opts'][opt]


def get_draws(id=None, otherids=(), niter=1e3, remin=5):
    """ 
    Run pyblocxs using current sampler and current sampler configuration
    options for *niter* number of iterations.  The results are returned
    as a 2-tuple of Numpy ndarrays.  The tuple specifys an array of statistic
    values and a 2-D array of associated parameter values.


    `id`              Sherpa data id
    `otherids`        Additional Sherpa data ids for simultaneous fit 
    `niter`           Number of iterations, default = 1e3
    `remin`           Number of restarts upon finding new minimum, default = 5

    returns a tuple of ndarrays e.g. (stats, params)

    Example:

    stats, params = get_draws(1, niter=1e4)

    """
    fit = ui._session._get_fit(id, otherids)[1]

    covar_results = ui._session.get_covar_results()
    if covar_results is None:
        raise RuntimeError("Covariance has not been calculated")
    sigma = covar_results.extra_output

    mu = fit.model.thawedpars

    fit_results = ui._session.get_fit_results()
    if fit_results is None:
        raise RuntimeError("Fit has not been run")
    dof = fit_results.dof

    priors = []
    for par in fit.model.pars:
        if not par.frozen:
            name = par.fullname
            # assume all parameters have flat priors
            func = flat
            if name in _session.priors:
                # update the parameter priors with user defined values
                func = _session.priors[name]
            priors.append(func)

    sampler = _session.samplers[_session.sampler]['class']
    kwargs = _session.samplers[_session.sampler]['opts'].copy()
    kwargs['priors'] = priors

    info('Using Priors: ' + str(priors))

    stats, accept, params = Walk(sampler(fit, sigma, mu, dof))(niter, **kwargs)
    
    # slice off mode from Sherpa fit
    #params = params[:,1:]
    #stats = -2.0*stats[1:]
    stats = -2.0*stats

    return (stats, accept, params)


def get_error_estimates(x, sorted=False):
    """
    Compute the quantiles and return the median, -1 sigma value, and +1 sigma
    value for the array *x*.

    `x`        input ndarray
    `sorted`   boolean flag to sort array, default=False

    returns a 3-tuple (median, -1 sigma value, and +1 sigma value)

    """
    xs = numpy.array(x)
    if not sorted:
        xs.sort()

    sigfrac = 0.682689
    median = quantile(xs, 0.5)
    lval   = quantile(xs, (1-sigfrac)/2.0)
    hval   = quantile(xs, (1+sigfrac)/2.0)

    return (median, lval, hval)

def plot_pdf(x, name='x', bins=12, overplot=False):
    """
    Compute a histogram and plot the probability density (PDF) of x.

    `x`        input ndarray
    `name`     the label for the input data, default = 'x'
    `bins`     the number of bins in the histogram, default = 12
    `overplot` overplot over an existing plot, default = False

    returns None

    """
    import sherpa.plot
    hist = sherpa.plot.Histogram()
    pdf, xx = numpy.histogram(x, bins=bins, normed=True)

    sherpa.plot.begin()
    try:
        hist.plot(xx[:-1], xx[1:], pdf, xlabel=name,
                  ylabel='probability density', title='PDF: %s' % name,
                  overplot=overplot)
    except:
        sherpa.plot.exceptions()
        raise
    else:
        sherpa.plot.end()

def plot_cdf(x, name='x', overplot=False):
    """
    Compute quantiles and plot the cumulative distribution (CDF) of x.

    `x`        input ndarray
    `name`     the label for the input data, default = 'x'
    `overplot` overplot over an existing plot, default = False

    returns None

    """
    import sherpa.plot
    plot = sherpa.plot.Plot()
    x = numpy.sort(x)
    median, lval, hval, = get_error_estimates(x, True)
    y = (numpy.arange(x.size) + 1) * 1.0 / x.size

    sherpa.plot.begin()
    try:
        plot.plot_prefs["linecolor"]="red"
        plot.plot(x, y, xlabel=name, ylabel="p(<=x)",
                  title="CDF: %s" % name)
        plot.vline(median, linecolor="orange", linestyle="dash",
                   linewidth=1.5, overplot=True, clearwindow=False)
        plot.vline(lval, linecolor="blue", linestyle="dash",
                   linewidth=1.5, overplot=True, clearwindow=False)
        plot.vline(hval,  linecolor="blue", linestyle="dash",
                   linewidth=1.5, overplot=True, clearwindow=False)
    except:
        sherpa.plot.exceptions()
        raise
    else:
        sherpa.plot.end()

def plot_trace(x, name='x', overplot=False):
    """
    Plot the trace of 'x'.

    `x`        input ndarray
    `name`     the label for the input data, default = 'x'
    `overplot` overplot over an existing plot, default = False

    returns None

    """
    import sherpa.plot
    plot = sherpa.plot.Plot()
    iter = numpy.arange(len(x), dtype=float)
    sherpa.plot.begin()
    try:
        plot.plot(iter, x, xlabel="iteration", ylabel=name,
                  title="Trace: %s" % name)
    except:
        sherpa.plot.exceptions()
        raise
    else:
        sherpa.plot.end()
