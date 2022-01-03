#!/usr/bin/env python
from __future__ import print_function, division
import numpy
import sys
import astropy.io.fits as pyfits

changes_needed = []

def should_be(fitsfile, header, keyword, expected=None):
	v = header.get(keyword)
	if expected is None:
		print('%s: %s' % (keyword, v))
		return []
	elif v == expected:
		print('%s: %s (as expected)' % (keyword, v))
		return []
	else:
		print('%s: %s (expected: %s)' % (keyword, v, expected))
		return [(fitsfile, header, keyword, expected)]
	
def apply_changes(f, filename):
	changed_anything = False
	for fitsfile, header, keyword, expected in changes_needed:
		if fitsfile != f: continue
		header[keyword] = expected
		changed_anything = True
	if changed_anything:
		print('   -> writing ',filename) # + '.withkeywords.fits'
		#fitsfile.writeto(filename + '.withkeywords.fits', clobber=True)
		fitsfile.writeto(filename, overwrite=True)
	else:
		print('   -> no changes needed')

if len(sys.argv) != 5:
	print('SYNOPSIS: fixkeywords.py src.pi bkg.pi rmf.rmf arf.arf')
	print() 
	print('Checks and corrects the keywords connecting the files')
	print('Corrects zero energy bounds')
	print() 
	print('Johannes Buchner (C) 2017')
	sys.exit(1)

src = sys.argv[1]
bkg = sys.argv[2]
rmf = sys.argv[3]
arf = sys.argv[4]

fsrc = pyfits.open(src)
fsrch = fsrc[1].header
print('Source file:', src)
print('AREASCAL:', fsrch.get('AREASCAL'))
print('BACKSCAL:', fsrch.get('BACKSCAL'))
print('EXPOSURE:', fsrch.get('EXPOSURE'))
changes_needed += should_be(fsrc, fsrch, 'BACKFILE', bkg)
changes_needed += should_be(fsrc, fsrch, 'RESPFILE', rmf)
changes_needed += should_be(fsrc, fsrch, 'ANCRFILE', arf)
apply_changes(fsrc, src)

print()
changes_needed = []
fbkg = pyfits.open(bkg)
fbkgh = fbkg[1].header
print('Background file:', bkg)
print('AREASCAL:', fbkgh.get('AREASCAL'))
print('BACKSCAL:', fbkgh.get('BACKSCAL'))
print('EXPOSURE:', fbkgh.get('EXPOSURE'))
changes_needed += should_be(fbkg, fbkgh, 'RESPFILE', rmf)
changes_needed += should_be(fbkg, fbkgh, 'ANCRFILE', arf)
apply_changes(fbkg, bkg)

print()
print('Response file:', rmf)
f = pyfits.open(rmf)
SMALL = 0.001
if f['EBOUNDS'].data[0]['E_MIN'] < SMALL or f['MATRIX'].data[0]['ENERG_LO'] < SMALL:
	f['EBOUNDS'].data[0]['E_MIN'] = SMALL
	f['MATRIX'].data[0]['ENERG_LO'] = SMALL
	f.writeto(rmf, overwrite=True)
	print('  -> energy bounds corrected')
else:
	print('  -> file is ok')

print()
print('Ancillary file:', arf)
f = pyfits.open(arf)
if f['SPECRESP'].data[0]['ENERG_LO'] < SMALL:
	f['SPECRESP'].data[0]['ENERG_LO'] = SMALL
	f.writeto(arf, overwrite=True)
	print('  -> energy bounds corrected')
else:
	print('  -> file is ok')
