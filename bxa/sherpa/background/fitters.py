from __future__ import print_function
"""
Lets try something simpler.

Background model has stages
SingleFitter goes through stages and fits each with chi^2, then cstat

MultiFitter fits first one with SingleFitter,
then goes through all the others
by setting the parameter values to those of the previous id
and then fitting each stage


"""

import os
if 'MAKESPHINXDOC' not in os.environ:
	import sherpa.astro.ui as ui
	from sherpa.stats import Cash, CStat
	from sherpa.models.parameter import Parameter
	from sherpa.models import ArithmeticModel, CompositeModel
	from sherpa.astro.ui import *
	from sherpa.astro.instrument import RSPModelNoPHA, RMFModelNoPHA
else:
	CompositeModel, ArithmeticModel = object, object
	load_user_stat = lambda _1, _2, _3: None
import numpy
import json
import logging
import warnings

"""
custom background statistic, similar to chi^2

Sherpa itself does not expose the statistic of the background fit
as far as I can tell. This has the benefit of being rather stable
and giving large, sensitive values when the fit is poor. (CStat tends to 
flatten out)

i: spectrum ID
"""

logi = logging.getLogger('bxa.internal')
logi.setLevel(logging.WARN)

def my_bkg_stat(i):
	p = get_bkg_fit_plot(i)
	m = p.modelplot
	d = p.dataplot
	chi = (((d.y - m.y) / (m.y + 1e-20)) ** 2)
	return chi.mean()

def group_adapt(data, model, nmin = 20):
	i = 0
	while i < len(data):
		for j in range(i, len(data)+1):
			mask = numpy.arange(i, j)
			n = data[mask].sum()
			if n >= nmin or j + 1 >= len(data):
				yield (n, model[mask].sum())
				break
		i = j + 1

def wstatfunc(data, model, staterror=None, syserror=None, weight=None):
	n = data.astype('int').sum()
	l = len(data)
	if n >= l * 20: # no rebinning needed
		r = (((data - model) / model)**2).sum()
		return r, r
	else:
		r = numpy.sum([((d - m)/m)**2 for d, m in group_adapt(data.astype('int'), model, nmin=20)])
		for p in get_bkg_model().pars:
			logi.debug('%s = %.f' % (p.fullname, p.val))
		logi.info('bxaroughstat: %.3f' % r)
		return r, r
def wstatfunc(data, model, staterror=None, syserror=None, weight=None):
	n = data.astype('int').sum()
	l = len(data)
	r = (((data - model) / model)**2).sum()
	return r, r
def custom_staterr_func(data):
	return data**0.5
load_user_stat("bxaroughstat", wstatfunc, custom_staterr_func)


