#!/usr/bin/env python

"""
User interface to metropolis-hastings code
"""

import mh

import numpy as np
import sherpa.astro.ui as ui
import pychips.all as chips
import pycrates as crates

import logging

__all__ = ["get_parameter_info", "get_draws", "write_draws", "fit_draws", "examine_draws"]

def get_parameter_info(id=None):
    """Returns the parameter information needed for calling mht.
    
    This routine will call covariance() if needed, but not
    fit().

    For now only works with a single dataset, and requires
    the Cash statistic.
    """

    if id == None:
        idval = ui.get_default_id()
    else:
        idval = id

    # Employ a lot of safety checks
    #
    fr = ui.get_fit_results()
    if fr == None:
        raise RuntimeError, "No fit results available!"
    if len(fr.datasets) != 1:
        raise RuntimeError, "Fit is for multiple datasets (%s) which we do not support!" % fr.datasets
    if fr.datasets[0] != idval:
        raise RuntimeError, "Fit results are for dataset %s, not %s" % (fr.datasets[0], idval)
    if fr.statname != "cash":
        raise RuntimeError, "Fit was run using statistic=%s rather than cash!" % fr.statname
    if not fr.succeeded:
        # Should use standard sherpa logging
        print "Warning: fit to dataset %s did not complete successfully:\n%s" % (idval, fr.message)
        
    cr = ui.get_covar_results()
    if cr == None or len(cr.datasets) != 1 or cr.datasets[0] != idval:
        # Should use standard sherpa logging
        print "Running covariance for dataset %s" % idval
        ui.covariance(idval)
        cr = ui.get_covar_results()

    if cr.statname != "cash":
        raise RuntimeError, "Covariance was run using statistic=%s rather than cash!" % cr.statname

    if len(fr.parnames) != len(cr.parnames):
        raise RuntimeError, "Number of parameters used in fit and covariance analysis do not agree!\n  fit=%s\n  covar=%s\n" % (fr.parnames, cr.parnames)
    for (p1,p2) in zip(fr.parnames, cr.parnames):
        if p1 != p2:
            raise RuntimeError, "Order of fit/covariance parameters does not match: %s vs %s" % (p1,p2)
    for (pname,v1,v2) in zip(fr.parnames,fr.parvals, cr.parvals):
        if v1 != v2:
            raise RuntimeError, "Value of fit/covariance parameters does not match for parameter %s: %g vs %g" % (pname, v1,v2)

    if not hasattr(cr, "extra_output") or cr.extra_output == None:
        raise RuntimeError, "get_covar_results has no .extra_output or it is None; is this CIAOX?"

    # Store the information, we explicitly copy all items to avoid
    # problems if fit/covariance are run again. This is done by converting
    # all tuples to numpy arrays, even for strings, and is actually
    # not needed.
    #
    out = {
        "dataset":  idval,
        "npars":    len(fr.parnames),
        "parnames": np.asarray(fr.parnames),
        "parvals":  np.asarray(fr.parvals),
        "parmins":  np.asarray(cr.parmins),
        "parmaxes": np.asarray(cr.parmaxes),
        "sigma":    cr.sigma,
        "covar":    cr.extra_output.copy(),
        "statval":  fr.statval
        }
    return out

def get_draws(id=None, niter=1000, df=4, verbose=True, normalize=True, file=None, params=None):
    """Calculates and returns the draws.

    If params is None then use the fit and covariance values for the
    given dataset (id parameter), otherwise use the information stored
    in params (which should be the return value of get_parameter_info).

    If normalize=True then the on-screen output (when verbose is True)
    and file output (when file is not None) are normalized by the
    best-fit values (this is for the statistic and parameter values).
    """

    if id == None:
        idval = ui.get_default_id()
    else:
        idval = id
    if params == None:
        pinfo = get_parameter_info(id=idval)
    else:
        pinfo = params

    return mh.mht(pinfo["parnames"], pinfo["parvals"], pinfo["covar"],
                  id=idval, niter=niter, df=df,
                  normalize=normalize, verbose=verbose, file=file)

