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
import filecmp
import shutil
import tempfile

def remove(filename):
	if os.path.exists(filename): 
		os.unlink(filename)

def run(*args, **kwargs):
	print("    running command:", *args)
	subprocess.check_call(*args, **kwargs)

def combine_responses(arfs, rmfs, rel_weights, outprefix):
	"""Average full responses, keeping separate ARFs only for identical RMFs.

	Weights are proportional to exposure * AREASCAL. For differing RMFs,
	include each ARF before averaging, and return ANCRFILE=NONE so the
	effective area is not applied twice.
	"""
	same_rmf = all(filecmp.cmp(rmfs[0], rmf, shallow=False) for rmf in rmfs[1:])
	separate_arf = same_rmf and all(str(arf).strip().lower() != 'none' for arf in arfs)
	with tempfile.TemporaryDirectory(prefix='addspec_') as tmpdir:
		if separate_arf:
			inputs = arfs
		else:
			inputs = []
			for i, (arf, rmf) in enumerate(zip(arfs, rmfs)):
				if str(arf).strip().lower() == 'none':
					# A response with no separate ARF is already complete.
					inputs.append(rmf)
					continue
				response = os.path.join(tmpdir, '%d.rsp' % i)
				run(['marfrmf', 'rmfil=' + rmf, 'arfil=' + arf,
					'outfil=' + response, 'ebfil=%', 'qdivide=no',
					'qoverride=no', 'clobber=yes'])
				inputs.append(response)
		# Use a list file to avoid the FTOOLS command-line length limit.
		listfile = os.path.join(tmpdir, 'responses.txt')
		with open(listfile, 'w') as fout:
			for filename, weight in zip(inputs, rel_weights):
				fout.write('%s %.17g\n' % (filename, weight))
		if separate_arf:
			arf = outprefix + '.arf'
			rmf = outprefix + '.rmf'
			run(['addarf', 'list=@' + listfile, 'out_ARF=' + arf, 'clobber=yes'])
			shutil.copyfile(rmfs[0], rmf)
		else:
			arf = 'NONE'
			rmf = outprefix + '.rsp'
			run(['addrmf', 'list=@' + listfile, 'rmffile=' + rmf, 'clobber=yes'])
	return arf, rmf


def sum_pha(outfile, filenames, backscals, areascals, exposures, rel_weights, **kwargs):
	print()
	print("creating '%s' ..." % outfile)
	remove(outfile)
	run(['mathpha', 'expr=' + '+'.join(filenames), "outfil=" + outfile, 
		'units=C', 'exposure=CALC', 'properr=NO', 'errmeth=POISS-0', 'areascal=NULL',
		'ncomments=1', "comment1=Created_by_addspec.py_alpha", 'chatter=5'])

	# update AREASCAL, BACKSCAL keywords:
	# With T = sum(exposures), T * AREASCAL must equal sum(t_i * a_i).
	# Response weights already contain a_i, so do not use them again here.
	areascal = np.average(areascals, weights=exposures)
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
	if N == 0:
		raise ValueError('At least one spectrum is required')
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

	for values in (exposures, bexposures, areascals, bareascals):
		if not np.all(np.isfinite(values) & (values > 0)):
			raise ValueError('EXPOSURE and scalar AREASCAL must be finite and positive')
	# With exposure-weighted output AREASCAL, these weights preserve
	# sum(t_i * a_i * ARF_i * RMF_i) for a common incident spectrum.
	weights = areascals * exposures
	rel_weights = weights / weights.sum()
	bweights = bareascals * bexposures
	rel_bweights = bweights / bweights.sum()
	assert len(arfs) == N
	assert len(rmfs) == N
	assert len(barfs) == N
	assert len(brmfs) == N

	print("combining source responses:", arfs, rmfs)
	arf, rmf = combine_responses(arfs, rmfs, rel_weights, outprefix)
	print("combining background responses:", barfs, brmfs)
	barf, brmf = combine_responses(barfs, brmfs, rel_bweights, outprefix + '_bkg')
	
	outfile = "%s.pha" % outprefix
	boutfile = "%s_bkg.pha" % outprefix

	sum_pha(
		outfile = outfile,
		filenames = filenames,
		areascals = areascals,
		exposures = exposures,
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
		exposures = bexposures,
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

If as a outprefix "sum" is given, the spectra are sum.pha and sum_bkg.pha.
Identical input RMFs with separate ARFs retain .arf and .rmf outputs.
Otherwise, a combined .rsp is written and ANCRFILE is set to NONE.

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
