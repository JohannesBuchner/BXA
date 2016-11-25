#!/usr/bin/env python
# -*- coding: utf-8 -*- 

"""
BXA (Bayesian X-ray Analysis) for Sherpa

Copyright: Johannes Buchner (C) 2013-2016
"""

import os
from math import log10, isnan, isinf
if 'MAKESPHINXDOC' not in os.environ:
	import sherpa.astro.ui as ui
	from sherpa.stats import Cash, CStat

import numpy

from sherpa.models import ArithmeticModel, CompositeModel
class VariableCachedModel(CompositeModel, ArithmeticModel):
	def __init__(self, othermodel):
		self.othermodel = othermodel
		self.cache = None
		self.lastp = None
		print 'calling CompositeModel...'
		CompositeModel.__init__(self, name='cached(%s)' % othermodel.name, parts=(othermodel,))
	
	def calc(self, p, left, right, *args, **kwargs):
		if self.cache is None or self.lastp != p:
			print '   recomputing cached model ... '
			self.cache = self.othermodel.calc(p, left, right, *args, **kwargs)
			self.lastp = p
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

class CachedModel(CompositeModel, ArithmeticModel):
	def __init__(self, othermodel):
		self.othermodel = othermodel
		self.cache = None
		self.lastp = None
		print 'calling CompositeModel...'
		CompositeModel.__init__(self, name='cached(%s)' % othermodel.name, parts=(othermodel,))
	
	def calc(self, p, left, right, *args, **kwargs):
		if self.cache is None or (self.lastp != p).any():
			print '   recomputing cached model ... '
			self.cache = self.othermodel.calc(p, left, right, *args, **kwargs)
			self.lastp = left
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