def write_draws(draws, outfile, params=None, format="ascii"):
    """Writes the draws (except for iteration number 0) to the file outfile.

    Over-writes the file if it exists. If params is given then it
    should be the output of get_parameter_info and is used to
    add extra information to the output file (well, it will do,
    for now it does not).

    The output format is determined by the format parameter; it
    can be one of
      "fits"  - FITS binary table
      "ascii" - simple ASCII table (two comment lines then data)
      "dtf"   - ASCII file in CIAO TEXT/DTF format (CIAO tools can
                treat it similarly to a FITS table)
      None    - let Crates determine, probably because you have
                specified an option within the outfile name
                (specialised use only)
    """

    formats = { "ascii": "text/simple", "dtf": "text/dtf", "fits": "fits" }
    if format != None and not formats.has_key(format.lower()):
        raise RuntimeError, "Unknown output format '%s'" % format

    # Use crates to create the output file. 
    #
    cr = crates.TABLECrate()

    # We need to store the crate data objects so that they are not
    # garbage collected until after the write_file() call.
    #
    store = {}
    def create_col(cname, cval):
        store[cname] = crates.CrateData()
        store[cname].name = cname
        if 1 != store[cname].load(cval,1):
            raise RuntimeError, "Unable to add column %s to the Crate Data object." % cname
        if 1 != crates.add_col(cr, store[cname]):
            raise RuntimeError, "Unable to add column %s to the Crates." % cname

    def create_key(kname, kval, desc=None):
        store[kname] = crates.CrateKey()
        store[kname].name = kname
        if desc != None:
            store[kname].desc = desc
        if 1 != store[kname].load(kval):
            raise RuntimeError, "Unable to set key %s to %g" % (name, kval)
        if 1 != crates.add_key(cr, store[kname]):
            raise RuntimeError, "Unable to add key %s to Crates." % kname

    # Column data, and then keywords.
    # Note that we do not write out any iteration numbered 0 as this is
    # assumed to be the "best-fit" position.
    #
    idx = draws["iteration"] > 0
    for cname in ["iteration", "accept", "statistic", "alphas"]:
        create_col(cname, draws[cname][idx])
    for cname in draws["parnames"]:
        create_col(cname, draws[cname][idx])

    if params == None:
        create_key("statmin", draws["statistic"][0], "statistic at best-fit location")
        for k in draws["parnames"]:
            create_key("P_%s" % k, draws[k][0], "best-fit value")
    else:
        create_key("statmin", params["statval"], "statistic at best-fit location")
        create_key("sigma", params["sigma"], "sigma value for lower/upper limits")
        for (k,v,l,h) in zip(params["parnames"], params["parvals"], params["parmins"], params["parmaxes"]):
            create_key("p_%s" % k, v, "best-fit value")
            create_key("dl_%s" % k, l, "best-fit lower limit")
            create_key("dh_%s" % k, h, "best-fit upper limit")

    # Write out the file
    #
    if format == None:
        outname = outfile
    else:
        outname = outfile + "[opt kernel=%s]" % formats[format.lower()]
    if 1 != crates.write_file(cr, outname):
        raise IOError, "Unable to write data out to '%s'" % outname
    print "Created: %s" % outfile
    
