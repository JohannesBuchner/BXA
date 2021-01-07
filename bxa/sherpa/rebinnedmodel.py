from __future__ import print_function
"""
Precomputes a interpolated grid model from a complex model.

That model can then be used for fast access.
"""

import os

if 'MAKESPHINXDOC' not in os.environ:
	from sherpa.astro.ui import *
	from sherpa.models.parameter import Parameter
	from sherpa.models import ArithmeticModel
else:
	ArithmeticModel = object

import itertools
import numpy
from tqdm import tqdm

"""
custom interpolation code, needs
https://github.com/JohannesBuchner/npyinterp
"""
from monointerp import interp


"""
slowmodel:
   a arbitrary model that should be turned into a fast model by gridding
ebins:
   energy bins to compute over, e.g. ebins=numpy.linspace(0.1, 50, 200)
parameters:
   a list of parameters to modify and the number of grid points to use.
   Example:
      parameters = [
        (warmabs.myabs.nH, 21),
        (warmabs.myabs.ionisation, 10),
      ]
      This creates a grid with 21x10 points.
   
   Note that normalisation and redshift should not be part of the gridding,
   they are additionally added to the final model. 
   
   Note that all parameters that are not varied are fixed and should be set to 
   the right (fixed) values.
   
   Note that the interpolation is always linear in the parameters. If you would
   like a interpolation in logarithmic gridding, introduce a helper parameter:
   
     # create helper parameter
     lognH = Parameter(modelname='mymodel', name='nH', val=20, min=20, max=26,
         hard_min=20, hard_max=26)
     # link to the parameter we want to change
     warmabs.myabs.nH = lognH 
     # now pass lognH for logarithmic gridding
     parameters = [
        (lognH, 21),
        (warmabs.myabs.ionisation, 10),
     ]
   
"""
class RebinnedModel(ArithmeticModel):
	def __init__(self, slowmodel, ebins, parameters, filename, modelname='rebinnedmodel'):
		params = [param for param, nbins in parameters]
	
		bins = [numpy.linspace(param.min, param.max, nbins) for param, nbins in parameters]
		left = ebins[:-1]
		right = ebins[1:]
		width = right - left
		ntot = numpy.product([len(bin) for bin in bins])
		try:
			alldata = numpy.load(filename)
			data = alldata['y']
			assert numpy.allclose(alldata['x'], ebins), 'energy binning differs -- plese delete "%s"' % filename
			print('loaded from %s' % filename)
		except IOError:
			print('creating rebinnedmodel, this might take a while')
			print('interpolation setup:')
			print('   energies:', ebins[0], ebins[1], '...', ebins[-2], ebins[-1])
			for (param, nbins), bin in zip(parameters, bins):
				print('   %s: %s - %s with %d points' % (param.fullname, param.min, param.max, nbins))
				print('        ', bin)
		
			data = numpy.zeros((ntot, len(ebins)-1))
			for j, element in enumerate(tqdm(list(itertools.product(*bins)), disable=None)):
				for i, p in enumerate(params):
					if p.val != element[i]:
						p.val = element[i]
				values = [p.val for p in slowmodel.pars]
				model = slowmodel.calc(values, left, right)
				#assert numpy.isfinite(model).all(), ('model:', model)
				#model = modelcum / width
				#assert numpy.isfinite(model).all(), ('model', model)
				data[j] = model
				# (modelcum * width).cumsum()
			print('model created. storing to %s' % filename)
			numpy.savez(filename, x=ebins, y=data)
		self.init(modelname=modelname, x=ebins, data=data, parameters=parameters) 
	
	def init(self, modelname, x, data, parameters):
		#print 'BinReaderModel(%s)' % modelname
		self.data = data
		
		pars = []
		#print '  copying parameters'
		for param, nbins in parameters:
			lo = param.min
			hi = param.max
			newp = Parameter(modelname=modelname, name=param.name, 
				val=param.val, min=lo, max=hi, hard_min=lo, hard_max=hi)
			setattr(self, param.name, newp)
			pars.append(newp)
		#print '  adding norm'
		newp = Parameter(modelname=modelname, name='norm', val=1, min=0, max=1e10, hard_min=-1e300, hard_max=1e300)
		self.norm = newp
		pars.append(newp)
		#print '  adding redshift'
		newp = Parameter(modelname=modelname, name='redshift', val=0, min=0, max=10, hard_min=0, hard_max=100)
		self.redshift = newp
		pars.append(newp)
		
		self.x = x
		self.binnings = [(param.min, param.max, nbins) for param, nbins in parameters]
		super(RebinnedModel, self).__init__(modelname, pars=pars)
	def get(self, coords):
		# compute row to access
		j = 0
		for i, ((lo, hi, n), c) in list(enumerate(zip(self.binnings, coords))):
			k = int((c - lo) * n / (hi - lo))
			if k == n: 
				k = n - 1
			#print '  for param %d: %d/%d -> %d' % (i, k, n, j * n + k)
			j = j * n + k
		#print 'accessing', j
		return self.data[j]
	def calc(self, p, left, right, *args, **kwargs):
		# print('  calc', p, left, right, args, kwargs)
		coords = p[:-2]
		norm = p[-2]
		redshift = p[-1]
		#print '    shifting ...'
		shiftedleft  = left *(1.+redshift)
		shiftedright = right*(1.+redshift)
		x = self.x
		#print '    getting ...'
		y = self.get(coords)
		#print '    y', y
		
		left = x[:-1]
		right = x[1:]
		width = right - left
		assert (y >= 0).all()
		yw = (y).cumsum()
		#for a, b, c, d in zip(x, width, y, yw):
		#	print '%.3f %.3f %.3f %.3f' % (a, b, c, d)
		
		#print '    y*w', y
		#print '    interp ...'
		r = interp(shiftedleft, shiftedright, x, yw)
		#for a, b, c in zip(shiftedleft, shiftedright, r):
		#	print '%.3f %.3f %.3f' % (a, b, c)
		#print '    result', r
		assert numpy.isfinite(r).all(), r
		#print r[len(r)/2], yw[len(yw)/2], norm
		return r * norm