"""
custom routine to find the best normalisation in a robust way.

Often the starting point can be way off and the statistic will not 
give good indications which way to go. So use my_bkg_stat. This routine
tries to go both up and down from the starting point to escape this flatness.

i: spectrum ID
params: list of params to deal with, in sequence
"""
def robust_opt(i, params):
	logi.debug('        robust_opt: my optimization     --- of %s' % i)
	logi.debug('        robust_opt: \tparameters:', ', '.join([p.fullname for p in params]))
	#plot_bkg_fit_resid(i)
	for p in params:
		logi.debug('        robust_opt: \toptimizing %s normalization [%e .. %e]' % (p.fullname, p.min, p.max))
		startval = p.val
		beststat = my_bkg_stat(i)
		bestval = p.val
		logi.info('        robust_opt: \t\tstart val = %e: %e' % (p.val, beststat))
		go_up = True
		go_down = True
		for n in list(3.**numpy.arange(1, 20)) + [None] + list(1.1**numpy.arange(1, 13)):
			if n is None:
				startval = bestval
				logi.info('        robust_opt: \t\trefining from %e' % (startval))
				go_up = True
				go_down = True
				continue
			if go_up and startval * n > p.max:
				logi.info('        robust_opt: \t\thit upper border (%e * %e > %e)' % (startval, n, p.max))
				go_up = False
			if go_down and startval / n < p.min:
				logi.info('\t\thit lower border (%e / %e > %e)' % (startval, n, p.min))
				go_down = False
			if go_up:
				logi.debug('        robust_opt: \t\ttrying %e ^' % (startval * n))
				p.val = startval * n
				newstat = my_bkg_stat(i)
				logi.debug('        robust_opt: \t\tval = %e: %e' % (p.val, newstat))
				if newstat <= beststat:
					bestval = p.val
					beststat = newstat
					logi.debug('        robust_opt: \t\t\timprovement: %e' % p.val)
				if newstat > beststat + 100:
					go_up = False
			if go_down:
				logi.debug('        robust_opt: \t\ttrying %e v' % (startval / n))
				p.val = startval / n
				newstat = my_bkg_stat(i)
				logi.debug('        robust_opt: \t\tval = %e: %e' % (p.val, newstat))
				if newstat + 1e-3 < beststat:
					bestval = p.val
					beststat = newstat
					logi.debug('        robust_opt: \t\t\timprovement: %e' % p.val)
				if newstat > beststat + 100:
					go_down = False
		p.val = bestval
		logi.debug('        robust_opt: \tnew normalization of %s: %e' % (p.fullname, p.val))
		#plot_bkg_fit_resid(i)
	logi.info('        robust_opt: optimization of %s in %s done, reached %.3f' % (', '.join([p.fullname for p in params]), i, beststat))
	if beststat > 0.2:
		logi.info('        robust_opt: no good fit found: %.3f' % beststat)
		if False:
			plot_bkg_fit_resid(i)
			print('press ENTER to continue >> ', end=' ')
			sys.stdin.readline()
	
	logi.debug('        robust_opt: my optimization end ---')

logbs = logging.getLogger('bxa.BackgroundStorage')
logbs.setLevel(logging.WARN)

"""
Loads background file and assigns unit response matrix.

Capabilities for loading and storing previously fitted background models.
"""
class BackgroundStorage(object):
	def __init__(self, backgroundfilename, i, load=False):
		self.backgroundfilename = backgroundfilename
		self.backgroundparamsfile = backgroundfilename + '_bkgparams.json'
		logbs.info('      BackgroundStorage: for background model params of ID=%s, will use "%s" as storage' % (i, self.backgroundparamsfile))
		if load:
			load_pha(i, self.backgroundfilename)
		self.i = i
		self.load_rsp()
	def load_rsp(self):
		i = self.i
		copy_data(i,1000+2)
		unit_arf = get_bkg_arf(1000+2)
		unit_arf.specresp = 0.*unit_arf.specresp + 1.0 # * unit_arf.specresp.mean()
		self.bunitrsp = get_response(1000+2,bkg_id=1)
		delete_data(1000+2)
	def load_bkg_model(self):
		i = self.i
		m = get_bkg_model(i)
		bkg_model = json.load(open(self.backgroundparamsfile, 'r'))
		bkg_pars = bkg_model['params']
		for p in m.pars:
			logbs.info("loaded parameter: \tbkg[%s] = %e" % (p.fullname, bkg_pars[p.fullname]))
			if bkg_pars[p.fullname] > p.max or bkg_pars[p.fullname] < p.min:
				warnings.warn('WARNING: ignoring stored parameter value for %s (val=%s, min=%s, max=%s)' % (p.fullname, p.val, p.min, p.max))
				continue
			p.val = bkg_pars[p.fullname]
		return bkg_model
	
	def store_bkg_model(self, stats, **kwargs):
		i = self.i
		m = get_bkg_model(i)
		params = dict([(p.fullname, p.val) for p in m.pars])
		oldstats = 1e300

		try:
			prev_model = json.load(open(self.backgroundparamsfile, 'r'))
			oldstats = prev_model['stats']
		except IOError as e:
			warnings.warn('store_bkg_model: could not check previously stored model, perhaps this is the first. (Error was: %s)' % e)
		if stats > oldstats + 0.02:
			logbs.warn('store_bkg_model: ERROR: refusing to store worse model! %.3f (new) vs %.3f (old)' % (stats, oldstats))
		else:
			set_analysis(i, "energy", "counts")
			p = get_bkg_fit_plot(i)
			with open(self.backgroundparamsfile, 'w') as f:
				json.dump(dict(params=params, stats=stats,
					plot=dict(x=p.dataplot.x.tolist(), ydata=p.dataplot.y.tolist(), ymodel=p.modelplot.y.tolist()),
					**kwargs), 
					f, indent=4)
			logbs.info('store_bkg_model: stored as "%s"' % self.backgroundparamsfile)
		names = [p.fullname for p in m.pars]
		values = [p.val for p in m.pars]
		return names, values
