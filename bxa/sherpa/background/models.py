"""
Background models for various telescopes and instruments
"""

import numpy
import json
import logging
import warnings
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

class BackgroundModel(object):
	pass

logbm = logging.getLogger('bxa.BackgroundModel')
logbm.setLevel(logging.INFO)

"""
Background model for Chandra, as for the CDFS.

Uses a flat continuum, two broad gaussians and 8 narrow instrumental lines.
"""
class ChandraBackground(BackgroundModel):
	def __init__(self, storage):
		self.storage = storage
		i = self.storage.i
		self.centers = [1.486, 1.739, 2.142, 7.478, 8.012, 8.265, 8.4939, 9.7133]
		continuum, softsoftend, softend = box1d('continuum_%s' % i), gauss1d('softsoftend_%s' % i), gauss1d('softend_%s' % i)
		line1, line2, line3, line4, line5, line6, line7, line8 = [
			gauss1d('line%d_%s' % (j, i)) for j in range(1, 9)]

		self.lines = [line1, line2, line3, line4, line5, line6, line7, line8]
		self.abslines = [line5, line6, line7]
		self.linelines = [line1, line2, line3, line4, line8]
		#lines = linelines + abslines
		self.boxes = [continuum]

		self.softboxes = [softend, softsoftend]
		self.plboxes = self.boxes + self.softboxes
		
		logbm.info('creating Chandra background model')
		for l, c in zip(self.lines, self.centers):
			l.pos = c
			l.pos.min = c - 0.1
			l.pos.max = c + 0.1

		for l in self.lines:
			l.ampl = 2000
			l.ampl.min = 1e-8
			l.ampl.max = 1e12
			l.fwhm = 0.02
			l.fwhm.min = 0.002
			l.pos.freeze()

		for l in self.abslines:
			l.fwhm.max = 0.4

		for l in self.linelines:
			l.fwhm.max = 0.1

		# narrow soft end
		softsoftend.pos = 0.3
		softsoftend.pos.min = 0
		softsoftend.pos.max = 0.6
		softsoftend.pos.freeze()
		softsoftend.fwhm = 0.5
		softsoftend.fwhm.min = 0.2
		softsoftend.fwhm.max = 0.7
		softsoftend.fwhm.freeze()

		# wide gaussian
		softend.pos = 0
		softend.pos.max = 1
		softend.pos.min = -1
		softend.pos.freeze()
		softend.fwhm = 3.8
		softend.fwhm.min = 2
		softend.fwhm.max = 7
		softend.fwhm.freeze()

		for b in self.plboxes:
			b.ampl.val = 1
			b.ampl.freeze()
		changepoints = [0.2, 0.8, 1.3, 2.5, 8.2, 8.4, 8.75, 12]
		changepoints = [0., 12]

		for b,clo,chi in zip(self.boxes, changepoints[:-1], changepoints[1:]):
			b.xlow = clo
			b.xhi = chi
			b.xlow.freeze()
			b.xhi.freeze()
			b.ampl.min = 1e-8
			b.ampl.max = 1e8
			b.ampl.val = 1
		
		contlevel = const1d("contlevel_%s" % i)
		softlevel = const1d("softlevel_%s" % i)
		softsoftlevel = const1d("softsoftlevel_%s" % i)
		contlevel.c0.min = 1e-6
		softlevel.c0.min = 1e-4
		softsoftlevel.c0.min = 1e-4
		contlevel.c0.max = 1e10
		softlevel.c0.max = 1e10
		softsoftlevel.c0.max = 1e10
		
		# init
		contlevel.c0.val = 1e-3
		softlevel.c0.val = 1e1
		softsoftlevel.c0.val = 1e1
		self.stages = ['continuum', 'softfeatures'] + ['line%d' % i for i, line in enumerate(self.linelines + self.abslines)] + ['full']
		self.contlevel = contlevel
		self.softlevel = softlevel
		self.softsoftlevel = softsoftlevel
		
		
	def set_zero(self):
		for l in self.lines + self.plboxes:
			l.ampl.min = 0
			l.ampl.val = 0
	
	"""
	range over which this model is valid
	"""
	def set_filter(self):
		ignore(None, 0.4)
		ignore(9.8, None)
		notice(0.4, 9.8)
	def set_model(self, stage):
		i = self.storage.i
		withsoft = stage not in ('continuum')
		withlines = stage not in ('continuum', 'softfeatures')
		logbm.info('stage "%s" for %s ...' % (stage, i))
		continuum = self.boxes[0]
		contlevel = self.contlevel
		softlevel = self.softlevel
		softsoftlevel = self.softsoftlevel
		softend, softsoftend = self.softboxes
		bg_model = continuum * contlevel
		bunitrsp = self.storage.bunitrsp
		set_bkg_model(i, bg_model)
		set_bkg_full_model(i, bunitrsp(bg_model))
		logbm.debug('zooming to %.1f %.1f' % (2.5, 7))
		ignore(None, 2.5)
		ignore(7, None)
		notice(2.5, 7)
		self.stagepars = [contlevel.c0]
		self.pars = list(self.stagepars)
		if stage == 'continuum': 
			return
		
		logbm.debug('adding soft end...')
		bg_model += (softend * softlevel + softsoftend * softsoftlevel) * contlevel
		delete_bkg_model(i)
		set_bkg_model(i, bg_model)
		set_bkg_full_model(i, bunitrsp(bg_model))
		ignore(None, 0.4)
		ignore(2., None)
		notice(0.4, 2)
		logbm.debug('zooming to %.1f %.1f' % (0.4, 2.))
		self.stagepars = [softsoftlevel.c0, softlevel.c0, softsoftlevel.c0]
		self.pars += self.stagepars
		if stage == 'softfeatures': 
			return
		logbm.debug('adding lines...')
		for j, l in enumerate(self.linelines + self.abslines):
			bg_model += l * contlevel
			set_bkg_model(i, bg_model)
			set_bkg_full_model(i, bunitrsp(bg_model))
			if l.ampl.frozen: continue
			lo = l.pos.val - max(3*l.fwhm.val, 0.2)
			hi = l.pos.val + max(3*l.fwhm.val, 0.2)
			logbm.debug('zooming to %.1f %.1f' % (lo, hi))
			ignore(None, lo)
			ignore(hi, None)
			notice(lo, hi)
			self.stagepars = [l.ampl]
			self.pars += self.stagepars
			if stage == 'line%d' % j: 
				return
			self.set_filter()
		# finally, full fit
		self.stagepars = self.pars

