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
	class CompositeModel(object):
		pass
	RSPModelNoPHA, RMFModelNoPHA = object, object

def pca(M):
	mean = M.mean(axis=0)
	Moffset = M - mean.reshape((1,-1))
	U, s, Vt = numpy.linalg.svd(Moffset, full_matrices=False)
	V = Vt.T
	print('variance explained:', s**2/len(M))
	c = numpy.cumsum(s**2/len(M))
	c = c / c[-1]
	for cut in 0.80, 0.90, 0.95, 0.99:
		idx, = numpy.where(c>cut)
		n = idx.min() + 1
		print('  --> need %d components to explain %.2f%%' % (n, cut))
	return U, s, V, mean

def pca_predict(U, s, V, mean):
	S = numpy.diag(s)
	return numpy.dot(U, numpy.dot(S, V.T)) + mean.reshape((1,-1))

def pca_get_vectors(s, V, mean):
	#U = numpy.eye(len(s))
	#return pca_predict(U, s, V, mean)
	Sroot = numpy.diag(s**0.5)
	return numpy.dot(Sroot, V.T)

def pca_cut(U, s, V, mean, ncomponents=20):
	return U[:, :ncomponents], s[:ncomponents], V[:,:ncomponents], mean
def pca_cut_adapt(U, s, V, mean):
	return U[:, :ncomponents], s[:ncomponents], V[:,:ncomponents], mean

def pca_check(M, U, s, V, mean):
	# if we use only the first 20 PCs the reconstruction is less accurate
	Mhat2 = pca_predict(U, s, V, mean)
	print("Using %d PCs, MSE = %.6G"  % (len(s), numpy.mean((M - Mhat2)**2)))
	return M - Mhat2

def get_unit_response(i):
	copy_data(i,"temp_unitrsp")
	unit_arf = get_bkg_arf("temp_unitrsp")
	unit_arf.specresp = 0. * unit_arf.specresp + 1.0
	bunitrsp = get_response("temp_unitrsp", bkg_id=1)
	delete_data("temp_unitrsp")
	return bunitrsp


class IdentityResponse(RSPModelNoPHA):
	def __init__(self, n, model, arf, rmf):
		self.n = n
		RSPModelNoPHA.__init__(self, arf=arf, rmf=rmf, model=model)
		self.elo = numpy.arange(n)
		self.ehi = numpy.arange(n)
		self.lo = numpy.arange(n)
		self.hi = numpy.arange(n)
		self.xlo = numpy.arange(n)
		self.xhi = numpy.arange(n)
	def apply_rmf(src):
		return src
	def calc(self, p, x, xhi=None, *args, **kwargs):
		src = self.model.calc(p, self.xlo, self.xhi)
		assert numpy.isfinite(src).all(), src
		return src


class IdentityRMF(RMFModelNoPHA):
	def __init__(self, n, model, rmf):
		self.n = n
		RMFModelNoPHA.__init__(self, rmf=rmf, model=model)
		self.elo = numpy.arange(n)
		self.ehi = numpy.arange(n)
		self.lo = numpy.arange(n)
		self.hi = numpy.arange(n)
		self.xlo = numpy.arange(n)
		self.xhi = numpy.arange(n)
	def apply_rmf(src):
		return src
	def calc(self, p, x, xhi=None, *args, **kwargs):
		src = self.model.calc(p, self.xlo, self.xhi)
		assert numpy.isfinite(src).all(), src
		return src


def get_identity_response(i):
	n = get_bkg(i).counts.size
	rmf = get_rmf(i)
	try:
		arf = get_arf(i)
		return lambda model: IdentityResponse(n, model, arf=arf, rmf=rmf)
	except:
		return lambda model: IdentityRMF(n, model, rmf=rmf)



logf = logging.getLogger('bxa.Fitter')
logf.setLevel(logging.INFO)

