#!/usr/bin/env python
"""

Background model has stages
SingleFitter goes through stages and fits each with chi^2, then cstat

MultiFitter fits first one with SingleFitter,
then goes through all the others
by setting the parameter values to those of the previous id
and then fitting each stage


"""
import numpy
from numpy import log10
import json
import logging
import os
import astropy.io.fits as pyfits
import scipy.stats
import scipy.optimize
import datetime
import time


def create_ogip_atable(BackArray, BackSpecFile, SourceSpecFile, outfilename, ilo, ihi):
	"""
	Convert the PCA background model (1D array of counts per channel) into a additive Xspec table model.

	Parameters
	------------
	BackSpecFile: str
		background spectrum file (fits)
	BackArray: numpy array
		background model data
	outfilename: str
		where the atable fits file should be written to
	ilo: int
		lower index of valid data in BackArray
	ihi: int
		upper index of valid data in BackArray
	"""
	# code written by Liu Teng
	# adapted by Johannes Buchner

	bkgspec, hdr = pyfits.getdata(BackSpecFile, header=True, extname='SPECTRUM')
	Nchannel = len(bkgspec)

	hdu0 = pyfits.PrimaryHDU()
	nowstr1 = datetime.datetime.fromtimestamp(time.time()).isoformat()
	nowstr = nowstr1[:nowstr1.rfind('.')]
	hdu0.header['CREATOR'] = "SampSpecFit"
	hdu0.header['DATE'] = nowstr
	hdu0.header['HDUCLASS'] = ('OGIP','format conforms to OGIP standard')
	hdu0.header['HDUDOC']   = ('OGIP/92-009','document defining format')
	hdu0.header['HDUCLAS1'] = ('XSPEC TABLE MODEL','model spectra for XSPEC')
	hdu0.header['HDUVERS1'] = ('1.0.0','version of format')
	hdu0.header['MODLNAME'] = ('pcabkg', 'model name (12 chars max)')
	hdu0.header['MODLUNIT'] = ('ph/cm^2/s', 'model units (12 chars max)')
	hdu0.header['REDSHIFT'] = (False,'whether redshift is to be a parameter')
	hdu0.header['ADDMODEL'] = (True,'whether this is an additive model')
	hdu0.header['LOELIMIT'] = (0, 'model value for energies below those tabulated')
	hdu0.header['HIELIMIT'] = (0, 'model value for energies above those tabulated')
	hdu0.header['EXTEND']   = True
	hdu0.header['SIMPLE']   = True

	if SourceSpecFile:
		source_hdr = pyfits.getheader(SourceSpecFile, extname='SPECTRUM')
		backscal = hdr['BACKSCAL'] / source_hdr['BACKSCAL']
	else:
		print()
		print()
		print("Warning: no source file provided. You need to scale the atable by the source BACKSCAL parameter!")
		backscal = hdr['BACKSCAL']
	dtype1 = [('NAME', 'S12'), ('METHOD', '>i4'), ('INITIAL', '>f4'), ('DELTA', '>f4'), ('MINIMUM', '>f4'), ('BOTTOM', '>f4'), ('TOP', '>f4'), ('MAXIMUM', '>f4'), ('NUMBVALS', '>i4'), ('VALUE', '>f4', (3,))]
	parameters = numpy.array([
		('isSource', 0, 1, -1, 0, 0, 1, 1, 2, numpy.array([0, 1, 0])),
	], dtype=dtype1)
	
	hdu1 = pyfits.BinTableHDU(data=parameters)
	hdu1.header['DATE'] = nowstr
	hdu1.header['EXTNAME'] = 'PARAMETERS'
	hdu1.header['HDUCLASS'] = 'OGIP'
	hdu1.header['HDUCLAS1'] = 'XSPEC TABLE MODEL'
	hdu1.header['HDUCLAS2'] = 'PARAMETERS'
	hdu1.header['HDUVERS1'] = '1.0.0'
	hdu1.header['NINTPARM'] = len(parameters)
	hdu1.header['NADDPARM'] = 0

	dtype2 = [('ENERG_LO', '>f4'), ('ENERG_HI', '>f4')]
	hdu2 = pyfits.BinTableHDU(data=numpy.array([(i, i+1) for i in range(0,Nchannel)], dtype=dtype2))
	hdu2.header['ilow'] = ilo+1
	hdu2.header['ihigh'] = ihi+1
	hdu2.header['DATE'] = nowstr
	hdu2.header['EXTNAME']  = 'ENERGIES'
	hdu2.header['HDUCLASS'] = 'OGIP'
	hdu2.header['HDUCLAS1'] = 'XSPEC TABLE MODEL'
	hdu2.header['HDUCLAS2'] = 'ENERGIES'
	hdu2.header['HDUVERS1'] = '1.0.0'
	hdu2.header['TUNIT1']   = 'keV'
	hdu2.header['TUNIT2']   = 'keV'

	dtype = [('PARAMVAL', '>f4', (len(parameters),)), 
	('INTPSPEC', '>f4', (Nchannel,)),
	]
	# store the model in counts / s / cm^2
	bspec = numpy.pad(BackArray, (ilo, Nchannel-ihi)) / hdr['EXPOSURE'] / hdr['AREASCAL']
	print("background spectrum is scaled by:", hdr['EXPOSURE'], hdr['AREASCAL'])
	# for the source, adjust by the background scaling factor
	sspec = bspec / backscal
	print(BackArray.mean())
	print("source spectrum is up-scaled by:", backscal)
	table = numpy.array([
		((0,), bspec),
		((1,), sspec),
	], dtype=dtype)
	hdu3 = pyfits.BinTableHDU(data=table)
	hdu3.header['DATE'] = nowstr
	hdu3.header['EXTNAME']  = 'SPECTRA'
	hdu3.header['TUNIT1']   = 'none'
	hdu3.header['TUNIT2']   = 'ph/channel/s'
	hdu3.header['TUNIT3']   = 'ph/channel/s'
	hdu3.header['HDUCLAS1'] = 'XSPEC TABLE MODEL'
	hdu3.header['HDUCLAS2'] = 'MODEL SPECTRA'
	hdu3.header['HDUVERS1'] = '1.0.0'

	pyfits.HDUList([hdu0,hdu1,hdu2,hdu3]).writeto(outfilename, overwrite=True)
	print("""

-> Xspec atable of the best-fit background created at: %(modelfilename)s.
Keep in mind that you need to use a diagonal RMF and no ARF for this
contribution. To use it in xspec:

    # load source data
    data 1:1 %(sourcefilename)s
    backgrnd 1 none

    # set your energy limits (before dummyrsp!)
    ignore 1:*
    notice 1:0.5-8.0

    # load background data separately
    data 2:2 %(backfilename)s
    ignore 2:*
    notice 2:%(ilo)d-%(ihi)d

    # set unit RMF for background model
    response 2 none
    dummyrsp 0 %(nchan)d %(nchan)d lin 0 1 2:1
    dummyrsp 0 %(nchan)d %(nchan)d lin 0 1 2:2

    # set background PCA model and its parameters:
    model 2:pcabkg atable{%(modelfilename)s}
    1
    1 -1
    0

    # then set your source model
    # model powerlaworwhatever

"""  % dict(
		sourcefilename=SourceSpecFile, modelfilename=outfilename,
		backfilename=BackSpecFile, nchan=Nchannel, ilo=ilo, ihi=ihi)
	)


