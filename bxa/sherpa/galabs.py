#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from __future__ import print_function

"""
BXA (Bayesian X-ray Analysis) for Sherpa

Copyright: Johannes Buchner (C) 2013-2019
"""

import os
if 'MAKESPHINXDOC' not in os.environ:
	import sherpa.astro.ui as ui
	from sherpa.stats import Cash, CStat

from .cachedmodel import CachedModel

def auto_galactic_absorption(id=None):
	#model = ui._session.get_model(id).model
	filename = ui._session.get_data(id).name + '.nh'
	print(('loading nH from %s (expecting something like 1e21 in there)' % filename))
	nH = float(open(filename).read().strip())
	galabso = ui.xstbabs('galabso%s' % id)
	#galabsmodel = model * galabso
	galabso.nH = nH / 1e22
	print(('setting galactic nH to %s [units of 1e22/cm²]' % (galabso.nH.val)))
	galabso.nH.freeze()
	return galabso
	cgalabso = CachedModel(galabso)
	print('returning cached galaxy absorption model')
	return cgalabso
	#ui._session.set_model(id, galabsmodel)