# Model
class PCAModel(ArithmeticModel):
	def __init__(self, modelname, data):
		self.U = data['U']
		self.V = numpy.matrix(data['components'])
		self.mean = data['mean']
		self.s = data['values']
		self.ilo = data['ilo']
		self.ihi = data['ihi']

		p0 = Parameter(modelname=modelname, name='lognorm', val=1, min=-5, max=20,
			hard_min=-100, hard_max=100)
		pars = [p0]
		for i in range(len(self.s)):
			pi = Parameter(modelname=modelname, name='PC%d' % (i+1),
				val=0, min=-20, max=20,
				hard_min=-1e300, hard_max=1e300)
			pars.append(pi)
		super(ArithmeticModel, self).__init__(modelname, pars=pars)

	def calc(self, p, left, right, *args, **kwargs):
		try:
			lognorm = p[0]
			pars = numpy.array(p[1:])
			y = numpy.array(pars * self.V.T + self.mean).flatten()
			cts = (10**y - 1) * 10**lognorm

			out = left * 0.0
			out[self.ilo:self.ihi] = cts.cumsum()
			return out
		except Exception as e:
			print("Exception in PCA model:", e, p)
			raise e

	def startup(self, *args):
		pass
	def teardown(self, *args):
		pass
	def guess(self, dep, *args, **kwargs):
		self._load_params()


class GaussModel(ArithmeticModel):
	def __init__(self, modelname):
		self.LineE = Parameter(modelname=modelname, name='LineE', val=1, min=0, max=1e38)
		self.Sigma = Parameter(modelname=modelname, name='Sigma', val=1, min=0, max=1e38)
		self.norm = Parameter(modelname=modelname, name='norm', val=1, min=0, max=1e38)
		pars = (self.LineE, self.Sigma, self.norm)
		super(ArithmeticModel, self).__init__(modelname, pars=pars)

	def calc(self, p, left, right, *args, **kwargs):
		try:
			LineE, Sigma, norm = p
			cts = norm * numpy.exp(-0.5 * ((left - LineE)/Sigma)**2)
			out = cts.cumsum()
			return cts
		except Exception as e:
			print("Exception in PCA model:", e, p)
			raise e

	def startup(self):
		pass

	def teardown(self):
		pass
	def guess(self, dep, *args, **kwargs):
		self._load_params()


