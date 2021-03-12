from __future__ import print_function
import os, numpy
from sherpa.astro.ui import *
import bxa.sherpa as bxa
bxa.default_logging()
print('loading background fitting module...')
from bxa.sherpa.background.models import SwiftXRTBackground
from bxa.sherpa.background.fitters import SingleFitter

# BXA fully supports fitting multiple ids with the usual id=2, otherids=(3,4,5) 
#     parameters
id = 2
load_pha(id, 'swift/interval0pc.pi')
z = 0.2
set_xlog()
set_ylog()

print('calling singlefitter...')
fitter = SingleFitter(id, 'swift/interval0pc', SwiftXRTBackground)
try:
	fitter.tryload()
except IOError:
	fitter.fit(plot=True)
# that is all for the background model -- it has been fitted 
# or loaded from a previous fit
print('freezing background params')
for p in get_bkg_model(id).pars: 
	p.freeze()

# need to re-initialise energy selection and statistics:

set_stat('cstat')
ignore(None, 0.5)
ignore(5, None)
notice(0.5, 5)

# next we set up a source model.
galabso = bxa.auto_galactic_absorption(id)
srcmodel = xszpowerlw.src * xszwabs.abso * xswabs.galabso

set_model(id, srcmodel)
print(get_model(id))

# the full model consists of background and source. But the background model
# is not convolved through the source response, so this line is necessary:
set_full_model(id, get_bkg_model(id) * get_bkg_scale(id) + get_response(id)(srcmodel))

# an example on how to access some source properties, such as redshift
#   by storing in a json file.

# define limits of the parameter space

src.PhoIndex.min = 1
src.PhoIndex.max = 3
src.PhoIndex.val = 2
src.norm.min = 1e-10
src.norm.max = 100
src.norm.val = 0.001
src.redshift = z
abso.redshift = z
abso.nH.min = 1e19 / 1e22
abso.nH.max = 1e24 / 1e22
abso.nH.val = 1e22 / 1e22

# creating ancillary parameters for logarithmic treatment
print('creating prior functions...')
from sherpa.models.parameter import Parameter
srclevel = Parameter('src', 'level', numpy.log10(src.norm.val), -8, -1, -8, -1)
srcnh = Parameter('src', 'nh', numpy.log10(abso.nH.val)+22, 19, 24, 19, 24)
galnh = Parameter('gal', 'nh', numpy.log10(galabso.nH.val)+22, 19, 24, 19, 24)

src.norm = 10**srclevel
abso.nH = 10**(srcnh - 22)
galabso.nH = 10**(galnh - 22)

# example of a custom prior
f = bxa.invgauss.get_invgauss_func(galnh.val, 0.15)

def limited_19_24(x):
	v = f(x)
	if v <= 19:
		v = 19
	if v >= 24:
		v = 24
	return v

priors = []
parameters = [srclevel, src.PhoIndex, srcnh, galnh]

import bxa.sherpa as bxa
priors += [bxa.create_uniform_prior_for(srclevel)]
priors += [bxa.create_uniform_prior_for(src.PhoIndex)]
priors += [bxa.create_uniform_prior_for(srcnh)]
priors += [limited_19_24] # galnh
priorfunction = bxa.create_prior_function(priors = priors)
print('running BXA ...')
solver = bxa.BXASolver(id, prior=priorfunction, parameters = parameters, 
	outputfiles_basename = 'superfit')
solver.run(resume=True)
