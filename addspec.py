"""
Copyright 2021 Johannes Buchner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import numpy as np
import sys, os
import astropy.io.fits as pyfits
import subprocess

def remove(filename):
	if os.path.exists(filename): 
		os.unlink(filename)

def run(*args, **kwargs):
	print("    running command:", *args)
	subprocess.check_call(*args, **kwargs)

def sum_pha(outfile, filenames, backscals, areascals, rel_weights, **kwargs):
	print()
	print("creating '%s' ..." % outfile)
	remove(outfile)
	run(['mathpha', 'expr=' + '+'.join(filenames), "outfil=" + outfile, 
		'units=C', 'exposure=CALC', 'properr=NO', 'errmeth=POISS-0', 'areascal=NULL',
		'ncomments=1', "comment1=Created_by_addspec.py_alpha", 'chatter=5'])

	# update AREASCAL, BACKSCAL keywords:
	areascal = (areascals * rel_weights).sum()
	backscal = (backscals * rel_weights).sum()
	print("    EXPOSURE and counts were summed")
	print("    relative weights for scale factors:", rel_weights)
	print("    averaged AREASCAL:", areascal)
	print("    averaged BACKSCAL:", backscal)
	with open('.tmp.modhead', 'w') as fout:
		fout.write("AREASCAL %.20f\n" % areascal)
		fout.write("BACKSCAL %.20f\n" % backscal)
		for k, v in kwargs.items():
			fout.write("%s %s\n" % (k, v))
	
	run(['fmodhead', outfile + '[SPECTRUM]', '.tmp.modhead'])
	os.unlink('.tmp.modhead')



def main(outprefix, filenames):

	N = len(filenames)
	print("files:", N, filenames)

	backscals = np.empty(N)
	areascals = np.empty(N)
	exposures = np.empty(N)
	bbackscals = np.empty(N)
	bareascals = np.empty(N)
	bexposures = np.empty(N)
	arfs = []
	rmfs = []
	barfs = []
	brmfs = []

	bfilenames = []

	for i, filename in enumerate(filenames):
		header = pyfits.getheader(filename, extname='SPECTRUM')
		backscals[i] = header['BACKSCAL']
		areascals[i] = header['AREASCAL']
		exposures[i] = header['EXPOSURE']
		arf = header['ANCRFILE']
		rmf = header['RESPFILE']
		arfs.append(arf)
		rmfs.append(rmf)

		backfile = header['BACKFILE']
		bfilenames.append(backfile)
		bheader = pyfits.getheader(backfile, extname='SPECTRUM')
		bbackscals[i] = bheader['BACKSCAL']
		bareascals[i] = bheader['AREASCAL']
		bexposures[i] = bheader['EXPOSURE']
		barf = bheader['ANCRFILE']
		brmf = bheader['RESPFILE']
		barfs.append(barf if str(barf).lower() != 'none' else arf)
		brmfs.append(brmf if str(brmf).lower() != 'none' else rmf)
		
		del arf, rmf, barf, brmf, backfile

	print("Files:", filenames, bfilenames)


	print("BACKSCAL:", backscals, bbackscals)
	print("AREASCAL:", areascals, bareascals)
	print("EXPOSURE:", exposures, bexposures)

	weights = areascals * exposures
	rel_weights = weights / weights.sum()
	weightstr = ' '.join(['%e' % w for w in rel_weights])
	bweights = bareascals * bexposures
	rel_bweights = bweights / bweights.sum()
	bweightstr = ' '.join(['%e' % w for w in rel_bweights])
	assert len(arfs) == N
	assert len(rmfs) == N
	assert len(barfs) == N
	assert len(brmfs) == N

	print("combining ARFs:", arfs)
	arf = outprefix + '.arf'
	run(['addarf', ' '.join(arfs), weightstr, arf, 'clobber=yes'])
	barf = outprefix + '_bkg.arf'
	run(['addarf', ' '.join(barfs), bweightstr, barf, 'clobber=yes'])
	print("combining RMFs:", rmfs)
	rmf = outprefix + '.rmf'
	run(['addrmf', ' '.join(rmfs), weightstr, rmf, 'clobber=yes'])
	brmf = outprefix + '_bkg.rmf'
	run(['addrmf', ' '.join(brmfs), bweightstr, brmf, 'clobber=yes'])
	
	outfile = "%s.pha" % outprefix
	boutfile = "%s_bkg.pha" % outprefix

	sum_pha(
		outfile = outfile,
		filenames = filenames,
		areascals = areascals,
		backscals = backscals,
		rel_weights = rel_weights,
		ANCRFILE = arf,
		RESPFILE = rmf,
		BACKFILE = boutfile,
	)
	sum_pha(
		outfile = boutfile,
		filenames = bfilenames,
		areascals = bareascals,
		backscals = bbackscals,
		rel_weights = rel_bweights,
		ANCRFILE = barf,
		RESPFILE = brmf,
	)

if __name__ == '__main__':
	if len(sys.argv) < 3:
		sys.stderr.write("""SYNOPSIS: addspec.py <outprefix> file1.pha file2.pha ...
or
SYNOPSIS: addspec.py <outprefix> @filelist.txt

In the second case, each line of filelist.txt contains a file name.

If as a outprefix "sum" is given, the output files are named
sum.pha sum.arf sum.rmf sum_bkg.pha sum_bkg.arf sum_bkg.rmf

Johannes Buchner (C) 2021, MIT Licence
""")
		sys.exit(1)

	filenames = sys.argv[2:]
	if len(filenames) == 1 and filenames[0][0] == '@':
		filenames = [filename.rstrip() for filename in open(filenames[0][1:])]
	main(
		outprefix = sys.argv[1],
		filenames = filenames,
	)
