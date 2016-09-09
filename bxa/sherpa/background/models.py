"""
Background models for various telescopes and instruments
"""

from sherpa.astro.ui import *
import numpy
import json
import logging
import warnings

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
		withsoft = stage > 0
		withlines = stage > 1
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
			logbm.debug('zooming to %.1f %.1f' % (l.pos.val - 3*l.fwhm.val, l.pos.val + 3*l.fwhm.val))
			ignore(None, l.pos.val - max(3*l.fwhm.val, 0.2))
			ignore(l.pos.val + max(3*l.fwhm.val, 0.2), None)
			self.stagepars = [l.ampl]
			self.pars += self.stagepars
			if stage == 'line%d' % j: 
				return
			self.set_filter()
		# finally, full fit
		self.stagepars = self.pars

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

__dir__ = [SwiftXRTBackground, SwiftXRTWTBackground, ChandraBackground]