class PCAFitter(object):
	"""Fitter mixing PCA-based templates and gaussian lines """
	def __init__(self, id=None):
		"""
		id: which data id to fit

		filename: prefix for where to store background information

		load: whether the background file should be loaded now
		"""
		self.id = id
		logf.info('PCAFitter(for ID=%s)' % (id))
		hdr = get_bkg(id).header
		self.ndata = len(get_bkg(id).counts)

		telescope = hdr.get('TELESCOP','')
		instrument = hdr.get('INSTRUME', '')
		if telescope == '' and instrument == '':
			raise Exception('ERROR: The TELESCOP/INSTRUME headers are not set in the data file.')
		for folder in os.environ.get('BKGMODELDIR', '.'), os.path.dirname(__file__):
			filename = os.path.join(folder, ('%s_%s_%d.json' % (telescope, instrument, self.ndata)).lower())
			if os.path.exists(filename):
				self.load(filename)
				return
			filename = os.path.join(folder, ('%s_%d.json' % (telescope, self.ndata)).lower())
			if os.path.exists(filename):
				self.load(filename)
				return
		raise Exception('ERROR: Could not load PCA components for this detector (%s %s, %d channels). Try the SingleFitter instead.' % (telescope, instrument, self.ndata))

	def load(self, filename):
		logf.info('loading PCA information from %s' % (filename))
		data = json.load(open(filename))
		self.pca = dict()
		for k, v in data.items():
			self.pca[k] = numpy.array(v)

	def decompose(self):
		ilo = int(self.pca['ilo'])
		ihi = int(self.pca['ihi'])
		lo = self.pca['lo']
		hi = self.pca['hi']
		mean = self.pca['mean']
		V = numpy.matrix(self.pca['components'])
		s = self.pca['values']
		U = self.pca['U']
		cts = get_data(self.id).counts[ilo:ihi]
		ncts = cts.sum()
		logf.info('have %d background counts for deconvolution' % ncts)
		y = numpy.log10(cts * 1. / ncts  + 1.0)
		z = (y - mean) * V
		assert z.shape == (1,len(s)), z.shape
		z = z.tolist()[0]
		return numpy.array([numpy.log10(ncts + 0.1)] + z)

	def calc_bkg_stat(self):
		ss = [s for s in get_stat_info() if self.id in s.ids and s.bkg_ids is not None and len(s.bkg_ids) > 0]
		if len(ss) != 1:
			for s in get_stat_info():
				if self.id in s.ids and len(s.bkg_ids) > 0:
					print('get_stat_info returned: ids=%s bkg_ids=%s' % (s.ids, s.bkg_ids))

		assert len(ss) == 1
		return ss[0].statval

	def fit(self):
		# try a PCA decomposition of this spectrum
		logf.info('fitting background of ID=%s using PCA method' % (self.id))
		initial = self.decompose()
		logf.info('fit: initial PCA decomposition: %s' % (initial))
		id = self.id
		set_method('neldermead')
		bkgmodel = PCAModel('pca%s' % id, data=self.pca)
		self.bkgmodel = bkgmodel
		response = get_identity_response(self.id)
		convbkgmodel = response(bkgmodel)
		set_bkg_full_model(self.id, convbkgmodel)
		for p, v in zip(bkgmodel.pars, initial):
			p.val = v
		srcmodel = get_model(self.id)
		set_full_model(self.id, srcmodel)
		fit_bkg(id=self.id)
		logf.info('fit: first full fit done')
		final = [p.val for p in get_bkg_model(id).pars]
		logf.info('fit: parameters: %s' % (final))
		initial_v = self.calc_bkg_stat()
		logf.info('fit: stat: %s' % (initial_v))

		# lets try from zero
		logf.info('fit: second full fit from zero')
		for p in bkgmodel.pars:
			p.val = 0
		fit_bkg(id=self.id)
		initial_v0 = self.calc_bkg_stat()
		logf.info('fit: parameters: %s' % (final))
		logf.info('fit: stat: %s' % (initial_v0))

		# pick the better starting point
		if initial_v0 < initial_v:
			logf.info('fit: using zero-fit')
			initial_v = initial_v0
			final = [p.val for p in get_bkg_model(id).pars]
		else:
			logf.info('fit: using decomposed-fit')
			for p, v in zip(bkgmodel.pars, final):
				p.val = v

		# start with the full fit and remove(freeze) parameters
		print('%d parameters, stat=%.2f' % (len(initial), initial_v))
		results = [(2 * len(final) + initial_v, final, len(final), initial_v)]
		for i in range(len(initial)-1, 0, -1):
			bkgmodel.pars[i].val = 0
			bkgmodel.pars[i].freeze()
			fit_bkg(id=self.id)
			final = [p.val for p in get_bkg_model(id).pars]
			v = self.calc_bkg_stat()
			print('--> %d parameters, stat=%.2f' % (i, v))
			results.insert(0, (v + 2*i, final, i, v))

		print()
		print('Background PCA fitting AIC results:')
		print('-----------------------------------')
		print()
		print('stat Ncomp AIC')
		for aic, params, nparams, val in results:
			print('%-05.1f %2d %-05.1f' % (val, nparams, aic))
		aic, final, nparams, val = min(results)
		for p, v in zip(bkgmodel.pars, final):
			p.val = v
		for i in range(nparams):
			bkgmodel.pars[i].thaw()

		print()
		print('Increasing parameters again...')
		# now increase the number of parameters again
		#results = [(aic, final, nparams, val)]
		last_aic, last_final, last_nparams, last_val = aic, final, nparams, val
		for i in range(last_nparams, len(bkgmodel.pars)):
			next_nparams = i + 1
			bkgmodel.pars[i].thaw()
			for p, v in zip(bkgmodel.pars, last_final):
				p.val = v
			fit_bkg(id=self.id)
			next_final = [p.val for p in get_bkg_model(id).pars]
			v = self.calc_bkg_stat()
			next_aic = v + 2*next_nparams
			if next_aic < last_aic:
				# accept
				print('%d parameters, aic=%.2f ** accepting' % (next_nparams, next_aic))
				last_aic, last_final, last_nparams, last_val = next_aic, next_final, next_nparams, v
			else:
				print('%d parameters, aic=%.2f' % (next_nparams, next_aic))
			# stop if we are 3 parameters ahead what we needed
			if next_nparams >= last_nparams + 3:
				break

		print('Final choice: %d parameters, aic=%.2f' % (last_nparams, last_aic))
		# reset to the last good solution
		for p, v in zip(bkgmodel.pars, last_final):
			p.val = v

		last_model = convbkgmodel
		for i in range(10):
			print()
			print('Adding Gaussian#%d' % (i+1))
			# find largest discrepancy
			set_analysis(id, "ener", "rate")
			m = get_bkg_fit_plot(id)
			y = m.dataplot.y.cumsum()
			z = m.modelplot.y.cumsum()
			diff_rate = numpy.abs(y - z)
			set_analysis(id, "ener", "counts")
			m = get_bkg_fit_plot(id)
			x = m.dataplot.x
			y = m.dataplot.y.cumsum()
			z = m.modelplot.y.cumsum()
			diff = numpy.abs(y - z)
			i = numpy.argmax(diff)
			energies = x
			e = x[i]
			print('largest remaining discrepancy at %.3fkeV[%d], need %d counts' % (x[i], i, diff[i]))
			#e = x[i]
			power = diff_rate[i]
			# lets try to inject a gaussian there

			g = xsgaussian('g_%d_%d' % (id, i))
			print('placing gaussian at %.2fkeV, with power %s' % (e, power))
			# we work in energy bins, not energy
			g.LineE.min = energies[0]
			g.LineE.max = energies[-1]
			g.LineE.val = e
			if i > len(diff) - 2:
				i = len(diff) - 2
			if i < 2:
				i = 2
			g.Sigma = (x[i + 1] - x[i - 1])
			g.Sigma.min = (x[i + 1] - x[i - 1])/3
			g.Sigma.max = x[-1] - x[0]
			g.norm.min = power * 1e-6
			g.norm.val = power
			convbkgmodel2 = response(g)
			next_model = last_model + convbkgmodel2
			set_bkg_full_model(self.id, next_model)
			fit_bkg(id=self.id)
			next_final = [p.val for p in get_bkg_model(id).pars]
			next_nparams = len(next_final)
			v = self.calc_bkg_stat()
			next_aic = v + 2 * next_nparams
			print('with Gaussian:', next_aic, '; change: %.1f (negative is good)' % (next_aic - last_aic))
			if next_aic < last_aic:
				print('accepting')
				last_model = next_model
				last_aic, last_final, last_nparams, last_val = next_aic, next_final, next_nparams, v
			else:
				print('not significant, rejecting')
				set_bkg_full_model(self.id, last_model)
				for p, v in zip(last_model.pars, last_final):
					p.val = v
				break

def auto_background(id):
	"""Automatically fits background *id* based on PCA-based templates,
	and additional gaussian lines as needed by AIC."""
	bkgmodel = PCAFitter(id)
	log_sherpa = logging.getLogger('sherpa.astro.ui.utils')
	prev_level = log_sherpa.level
	try:
		log_sherpa.setLevel(logging.WARN)
		bkgmodel.fit()
	finally:
		log_sherpa.setLevel(prev_level)
	m = get_bkg_fit_plot(id)
	numpy.savetxt('test_bkg.txt', numpy.transpose([m.dataplot.x, m.dataplot.y, m.modelplot.x, m.modelplot.y]))
	return get_bkg_model(id)


__all__ = ['PCAFitter', 'PCAModel', 'auto_background', 'get_identity_response', 'get_unit_response']
