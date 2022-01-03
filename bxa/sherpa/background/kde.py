from __future__ import print_function
"""
PCA-based background model.
"""
import numpy
import json
import logging
import warnings
import os

if 'MAKESPHINXDOC' not in os.environ:
	import sherpa.astro.ui as ui
	from sherpa.stats import Cash, CStat
	from sherpa.models.parameter import Parameter
	from sherpa.models import ArithmeticModel, CompositeModel
	from sherpa.astro.ui import *
	from sherpa.astro.instrument import RSPModelNoPHA, RMFModelNoPHA
else:
	# mock objects when sherpa doc is built
	ArithmeticModel = object

from .pca import get_identity_response

logf = logging.getLogger('bxa.Fitter')
logf.setLevel(logging.INFO)
import scipy.stats

# Model
class KDEModel(ArithmeticModel):
	def __init__(self, channels, model, modelname='KDE'):
		self.channels = channels
		self.model = model

		p0 = Parameter(modelname=modelname, name='lognorm', val=1, min=-5, max=20,
			hard_min=-100, hard_max=100)
		super(ArithmeticModel, self).__init__(modelname, pars=[p0])

	def calc(self, p, left, right, *args, **kwargs):
		lognorm = p[0]
		return 10**lognorm * numpy.interp(left, self.channels, self.model)

	def startup(self, *args):
		pass
	def teardown(self, *args):
		pass
	def guess(self, dep, *args, **kwargs):
		pass

def set_kde_background(id, bw_method=None):
	cts = get_bkg(id).counts.astype(int)
	ndata = len(cts)
	samples = []
	for chan, counts in enumerate(cts):
		samples += [chan] * counts
	kde = scipy.stats.gaussian_kde(samples, bw_method=bw_method)
	channels = numpy.arange(ndata)
	density = kde(channels)
	bkgmodel = KDEModel(channels=channels, model=density / density.sum() * cts.sum())

	response = get_identity_response(id)
	convbkgmodel = response(bkgmodel)
	set_bkg_full_model(id, convbkgmodel)
	return get_bkg_model(id)

__all__ = ['KDEModel', 'set_kde_background']
