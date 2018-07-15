from __future__ import print_function

import bxa.sherpa as bxa
print('loading background fitting module...')
from bxa.sherpa.background.fitters import SingleFitter
import bxa.sherpa.background.xmm

import logging
logging.basicConfig(filename='bxa.log',level=logging.DEBUG)
logFormatter = logging.Formatter("[%(name)s %(levelname)s]: %(message)s")
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.INFO)
logging.getLogger().addHandler(consoleHandler)

# Example script for analysing XMM observations


# choose your preferred model for galactic absorption
galabs = xstbabs.galabs
# the galactic NH in the direction of your source
# e.g. from http://www.swift.ac.uk/analysis/nhtot/index.php
galabs.nH = 0.01
galabs.nH.freeze()

i = 1
#load MOS data set
load_pha(i, 'mos_spec.fits') 
load_rmf(i, 'mos.rmf')
load_arf(i, 'mos.arf')
load_bkg(i, 'mos_backspec.fits')
ignore(None, 0.3)
ignore(10.0, None)
mosbkgmodel = bxa.sherpa.background.xmm.get_mos_bkg_model(i, galabs, fit=True)

print('freezing MOS background parameters...')
for p in get_bkg_model(i).pars:
	p.freeze()

i = 2
# load PN data set
load_pha(i, 'pn_spec.fits')
load_rmf(i, 'pn.rmf')
load_arf(i, 'pn.arf')
load_bkg(i, 'pn_backspec.fits')
ignore(None, 0.3)
ignore(10.0, None)
pnbkgmodel = bxa.sherpa.background.xmm.get_pn_bkg_model(i, galabs, fit=True)

print('freezing PN background parameters...')
for p in get_bkg_model(i).pars:
	p.freeze()

# set up model for source spectrum
inner_model = galabs * xszpowerlw.pl
set_model(1, inner_model)
set_model(2, inner_model)

# add the background to the source spectrum
# use caching to make background fast (is fixed at this point anyways)
from bxa.sherpa.cachedmodel import CachedModel
set_bkg_full_model(1, CachedModel(get_bkg_model(1,1)))
set_full_model(1, get_response(1)(inner_model) + CachedModel(mosbkgmodel))
set_bkg_full_model(2, CachedModel(get_bkg_model(2,1)))
set_full_model(2, get_response(2)(inner_model) + CachedModel(pnbkgmodel))


# now run BXA, fitting etc.