def create_spectral_files(fitter, result, src_filename):
	ext = fitter.bkg_filename.split('.')[-1]
	f = pyfits.open(fitter.bkg_filename)
	# replace the COUNTS column with our model prediction
	# we need to change the data type from ints to floats
	origdata = f['SPECTRUM'].data
	i = origdata.dtype.names.index('COUNTS')
	dtype = [('COUNTS', '>f4') if name == 'COUNTS' else (name, origdata.dtype.fields[name][0]) for name in origdata.dtype.names]
	v = f['SPECTRUM'].data['COUNTS'] * 0.
	v[fitter.ilo:fitter.ihi] = result
	lnewdata = []
	for j, (origrow, newv) in enumerate(zip(origdata, v)):
		newrow = list(origrow)
		newrow[i] = newv
		lnewdata.append(tuple(newrow))
	newdata = numpy.array(lnewdata, dtype=dtype)
	hdu = pyfits.BinTableHDU(data=newdata, name=f['SPECTRUM'].name)
	for k, v in list(f['SPECTRUM'].header.items()):
		if k not in hdu.header:
			hdu.header[k] = v
	hdulist = [hdu if e.name == 'SPECTRUM' else e for e in f]
	fout = fitter.bkg_filename[:-len(ext)] + 'bstat.' + ext
	hdus = pyfits.HDUList(hdulist)
	hdus.writeto(fout, overwrite=True)
	hdus.close()
	del f
	
	# update source file
	print('creating src file with updated BACKFILE header ...')
	bext = src_filename.split('.')[-1]
	f = pyfits.open(src_filename)
	for e in f:
		if 'BACKFILE' in e.header:
			e.header['BACKFILE'] = fout
	foutsrc = src_filename[:-len(bext)] + 'bstat.' + bext
	f.writeto(foutsrc, overwrite=True)
	f.close()
	return foutsrc