def fit_draws(draws, parname, nbins=50, params=None, plot=True, verbose=True):
    """Fit a gaussian to the histogram of the given parameter.

    Before using this routine you should use get_parameter_info()
    to extract the parameter info for use by get_draws(). This is
    because using this routine will invalidate the internal
    data structures that get_draws() uses when its params argument
    is None.

    If params is not None then it should be the return value of
    get_parameter_info().

    If plot is True then a plot of the histogram and fit will be
    made.

    If verbose is True then a quick comparison of the fit
    results will be displayed.
    """

    if parname not in draws["parnames"]:
        raise RuntimeError, "Unknown parameter '%s'" % parname

    # Exclude any point with an iteration number of 0
    #
    idx = draws["iteration"] > 0
    parvals = draws[parname][idx]

    (hy,hx) = np.histogram(parvals, bins=nbins, new=True)
    xlo = hx[:-1]
    xhi = hx[1:]

    id = parname
    ui.load_arrays(id, 0.5*(xlo+xhi), hy)

    # We can guess the amplitude and position fairly reliably;
    # for the FWHM we just use the inter-quartile range of the
    # X axis.
    #
    ui.set_source(id, ui.gauss1d.gparam)
    gparam.pos = xlo[xlo.size // 2]
    gparam.ampl = hy[xlo.size // 2]
    gparam.fwhm = xlo[xlo.size * 3 // 4] - xlo[xlo.size // 4]

    # Get the best-fit value if available
    if params != None:
        p0 = dict(zip(params["parnames"], params["parvals"]))[parname]

    logger = logging.getLogger("sherpa")
    olvl = logger.level
    logger.setLevel(40)
    
    ostat = ui.get_stat_name()
    ui.set_stat("leastsq")
    ui.fit(id)
    ui.set_stat(ostat)

    logger.setLevel(olvl)

    if plot:
        # We manually create the plot since we want to use a histogram for the
        # data and the Sherpa plots use curves.
        #
        ##dplot = ui.get_data_plot(id)
        mplot = ui.get_model_plot(id)

        chips.lock()
        try:
            chips.open_undo_buffer()
            chips.erase()
            chips.add_histogram(xlo, xhi, hy)
            ##chips.add_histogram(xlo, xhi, mplot.y, ["line.color", "red", "line.style", "dot"])
            chips.add_curve(mplot.x, mplot.y, ["line.color", "red", "symbol.style", "none"])

            if params != None:
                chips.add_vline(p0, ["line.color", "green", "line.style", "longdash"])

            chips.set_plot_xlabel(parname)
        except:
            chips.discard_undo_buffer()
            chips.unlock()
            raise
        chips.close_undo_buffer()
        chips.unlock()

    sigma = gparam.fwhm.val / (2.0 * np.sqrt(2 * np.log(2)))

    if verbose:
        print ""
        print "Fit to histogram of draws for parameter %s gives" % parname
        print "     mean     = %g" % gparam.pos.val
        print "     sigma    = %g" % sigma
        print ""

        if params != None:
            idx = params["parnames"] == parname
            print "     best fit = %g" % p0
            print "  covar sigma = %g" % params["parmaxes"][idx][0]
            print ""

    return (gparam.pos.val, sigma, gparam.ampl.val)

def _quantile(sorted_array, f):
    """Return the quantile element from sorted_array, where f is [0,1] using linear interpolation.

    Based on the description of the GSL routine
    gsl_stats_quantile_from_sorted_data - e.g.
    http://www.gnu.org/software/gsl/manual/html_node/Median-and-Percentiles.html
    but all errors are my own.

    sorted_array is assumed to be 1D and sorted.
    """

    if len(sorted_array.shape) != 1:
        raise RuntimeError, "Error: input array is not 1D"
    n = sorted_array.size

    q = (n-1) * f
    i = np.int(np.floor(q))
    delta = q - i

    return (1.0-delta) * sorted_array[i] + delta * sorted_array[i+1]

def examine_draws(draws, parname, params=None, plot=True, verbose=True):
    """Use the cumulative-distribution of the draws to get mode and sigma values for a parameter.

    The return value is (median, lower 1-sigma value, upper 1-sigma value).

    If params is not None then it should be the return value of
    get_parameter_info().

    If plot is True then the cumulative distribution function will
    be displayed.

    If verbose is True then a quick comparison of the fit
    results will be displayed.
    """

    if parname not in draws["parnames"]:
        raise RuntimeError, "Unknown parameter '%s'" % parname

    # Exclude any point with an iteration number of 0
    #
    idx = draws["iteration"] > 0
    x = np.sort(draws[parname][idx])

    sigfrac = 0.682689
    median = _quantile(x, 0.5)
    lval   = _quantile(x, (1-sigfrac)/2.0)
    hval   = _quantile(x, (1+sigfrac)/2.0)

    y = (np.arange(x.size) + 1) * 1.0 / x.size

    # Get the best-fit value if available
    if params != None:
        idx    = params["parnames"] == parname
        p0     = params["parvals"][idx][0]
        psigma = params["parmaxes"][idx][0]

    if plot:

        chips.lock()
        try:
            chips.open_undo_buffer()
            chips.erase()

            chips.add_curve(x, y, ["symbol.style", "none", "line.style", "solid"])

            chips.add_vline(median, ["style", "dot"])
            chips.add_vline(lval, ["style", "dot"])
            chips.add_vline(hval, ["style", "dot"])

            if params != None:
                chips.add_vline(p0, ["line.color", "green", "line.style", "longdash"])
                chips.add_vline(p0-psigma, ["line.color", "green", "line.style", "longdash"])
                chips.add_vline(p0+psigma, ["line.color", "green", "line.style", "longdash"])

            chips.set_plot_xlabel(parname)
            chips.set_plot_ylabel(r"p(\leq x)")
        except:
            chips.discard_undo_buffer()
            chips.unlock()
            raise
        chips.close_undo_buffer()
        chips.unlock()

    if verbose:
        print ""
        print "CDF of draws for parameter %s gives" % parname
        print "     median   = %g" % median
        print "     sigma    = %g , %g" % (lval-median, median-hval) 
        print ""

        if params != None:
            print "     best fit = %g" % p0
            print "  covar sigma = %g" % psigma
            print ""

    return (median, lval, hval)
