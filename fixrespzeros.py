from __future__ import print_function
import numpy
import sys
import astropy.io.fits as pyfits

f = pyfits.open(sys.argv[1])
if f['EBOUNDS'].data[0]['E_MIN'] < 0.001 or f['MATRIX'].data[0]['ENERG_LO'] < 0.001:
	f['EBOUNDS'].data[0]['E_MIN'] = 0.001
	f['MATRIX'].data[0]['ENERG_LO'] = 0.001
	f.writeto(sys.argv[1], clobber=True)
	print('file corrected', sys.argv[1])
else:
	print('file is ok', sys.argv[1])
f = pyfits.open(sys.argv[2])
if f['SPECRESP'].data[0]['ENERG_LO'] < 0.001:
	f['SPECRESP'].data[0]['ENERG_LO'] = 0.001
	f.writeto(sys.argv[2], clobber=True)
	print('file corrected', sys.argv[2])
else:
	print('file is ok', sys.argv[2])