"""
Background model for XMM/PN, as for the XMM-XXL.

Developed by Richard Sturm at MPE
Written for Sherpa by Zhu Liu
Adapted into this framework by Johannes Buchner
"""
class XMMPNBackground(BackgroundModel):
	pncenters = [1.49165, 1.49165, 4.53177, 5.42516, 6.38155, 7.48675, 8.04087, 8.04087, 8.60924, 8.89395, 9.56160]
	pnlinewidth = [5.73813E-02, 3.63469E-02, 6.10487E-02, 7.08380E-02, 9.59053E-02, 6.52422E-02, 9.48594E-02, 6.26174E-05, 0.120893, 0.114254, 0.108717]
	pnlinenorm = [7.81356E-03, 3.96601E-03, 7.30727E-04, 4.96413E-04, 5.31295E-9, 6.84796E-04, 3.01564E-02, 1.41847E-04, 8.87887E-03, 5.75592E-03, 1.71367E-03]
	def __init__(self, storage, galactic_NH = 1e20):
		self.storage = storage
		i = self.storage.i

		self.pnrsp = get_response(i)
		self.pnbrsp = get_response(i,bkg_id=1)
		self.pnscale = get_bkg_scale(i)
		copy_data(i,1000+2)
		self.pnbunitrsp = get_response(1000+2, bkg_id=1)
		delete_data(1000+2)
		self.pnbkgcons = xsconstant('pncons_%s' % i)
		self.pnbkgspline1 = xsspline('pnspline1_%s' % i)
		self.pnbkgexpdec = xsexpdec('pnexpdec_%s' % i)
		self.pnbkgsmedge1 = xssmedge('pnsmedge1_%s' % i)
		self.pnbkgspline2 = xsspline('pnspline2_%s' % i)
		self.pnbkgsmedge2 = xssmedge('pnsmedge2_%s' % i)
		self.pnbkginspl = xspowerlaw('pnbkpl_%s' % i)
		self.pnlines = []
		for j in range(1, 11+1):
			comp = xsgaussian('pngau%d_%s' % (j,i))
			self.pnlines.append(comp)
			setattr(self, 'pnbkgline%d' % j, comp)
		self.pnbkgpl = xspowerlaw('pnpnexpl_%s' % i)
		self.pnbkgapec = xsapec('pnapec_%s' % i)
		self.pnbkglcapec = xsapec('pnlcapec_%s' % i)
		
		self.galabs = xsphabs('absgal_%s' % i)
		self.galabs.nH = galactic_NH / 1e22
		self.galabs.nH.freeze()
		
		self.pnfixwid = [self.pnbkgline2, self.pnbkgline3, self.pnbkgline4, self.pnbkgline5, self.pnbkgline6, self.pnbkgline8, self.pnbkgline11]
		self.pnfree = [self.pnbkgline1, self.pnbkgline7, self.pnbkgline9, self.pnbkgline10]
		
		#define PN background model
		#pn_bkg = self.pnbunitrsp(self.pnbkgcons*(self.pnbkgspline1*self.pnbkgexpdec + self.pnbkgsmedge1*self.pnbkgsmedge2*(self.pnbkgspline2*self.pnbkginspl + 
		#	self.pnbkgline1 + self.pnbkgline2 + self.pnbkgline3 + self.pnbkgline4 + self.pnbkgline5 + self.pnbkgline6 + self.pnbkgline7 + self.pnbkgline8 + 
		#	self.pnbkgline9 + self.pnbkgline10 + self.pnbkgline11))) + self.pnbrsp(self.galabs*(self.pnbkgpl+self.pnbkgapec)+self.pnbkglcapec)
		
		# Define source model: galabs*(intgalabs*(srcpl+torus+pnsoftpl))
		#set_model(i,galabs*(intgalabs*(xspowerlaw.srcpl)))
		#set_full_model(i,(pnrsp(galabs*(intgalabs*(xspowerlaw.srcpl))) + pnscale*(pn_bkg)))
		
		for l, c in zip(self.pnlines, self.pncenters):
			l.LineE = c
			l.LineE.min = c - 0.05
			l.LineE.max = c + 0.05
		
		self.pnbkgline2.LineE = self.pnbkgline1.LineE
		self.pnbkgline8.LineE = self.pnbkgline7.LineE
		
		for l, s in zip(self.pnlines, self.pnlinewidth):
			l.Sigma = s

		for l in self.pnfree:
			l.Sigma.min = 1E-5
			l.Sigma.max = 0.2
		
		for l in self.pnfixwid:
			l.Sigma.freeze()
		
		for l, n in zip(self.pnlines, self.pnlinenorm):
			l.norm = n
			l.norm.min = 1E-10
			l.norm.max = 1E10
			
		# Scaling constant
		self.pnbkgcons.factor = 1.0
		self.pnbkgcons.factor.freeze()
		
		# thermal radiation
		self.pnbkgapec.kT = 0.286928
		self.pnbkgapec.kT.min = 0.008
		self.pnbkgapec.kT.max = 64
		self.pnbkgapec.Abundanc = 1.0
		self.pnbkgapec.Abundanc.freeze()
		self.pnbkgapec.Redshift = 0.0
		self.pnbkgapec.Redshift.freeze()
		self.pnbkgapec.norm = 5.58410E-05
		self.pnbkgapec.norm.min = 1e-10
		self.pnbkgapec.norm.max = 1e10
		
		# local thermal radiation
		self.pnbkglcapec.kT = 0.1
		self.pnbkglcapec.kT.freeze()
		self.pnbkglcapec.Abundanc = 1.0
		self.pnbkglcapec.Abundanc.freeze()
		self.pnbkglcapec.Redshift = 0.0
		self.pnbkglcapec.Redshift.freeze()
		self.pnbkglcapec.norm = 3.89164E-05
		self.pnbkglcapec.norm.min = 1e-10
		self.pnbkglcapec.norm.max = 1e10
		
		# exponential decay
		self.pnbkgexpdec.factor = 44.3418
		self.pnbkgexpdec.factor.min = 0
		self.pnbkgexpdec.factor.max = 100
		self.pnbkgexpdec.norm = 6830.89
		self.pnbkgexpdec.norm.freeze()
		
		# Smear function
		self.pnbkgsmedge1.edgeE = 0.538408
		self.pnbkgsmedge1.edgeE.freeze()
		self.pnbkgsmedge1.MaxTau = 1.40238
		self.pnbkgsmedge1.MaxTau.min = 0 
		self.pnbkgsmedge1.MaxTau.max = 10
		self.pnbkgsmedge1.index = -2.67000
		self.pnbkgsmedge1.index.freeze()
		self.pnbkgsmedge1.width = 0.313365
		self.pnbkgsmedge1.width.min = 0.01
		self.pnbkgsmedge1.width.max = 100
		
		self.pnbkgsmedge2.edgeE = 1.38826
		self.pnbkgsmedge2.edgeE.freeze()
		self.pnbkgsmedge2.MaxTau.min = 0 
		self.pnbkgsmedge2.MaxTau.max = 10
		self.pnbkgsmedge2.MaxTau = 9.37167
		self.pnbkgsmedge2.index = -2.67000
		self.pnbkgsmedge2.index.freeze()
		self.pnbkgsmedge2.width = 5.7642
		self.pnbkgsmedge2.width.min = 0.01
		self.pnbkgsmedge2.width.max = 100
		
		# Spline funtion
		self.pnbkgspline1.Estart = 0.200000
		self.pnbkgspline1.Estart.freeze()
		self.pnbkgspline1.Ystart = -1.31506
		self.pnbkgspline1.Ystart.min = -1e+6
		self.pnbkgspline1.Ystart.max = 1e+6
		self.pnbkgspline1.Yend = 1064.16
		self.pnbkgspline1.Yend.min = -1e+6
		self.pnbkgspline1.Yend.max = 1e+6
		self.pnbkgspline1.YPstart = -106.183
		self.pnbkgspline1.YPstart.min = -1e+6
		self.pnbkgspline1.YPstart.max = 1e+6
		self.pnbkgspline1.YPend = -366.092
		self.pnbkgspline1.YPend.min = -1e+6
		self.pnbkgspline1.YPend.max = 1e6
		self.pnbkgspline1.Eend = 1.74715
		self.pnbkgspline1.Eend.min = 0
		self.pnbkgspline1.Eend.max = 100
		
		self.pnbkgspline2.Estart = 3.29056
		self.pnbkgspline2.Ystart = 1.00643
		self.pnbkgspline2.Ystart.min = -1e+6
		self.pnbkgspline2.Ystart.max = 1e+6
		self.pnbkgspline2.Yend = 0.887026
		self.pnbkgspline2.Yend.min = -1e+6
		self.pnbkgspline2.Yend.max = 1e+6
		self.pnbkgspline2.YPstart = -0.278401
		self.pnbkgspline2.YPstart.min = -1e+6
		self.pnbkgspline2.YPstart.max = 1e+6
		self.pnbkgspline2.YPend = 4.84809E-03
		self.pnbkgspline2.YPend.min = -1e+6
		self.pnbkgspline2.YPend.max = 1e6
		self.pnbkgspline2.Eend = 7.32701
		self.pnbkgspline2.Eend.min = 0
		self.pnbkgspline2.Eend.max = 100
		
		# Background power law
		self.pnbkginspl.PhoIndex = 0.279
		self.pnbkginspl.PhoIndex.min = -2
		self.pnbkginspl.PhoIndex.max = 9
		self.pnbkginspl.norm = 8.23614E-03
		self.pnbkginspl.norm.min = 1E-10
		self.pnbkginspl.norm.max = 1E6
		
		# Extragalactic background
		self.pnbkgpl.PhoIndex = 1.46
		self.pnbkgpl.PhoIndex.freeze()
		self.pnbkgpl.norm = 1.25288E-05
		self.pnbkgpl.norm.min = 1e-10
		self.pnbkgpl.norm.max = 1e3
		
		self.stages = []
		self.stage_models = {}
		self.stage_models_full = {}
		
		base = self.pnbkgspline2*self.pnbkginspl
		logbm.info( '    XMMPNBackground: creating stages for %s' % i)
		self.addStage('1', base)
		self.addStage('2', base + self.pnbkgline2)
		self.addStage('3', base + self.pnbkgline1 + self.pnbkgline2)
		self.addStage('4', base + self.pnbkgline1 + self.pnbkgline2 + self.pnbkgline7 + self.pnbkgline8)
		self.addStage('5', base + self.pnbkgline1 + self.pnbkgline2 + self.pnbkgline7 + self.pnbkgline8 + self.pnbkgline9 + self.pnbkgline10)
		lines = self.pnbkgline1 + self.pnbkgline2 + self.pnbkgline3 + self.pnbkgline4 + self.pnbkgline5 + self.pnbkgline6 + self.pnbkgline7 + self.pnbkgline8 + self.pnbkgline9 + self.pnbkgline10 + self.pnbkgline11
		self.addStage('6', base + lines)
		self.addStage('7', base + lines, self.galabs*(self.pnbkgapec))
		self.addStage('8', base + lines, self.galabs*(self.pnbkgapec+self.pnbkgpl))
		self.addStage('9', base + lines, self.galabs*(self.pnbkgapec+self.pnbkgpl)+self.pnbkglcapec)
		logbm.info( '    XMMPNBackground: setup for %s completed' % i)

	def addStage(self, name, instrument_bg, external_bg=None):
		model = self.pnbkgcons*(self.pnbkgspline1*self.pnbkgexpdec + self.pnbkgsmedge1*self.pnbkgsmedge2*(instrument_bg))
		full_model = self.pnbunitrsp(self.pnbkgcons*(self.pnbkgspline1*self.pnbkgexpdec + self.pnbkgsmedge1*self.pnbkgsmedge2*(instrument_bg)))
		if external_bg is not None:
			model = model + external_bg
			full_model = full_model + self.pnrsp(external_bg)
		self.stage_models[name] = model
		self.stage_models_full[name] = full_model
		self.stages.append(name)
		
	"""
	range over which this model is valid
	"""
	def set_filter(self):
		i = self.storage.i
		notice(None, None)
		ignore(None, 0.3)
		ignore(10.0, None)
	
	def set_model(self, stage):
		i = self.storage.i
		
		logbm.info( '    XMMPNBackground: going to stage %s on %s' % (stage, i))
		bg_model = self.stage_models[stage]
		bg_model_full = self.stage_models_full[stage]
		self.stagepars = list(bg_model.pars)
		self.pars = list(self.stagepars)
		
		delete_bkg_model(i)
		logbm.info( '    XMMPNBackground: setting model')
		set_bkg_model(i, bg_model)
		set_bkg_full_model(i, bg_model_full)
		self.set_filter()
