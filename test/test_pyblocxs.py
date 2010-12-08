#!/usr/bin/env python

from sherpa.astro.ui import *
from pychips.all import *
import time
#import cProfile
from pyblocxs import *

def plot_cdf(x, p0, lsigma, hsigma, parname, color):

    x = np.sort(x)
    (median, lval, hval) = get_error_estimates(x, sorted=True)
    y = (np.arange(x.size) + 1) * 1.0 / x.size
    
    attr = ["symbol.style", "none", "line.style", "solid", "line.color", color]
    add_curve(x, y, attr)
    set_axis_ticklabel_size("ax1", 7)
    set_axis_ticklabel_size("ay1", 7)

    #set_axis_ticklabel_angle("ax1", 45)
    #set_axis_ticklabel_angle("ay1", 45)

    attr = ["style", "dot", "color", "orange"]
    add_vline(median, attr)

    attr = ["style", "dot", "color", "aquamarine"]
    add_vline(lval, attr)
    add_vline(hval, attr)

    attr = ["style", "longdash", "color", "yellow"]
    add_vline(p0, attr)

    attr = ["style", "longdash", "color", "purple"]
    add_vline(p0+lsigma, attr)
    add_vline(p0+hsigma, attr)

    #set_plot_title("{\\color{%s} CDF}" % color)
    set_plot_title("CDF")
    set_plot_title_size(10)
    set_plot_xlabel(parname)
    set_plot_ylabel(r"p(\leq x)")
    set_axis_label_size("ax1", 9)
    set_axis_label_size("ay1", 9)
    add_label(0.75, 0.45, r"Conf", ["color", "purple", "coordsys", PLOT_NORM, "size", 9])
    add_label(0.75, 0.35, r"Quantile", ["color", "aquamarine", "coordsys", PLOT_NORM, "size", 9])


def setup():

    load_pha("3c273.pi")

    set_stat('cash')
    set_method('neldermead')

    set_source(xsphabs.abs1*powlaw1d.p1)
    p1.gamma = 2.66
    p1.ampl = .7
    p1.integrate=False
    abs1.nh = 0.06

    notice(0.1,6.0)

    tt = time.time()
    fit()
    print("fit in %s s" % (time.time() - tt))

    tt = time.time()
    covar()
    print("covar in %s s" % (time.time() - tt))

    tt = time.time()
    conf()
    print("conf in %s s" % (time.time() - tt))    


def run_fit_plot():

    ### fit plot ###

    set_stat('chi2datavar')
    plot_fit_resid()
    set_stat('cash')


def run_cdfs(params):

    ### parameter CDFs ###

    p0 = get_conf_results().parvals
    hsigma = get_conf_results().parmaxes
    lsigma = get_conf_results().parmins

    add_window()
    add_plot()
    split(2, 2, 0.17, 0.17)
    current_plot("all")
    set_plot(["style","open"])

    current_plot("plot1")
    plot_cdf(params[0], p0[0], lsigma[0], hsigma[0], "abs1.nh", "red")

    current_plot("plot2")
    plot_cdf(params[1], p0[1], lsigma[1], hsigma[1], "p1.gamma", "green")

    current_plot("plot3")
    plot_cdf(params[2], p0[2], lsigma[2], hsigma[2], "p1.ampl", "gold")


def run_scatter(params, method):

    ### scatter plots + region projection ###

    add_window()
    add_plot()
    split(2, 2, 0.17, 0.17)
    current_plot("all")
    set_plot(["style","open"])

    current_plot("plot1")
    add_curve(params[0],params[1],
              ['line.style', 'none', 'symbol.style', '4',
               'symbol.color', 'red', 'symbol.size', '1'])
    reg_proj(abs1.nh, p1.gamma, overplot=True)
    set_plot_xlabel(abs1.nh.fullname)
    set_plot_ylabel(p1.gamma.fullname)
    set_plot_title(method)

    current_plot("plot2")
    add_curve(params[1],params[2],
              ['line.style', 'none', 'symbol.style', '4',
               'symbol.color', 'green', 'symbol.size', '1'])
    reg_proj(p1.gamma, p1.ampl, overplot=True)
    set_plot_xlabel(p1.gamma.fullname)
    set_plot_ylabel(p1.ampl.fullname)
    set_plot_title(method)

    current_plot("plot3")
    add_curve(params[2],params[0],
              ['line.style', 'none', 'symbol.style', '4',
               'symbol.color', 'gold','symbol.size', '1'])
    reg_proj(p1.ampl, abs1.nh, overplot=True)
    set_plot_xlabel(p1.ampl.fullname)
    set_plot_ylabel(abs1.nh.fullname)
    set_plot_title(method)

def run_mh(method):

    #set_prior(p1.ampl, inverse)
    #set_prior(abs1.nh, inverse2)
    #print list_priors()
    set_sampler(method)

    tt = time.time()
    stats, accept, params = get_draws(niter=1e3)
    print("'%s' in %s secs" % (method, time.time() - tt))

    return stats, params


def main():

    #method = 'MH'
    method = 'MetropolisMH'

    setup()

    stats, params = run_mh(method)

    run_fit_plot()

    run_cdfs(params)

    run_scatter(params, method)



if __name__ == '__main__':

    main()