"""
Find background model.

I analysed the background for many instruments, and stored mean and
 principle components. The data file tells us which instrument we deal with,
 so we load the correct file.
First guess: 
 1) PCA decomposition.
 2) Mean scaled, other components zero
The one with the better cstat is kept.
Then start with 0 components and add 1, 2 components until no improvement
in AIC/cstat.

"""
logf = logging.getLogger('bxa.Fitter')
logf.setLevel(logging.INFO)

class Parameter(object):
	def __init__(self, modelname, name, val, min, max, hard_min=min, hard_max=max):
		self.modelname = modelname
		self.name = name
		self.val = val
		self.min = min
		self.max = max

# Model 
class PCAModel(object):
	def __init__(self, data):
		modelname = 'pca'
		#self.U = data['U']
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
		self.pars = pars
	
	def calc(self, p):
		try:
			lognorm = p[0]
			pars = numpy.array(p[1:])
			y = numpy.array(pars * self.V.T + self.mean).flatten()
			cts = (10**y - 1) * 10**lognorm
			return cts
		except Exception as e:
			print("Exception in PCA model:", e, p)
			raise e

def gaussmodel_calc(x, LineE, Sigma, norm):
	cts = norm * numpy.exp(-0.5 * ((x - LineE)/Sigma)**2)
	return cts

def minimize(f, x0):
	return scipy.optimize.minimize(f, x0=x0, method='Nelder-Mead', tol=0.001, options=dict(maxiter=1000, disp=False))

