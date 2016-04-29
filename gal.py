import json
import astropy.io.fits as pyfits
import requests

url = "http://www.swift.ac.uk/analysis/nhtot/donhtot.php"

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
	import time
	for infile in sys.argv[1:]:
		outfile = infile + '.nh'
		if not os.path.exists(outfile):
			f = pyfits.open(infile)
			print('looking for RA_OBJ, DEC_OBJ headers ...')
			ra  = f[0].header['RA_OBJ']
			dec = f[0].header['DEC_OBJ']
			print('requesting galactic NH from swift.ac.uk...')
			nh = get_gal_nh(ra, dec)
			print('writing to %s ...' % outfile)
			open(outfile, 'w').write("%e\n" % nh)
		else:
			print('File %s already exists.' % outfile)


