from __future__ import print_function
import os, numpy
from sherpa.astro.ui import *
import bxa.sherpa as bxa
bxa.default_logging()
print('loading background fitting module...')
from bxa.sherpa.background.pca import auto_background

# BXA fully supports fitting multiple ids with the usual id=2, otherids=(3,4,5) 
#     parameters
id = 2
load_pha(id, 'swift/interval0pc.pi')
set_stat('cstat')
set_xsabund('wilm')
set_xsxsect('vern')

# next we set up a source model.
#    with automatic milky way absorption
galabso = bxa.auto_galactic_absorption(id)
model = xszpowerlw.src * xszwabs.abso * galabso
src.norm.val = 1e-5

#    with automatic background from PCA
set_model(id, model)
convmodel = get_model(id)
bkg_model = auto_background(id)
#set_bkg_full_model(id, bkg_model)
set_full_model(id, convmodel + bkg_model*get_bkg_scale(id))

id2 = None
if os.path.exists('interval0wt.pi'):
	id2 = 3
	load_pha(id2, 'interval0wt.pi')
	if get_rmf(id2).energ_lo[0] == 0: get_rmf(id2).energ_lo[0] = 0.001
	if get_arf(id2).energ_lo[0] == 0: get_arf(id2).energ_lo[0] = 0.001
	if get_bkg(id2).counts.sum() > 100:
		set_model(id2, model)
		convmodel2 = get_model(id2)
		bkg_model2 = auto_background(id2)
		#set_bkg_full_model(id2, bkg_model2)
		set_full_model(id2, convmodel2 + bkg_model2*get_bkg_scale(id2))
	else:
		delete_data(id2)
		id2 = None

ignore(None, 0.5)
ignore(5, None)

src.PhoIndex.min = 1
src.PhoIndex.max = 3
src.PhoIndex.val = 2
src.norm.min = 1e-10
src.norm.max = 100
src.norm.val = 0.001
src.redshift.min = 0
src.redshift.max = 10
abso.redshift = src.redshift
abso.nH.min = 1e19 / 1e22
abso.nH.max = 1e24 / 1e22

#print 'fitting...'
#fit()
#show_model(id)

# creating ancillary parameters for logarithmic treatment
print('creating prior functions...')
from sherpa.models.parameter import Parameter
srclevel = Parameter('src', 'level', numpy.log10(src.norm.val), -8, 2, -8, 2)
srcnh = Parameter('src', 'nh', numpy.log10(abso.nH.val)+22, 19, 24, 19, 24)
galnh = Parameter('gal', 'nh', numpy.log10(galabso.nH.val)+22, 19, 24, 19, 24)

src.norm = 10**srclevel
abso.nH = 10**(srcnh - 22)

priors = []
parameters = [srclevel, src.PhoIndex, srcnh, src.redshift, bkg_model.pars[0]]

import bxa.sherpa as bxa
priors += [bxa.create_uniform_prior_for(srclevel)]
priors += [bxa.create_gaussian_prior_for(src.PhoIndex, 1.95, 0.15)]
priors += [bxa.create_uniform_prior_for(srcnh)]
priors += [bxa.create_gaussian_prior_for(src.redshift, 0.3, 0.05)] # redshift uncertainty
priors += [bxa.create_uniform_prior_for(bkg_model.pars[0])]
otherids = ()

if id2:
	parameters.append(bkg_model2.pars[0])
	priors += [bxa.create_uniform_prior_for(bkg_model2.pars[0])]
	otherids = (id2,)

priorfunction = bxa.create_prior_function(priors = priors)
print('running BXA ...')
solver = bxa.BXASolver(id, otherids=otherids, prior=priorfunction, parameters = parameters, 
	outputfiles_basename = 'wabs_noz')
solver.run()

m = get_bkg_fit_plot(id)
numpy.savetxt('test_bkg.txt', numpy.transpose([m.dataplot.x, m.dataplot.y, m.modelplot.x, m.modelplot.y]))

m = get_fit_plot(id)
numpy.savetxt('test_src.txt', numpy.transpose([m.dataplot.x, m.dataplot.y, m.modelplot.x, m.modelplot.y]))

if id2:
	m = get_fit_plot(id2)
	numpy.savetxt('test_src2.txt', numpy.transpose([m.dataplot.x, m.dataplot.y, m.modelplot.x, m.modelplot.y]))
