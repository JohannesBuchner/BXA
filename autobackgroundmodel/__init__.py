#!/usr/bin/env python
"""
Creates background PCA model from a large sample of background spectra
"""
import astropy.io.fits as pyfits
import numpy
import sys
import h5py
import joblib
import json
import tqdm

import compress


def compile(filenames):
	data = []
	instrument = None
	telescope = None

	for filename in filenames:
		#print 'reading', filename
		f = pyfits.open(filename)
		s = f['SPECTRUM']
		y = numpy.copy(s.data['COUNTS'])
		#ncts = y.sum()
		#z = numpy.log10((y + 1.0)/ncts)
		#print ncts, len(y)
		instrument = str(s.header['INSTRUME'])
		telescope = str(s.header['TELESCOP'])
		#if y[:500].mean() > 5:
		if True or y[:200].mean() > 5:
			print('  reading "%s"' % filename)
			data.append(y)
		f.close()

	data = numpy.array(data)

	#with h5py.File(outfile, 'w') as f:
	#	d = f.create_dataset("spectra", data=data, compression="gzip", compression_opts=9, shuffle=True)
	#	d.attrs['INSTRUMENT'] = instrument
	#	d.attrs['TELESCOPE'] = telescope
	return data, instrument, telescope

def repack(filename):
	f = h5py.File(filename, 'r')
	attrs = f['spectra'].attrs
	data = f['spectra'][()]
	mincts = 50 * data.shape[1] # number of counts per bin

	print('original shape: %s' % str(data.shape))
	ncts = data.sum(axis=1)
	selected = ncts>mincts
	print('high-count:    %d have >%d counts' % (selected.sum(), mincts))
	print('count distribution:  %d %d %d %d %d' % tuple(numpy.percentile(ncts, [1, 10, 50, 90, 99])))

	# order by number of counts in the hope we can get spectra in faint and bright background regions together
	indices = numpy.argsort(ncts)
	indices2 = indices[::-1]
	indices3 = numpy.random.randint(0, len(data), 40 * len(data))
	indices = numpy.hstack((indices3, indices2, indices))

	# start with individuals already above threshold
	newdata = []
	initdata = data[selected,:]

	# group together those below threshold, in order of indices, reverse
	pack = 0
	packlen = 0

	for i in tqdm.tqdm(indices[::-1]):
		if ncts[i] > mincts:
			continue
		pack += data[i,:]
		packlen += 1
		if pack.sum() > mincts:
			newdata.append(pack)
			pack = 0
			packlen = 0

	newdata = numpy.vstack(tuple(newdata))
	newdata = numpy.concatenate((initdata, newdata))
	print('repacked shape:', newdata.shape)
	print('dropped:       ', packlen)
	outfile = filename + 'repacked.hdf5'

	with h5py.File(outfile, 'w') as f:
		d = f.create_dataset("spectra", data=newdata, compression="gzip", compression_opts=9, shuffle=True)
		for k, v in attrs.items():
			print('   storing attribute %s = %s' % (k, v))
			d.attrs[k] = v
	return newdata, outfile

def simplify(v):
	try:
		return int(v)
	except:
		return v

def export(outfilename, filename):
	f = h5py.File(filename, 'r')
	#nbins = f['spectra'].shape[1]
	with open(outfilename, 'w') as fout:
		#print("  - getting keys:")
		#for k in list(f.keys()):
		#	print(target, k, f[k].shape)
		data = dict([(k, f[k][()].tolist()) for k in list(f.keys())])
		#print("getting attributes:")
		for k, v in f.attrs.items():
		#	print(target, k, v)
			data[k] = simplify(v)
		json.dump(data, fout, indent=2)


if __name__ == '__main__':
	filenames = sys.argv[1:]
	if len(filenames) == 0:
		sys.stderr.write("""SYNOPSIS: %s <filenames>

Builds a machine-learned background model from a large set of
background spectra (filenames).

Johannes Buchner (C) 2017-2019
""" % sys.argv[0])
		sys.exit(1)

	print("fetching counts from %d files ..." % len(filenames))
	datasets = joblib.Parallel(-1)((joblib.delayed(compile)(filenames[i::10]) for i in range(10)))

	print("combining ...", len(datasets))
	telescopes = set([telescope for _, instrument, telescope in datasets])
	assert len(telescopes) == 1, "trying to combine multiple telescopes!"
	instruments = set([instrument for _, instrument, telescope in datasets])
	instrument = list(instruments)[0]
	telescope = list(telescopes)[0]
	if len(instruments) == 1:
		telescope = telescope + '_' + instrument
	else:
		telescope = telescope

	newdata = numpy.concatenate(tuple([data for data, _, _ in datasets]))
	nbins = newdata.shape[1]
	del datasets
	attrs = {'INSTRUMENT': instrument, 'TELESCOPE': telescope}


	print('combined shape:', newdata.shape)
	outfile = '%s.hdf5' % telescope

	with h5py.File(outfile, 'w') as f:
		d = f.create_dataset("spectra", data=newdata, compression="gzip", compression_opts=9, shuffle=True)
		for k, v in list(attrs.items()):
			print(('   storing attribute %s = %s' % (k, v)))
			d.attrs[k] = v

	newdata, repackedfile = repack(outfile)

	print('applying PCA ...')
	del newdata
	componentfile = compress.run(cmd='create', filename=repackedfile)
	try:
		print('plotting PCA ...')
		compress.run(cmd='components', filename=repackedfile)
	except Exception:
		pass

	print('exporting to "%s.json" ...' % telescope.lower())
	export(telescope.lower() + '_%d.json' % nbins, componentfile)
	print('exporting to "%s.json" ... done' % telescope.lower())
