"""
Compute poisson-based GOF
"""

from __future__ import print_function
import sys, os
import numpy
import scipy.stats, scipy.special
import matplotlib.pyplot as plt

def build(options, k):
	if len(options) == 1:
		o = options[0]
		if k < len(o):
			#print 'yielding kth option', k, o
			yield [o[k]]
	else:
		for i, o in enumerate(options[0]):
			if i > k:
				break
			for p in build(options[1:], k - i):
				yield [o] + p

def gen_choices(cpart, k):
	nchoices = numpy.prod([len(c) for c in cpart])
	print(' gen?', k, len(cpart), nchoices)
	#print [c for c in build(cpart, k) if c is not None]
	probs = sum((numpy.prod(c) for c in build(cpart, k) if c is not None))
	return probs

	if k == 0:
		probs = numpy.prod([cp[0] for cp in cpart])
	elif k == 1:
		for i in range(len(cpart)):
			probs += numpy.prod([cp[1] if j == i else cp[0] for j, cp in enumerate(cpart)])
	elif k == 2:
		for i in range(len(cpart)):
			probs += numpy.prod([cp[2] if j == i else cp[0] for j, cp in enumerate(cpart)])
			for j in range(i + 1, len(cpart)):
				probs += numpy.prod([cp[1] if k == i or k == j else cp[0] 
					for k, cp in enumerate(cpart)])
	else:
		probs = sum((numpy.prod(c) for c in build(cpart, k)))
		
		for c in range(nchoices):
			prob = 1
			kc = 0
			for cp in cpart:
				ci = c % len(cp)
				kc += ci
				if kc > k:
					break
				c /= len(cp)
				prob *= cp[ci]
			if kc != k:
				continue
			print(' gen!', kc, prob)
			probs += prob
	return probs

def calc_models_range(data):
	stats = []
	lowmodel = numpy.zeros_like(data)*1e-10
	highmodel = numpy.ones_like(data)*1e10
	for i in range(20):
		n = 4**i
		m = len(data) / n
		if n > len(data):
			break
		kplusones = []
		masks = []
		for j in range(int(numpy.ceil(len(data) * 1. / n))):
			mask = slice(j * n, (j + 1) * n)
			dpart = data[mask]
			lowpart  = lowmodel[mask]
			highpart = highmodel[mask]
			
			k = int(dpart.sum()) if len(dpart) > 0 else 0
			kplusones.append(k + 1)
			masks.append(mask)
		
		#print 'GOF MODEL RANGE', k, n, m, 0.1 / m
		lowmodel_parts  = scipy.special.gammaincinv(kplusones, 0.1 / m) / n
		highmodel_parts = scipy.special.gammaincinv(kplusones, 1 - 0.1 / m) / n
		assert not numpy.any(numpy.isnan(lowmodel_parts)), (lowmodel_parts, kplusones, m, n)
		assert not numpy.any(numpy.isnan(highmodel_parts)), (highmodel_parts, kplusones, m, n)
		for mask, lowmodel_part, highmodel_part in zip(masks, lowmodel_parts, highmodel_parts):
			lowpart  = lowmodel[mask]
			highpart = highmodel[mask]
			lowpart [lowpart  < lowmodel_part]  = lowmodel_part
			highpart[highpart > highmodel_part] = highmodel_part
	
	return lowmodel, highmodel

def calc_multigof(data, model):
	#choice_limit = 1e-2 / len(data)
	#choices = numpy.array([[scipy.stats.poisson(m).pmf(i)
			#for i in range(
				#int(scipy.stats.poisson(m).ppf(choice_limit)),
				#int(scipy.stats.poisson(m).ppf(1 - choice_limit) + 1))]
					#for m in model])
	
	stats = []
	for i in range(20):
		n = 4**i
		if n > len(data):
			break
		
		for j in range(int(numpy.ceil(len(data) * 1. / n))):
			dpart = data [j*n:(j + 1)*n]
			mpart = model[j*n:(j + 1)*n]
			#cpart = choices[j*n: (j + 1)*n]
			#print data.shape, dpart.shape, j*n, (j + 1)*n, dpart, data
			k = int(dpart.sum()) if len(dpart) > 0 else 0
			m = mpart.sum()
			
			# compare this probability to all the other k
			#probs = gen_choices(cpart, k)
			stats.append([n, j, 0., m, k]) #  * len(data) / n])
			#print '  multigof', n, j, probs, len(stats)
			# lam = sum(mpart) WRONG!
			# go through all possibilities to get k
	stats = numpy.array(stats)
	m = stats[:,3]
	k = stats[:,4]
	probs = numpy.where(m > 0, scipy.stats.poisson(m).pmf(k), 
		numpy.where(k == 0, 1, 1e-10))
	assert not numpy.isnan(probs).any(), [m, k]
	stats[:,2] = probs
	return stats

def group_adapt(data, nmin = 10):
	i = 0
	while i < len(data):
		#print ' ',i,'--',len(data)
		for j in range(i + 1, len(data) + 1):
			#print ' ',i,j
			if sum(data[i:j + 1]) >= nmin or j + 1 >= len(data):
				yield (i,j + 1)
				#print '  groups', i,j
				break
		i = j + 1

