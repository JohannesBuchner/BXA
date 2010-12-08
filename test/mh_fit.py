from sherpa.astro.ui import *
import time
import cProfile
from pyblocxs import *

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

def doit():
    stats, accept, params = get_draws(niter=1e3)

#abs1.nh = 0.06

tt = time.time()
stats, accept, params = get_draws(niter=1e3)
#cProfile.run("doit()", sort=1)
print("MCMC in %s secs" % (time.time() - tt))

#tt = time.time()
#conf()
#print("conf in %s s" % (time.time() - tt))

plot_pdf(params[0], 'abs1.nh')

# import sherpa.plot
# hist = sherpa.plot.Histogram()
# import numpy
# pdf, xx = numpy.histogram(params[0], bins=12, normed=True)
# import sherpa.plot.pylab_backend as backend
# backend.histo(xx[:-1], xx[1:], pdf)