"""
Robust fitting strategies for background models
"""


logf = logging.getLogger('bxa.Fitter')
logf.setLevel(logging.INFO)

class SingleFitter(object):
	def __init__(self, id, filename, backgroundmodel, load=False):
		""" 
		id: which data id to fit
		
		filename: prefix for where to store background information
		
		backgroundmodel: A background model, such as ChandraBackground
		
		load: whether the background file should be loaded now
		"""
		self.id = id
		logf.info('SingleFitter(for ID=%s, storing to "%s")' % (id, filename))
		logf.debug('  creating backgroundstorage ...')
		b = BackgroundStorage(filename, id, load=load)
		logf.debug('  creating Background Model ...')
		self.bm = backgroundmodel(b)
	def store(self):
		i = self.id
		newstats = my_bkg_stat(i)
		self.bm.storage.store_bkg_model(newstats, stage=self.stage)
	def tryload(self):
		for stage in self.bm.stages:
			self.prepare_stage(stage=stage)
			props = self.bm.storage.load_bkg_model()
			logf.info('Background loaded, stage %s%s' % (stage, '(last)' if self.bm.stages[-1] == stage else '(more to go)'))
			if stage == props['stage']:
				break
		
	def fit(self, reinit=True, plot=False):
		for stage in self.bm.stages:
			self.prepare_stage(stage=stage)
			self.fit_stage(stage=stage, plot=plot)
		logf.info('Background fit complete.')
	
	#def fit_continue(self, reinit=True, plot=False):
	#	stages = list(self.bm.stages)
	#	for stage in self.bm.stages:
	#		self.prepare_stage(stage=stage)
	#		try:
	#			props = self.bm.storage.load_bkg_model()
	#			logf.info('Background loaded, stage %s%s' % (stage, '(last)' if self.bm.stages[-1] == stage else '(more to go)'))
	#			stages.pop(0)
	#			if stage == props['stage']:
	#				break
	#	for stage in stages:
	#		self.prepare_stage(stage=stage)
	#		self.fit_stage(stage=stage, plot=plot)
			
	
	def prepare_stage(self, stage, prev=None, link=False):
		i = self.id
		logf.info('prepare_stage %s of ID=%s' % (stage, i))
		self.bm.set_model(stage=stage)
		if prev is not None and link:
			otherpars = prev
			this = self.bm
			assert len(otherpars) == len(self.bm.pars), (other, 'incompatible with', self.bm.pars)
			for pa, pb in zip(otherpars, self.bm.pars):
				aname = pa.fullname.split('_')[0]
				bname = pb.fullname.split('_')[0]
				assert aname == bname, ('names should be the same', pa.fullname, pb.fullname)
				logf.debug('   linking %s <- %s' % (pb.fullname, pa.fullname))
				pb = pa
		elif prev is not None:
			for pa, pb in zip(self.bm.pars, prev):
				if pa.link:
					logf.debug('   unlinking %s' % (pa.fullname))
					pa.unlink()
				if pa in self.bm.stagepars:
					pa.val = pb.val
		# only thaw those parameters that are new
		for pa in self.bm.pars:
			if pa in self.bm.stagepars:
				if pa.link: continue
				pa.thaw()
			else:
				pa.freeze()
		logf.info('prepare_stage %s of ID=%s done' % (stage, i))
				
	def fit_stage(self, stage, plot=False):
		i = self.id
		#set_method_opt('ftol', 0.1)
		def doplot():
			if plot:
				s = my_bkg_stat(i)
				logf.debug('fit_stage %s of ID=%s (stat: %.3f)... plotting ... ' % (stage, i, s))
				plot_bkg_fit_resid(i)
				logf.debug('fit_stage %s of ID=%s (stat: %.3f)... plotting done' % (stage, i, s))
		logf.info('fit_stage %s of ID=%s' % (stage, i))
		logf.debug(get_bkg_model(i))
		
		if get_bkg(i).counts.sum() > 500:
			logf.info('fit_stage %s of ID=%s. rough fit ...' % (stage, i))
			prev_filter = get_filter(i)
			logf.debug('grouping')
			group_counts(i, 20)
			set_stat('chi2gehrels')
			logf.debug('plotting')
			doplot()
			
			normparams = [p for p in self.bm.stagepars if p.name in ['ampl', 'norm']]
			if normparams:
				logf.debug('simple optimization')
				robust_opt(i, normparams)
			logf.debug('calling fit_bkg()')
			fit_bkg(i)
			
			logf.debug('plotting')
			doplot()
			ungrouping_bug = False
			logf.debug('ungrouping')
			try:
				ungroup(i)
			except Exception as e:
				logf.warn('ungrouping failed')
				ungrouping_bug = True
			
			logf.debug('setting filters')
			ignore()
			notice(prev_filter)
			self.stage = stage
			logf.debug('storing')
			self.store()
		
		logf.info('fit_stage %s of ID=%s.  fine fit ...' % (stage, i))
		set_method_opt('ftol', 0.001)
		set_stat('cstat')
		doplot()
		fit_bkg(i)
		doplot()
		logf.info('fit_stage %s of ID=%s.  fitted' % (stage, i))
		self.stage = stage
		self.store()
		logf.info('fit_stage %s of ID=%s.  stage done' % (stage, i))
		try:
			ungroup(i)
		except Exception as e:
			logf.warn('ungrouping failed')
		
