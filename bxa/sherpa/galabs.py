#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
BXA (Bayesian X-ray Analysis) for Sherpa

Copyright: Johannes Buchner (C) 2013-2015
"""

import os
from math import log10, isnan, isinf
if 'MAKESPHINXDOC' not in os.environ:
	import sherpa.astro.ui as ui
	from sherpa.stats import Cash, CStat

import numpy

from sherpa.models import ArithmeticModel, CompositeModel
class CachedModel(CompositeModel, ArithmeticModel):
	def __init__(self, othermodel):
		self.othermodel = othermodel
		self.cache = None
		print 'calling CompositeModel...'
		CompositeModel.__init__(self, name='cached(%s)' % othermodel.name, parts=(othermodel,))
	
	def calc(self, p, left, right, *args, **kwargs):
		if self.cache is None:
			self.cache = self.othermodel.calc(p, left, right, *args, **kwargs)
		return self.cache

	def startup(self):
		self.othermodel.startup()
		CompositeModel.startup(self)
	
	def teardown(self):
		self.othermodel.teardown()
		CompositeModel.teardown(self)

	def guess(self, dep, *args, **kwargs):
		self.othermodel.guess(dep, *args, **kwargs)
		CompositeModel.guess(self, dep, *args, **kwargs)

def auto_galactic_absorption(id=None):
	#model = ui._session.get_model(id).model
	filename = ui._session.get_data(id).name + '.nh'
	print('loading nH from %s (expecting something like 1e21 in there)' % filename)
	nH = float(open(filename).read().strip())
	galabso = ui.xstbabs.galabso
	#galabsmodel = model * galabso
	galabso.nH = nH / 1e22
	print('setting galactic nH to %s [units of 1e22/cm²]' % (galabso.nH))
	galabso.nH.freeze()
	cgalabso = CachedModel(galabso)
	#print('returning cached galaxy absorption model')
	return cgalabso
	#ui._session.set_model(id, galabsmodel)


