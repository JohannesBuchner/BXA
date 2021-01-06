#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from __future__ import print_function

"""
Empirical XMM background model.

Written by Zhu Liu, adapted by Torben Simm and Johannes Buchner
(C) 2013-2016

For example usage, see examples/sherpa/background/xmm/fit.py
"""	

import os
import numpy

if 'MAKESPHINXDOC' not in os.environ:
	import sherpa.astro.ui as ui
	from sherpa.stats import Cash, CStat
	from sherpa.models.parameter import Parameter
	from sherpa.models import ArithmeticModel, CompositeModel
	from sherpa.astro.ui import *
	from sherpa.astro.instrument import RSPModelNoPHA, RMFModelNoPHA
else:
	CompositeModel, ArithmeticModel = object, object

print("""

Using XMM empirical background model originally by Richard Sturm.
Please reference Maggi P., et al., 2014, A&A, 561, AA76.

""")


def get_embedded_file(filename):
    """
    Gets the path of a file in the same folder as this script
    """
    return os.path.join(os.path.dirname(__file__), filename)

def get_pn_bkg_model(i, galabs, fit=False):
#=================================================================
# Parameters:
# i = sherpa ID of data set  
# galabs = name of model for galactic absorption
# pnbrsp = response model of bkg data set 
# fit: True = fit bkg spectrum; False = just set_bkg_full_model
# returns unit response for bkg model
#=================================================================
    #get instrument response model for bkg spectrum
    if get_rmf(i).energ_lo[0] == 0: get_rmf(i).energ_lo[0] = 0.001
    if get_arf(i).energ_lo[0] == 0: get_arf(i).energ_lo[0] = 0.001 
    pnbrsp = get_response(i,bkg_id=1)
    pnscale = get_bkg_scale(i) #get background scaling factor 

    #create unit response
    dia_pn_rmf=get_embedded_file('pn_dia.rmf')
    dia_pn_arf=get_embedded_file('pn_dia.arf')
    copy_data(i,1000+2) 	
    load_bkg_rmf(1000+2, dia_pn_rmf) #load diagonal bkg matrices
    load_bkg_arf(1000+2, dia_pn_arf)
    pnbunitrsp = get_response(1000+2, bkg_id=1)	
    delete_data(1000+2)

    #gaussian line center energy, line width, and initial normalization; for *PN background*
    pncenters = [1.49165, 1.49165, 4.53177, 5.42516, 6.38155, 7.48675, 8.04087, 8.04087, 8.60924, 8.89395, 9.56160]
    pnlinewidth = [5.73813E-02, 3.63469E-02, 6.10487E-02, 7.08380E-02, 9.59053E-02, 6.52422E-02, 9.48594E-02, 6.26174E-05, 0.120893, 0.114254, 0.108717]
    pnlinenorm = [7.81356E-03, 3.96601E-03, 7.30727E-04, 4.96413E-04, 5.31295E-9, 6.84796E-04, 3.01564E-02, 1.41847E-04, 8.87887E-03, 5.75592E-03, 1.71367E-03]

    pnbkgcons, pnbkgspline1, pnbkgexpdec, pnbkgsmedge1, pnbkgsmedge2, pnbkgspline2, pnbkginspl, pnbkgline1, pnbkgline2, pnbkgline3, pnbkgline4, pnbkgline5, pnbkgline6, pnbkgline7, pnbkgline8, pnbkgline9, pnbkgline10, pnbkgline11, pnbkgpl, pnbkgapec, pnbkglcapec, = (xsconstant.pncons, xsspline.pnspline1, xsexpdec.pnexpdec, xssmedge.pnsmedge1, xssmedge.pnsmedge2, xsspline.pnspline2, xspowerlaw.pnbkpl, xsgaussian.pngau1, xsgaussian.pngau2, xsgaussian.pngau3, xsgaussian.pngau4, xsgaussian.pngau5, xsgaussian.pngau6, xsgaussian.pngau7, xsgaussian.pngau8, xsgaussian.pngau9, xsgaussian.pngau10, xsgaussian.pngau11, xspowerlaw.pnpnexpl, xsapec.pnapec, xsapec.pnlcapec)

    pnlines = [pnbkgline1, pnbkgline2, pnbkgline3, pnbkgline4, pnbkgline5, pnbkgline6, pnbkgline7, pnbkgline8, pnbkgline9, pnbkgline10, pnbkgline11]

    pnfixwid = [pnbkgline2, pnbkgline3, pnbkgline4, pnbkgline5, pnbkgline6, pnbkgline8, pnbkgline11]
    pnfree = [pnbkgline1, pnbkgline7, pnbkgline9, pnbkgline10]

    #define PN background model
    pn_bkg = pnbunitrsp(pnbkgcons*(pnbkgspline1*pnbkgexpdec + pnbkgsmedge1*pnbkgsmedge2*(pnbkgspline2*pnbkginspl + 
	     pnbkgline1 + pnbkgline2 + pnbkgline3 + pnbkgline4 + pnbkgline5 + pnbkgline6 + pnbkgline7 + pnbkgline8 + 
	     pnbkgline9 + pnbkgline10 + pnbkgline11))) + pnbrsp(galabs*(pnbkgpl+pnbkgapec)+pnbkglcapec)

    for l, c in zip(pnlines, pncenters):
        l.LineE = c
        l.LineE.min = c - 0.05
        l.LineE.max = c + 0.05

    pnbkgline2.LineE = pnbkgline1.LineE
    pnbkgline8.LineE = pnbkgline7.LineE 

    for l, s in zip(pnlines, pnlinewidth):
        l.Sigma = s
        
    for l in pnfree:
        l.Sigma.min = 1E-5
        l.Sigma.max = 0.2
			
    for l in pnfixwid:
        l.Sigma.freeze()
			
    for l, n in zip(pnlines, pnlinenorm):
        l.norm = n
        l.norm.min = 1E-10
        l.norm.max = 1E10

    # Scaling constant
    pnbkgcons.factor = 1.0
    pnbkgcons.factor.freeze()
    
    # thermal radiation
    pnbkgapec.kT = 0.286928
    pnbkgapec.kT.min = 0.008
    pnbkgapec.kT.max = 64
    pnbkgapec.Abundanc = 1.0
    pnbkgapec.Abundanc.freeze()
    pnbkgapec.Redshift = 0.0
    pnbkgapec.Redshift.freeze()
    pnbkgapec.norm = 5.58410E-05
    pnbkgapec.norm.min = 1e-10
    pnbkgapec.norm.max = 1e10
    
    # local thermal radiation
    pnbkglcapec.kT = 0.1
    pnbkglcapec.kT.freeze()
    pnbkglcapec.Abundanc = 1.0
    pnbkglcapec.Abundanc.freeze()
    pnbkglcapec.Redshift = 0.0
    pnbkglcapec.Redshift.freeze()
    pnbkglcapec.norm = 3.89164E-05
    pnbkglcapec.norm.min = 1e-10
    pnbkglcapec.norm.max = 1e10
    
    # exponential decay
    pnbkgexpdec.factor = 44.3418
    pnbkgexpdec.factor.min = 0
    pnbkgexpdec.factor.max = 100
    pnbkgexpdec.norm = 6830.89
    pnbkgexpdec.norm.freeze()
    
    # Smear function
    pnbkgsmedge1.edgeE = 0.538408
    pnbkgsmedge1.edgeE.freeze()
    pnbkgsmedge1.MaxTau = 1.40238
    pnbkgsmedge1.MaxTau.min = 0 
    pnbkgsmedge1.MaxTau.max = 10
    pnbkgsmedge1.index = -2.67000
    pnbkgsmedge1.index.freeze()
    pnbkgsmedge1.width = 0.313365
    pnbkgsmedge1.width.min = 0.01
    pnbkgsmedge1.width.max = 100
    
    pnbkgsmedge2.edgeE = 1.38826
    pnbkgsmedge2.edgeE.freeze()
    pnbkgsmedge2.MaxTau.min = 0 
    pnbkgsmedge2.MaxTau.max = 10
    pnbkgsmedge2.MaxTau = 9.37167
    pnbkgsmedge2.index = -2.67000
    pnbkgsmedge2.index.freeze()
    pnbkgsmedge2.width = 5.7642
    pnbkgsmedge2.width.min = 0.01
    pnbkgsmedge2.width.max = 100
    	
    # Spline funtion
    pnbkgspline1.Estart = 0.200000
    pnbkgspline1.Estart.freeze()
    pnbkgspline1.Ystart = -1.31506
    pnbkgspline1.Ystart.min = -1e+6
    pnbkgspline1.Ystart.max = 1e+6
    pnbkgspline1.Yend = 1064.16
    pnbkgspline1.Yend.min = -1e+6
    pnbkgspline1.Yend.max = 1e+6
    pnbkgspline1.YPstart = -106.183
    pnbkgspline1.YPstart.min = -1e+6
    pnbkgspline1.YPstart.max = 1e+6
    pnbkgspline1.YPend = -366.092
    pnbkgspline1.YPend.min = -1e+6
    pnbkgspline1.YPend.max = 1e6
    pnbkgspline1.Eend = 1.74715
    pnbkgspline1.Eend.min = 0
    pnbkgspline1.Eend.max = 100
    
    pnbkgspline2.Estart = 3.29056
    pnbkgspline2.Ystart = 1.00643
    pnbkgspline2.Ystart.min = -1e+6
    pnbkgspline2.Ystart.max = 1e+6
    pnbkgspline2.Yend = 0.887026
    pnbkgspline2.Yend.min = -1e+6
    pnbkgspline2.Yend.max = 1e+6
    pnbkgspline2.YPstart = -0.278401
    pnbkgspline2.YPstart.min = -1e+6
    pnbkgspline2.YPstart.max = 1e+6
    pnbkgspline2.YPend = 4.84809E-03
    pnbkgspline2.YPend.min = -1e+6
    pnbkgspline2.YPend.max = 1e6
    pnbkgspline2.Eend = 7.32701
    pnbkgspline2.Eend.min = 0
    pnbkgspline2.Eend.max = 100
    
    # Background power law
    pnbkginspl.PhoIndex = 0.279
    pnbkginspl.PhoIndex.min = -2
    pnbkginspl.PhoIndex.max = 9
    pnbkginspl.norm = 8.23614E-03
    pnbkginspl.norm.min = 1E-10
    pnbkginspl.norm.max = 1E6
    
    # Extragalactic background
    pnbkgpl.PhoIndex = 1.46
    pnbkgpl.PhoIndex.freeze()
    pnbkgpl.norm = 1.25288E-05
    pnbkgpl.norm.min = 1e-10
    pnbkgpl.norm.max = 1e3

    if(fit): #fit bkg 
        set_bkg_full_model(i,pnbunitrsp(pnbkgcons*(pnbkgspline1*pnbkgexpdec + pnbkgsmedge1*pnbkgsmedge2*(pnbkgspline2*pnbkginspl))))
        print('Fitting (1/8)...')
        fit_bkg(i)
        set_bkg_full_model(i,pnbunitrsp(pnbkgcons*(pnbkgspline1*pnbkgexpdec + pnbkgsmedge1*pnbkgsmedge2*(pnbkgspline2*pnbkginspl + 
					pnbkgline2))))
        print('Fitting (2/8)...')
        fit_bkg(i)
        set_bkg_full_model(i,pnbunitrsp(pnbkgcons*(pnbkgspline1*pnbkgexpdec + pnbkgsmedge1*pnbkgsmedge2*(pnbkgspline2*pnbkginspl + 
					pnbkgline1 + pnbkgline2))))
        print('Fitting (3/8)...')
        fit_bkg(i)
        set_bkg_full_model(i,pnbunitrsp(pnbkgcons*(pnbkgspline1*pnbkgexpdec + pnbkgsmedge1*pnbkgsmedge2*(pnbkgspline2*pnbkginspl + 
					pnbkgline1 + pnbkgline2 + pnbkgline7 + pnbkgline8))))
        print('Fitting (4/8)...')
        fit_bkg(i)
        set_bkg_full_model(i,pnbunitrsp(pnbkgcons*(pnbkgspline1*pnbkgexpdec + pnbkgsmedge1*pnbkgsmedge2*(pnbkgspline2*pnbkginspl + 
					pnbkgline1 + pnbkgline2 + pnbkgline7 + pnbkgline8 + pnbkgline9 + pnbkgline10))))
        print('Fitting (5/8)...')
        fit_bkg(i)
        set_bkg_full_model(i,pnbunitrsp(pnbkgcons*(pnbkgspline1*pnbkgexpdec + pnbkgsmedge1*pnbkgsmedge2*(pnbkgspline2*pnbkginspl + 
        				pnbkgline1 + pnbkgline2 + pnbkgline3 + pnbkgline4 + pnbkgline5 + pnbkgline6 + pnbkgline7 + pnbkgline8 + pnbkgline9 + 
					pnbkgline10 + pnbkgline11))))
        print('Fitting (6/8)...')
        fit_bkg(i)
        set_bkg_full_model(i,pnbunitrsp(pnbkgcons*(pnbkgspline1*pnbkgexpdec + pnbkgsmedge1*pnbkgsmedge2*(pnbkgspline2*pnbkginspl + 
					pnbkgline1 + pnbkgline2 + pnbkgline3 + pnbkgline4 + pnbkgline5 + pnbkgline6 + pnbkgline7 + pnbkgline8 + pnbkgline9 + 
					pnbkgline10 + pnbkgline11))) + pnbrsp(galabs*(pnbkgapec)))
        print('Fitting (7/8)...')
        fit_bkg(i)
        set_bkg_full_model(i,pnbunitrsp(pnbkgcons*(pnbkgspline1*pnbkgexpdec + pnbkgsmedge1*pnbkgsmedge2*(pnbkgspline2*pnbkginspl + 
					pnbkgline1 + pnbkgline2 + pnbkgline3 + pnbkgline4 + pnbkgline5 + pnbkgline6 + pnbkgline7 + pnbkgline8 + pnbkgline9 + 
					pnbkgline10 + pnbkgline11))) + pnbrsp(galabs*(pnbkgapec+pnbkgpl)))
        print('Fitting (8/8)...')
        fit_bkg(i)
        set_bkg_full_model(i,pnbunitrsp(pnbkgcons*(pnbkgspline1*pnbkgexpdec + pnbkgsmedge1*pnbkgsmedge2*(pnbkgspline2*pnbkginspl + 
					pnbkgline1 + pnbkgline2 + pnbkgline3 + pnbkgline4 + pnbkgline5 + pnbkgline6 + pnbkgline7 + pnbkgline8 + pnbkgline9 + 
					pnbkgline10 + pnbkgline11))) + pnbrsp(galabs*(pnbkgapec+pnbkgpl)+pnbkglcapec))
        fit_bkg(i)
        
        freeze(pnbkgcons, pnbkgspline1, pnbkgexpdec, pnbkgsmedge1, pnbkgsmedge2, pnbkgspline2, pnbkginspl, pnbkgline1, pnbkgline2, 
					pnbkgline3, pnbkgline4, pnbkgline5, pnbkgline6, pnbkgline7, pnbkgline8, pnbkgline9, pnbkgline10, pnbkgline11, 
					galabs, pnbkgapec, pnbkgpl, pnbkglcapec)
        print(' ')
        print('PN background model set up and fitted')
        print('Please double-check that it is a good fit')
        print(' ')
    else:
        set_bkg_full_model(i,pnbunitrsp(pnbkgcons*(pnbkgspline1*pnbkgexpdec + pnbkgsmedge1*pnbkgsmedge2*(pnbkgspline2*pnbkginspl + 
	       pnbkgline1 + pnbkgline2 + pnbkgline3 + pnbkgline4 + pnbkgline5 + pnbkgline6 + pnbkgline7 + pnbkgline8 + pnbkgline9 + 
	       pnbkgline10 + pnbkgline11))) + pnbrsp(galabs*(pnbkgapec+pnbkgpl)+pnbkglcapec))
        print(' ')
        print('PN background model set up')
        print(' ')
    return pnscale*(pnbunitrsp(pncons*(pnspline1*pnexpdec + pnsmedge1*pnsmedge2*(pnspline2*pnbkpl + 
			pngau1 + pngau2 + pngau3 + pngau4 + pngau5 + pngau6 + pngau7 + pngau8 + pngau9 + 
			pngau10 + pngau11))) + pnbrsp(galabs*(pnapec+pnpnexpl)+pnlcapec))


