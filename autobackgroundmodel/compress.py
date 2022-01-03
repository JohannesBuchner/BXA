#!/usr/bin/env python
import h5py
import numpy
import sys
import plotcolors
import matplotlib.pyplot as plt

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
#def pca_cut_adapt(U, s, V, mean):
#	return U[:, :ncomponents], s[:ncomponents], V[:,:ncomponents], mean

def pca_check(M, U, s, V, mean):
	# if we use only the first 20 PCs the reconstruction is less accurate
	Mhat2 = pca_predict(U, s, V, mean)
	print("Using %d PCs, MSE = %.6G"  % (len(s), numpy.mean((M - Mhat2)**2)))
	return M - Mhat2

def run(cmd, filename):
	f = h5py.File(filename, 'r')
	attrs = f['spectra'].attrs
	data = f['spectra'][()]
	mincts = 50000
	#mincts = 10000

	if cmd == 'create':
		lo = data.min(axis=0)
		hi = data.max(axis=0)
		i, = numpy.where(lo != hi)
		ilo = i.min() + 1
		ihi = i.max() - 1
		selected = data.sum(axis=1)>mincts
		cts = data[selected,ilo:ihi]
		ncts = cts.sum(axis=1).reshape((-1,1))
		print('channel range:', ilo, ihi, cts.shape)
		print('lowest number of counts: %d' % ncts.min())
		y = numpy.log10(cts * 1. / ncts  + 1.0)

		lo = y.min(axis=0)
		hi = y.max(axis=0)
		#data = (y - lo.reshape((1,-1)) ) / (hi - lo).reshape((1,-1))
		data = y
		print('running pca', data.shape)
		U, s, V, mean = pca(data)
		U, s, V, mean = pca_cut(U, s, V, mean, 5)

		with h5py.File(filename + 'pca.hdf5', 'w') as f:
			f.attrs['ilo'] = ilo
			f.attrs['ihi'] = ihi
			for k, v in attrs.items():
				print(('   storing attribute %s = %s' % (k, v)))
				f.attrs[k] = v
			f.create_dataset("mean", data=mean, compression="gzip", compression_opts=9, shuffle=True)
			f.create_dataset("components", data=V, compression="gzip", compression_opts=9, shuffle=True)
			f.create_dataset("values", data=s, compression="gzip", compression_opts=9, shuffle=True)
			f.create_dataset("U", data=U, compression="gzip", compression_opts=9, shuffle=True)
			f.create_dataset("lo", data=lo, compression="gzip", compression_opts=9, shuffle=True)
			f.create_dataset("hi", data=hi, compression="gzip", compression_opts=9, shuffle=True)
		return filename + 'pca.hdf5'
		
	elif cmd == 'components':
		with h5py.File(filename + 'pca.hdf5', 'r') as f:
			ilo = f.attrs['ilo']
			ihi = f.attrs['ihi']
			mean = f['mean'][()]
			V = f['components'][()]
			s = f['values'][()]
			U = f['U'][()]
			scales = numpy.abs(U).mean(axis=0)
			vectors = pca_get_vectors(s, V, mean)[:6]
			plt.figure(figsize=(12, 4))
			name = '%(INSTRUMENT)s on %(TELESCOPE)s' % f.attrs
			plt.text(0.95, 0.95, name, va='top', ha='right', transform=plt.gca().transAxes, fontsize=20)
			colors = plotcolors.create(len(vectors), cmap='viridis')
			for i, (row, factor, color) in list(enumerate(zip(vectors, scales, colors))):
				if -row.min() > row.max():
					sgn = -1
				else:
					sgn = +1
				sgn = sgn * 3.00
				#sgn = sgn * 2.0**-i
				# make it so that deviation between mean and component is a factor of 10 somewhere
				#delta = numpy.max(numpy.abs(mean + sgn * factor * row))
				#sgn = sgn * 10. / delta
				print(i, row.min(), row.max(), sgn)
				plt.plot(list(range(ilo, ihi)), (10**(mean + sgn * factor * row) - 1) * 2**-i, '-', 
					color=color, alpha=0.75, lw=12 / (i+4), label='PC%s' % (i+1))
				plt.plot(list(range(ilo, ihi)), (10**mean - 1) * 2**-i, '-', color='k', lw=2, label='mean')
			#plt.xscale('log')
			plt.yscale('log')
			yvals = 10**mean - 1
			plt.xlim(ilo, ihi)
			plt.ylim(yvals.min()/40, yvals.max()*2)
			plt.ylabel('Counts [arb. norm.]')
			plt.xlabel('Energy Channel')
			plt.legend(loc='lower right', prop=dict(size=8), ncol=3)
			plt.savefig(filename + 'pca2.pdf', bbox_inches='tight')
			plt.close()
	elif cmd == 'showcomp':		
		with h5py.File(filename + 'pca.hdf5', 'r') as f:
			ilo = f.attrs['ilo']
			ihi = f.attrs['ihi']
			mean = f['mean'][()]
			V = f['components'][()]
			s = f['values'][()]
			U = f['U'][()]
			
			print(mean)
			for i, row in enumerate(pca_get_vectors(s, V, mean)):
				print(row)
				plt.title('PCA component %d' % (i+1))
				plt.plot(mean, '-', color='k')
				plt.plot(mean + row, '-', alpha=0.5)
				plt.show()
	elif cmd == 'check':
		with h5py.File(filename + 'pca.hdf5', 'r') as f:
			ilo = f.attrs['ilo']
			ihi = f.attrs['ihi']
			mean = f['mean'][()]
			V = f['components'][()]
			s = f['values'][()]
			U = f['U'][()]
			lo = f['lo'][()]
			hi = f['hi'][()]
			
			U, s, V, mean = pca_cut(U, s, V, mean, 4)
			z = pca_predict(U, s, V, mean)
			#y = z * (hi - lo).reshape((1,-1)) + lo.reshape((1,-1))
			y = z

			counts = 10**y - 1
			cts = data[data.sum(axis=1)>mincts,ilo:ihi]
			print(counts.shape, cts.shape)
			diff = counts * cts.sum(axis=1).reshape((-1,1)) - cts
			print('largest difference: %.3f' % numpy.abs(diff).max())
			i = numpy.abs(diff).max(axis=1).argmax()
			print(i, 'is the worst case', numpy.abs(diff[i,:]).max())
			iworst = i
			for i in [iworst, 47, 18, 126] + list(range(len(cts))):
				if i >= len(cts): continue
				
				plt.title('ID:%d, %d counts' % (i, cts[i,:].sum()))
				plt.plot(counts[i,:] * cts[i,:].sum(), '-', color='k')
				plt.plot(cts[i,:], '-', color='r', alpha=0.5)
				plt.show()
			
			#diff = (counts * cts.sum(axis=0).reshape(1,-1) - cts) / (cts + 1)
			#print 'largest ratio: %.3f' % numpy.abs(diff).max()
			
			
if __name__ == '__main__':
	filename = sys.argv[2]
	cmd = sys.argv[1]
	run(cmd=cmd, filename=filename)