"""
Background model for Swift/XRT.

Uses a flat continuum, two broad gaussians and 8 narrow instrumental lines.
"""
class SwiftXRTBackground(BackgroundModel):
	def __init__(self, storage):
		self.storage = storage
		
		i = self.storage.i
		logbm.info( '    SwiftXRTBackground: setting up for %s' % i)
		dip = box1d('dip_%s' % i)
		pbknpl = xsbknpower('pbknpl_%s' % i)
		g1, g2, g3, g4 = [gauss1d('gauss%d_%s' % (j,i)) for j in [1, 2, 3, 4]]

		pbknpl.BreakE.min = 0.2
		pbknpl.BreakE.max = 5
		pbknpl.BreakE.val = 2
		pbknpl.PhoIndx1.max = 4
		pbknpl.PhoIndx2.max = 4
		pbknpl.PhoIndx1.min = 0.8
		pbknpl.PhoIndx2.min = 0.8
		pbknpl.PhoIndx1.val = 2
		pbknpl.PhoIndx2.val = 1.5
		pbknpl.norm.min = 1e-10
		pbknpl.norm.max = 1
		pbknpl.norm.val = 0.004
		
		lines = [(0.1, 0.7, 1.1), (2, 2.15, 2.5), (1, 1.2, 1.4), (0, 0.4, 0.5)]
		

		for g, (lo, mid, hi) in zip([g1, g2, g3, g4], lines):
			g.pos.val = mid
			g.pos.min = lo
			g.pos.max = hi
			g.fwhm.val = 0.2
			g.fwhm.max = 1
			g.fwhm.min = 0.01
			g.ampl.val = 0.01
			g.ampl.max = 1
			g.ampl.min = 1e-6

		dip.xlow = 2
		dip.xhi = 3
		dip.xlow.min = 1.75
		dip.xlow.max = 2.25
		dip.xhi.min = 2.75
		dip.xhi.max = 3.25
		dip.ampl.val = 0.5
		dip.ampl.min = 1e-3
		dip.ampl.max = 1 - 1e-3
		self._pars = [pbknpl, dip, g1, g2, g3, g4]
		self.stages = [2, 3, 4, 5, 6, 7]
	def set_filter(self):
		logbm.debug('SwiftXRTBackground: setting filter 0.3-5keV')
		ignore(None, 0.3)
		ignore(5, None)
		notice(0.3, 5)

	def set_model(self, stage):
		i = self.storage.i
		[pbknpl, dip, g1, g2, g3, g4] = self._pars
		
		logbm.info('stage "%s" for ID=%s ...' % (stage, i))
		bunitrsp = self.storage.bunitrsp
		model = stage
		self.bg_model = pbknpl
		self.stagepars = list(pbknpl.pars)
		if model > 1:
			self.bg_model = self.bg_model + g1 
			self.stagepars += list(g1.pars)
		if model > 2:
			self.bg_model = self.bg_model + g2
			self.stagepars = list(g2.pars)
		if model > 3:
			self.bg_model = self.bg_model + g3
			self.stagepars = list(g3.pars)
		if model > 4:
			self.bg_model = (1 - dip) * self.bg_model
			self.stagepars = list(dip.pars)
		if model > 5:
			self.bg_model = self.bg_model + g4
			self.stagepars = list(g4.pars)
		self.pars = [p for p in self.bg_model.pars if not p.link]
		if model > 6: # finally, full fit
			self.stagepars = self.pars
		set_bkg_model(i, self.bg_model)
		set_bkg_full_model(i, bunitrsp(self.bg_model))
		self.set_filter()
		logbm.debug('background model set for stage "%s" for ID=%s' % (stage, i))

class SwiftXRTWTBackground(SwiftXRTBackground):
	def set_filter(self):
		logbm.debug('SwiftXRTBackground: setting filter 0.4-5keV')
		ignore(None, 0.4)
		ignore(5, None)
		notice(0.4, 5)

__all__ = ['SwiftXRTBackground', 'SwiftXRTWTBackground', 'ChandraBackground']
