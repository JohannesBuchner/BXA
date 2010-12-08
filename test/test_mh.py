#!/usr/bin/env python

from sherpa.astro.ui import *
import time
import cProfile
from pyblocxs import *
from pyblocxs import Normal

load_pha("3c273.pi")

set_stat('cash')
set_method('neldermead')

set_source(xsphabs.abs1*powlaw1d.p1)
p1.gamma = 2.66
p1.ampl = .7
abs1.nh = 0.06

notice(0.1,6.0)

tt = time.time()
fit()
print("fit in %s s" % (time.time() - tt))

tt = time.time()
covar()
print("covar in %s s" % (time.time() - tt))

print 'List priors'
list_priors()

prior1 = Normal('prior1')
set_prior(abs1.nh, prior1.pdf)

print 'List of priors'
print list_priors()

tt = time.time()
stats, accept, params = get_draws(niter=1e3)
#cProfile.run("doit()", sort=1)
print("MCMC in %s secs" % (time.time() - tt))

plot_pdf(params[0], 'abs1.nh')
