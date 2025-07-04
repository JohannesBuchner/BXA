#!/usr/bin/env python
"""

Kernel density estimation-based background model

It requires no learned models, the continuous shape is learned from the data.
Therefore relatively well-sampled backgrounds are needed.

Bins with zero counts are okay. Rebinning is not required.

"""
import numpy
from numpy import log10
import logging
import astropy.io.fits as pyfits
import scipy.stats
import scipy.optimize
import datetime
import time


def create_ogip_atable(BackArray, BackSpecFile, SourceSpecFile, outfilename, ilo, ihi):
	"""
	Convert the background model (1D array of counts per channel) into a additive Xspec table model.

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
	hdu0.header['MODLNAME'] = ('kdebkg', 'model name (12 chars max)')
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

class KDEFitter(object):
	""" a KDE approximation of the background spectrum """
	def __init__(self, bkg_filename):
		f = pyfits.open(bkg_filename)
		self.bkg_filename = bkg_filename
		self.cts = f[1].data['COUNTS'].astype(int)
		self.ndata = len(self.cts)
		self.ngaussians = 0
		self.ilo = 0
		self.ihi = self.ndata

	def fit(self, bw_method=None):
		# get photon counts as samples of the channels
		samples = []
		for chan, counts in enumerate(self.cts):
			samples += [chan] * counts

		# apply KDE
		kde = scipy.stats.gaussian_kde(samples, bw_method=bw_method)
		density = kde(numpy.arange(self.ndata))

		# make a model that matches the observed counts
		model = density / density.sum() * self.cts.sum()
		return model, [model]



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

def main():
	import sys
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
	fitter = KDEFitter(background_file)
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

__dir__ = [KDEFitter]
