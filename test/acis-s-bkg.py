#set_bkg_model("xsconstant.bkg_mdl_c1*(polynom1d.bkg_mdl_p1+gauss1d.bkg_mdl_g1+gauss1d.bkg_mdl_g2+gauss1d.bkg_mdl_g3+gauss1d.bkg_mdl_g4+gauss1d.bkg_mdl_g5+gauss1d.bkg_mdl_g6)")

set_bkg_model("polynom1d.bkg_mdl_p1+gauss1d.bkg_mdl_g1+gauss1d.bkg_mdl_g2+gauss1d.bkg_mdl_g3+gauss1d.bkg_mdl_g4+gauss1d.bkg_mdl_g5+gauss1d.bkg_mdl_g6")

set_par(bkg_mdl_p1.c0,0.000107813,-6.41459e-05,0.00190619)
#bkg_mdl_p1.c0.min = -6.41459e-05
#bkg_mdl_p1.c0.max = 0.00190619
#bkg_mdl_p1.c0 = 0.000107813

set_par(bkg_mdl_p1.c1,2.33656e-05,-0.0192035, 0.0192035)
#bkg_mdl_p1.c1.min = -0.0192035
#bkg_mdl_p1.c1.max = 0.0192035
#bkg_mdl_p1.c1  = 2.33656e-05

set_par(bkg_mdl_p1.c2,9.10151e-06,-0.002002,0.002002)
#bkg_mdl_p1.c2.min = -0.002002
#bkg_mdl_p1.c2.max = 0.002002
#bkg_mdl_p1.c2 = 9.10151e-06

set_par(bkg_mdl_p1.c3, 1.41672e-05,-6.41459e-05,0.00190619)
#bkg_mdl_p1.c3.min = -6.41459e-05
#bkg_mdl_p1.c3.max = 0.00190619
#bkg_mdl_p1.c3 = 1.41672e-05

set_par(bkg_mdl_p1.c4,1.17789e-05, -6.41459e-05,0.00190619)
#bkg_mdl_p1.c4.min = -6.41459e-05
#bkg_mdl_p1.c4.max = 0.00190619
#bkg_mdl_p1.c4 = 1.17789e-05

set_par(bkg_mdl_p1.c5, 1.53256e-06,-6.41459e-05,0.00190619)
#bkg_mdl_p1.c5.min = -6.41459e-05
#bkg_mdl_p1.c5.max = 0.00190619
#bkg_mdl_p1.c5 = 1.53256e-06

set_par(bkg_mdl_p1.c6, -2.72514e-07,-6.41459e-05,0.00190619)
#bkg_mdl_p1.c6.min = -6.41459e-05
#bkg_mdl_p1.c6.max = 0.00190619
#bkg_mdl_p1.c6 = -2.72514e-07

set_par(bkg_mdl_p1.c7, 1.21828e-07,-6.41459e-05,0.00190619)
#bkg_mdl_p1.c7.min = -6.41459e-05
#bkg_mdl_p1.c7.max = 0.00190619
#bkg_mdl_p1.c7 = 1.21828e-07

set_par(bkg_mdl_p1.c8, 3.88227e-08,-6.41459e-05,0.00190619)
#bkg_mdl_p1.c8.min = -6.41459e-05
#bkg_mdl_p1.c8.max = 0.00190619
#bkg_mdl_p1.c8 = 3.88227e-08

set_par(bkg_mdl_p1.offset, 5,-0.4015,9.9937)
#bkg_mdl_p1.offset.min = -0.4015
#bkg_mdl_p1.offset.max = 9.9937
#bkg_mdl_p1.offset = 5
freeze("bkg_mdl_p1")

set_par(bkg_mdl_g1.fwhm, 0.01,0.001, 345.157)
#bkg_mdl_g1.fwhm.min = 0.001
#bkg_mdl_g1.fwhm.max = 345.157
#bkg_mdl_g1.fwhm = 0.01

set_par(bkg_mdl_g1.pos, 0.574495,0.4015,9.9937)
#bkg_mdl_g1.pos.min = 0.4015
#bkg_mdl_g1.pos.max = 9.9937
#bkg_mdl_g1.pos = 0.574495

set_par(bkg_mdl_g1.ampl, 0.00301839,1.90619e-05,0.190619)
#bkg_mdl_g1.ampl.min = 1.90619e-05
#bkg_mdl_g1.ampl.max = 0.190619
#bkg_mdl_g1.ampl = 0.00301839
freeze("bkg_mdl_g1")


#bkg_mdl_g2.fwhm.min = 0.01
#bkg_mdl_g2.fwhm.max = 345.157
bkg_mdl_g2.fwhm = 0.0317183
#bkg_mdl_g2.pos.min = 0.4015
#bkg_mdl_g2.pos.max = 9.9937
bkg_mdl_g2.pos = 1.7752
#bkg_mdl_g2.ampl.min = 1.90619e-05
#bkg_mdl_g2.ampl.max = 0.190619
bkg_mdl_g2.ampl = 0.000594304
freeze("bkg_mdl_g2")

#bkg_mdl_g3.fwhm.min = 0.0345157
#bkg_mdl_g3.fwhm.max = 345.157
bkg_mdl_g3.fwhm = 0.0864722
#bkg_mdl_g3.pos.min = 0.4015
#bkg_mdl_g3.pos.max = 9.9937
bkg_mdl_g3.pos = 2.15107
#bkg_mdl_g3.ampl.min = 1.90619e-05
#bkg_mdl_g3.ampl.max = 0.190619
bkg_mdl_g3.ampl = 0.000349747
freeze("bkg_mdl_g3")

#bkg_mdl_g4.fwhm.min = 0.0345157
#bkg_mdl_g4.fwhm.max = 345.157
bkg_mdl_g4.fwhm = 0.1
#bkg_mdl_g4.pos.min = 0.4015
#bkg_mdl_g4.pos.max = 9.9937
bkg_mdl_g4.pos = 7.5
#bkg_mdl_g4.ampl.min = 1.90619e-05
#bkg_mdl_g4.ampl.max = 0.190619
bkg_mdl_g4.ampl = 0.000756713
freeze("bkg_mdl_g4")

#bkg_mdl_g5.fwhm.min = 0.0345157
#bkg_mdl_g5.fwhm.max = 345.157
bkg_mdl_g5.fwhm = 0.1
#bkg_mdl_g5.pos.min = 0.4015
#bkg_mdl_g5.pos.max = 9.9937
bkg_mdl_g5.pos = 9.6
#bkg_mdl_g5.ampl.min = 1.90619e-05
#bkg_mdl_g5.ampl.max = 0.190619
bkg_mdl_g5.ampl = 0.00147212
freeze("bkg_mdl_g5")

#bkg_mdl_g6.fwhm.min = 0.0345157
#bkg_mdl_g6.fwhm.max = 345.157
bkg_mdl_g6.fwhm = 0.180799
#bkg_mdl_g6.pos.min = 0.4015
#bkg_mdl_g6.pos.max = 9.9937
bkg_mdl_g6.pos = 1.32209
#bkg_mdl_g6.ampl.min = 0
#bkg_mdl_g6.ampl.max = 0.190619
bkg_mdl_g6.ampl = 1.88427e-05
freeze("bkg_mdl_g6")