class PCAFitter(object):
	def __init__(self, bkg_filename):
		f = pyfits.open(bkg_filename)
		self.bkg_filename = bkg_filename
		self.data = f[1].data['COUNTS'].astype(int)
		self.ndata = len(self.data)
		self.ngaussians = 0
		logf.info('PCAFitter starting')
		hdr = f[1].header
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
		nactivedata = self.pca['ihi'] - self.pca['ilo']
		assert self.pca['hi'].shape == (nactivedata,), 'spectrum has different number of channels: %d vs %s' % (len(self.pca['hi']), self.ndata)
		assert self.pca['lo'].shape == self.pca['hi'].shape
		assert self.pca['mean'].shape == self.pca['hi'].shape
		assert len(self.pca['components']) == nactivedata
		assert nactivedata <= self.ndata
		ilo = int(self.pca['ilo'])
		ihi = int(self.pca['ihi'])
		self.cts = self.data[ilo:ihi]
		self.x = numpy.arange(ihi-ilo)
		self.ilo = ilo
		self.ihi = ihi
	
	def decompose(self):
		#ilo = int(self.pca['ilo'])
		#ihi = int(self.pca['ihi'])
		#lo = self.pca['lo']
		#hi = self.pca['hi']
		mean = self.pca['mean']
		V = numpy.matrix(self.pca['components'])
		s = self.pca['values']
		#U = self.pca['U']
		ncts = self.cts.sum()
		logf.info('have %d background counts for deconvolution' % ncts)
		y = numpy.log10(self.cts * 1. / ncts  + 1.0)
		z = (y - mean) * V
		assert z.shape == (1,len(s)), z.shape
		return numpy.array([numpy.log10(ncts + 0.1)] + z.tolist()[0])
	
	def calc_bkg_stat(self, pred):
		if pred is None:
			return 1e100
		logls = scipy.stats.poisson(pred).logpmf(self.cts)
		stat = numpy.where(numpy.isfinite(logls), -2 * logls, 1e100 * (1 + numpy.max(self.cts) - numpy.nanmax(pred))**2).sum()
		#print("stat: %.1f" % stat)  #  pred, self.cts)
		return stat

	def complete_parameters(self, pars):
		newpars = numpy.zeros(len(self.model.pars))
		for i, p in enumerate(pars):
			newpars[i] = p
		return newpars

	def predict(self, pars):
		# add gaussians
		#ngausspars = 3 * self.ngaussians
		pred = 0
		for i in range(self.ngaussians):
			LineE, logSigma, lognorm = pars[3*i:3*(i+1)]
			if LineE < 0 or LineE > self.ndata:
				#print('LineE out of range:', LineE)
				return None
			# should not be narrower than a single bin, otherwise we get
			# overfitting
			if logSigma < log10(3.0) or logSigma > log10(self.ndata):
				#print('logSigma out of range:', logSigma, 10**logSigma)
				return None
			if lognorm < -6 or lognorm > 10:
				#print('lognorm out of range:', lognorm, 10**lognorm)
				return None
			pred = pred + gaussmodel_calc(self.x, LineE, 10**logSigma, 10**lognorm)
		pcapars = pars[3*self.ngaussians:]
		newpars = self.complete_parameters(pcapars)
		pred = pred + self.model.calc(newpars)
		return pred
	
	def calc_prior(self, pars):
		return 0 # no prior
		ngausspars = 3 * self.ngaussians
		#gausspars = pars[:ngausspars]
		pcapars = numpy.asarray(pars[ngausspars:])
		return numpy.sum((pcapars)**2) # gaussian prior with std 1
		
	
	def calc_bkg_stat_wrapped_gaussians(self, pars):
		return self.calc_bkg_stat(self.predict(pars)) + self.calc_prior(pars)
		
	def fit(self):
		# try a PCA decomposition of this spectrum
		logf.info('fitting background using PCA method')
		initial = self.decompose()
		logf.info('fit: initial PCA decomposition: %s' % (initial))
		# use neldermead first
		bkgmodel = PCAModel(data=self.pca)
		npars = len(bkgmodel.pars)
		self.model = bkgmodel
		for p, v in zip(bkgmodel.pars, initial):
			p.val = v
		
		predictions = []
		logf.info('fit: first fit ...')
		r = minimize(self.calc_bkg_stat_wrapped_gaussians, x0=initial)
		final = r.x
		predictions.append(self.predict(final))
		logf.info('fit: parameters: %s' % (final))
		initial_v = self.calc_bkg_stat_wrapped_gaussians(final)
		logf.info('fit: stat: %s' % (initial_v))
		
		# lets try from zero
		logf.info('fit: second full fit from zero ...')
		zero = numpy.zeros(len(initial))
		zero[0] = log10(numpy.mean(self.data))
		r = minimize(self.calc_bkg_stat_wrapped_gaussians, x0=zero)
		final_v0 = r.x
		initial_v0 = self.calc_bkg_stat_wrapped_gaussians(final)
		predictions.append(self.predict(final_v0))
		logf.info('fit: parameters: %s' % (final))
		logf.info('fit: stat: %s' % (initial_v0))
		
		# pick the better starting point
		if initial_v0 < initial_v:
			logf.info('fit: using zero-fit')
			initial_v = initial_v0
			final = final_v0
		else:
			logf.info('fit: using decomposed-fit')
		
		for p, v in zip(bkgmodel.pars, final):
			p.val = v
		
		# start with the full fit and remove(freeze) parameters
		print('%d parameters, stat=%.2f' % (len(initial), initial_v))
		results = [(2 * len(final) + initial_v, final, len(final), initial_v)]
		for i in range(len(initial)-1, 0, -1):
			initial = final[:i]
			r = minimize(self.calc_bkg_stat_wrapped_gaussians, x0=initial)
			final = self.complete_parameters(r.x)
			predictions.append(self.predict(final))
			v = self.calc_bkg_stat_wrapped_gaussians(final)
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
		
		print()
		print('Increasing parameters again...')
		# now increase the number of parameters again
		#results = [(aic, final, nparams, val)]
		last_aic, last_final, last_nparams, _ = aic, final, nparams, val
		for i in range(last_nparams, npars):
			next_nparams = i + 1
			initial = last_final[:i]
			r = minimize(self.calc_bkg_stat_wrapped_gaussians, x0=initial)
			v = self.calc_bkg_stat_wrapped_gaussians(r.x)
			next_final = self.complete_parameters(r.x)

			next_aic = v + 2*next_nparams
			if next_aic < last_aic:
				# accept
				print('%d parameters, aic=%.2f ** accepting' % (next_nparams, next_aic))
				last_aic, last_final, last_nparams, _ = next_aic, next_final, next_nparams, v
			else:
				print('%d parameters, aic=%.2f' % (next_nparams, next_aic))
			# stop if we are 3 parameters ahead what we needed
			if next_nparams >= last_nparams + 3:
				break
		
		print('Final choice: %d parameters, aic=%.2f' % (last_nparams, last_aic))
		# reset to the last good solution
		for p, v in zip(bkgmodel.pars, last_final):
			p.val = v
		
		last_pred = self.predict(last_final)
		predictions.append(last_pred)
		#if self.cts.sum() < len(self.cts): # do not add gaussians to low-count background spectra
		#	print 'Not adding Gaussians, because low count'
		#	return last_pred, predictions
		#return last_final
		del i
		for gi in range(10):
			print()
			print('Adding Gaussian#%d' % (gi+1))
			# find largest discrepancy
			
			y = self.cts.cumsum()
			z = last_pred.cumsum()
			diff = numpy.abs(y - z)
			xi = numpy.argmax(diff)
			print('largest remaining discrepancy at %d, need %d counts' % (xi, diff[xi]))
			power = diff[xi]
			print('placing gaussian there ...')
			# we work in energy bins, not energy
			initial = [xi, log10(4.), log10(power)] + list(last_final)[:last_nparams]
			self.ngaussians = gi + 1
			print('initial guess:', self.calc_bkg_stat_wrapped_gaussians(initial))
			r = minimize(self.calc_bkg_stat_wrapped_gaussians, x0=initial)
			next_final = r.x
			v = self.calc_bkg_stat_wrapped_gaussians(next_final)
			next_pred = self.predict(next_final)
			predictions.append(next_pred)
			
			next_nparams = last_nparams + 3
			next_aic = v + 2 * next_nparams
			print('with Gaussian:', next_aic, '; change: %.1f (negative is good)' % (next_aic - last_aic))
			if next_aic < last_aic:
				print('accepting')
				last_aic, last_final, last_nparams, _ = next_aic, next_final, next_nparams, v
				last_pred = next_pred
			else:
				print('not significant, rejecting')
				# reset to previous model
				return last_pred, predictions