def get_mos_bkg_model(i, galabs, fit=False):
#=================================================================
# Parameters:
# i = sherpa ID of data set  
# galabs = name of model for galactic absorption
# fit: True = fit bkg spectrum; False = just set_bkg_full_model
# returns unit response for bkg model
#=================================================================
    #get instrument response model for bkg spectrum
    if get_rmf(i).energ_lo[0] == 0: get_rmf(i).energ_lo[0] = 0.001
    if get_arf(i).energ_lo[0] == 0: get_arf(i).energ_lo[0] = 0.001 
    mosbrsp = get_response(i,bkg_id=1)
    mosscale = get_bkg_scale(i) #get background scaling factor 

    #create unit response
    dia_mos_rmf=get_embedded_file('mos_dia.rmf')
    dia_mos_arf=get_embedded_file('mos_dia.arf')
    copy_data(i,1000+2) 	
    load_bkg_rmf(1000+2, dia_mos_rmf) #load diagonal bkg matrices
    load_bkg_arf(1000+2, dia_mos_arf)
    mosbunitrsp = get_response(1000+2, bkg_id=1)	
    delete_data(1000+2)

    #gaussian line center energy, line width, and initial normalization; for *MOS background*
    moscenters = [1.48600, 1.48700, 1.74000, 5.41000, 5.89500, 6.42000, 9.71000]
    moslinewidth = [3.84602E-02, 0.165816, 3.54985E-02, 9.77018E-02, 7.45076E-02, 7.42365E-02, 9.04855E-02]
    moslinenorm = [9.93119E-03, 1.67028E-03, 1.75461E-03, 2.86358E-04, 2.07525E-04, 3.07555E-04, 4.58115E-04]
    
    # model component prefix
    mos = 'mos%s' % i

    mosbkgcons, mosbkgsmedge, mosbkgspline, mosbkgbknpl, mosbkgline1, mosbkgline2, mosbkgline3, mosbkgline4, mosbkgline5, mosbkgline6, mosbkgline7, mosbkgpl, mosbkgapec, mosbkglcapec = (xsconstant(mos+'cons'), xssmedge(mos+'smedge'), xsspline(mos+'spline'), xsbknpower(mos+'bknpl'), xsgaussian(mos+'gau1'), xsgaussian(mos+'gau2'), xsgaussian(mos+'gau3'), xsgaussian(mos+'gau4'), xsgaussian(mos+'gau5'), xsgaussian(mos+'gau6'), xsgaussian(mos+'gau7'), xspowerlaw(mos+'expl'), xsapec(mos+'apec'), xsapec(mos+'lcapec'))

    moslines = [mosbkgline1, mosbkgline2, mosbkgline3, mosbkgline4, mosbkgline5, mosbkgline6, mosbkgline7] 
    mos_bkg = 'mos_bkg_model'  

    #define MOS background model
    mos_bkg = mosbunitrsp(mosbkgcons*mosbkgsmedge*mosbkgspline*mosbkgbknpl + mosbkgline1 + mosbkgline2 + mosbkgline3 + 
	      mosbkgline4 + mosbkgline5 + mosbkgline6 + mosbkgline7) + mosbrsp(galabs*(mosbkgpl + mosbkgapec) + mosbkglcapec)

    for l, c in zip(moslines, moscenters):
        l.LineE = c
        l.LineE.min = c - 0.05
        l.LineE.max = c + 0.05
			
    for l, s in zip(moslines, moslinewidth):
        l.Sigma = s
        l.Sigma.min = 1E-4
        l.Sigma.max = 0.2
    mosbkgline1.Sigma.min = 1E-4
    mosbkgline1.Sigma.max = 1E-1

    for l, n in zip(moslines, moslinenorm):
        l.norm = n
        l.norm.min = 1E-10
        l.norm.max = 1E10

    # Constant factor
    mosbkgcons.factor = 1.0
    mosbkgcons.factor.freeze()
    
    # Smear function
    mosbkgsmedge.edgeE = 0.538408
    mosbkgsmedge.edgeE.freeze()
    mosbkgsmedge.MaxTau = 0.246633
    mosbkgsmedge.MaxTau.min = 0.0
    mosbkgsmedge.MaxTau.max = 10.0
    mosbkgsmedge.index = -2.67
    mosbkgsmedge.index.freeze()
    mosbkgsmedge.width = 1E-02 
    mosbkgsmedge.width.min = 1E-02
    mosbkgsmedge.width.max = 1E2
    
    # Spline funtion
    mosbkgspline.Estart = 3.08175
    mosbkgspline.Ystart = 1.00984
    mosbkgspline.Yend = 1.99144
    mosbkgspline.YPstart = -2.90195e-02
    mosbkgspline.YPend = 5.49102e-02
    mosbkgspline.Estart.freeze()
    mosbkgspline.Ystart.freeze()
    mosbkgspline.Yend.freeze()
    mosbkgspline.YPstart.freeze()
    mosbkgspline.YPend.freeze()
    mosbkgspline.Eend = 13.6492
    mosbkgspline.Eend.min = 0
    mosbkgspline.Eend.max = 100
    
    # Broken power law
    mosbkgbknpl.PhoIndx1 = 1.48636
    mosbkgbknpl.PhoIndx1.min = -2
    mosbkgbknpl.PhoIndx1.max = 9
    mosbkgbknpl.BreakE = 0.415173
    mosbkgbknpl.PhoIndx2 = 0.315615
    mosbkgbknpl.BreakE.freeze()
    mosbkgbknpl.PhoIndx2.freeze()
    mosbkgbknpl.norm = 2.90071E-03
    mosbkgbknpl.norm.min = 1E-10
    mosbkgbknpl.norm.max = 1E10
     
    # Extragalactic background
    mosbkgpl.PhoIndex = 1.46
    mosbkgpl.PhoIndex.freeze()
    mosbkgpl.norm = 4.58115E-04
    mosbkgpl.norm.min = 1E-10
    mosbkgpl.norm.max = 1E10
    
    # thermal radiation
    mosbkgapec.kT = 0.286928
    mosbkgapec.kT.min = 0.008
    mosbkgapec.kT.max = 64
    mosbkgapec.Abundanc = 1.0
    mosbkgapec.Abundanc.freeze()
    mosbkgapec.Redshift = 0.0
    mosbkgapec.Redshift.freeze()
    mosbkgapec.norm = 5.58410E-05
    mosbkgapec.norm.min = 1e-10
    mosbkgapec.norm.max = 1e10
    
    # local thermal radiation
    mosbkglcapec.kT = 0.1
    mosbkglcapec.kT.freeze()
    mosbkglcapec.Abundanc = 1.0
    mosbkglcapec.Abundanc.freeze()
    mosbkglcapec.Redshift = 0.0
    mosbkglcapec.Redshift.freeze()
    mosbkglcapec.norm = 3.89164E-05
    mosbkglcapec.norm.min = 1e-10
    mosbkglcapec.norm.max = 1e10

    if(fit): #fit bkg 
        set_bkg_full_model(i,mosbunitrsp(mosbkgcons*mosbkgsmedge*mosbkgspline*mosbkgbknpl))
        print('Fitting (1/8)...')
        fit_bkg(i)
        set_bkg_full_model(i,mosbunitrsp(mosbkgcons*mosbkgsmedge*mosbkgspline*mosbkgbknpl + mosbkgline2))
        print('Fitting (2/8)...')
        fit_bkg(i)
        set_bkg_full_model(i,mosbunitrsp(mosbkgcons*mosbkgsmedge*mosbkgspline*mosbkgbknpl + mosbkgline2 + 
					mosbkgline3))
        print('Fitting (3/8)...')
        fit_bkg(i)
        set_bkg_full_model(i,mosbunitrsp(mosbkgcons*mosbkgsmedge*mosbkgspline*mosbkgbknpl + mosbkgline1 + 
					mosbkgline2 + mosbkgline3))
        print('Fitting (4/8)...')
        fit_bkg(i)
        set_bkg_full_model(i,mosbunitrsp(mosbkgcons*mosbkgsmedge*mosbkgspline*mosbkgbknpl + mosbkgline1 + 
					mosbkgline2 + mosbkgline3 + mosbkgline4 + mosbkgline5 + mosbkgline6 + mosbkgline7))
        print('Fitting (5/8)...')
        fit_bkg(i)
        set_bkg_full_model(i,mosbunitrsp(mosbkgcons*mosbkgsmedge*mosbkgspline*mosbkgbknpl + mosbkgline1 + 
					mosbkgline2 + mosbkgline3 + mosbkgline4 + mosbkgline5 + mosbkgline6 + mosbkgline7) + 
					mosbrsp(galabs*(mosbkgapec)))
        print('Fitting (6/8)...')
        fit_bkg(i)
        set_bkg_full_model(i,mosbunitrsp(mosbkgcons*mosbkgsmedge*mosbkgspline*mosbkgbknpl + mosbkgline1 + 
					mosbkgline2 + mosbkgline3 + mosbkgline4 + mosbkgline5 + mosbkgline6 + mosbkgline7) + 
					mosbrsp(galabs*(mosbkgapec+mosbkgpl)))
        print('Fitting (7/8)...')
        fit_bkg(i)
        set_bkg_full_model(i,mosbunitrsp(mosbkgcons*mosbkgsmedge*mosbkgspline*mosbkgbknpl + mosbkgline1 + 
					mosbkgline2 + mosbkgline3 + mosbkgline4 + mosbkgline5 + mosbkgline6 + mosbkgline7) + 
					mosbrsp(galabs*(mosbkgapec+mosbkgpl)+mosbkglcapec))
        print('Fitting (8/8)...')
        fit_bkg(i)
        freeze(mosbkgcons, mosbkgsmedge, mosbkgspline, mosbkgbknpl, mosbkgline1, mosbkgline2, mosbkgline3, 
					mosbkgline4, mosbkgline5, mosbkgline6, mosbkgline7, mosbkgpl, mosbkgapec, mosbkglcapec)
        print(' ')
        print('MOS background model set up and fitted')
        print('Please double-check that it is a good fit')
        print(' ')
    else:
        set_bkg_full_model(i,mosbunitrsp(mosbkgcons*mosbkgsmedge*mosbkgspline*mosbkgbknpl + mosbkgline1 + 
					mosbkgline2 + mosbkgline3 + mosbkgline4 + mosbkgline5 + mosbkgline6 + mosbkgline7) + 
					mosbrsp(galabs*(mosbkgapec+mosbkgpl)+mosbkglcapec))
        print(' ')
        print('MOS background model set up')
        print(' ')
    
    return mosscale*(mosbunitrsp(mosbkgcons*mosbkgsmedge*mosbkgspline*mosbkgbknpl + mosbkgline1 + 
        mosbkgline2 + mosbkgline3 + mosbkgline4 + mosbkgline5 + mosbkgline6 + mosbkgline7) + 
        mosbrsp(galabs*(mosbkgapec+mosbkgpl)+mosbkglcapec))
    
    #return mosscale*(mosbunitrsp(moscons*mossmedge*mosspline*mosbknpl + mosgau1 + mosgau2 + mosgau3 + 
    #    		mosgau4 + mosgau5 + mosgau6 + mosgau7) + mosbrsp(galabs*(mosapec+mosexpl)+moslcapec))

def get_mos_bkg_model_cached(i, galabs):
	filename = get_bkg(i).name + '.bkgpars'
	if os.path.exists(filename):
		bkgmodel = get_mos_bkg_model(i, galabs, fit=False)
		for p, v in zip(bkgmodel.pars, numpy.loadtxt(filename)):
			p.val = v
	else:
		bkgmodel = get_mos_bkg_model(i, galabs, fit=True)
		numpy.savetxt(filename, [p.val for p in bkgmodel.pars])
	for p in bkgmodel.pars:
		p.freeze()
	return bkgmodel
	
def get_pn_bkg_model_cached(i, galabs):
	filename = get_bkg(i).name + '.bkgpars'
	if os.path.exists(filename):
		bkgmodel = get_pn_bkg_model(i, galabs, fit=False)
		for p, v in zip(bkgmodel.pars, numpy.loadtxt(filename)):
			p.val = v
	else:
		bkgmodel = get_pn_bkg_model(i, galabs, fit=True)
		numpy.savetxt(filename, [p.val for p in bkgmodel.pars])
	for p in bkgmodel.pars:
		p.freeze()
	return bkgmodel
