"""
Precomputes a interpolated grid model from a complex model.

That model can then be used for fast access.
"""

from sherpa.astro.ui import *
from sherpa.models.parameter import Parameter
from sherpa.models import ArithmeticModel
import itertools
import numpy
import progressbar

"""interpolation code
"""
from ctypes import cdll, c_int
from numpy.ctypeslib import ndpointer

lib = cdll.LoadLibrary('npyinterp.so')
lib.interpolate.argtypes = [
	ndpointer(dtype=numpy.float64, ndim=1, flags='C_CONTIGUOUS'), 
	ndpointer(dtype=numpy.float64, ndim=1, flags='C_CONTIGUOUS'), 
	ndpointer(dtype=numpy.float64, ndim=1, flags='C_CONTIGUOUS'), 
	c_int, 
	ndpointer(dtype=numpy.float64, ndim=1, flags='C_CONTIGUOUS'), 
	ndpointer(dtype=numpy.float64, ndim=1, flags='C_CONTIGUOUS'), 
	c_int]
def interp(left, right, x, y):
	## sherpa-2> %timeit calc_kcorr(z=3, obslo=0.2,obshi=2)
	## 1000 loops, best of 3: 1.94 ms per loop
	## (2577 times faster than atable)
	#print 'using interpolation library', len(left), len(right), len(x), len(y)
	z = numpy.zeros_like(left) - 1
	r = lib.interpolate(left, right, z, len(left), x, y, len(x))
	if r != 0:
		raise Exception("Interpolation failed")
	return z


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
			print 'loaded from %s' % filename
		except IOError:
			print 'creating rebinnedmodel, this might take a while'
			print 'interpolation setup:'
			print '   energies:', ebins[0], ebins[1], '...', ebins[-2], ebins[-1]
			for (param, nbins), bin in zip(parameters, bins):
				print '   %s: %s - %s with %d points' % (param.fullname, param.min, param.max, nbins)
				print '        ', bin
		
			data = numpy.zeros((ntot, len(ebins)-1))
			pbar = progressbar.ProgressBar(widgets=[progressbar.Percentage(), progressbar.Counter('%5d'), progressbar.Bar(), progressbar.ETA()],
				maxval=ntot).start()
			for j, element in enumerate(itertools.product(*bins)):
				for i, p in enumerate(params):
					if p.val != element[i]:
						p.val = element[i]
				pbar.update(j)
				values = [p.val for p in slowmodel.pars]
				model = slowmodel.calc(values, left, right)
				#assert numpy.isfinite(model).all(), ('model:', model)
				#model = modelcum / width
				#assert numpy.isfinite(model).all(), ('model', model)
				data[j] = model
				# (modelcum * width).cumsum()
			pbar.finish()
			print 'model created. storing to %s' % filename
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
			print '  for param %d: %d/%d -> %d' % (i, k, n, j * n + k)
			j = j * n + k
		print 'accessing', j
		return self.data[j]
	def calc(self, p, left, right, *args, **kwargs):
		print '  calc', p
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



"""
def rebinnedmodel(inputmodel, ebins, nparambins = 100):
	import astropy.io.fits as pyfits
	
	hdu = pyfits.PrimaryHDU(n)
	hdulist = pyfits.HDUList([hdu])
	hdulist.writeto('my.rmf')
	
	def arr(n, i):
		a = numpy.zeros(n)
		a[i] = 1
		return a
	
	elo = ebins[:-1]
	ehi = ebins[1:]
	n = len(ebins) - 1
	rmf_data = numpy.array([(eloi, ehii, 1, 0, n, arr(n, i)) for eloi, ehii in enumerate(zip(elo, ehi))],
		dtype = [('ENERG_LO', '>f4'),
			('ENERG_HI', '>f4'),
			('N_GRP', '>i2'),
			('F_CHAN', '>i2'),
			('N_CHAN', '>i2'),
		])
"""

