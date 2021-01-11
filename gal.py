#!/usr/bin/env python
from __future__ import print_function
import astropy.io.fits as pyfits
import requests

url = "https://www.swift.ac.uk/analysis/nhtot/donhtot.php"

def parse_response(html_response):
	""" parses the html response and extracts the weighted total NH value """
	akey = "headers='htotw'>"
	a = html_response.index(akey) + len(akey)
	l = html_response[a:].index("</td>")
	part = html_response[a:a+l]
	if part.endswith('</sup>'):
		part = part[:-len('</sup>')]
		base, expo = part.split(' &times;10<sup>')
		return float(base) * 10**float(expo)
	else:
		return float(part)

def get_gal_nh(ra, dec):
	""" asks swift.ac.uk for the total NH value at (ra,dec) """
	r = requests.post(url, data=dict(
		equinox=2000, Coords="%s %s" % (ra, dec),
		submit='Calculate NH')
		)
	nh = parse_response(r.text)
	return nh

if __name__ == '__main__':
	import sys, os
	cache = []
	for infile in sys.argv[1:]:
		outfile = infile + '.nh'
		if not os.path.exists(outfile):
			f = pyfits.open(infile)
			for i in 0, 1:
				header = f[i].header
				print('looking for RA, DEC headers ...')
				if 'RA_OBJ' in header:
					print('using RA_OBJ, DEC_OBJ headers ...')
					ra  = header['RA_OBJ']
					dec = header['DEC_OBJ']
					break
				elif 'RA_TARG' in header:
					print('using RA_TARG, DEC_TARG headers ...')
					ra  = header['RA_TARG']
					dec = header['DEC_TARG']
					break
			nhs = [nhc for rac, decc, nhc in cache if rac == ra and decc == decc]
			if len(nhs) > 0:
				print('same as a previous one')
				nh = nhs[0]
			else:
				print('requesting galactic NH from swift.ac.uk...')
				nh = get_gal_nh(ra, dec)
				cache.append((ra, dec, nh))
				
			print(('writing to %s ...' % outfile))
			open(outfile, 'w').write("%e\n" % nh)
			del ra, dec
		else:
			print(('File %s already exists.' % outfile))