def main():
	import sys
	#logging.basicConfig(filename='bxa.log',level=logging.DEBUG)
	#logFormatter = logging.Formatter("[%(name)s %(levelname)s]: %(message)s")
	logFormatter = logging.Formatter("%(levelname)s: %(message)s")
	consoleHandler = logging.StreamHandler()
	consoleHandler.setFormatter(logFormatter)
	consoleHandler.setLevel(logging.INFO)
	logging.getLogger().addHandler(consoleHandler)
	logf.setLevel(logging.INFO)

	if len(sys.argv) not in (2, 3):
		print('SYNOPSIS: %s <bkg.pi> [<src.pi>] ' % sys.argv[0])
		sys.exit(1)
	background_file = sys.argv[1]
	source_file = sys.argv[2] if len(sys.argv) > 2 else None
	del sys
	fitter = PCAFitter(background_file)
	result, predictions = fitter.fit()
	data = fitter.cts

	# write out bkg file
	print('creating bstat bkg file ...')

	if background_file.endswith('.fits'):
		numpy.savetxt(background_file[:-5] + '.dat', result)
	with open(background_file + '.bstat.out', 'w') as fout:
		numpy.savetxt(fout, numpy.transpose([data, result]))
	
	# plot fit
	print('plotting...')
	m = max(data.sum(), result.sum())
	x = numpy.arange(fitter.ilo, fitter.ihi)
	import matplotlib.pyplot as plt
	plt.figure()
	plt.title('data-model should follow 1:1 dashed line')
	plt.plot(data.cumsum(), result.cumsum(), '-', color='r', lw=2, alpha=0.7)
	plt.plot([0, m], [0, m] , '--', color='gray', lw=0.4)
	plt.ylabel('Cumulative counts (data)')
	plt.ylabel('Cumulative counts (model)')
	plt.savefig(background_file + '.bstat_cum.pdf', bbox_inches='tight')
	plt.close()
	plt.figure()
	plt.title('model (red) should describe data (black)')
	for r in predictions:
		if r is not None:
			plt.plot(x, r, '-', color='orange', lw=1, alpha=0.3)
	plt.plot(x, result, '-', color='r', lw=2)
	plt.plot(x, data, 'o ', color='k')
	plt.ylim(0, max(result.max(), data.max()))
	plt.xlabel('channel')
	plt.ylabel('counts')
	plt.savefig(background_file + '.bstat.pdf', bbox_inches='tight')
	plt.yscale('log')
	plt.ylim(0.01, max(result.max(), data.max()))
	plt.savefig(background_file + '.bstat_log.pdf', bbox_inches='tight')
	plt.close()
	print()
	print('-> Check that %s is a 1:1 line' % (background_file + '.bstat_cum.pdf'))
	if source_file:
		foutsrc = create_spectral_files(fitter, result, source_file)
		print()
		print('-> In xspec, to load the data with BStat statistic, run:')
		print()
		print('   data %s' % foutsrc)
		print('   statistic pstat # (to use BStat) ')
		print()
		create_ogip_atable(result, background_file, source_file,
			outfilename=background_file + '_model.fits', ilo=fitter.ilo, ihi=fitter.ihi)

if __name__ == '__main__':
	main()

__dir__ = [PCAFitter, PCAModel]