logmf = logging.getLogger('bxa.MultiFitter')
logmf.setLevel(logging.INFO)

class MultiFitter(object):
	def __init__(self, filename, backgroundmodel, load=True):
		"""
		filename should be a text file, containing all the 
		file names (if load=True) or storage prefixes
		
		backgroundmodel: background model to use (e.g. ChandraBackground)
		
		load: whether the background file should be loaded now
		"""
		ids = [l.strip() for l in open(filename).readlines()]
		names = list(ids)
		#if load:
		#	ids = list(range(1, 1+len(names)))
		logmf.debug('MultiFitter: loading...')
		self.fitters = {}
		for i, name in zip(ids, names):
			self.fitters[i] = SingleFitter(i, name, backgroundmodel, load=load)
		self.ids = sorted(ids, key=lambda i: get_bkg(i).counts.sum(), reverse=True)
		logmf.debug('MultiFitter: loading done')
		
	"""
	MultiFitter fits first one with SingleFitter,
	then goes through all the others
	by setting the parameter values to those of the previous id
	and then fitting each stage
	"""
	def fit(self, **kwargs):
		batchsize = 10
		logmf.info('MultiFitter: splitting work into batches of size %d' % batchsize)
		for part in range(int(numpy.ceil(len(self.ids[1:]) * 1. / batchsize))):
			batchids = self.ids[part*batchsize:part*batchsize+batchsize]
			logmf.debug('MultiFitter: batch with %s' % str(batchids))
			first = batchids[0]
			firstfit = self.fitters[first]
			logmf.info('MultiFitter: fit first ID=%s ...' % first)
			stages = firstfit.bm.stages
			pars_at_stages = {}
			for stage in firstfit.bm.stages:
				firstfit.prepare_stage(stage=stage)
				firstfit.fit_stage(stage=stage, **kwargs)
				pars_at_stages[stage] = list(firstfit.bm.pars)
			logmf.info('MultiFitter: fit first ID=%s done' % first)
			
			# we want to improve our statistics by fitting jointly
			for stage in stages:
				logmf.info('MultiFitter: joint fitting, stage "%s" ...' % stage)
				firstfit.prepare_stage(stage=stage)
				for i in batchids[1:]:
					self.fitters[i].prepare_stage(stage=stage, prev=pars_at_stages[stage], link=True)
				
				logmf.debug('MultiFitter: joint fitting, stage "%s", rough chi^2...' % stage)
				set_method_opt('ftol', 0.1)
				set_stat('chi2gehrels')
				logmf.debug('MultiFitter: joint fitting, stage "%s", rough chi^2 fit...' % stage)
				fit_bkg(*batchids)
				logmf.debug('MultiFitter: joint fitting, stage "%s", rough chi^2 storing...' % stage)
				for i in batchids:
					self.fitters[i].store()
				set_stat('cstat')
				logmf.debug('MultiFitter: joint fitting, stage "%s", cstat...' % stage)
				fit_bkg(*batchids)
				for i in batchids:
					self.fitters[i].store()
				#self.fitters[i].fit_stage(stage=stage, **kwargs)
				pars_at_stages[stage] = self.fitters[i].bm.pars
				logmf.info('MultiFitter: joint fitting, stage "%s" done' % stage)
			# now we release the links and try to improve the fits
			# individually
			for stage in stages:
				logmf.info('MultiFitter: individual fitting, stage "%s" ...' % stage)
				firstfit.prepare_stage(stage=stage)
				logmf.info('MultiFitter: individual fitting, stage "%s" unlinking ' % stage)
				for i in batchids[1:]:
					self.fitters[i].prepare_stage(stage=stage, prev=pars_at_stages[stage], link=False)
				logmf.info('MultiFitter: individual fitting, stage "%s" fitting ' % stage)
				for i in batchids:
					self.fitters[i].fit_stage(stage=stage, **kwargs)
					#pars_at_stages[stage] = self.fitters[i].bm.pars
				logmf.info('MultiFitter: individual fitting, stage "%s" done' % stage)
	def fit_jointly_stage(self, stage, ids, plot=False):
		def doplot(i):
			if plot:
				s = my_bkg_stat(i)
				logmf.debug('fit_jointly_stage %s of ID=%s (stat: %.3f)... plotting ... ' % (stage, i, s))
				plot_bkg_fit_resid(i)
				logmf.debug('fit_jointly_stage %s of ID=%s (stat: %.3f)... plotting done' % (stage, i, s))
		params = []
		prev_filters = []
		for i in ids:
			prev_filters.append(get_filter(i))
			group_counts(i, 20)
			set_stat('chi2gehrels')
			doplot(i)
			params += [p for p in self.bm.stagepars if not p.link and not p.frozen]
		fit_bkg(id=ids[0], otherids=ids[1:])
		doplot(ids[0])
		for i, prev_filter in zip(ids, prev_filters):
			ungroup(i)
			ignore()
			notice(prev_filter)
			self.fitters[i].store()
		logmf.debug('fit_jointly_stage %s: fine fit ...' % (stage))
		
		set_method_opt('ftol', 0.001)
		set_stat('cstat')
		doplot(ids[0])
		fit_bkg(id=ids[0], otherids=ids[1:])
		doplot(ids[0])
		logmf.debug('fit_jointly_stage %s: fitted' % (stage))
		for i in ids:
			self.fitters[i].store()
		logmf.debug('fit_jointly_stage %s: stage done' % (stage))

__all__ = ['SingleFitter', 'MultiFitter', 'BackgroundStorage', 'robust_opt', 'my_bkg_stat']