def write_multigof(filename, data, model, skip_plot_ifeq=None):
	segments = list(group_adapt(data))
	stats    = calc_multigof(data, model)
	#gof = -2 * numpy.log10(stats[:,2]).mean()
	#print gof,
	#gof = - numpy.mean([numpy.log10(stats[stats[:,0] == n][:,2]).mean() for n in sorted(set(stats[:,0]))])
	#gof = - 2 * numpy.log(
	#	numpy.mean([exp(numpy.log(stats[stats[:,0] == n][:,2]).sum()) * (stats[:,0] == n).sum() 
	#		for n in sorted(set(stats[:,0]))]))
	gof = -numpy.log10(
		numpy.min([stats[stats[:,0] == n][:,2].min() * (stats[:,0] == n).sum() 
			for n in sorted(set(stats[:,0]))]))
	if skip_plot_ifeq is not None and numpy.abs(gof - skip_plot_ifeq) < 0.01 and os.path.exists(filename + ".pdf"):
		return gof
	
	plt.figure(figsize=(4*1.5,7*1.5))
	plt.subplot(4, 1, 1)
	segdata = [model[i:j].sum() for i, j in segments]
	segerr  = [[s - scipy.stats.poisson(s).ppf(0.1) for s in segdata],
		   [scipy.stats.poisson(s).ppf(0.9) - s for s in segdata]]
	plt.errorbar(x=[(i+j)/2 for i,j in segments],
		xerr=[(j-i)/2 for i,j in segments],
		y=segdata,
		yerr=segerr,
		label='model')
	segmodel = [data[i:j].sum() for i, j in segments]
	segerr  = [[s - scipy.special.gammaincinv(s + 1, 0.1) for s in segmodel],
		   [scipy.special.gammaincinv(s + 1, 0.9) - s for s in segmodel]]
	plt.errorbar(x=[(i+j)/2. for i,j in segments],
		xerr=[(j-i)/2. for i,j in segments],
		y=segdata,
		yerr=segerr,
		label='data')
	plt.legend(loc='best', prop=dict(size=6))
	
	# plot probabilities
	plt.subplot(4, 1, 3)
	colors = dict(list(zip(sorted(set(stats[:,0])), ['b','g','r','c','m','y','k','w'])))
	for n in sorted(set(stats[:,0])):
		j = stats[stats[:,0] == n][:,1] * n
		p = stats[stats[:,0] == n][:,2]
		#print j, p
		plt.plot(j, p, '-x', drawstyle='steps-pre', label='%d' % n,
			color=colors[n])
	plt.gca().set_yscale('log')
	plt.ylim(1e-9, 1)
	plt.legend(loc='best', prop=dict(size=6))
	
	#for l in sorted(stats, key=lambda l: l[2])[:10]:
	#	print l
	
	plt.subplot(4, 1, 2)
	for n in sorted(set(stats[:,0])):
		j = stats[stats[:,0] == n][:,1] * n
		p = stats[stats[:,0] == n][:,3]
		plt.plot(j, p, '--o', drawstyle='steps-pre', label='%d model' % n,
			color=colors[n], markersize=3)
		p = stats[stats[:,0] == n][:,4]
		plt.plot(j, p, '-x', drawstyle='steps-pre', label='%d data' % n,
			color=colors[n])
	plt.gca().set_yscale('log')
	plt.legend(loc='best', prop=dict(size=6))
	
	#print gof
	plt.subplot(4, 1, 4)
	plt.hist(numpy.log10(stats[:,2]), bins=numpy.linspace(-10,0,30),
		label="avg: %.2f" % gof)
	plt.legend(loc='best', prop=dict(size=6))
	plt.savefig(filename + ".pdf")
	plt.close()
	return gof
	
gof_limit = 2

def write_gof(prefix, gof_avg, gof_total):
	verdict = ('good' if gof_avg < gof_limit else 'bad')
	print("%.2f %5s %s"  % (gof_avg, verdict, prefix))
	#file(filename + ".out", 'w').write(str(gof) + "\n")
	numpy.savetxt(prefix + ".out", [gof_total, gof_avg])
	with open(prefix + ".summary", 'w') as f:
		f.write(verdict + "\n")

def load_gof(prefix):
	gof_total, gof_avg = numpy.loadtxt(prefix + ".out")
	return gof_total, gof_avg

	
if __name__ == '__main__':
	gofs = []
	#gof_limit = 1.5

	for filename in sys.argv[1:]:
		table = numpy.loadtxt(filename)
		data, model = table[:len(table)/2,0], table[:len(table)/2,1]
		try:
			prev_gof, prev_avg = load_gof(filename)
		except Exception as e:
			print(e)
			prev_gof, prev_avg = None, None
		gof_avg = write_multigof(filename, data[:650], model[:650], skip_plot_ifeq=prev_avg)
		gof = gof_avg * len(data[:650])
		write_gof(filename, gof_avg, gof)
		gofs.append(gof_avg)

	gofs = numpy.array(gofs)
	plt.figure()
	plt.hist(gofs, bins=numpy.linspace(0,5,21) )
	print('good:', (gofs < gof_limit).sum(), (gofs < gof_limit).sum() * 1. / len(gofs))
	plt.ylabel("number of objects")
	plt.xlabel("gof")
	plt.savefig("gof.pdf", bbox_inches='tight')
	plt.close()

