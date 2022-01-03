Obscured Active Galactic Nuclei
=======================================

A script for fitting Active Galactic Nuclei is provided at
`xagnfitter.py <https://github.com/JohannesBuchner/BXA/blob/master/examples/sherpa/xagnfitter.py>`_.
This is the method used in Buchner+14, Buchner+15, Simmonds+17.

Features:

* Maximum information extraction in the low count regime, by Bayesian inference and background models.
* Provides robust uncertainty estimation of all parameters, including the

  * obscuring column density NH
  * Photon index Gamma
  * rest-frame, intrinsic accretion luminosity
  * etc.

* Redshift can be fixed, unknown or come from a probability distribution (photo-z)
* Realistic nuclear obscurer model (UXCLUMPY) that 

  * extends to the highest, Compton-thick column densities
  * is clumpy; does not confuse the line-of-sight inclination and viewing angle parameters
  * fits objects in the local Universe well

* Corrects for galactic absorption
* Optional: add an apec :math:`L<10^{42}` erg/s contamination component (set WITHAPEC=1)
* Can fit multiple observations simultaneously

I strongly recommend using the `xagnfitter <https://github.com/JohannesBuchner/BXA/blob/master/examples/sherpa/xagnfitter.py>`_
script instead of hardness ratios.

xagnfitter.py script
--------------------

It is included verbatim below:

.. literalinclude:: ../examples/sherpa/xagnfitter.py

Example run
--------------------

You can try running this against the AGN spectrum provided in the examples/sherpa/chandra/ folder.

The output should look something like this::

    $ WITHAPEC=0 MODELDIR=$HOME/Downloads/specmodels/ python3 ../xagnfitter.py 
    read ARF file cdfs4Ms_179.arf
    [sherpa.astro.io INFO]: read ARF file cdfs4Ms_179.arf
    read RMF file cdfs4Ms_179.rmf
    [sherpa.astro.io INFO]: read RMF file cdfs4Ms_179.rmf
    read ARF (background) file cdfs4Ms_179.arf
    [sherpa.astro.io INFO]: read ARF (background) file cdfs4Ms_179.arf
    read RMF (background) file cdfs4Ms_179.rmf
    [sherpa.astro.io INFO]: read RMF (background) file cdfs4Ms_179.rmf
    read background file cdfs4Ms_179_bkg.pi
    [sherpa.astro.io INFO]: read background file cdfs4Ms_179_bkg.pi
     Solar Abundance Vector set to wilm:  Wilms, J., Allen, A. & McCray, R. ApJ 542 914 (2000) (abundances are set to zero for those elements not included in the paper).
     Cross Section Table set to vern:  Verner, Ferland, Korista, and Yakovlev 1996
    loading nH from 179.pi.nh (expecting something like 1e21 in there)
    setting galactic nH to 0.0088 [units of 1e22/cm²]
    combining components
    linking parameters
    setting redshift
    creating priors
    setting source and background model ...
    [bxa.Fitter INFO]: PCAFitter(for ID=1)
    [bxa.Fitter INFO]: loading PCA information from /home/user/bin/ciao-4.13/ots/lib/python3.7/site-packages/bxa/sherpa/background/chandra_1024.json
    [bxa.Fitter INFO]: fitting background of ID=1 using PCA method
    [bxa.Fitter INFO]: have 2521 background counts for deconvolution
    [bxa.Fitter INFO]: fit: initial PCA decomposition: [ 3.40159007e+00 -6.29801294e-04  1.15351627e-02  8.72323308e-03
      7.12865031e-03 -8.44044155e-03 -4.73346905e-03  5.83916607e-04
     -4.79908423e-04 -9.18585670e-04 -1.87723042e-04]
    [bxa.Fitter INFO]: fit: first full fit done
    [bxa.Fitter INFO]: fit: parameters: [-0.24972366790501033, 0.1237617574156954, 1.619517445974407, -0.3466035071997995, -0.7134659455645368, 1.364537126802302, 0.10510218498377895, -0.41467820359992413, 0.9144121142234537, -1.144703704590311, -2.4736204436412694]
    tbvabs Version 2.3
    Cosmic absorption with grains and H2, modified from
    Wilms, Allen, & McCray, 2000, ApJ 542, 914-924
    Questions: Joern Wilms
    joern.wilms@sternwarte.uni-erlangen.de
    joern.wilms@fau.de

    http://pulsar.sternwarte.uni-erlangen.de/wilms/research/tbabs/

    PLEASE NOTICE:
    To get the model described by the above paper
    you will also have to set the abundances:
       abund wilm

    Note that this routine ignores the current cross section setting
    as it always HAS to use the Verner cross sections as a baseline.
    [bxa.Fitter INFO]: fit: stat: 2512.626888813398
    [bxa.Fitter INFO]: fit: second full fit from zero
    [bxa.Fitter INFO]: fit: parameters: [-0.24972366790501033, 0.1237617574156954, 1.619517445974407, -0.3466035071997995, -0.7134659455645368, 1.364537126802302, 0.10510218498377895, -0.41467820359992413, 0.9144121142234537, -1.144703704590311, -2.4736204436412694]
    [bxa.Fitter INFO]: fit: stat: 2512.421580816705
    [bxa.Fitter INFO]: fit: using zero-fit
    11 parameters, stat=2512.42
    --> 10 parameters, stat=2521.66
    --> 9 parameters, stat=2535.61
    --> 8 parameters, stat=2541.22
    --> 7 parameters, stat=2544.23
    --> 6 parameters, stat=2547.09
    --> 5 parameters, stat=2656.04
    --> 4 parameters, stat=2723.56
    --> 3 parameters, stat=2796.09
    --> 2 parameters, stat=2798.28
    --> 1 parameters, stat=5724.59

    Background PCA fitting AIC results:
    -----------------------------------

    stat Ncomp AIC
    5724.6  1 5726.6
    2798.3  2 2802.3
    2796.1  3 2802.1
    2723.6  4 2731.6
    2656.0  5 2666.0
    2547.1  6 2559.1
    2544.2  7 2558.2
    2541.2  8 2557.2
    2535.6  9 2553.6
    2521.7 10 2541.7
    2512.4 11 2534.4

    Increasing parameters again...
    Final choice: 11 parameters, aic=2534.42

    Adding Gaussian#1
    largest remaining discrepancy at 7.643keV[489], need 5 counts
    placing gaussian at 7.64keV, with power 9.18976317187143e-05
    with Gaussian: 2540.1578140930155 ; change: 5.7 (negative is good)
    not significant, rejecting
    running BXA ...
    [ultranest] Sampling 400 live points from prior ...
    [ultranest INFO]: Sampling 400 live points from prior ...


    Mono-modal Volume: ~exp(-3.81) * Expected Volume: exp(0.00) Quality: ok

    src.level       :      -8.0|************************************** ******************************************|     +3.0
    torus.phoindex  :      +1.2|            +1.6  ** ************************************  +2.3                  |     +2.8
    src.nH          :     +20.0|*********************************************************************************|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :      -2.2|********** ******************************************* **************************|     +1.8

    Z=-4e+08(0.00%) | Like=-3.8e+08..-2.2e+03 [-2.967e+11..-2604] | it/evals=80/490 eff=88.8889% N=400 

    Mono-modal Volume: ~exp(-3.81)   Expected Volume: exp(-0.23) Quality: ok

    src.level       :      -8.0|**************************************************************** ******* **      |     +3.0
    torus.phoindex  :      +1.2|           +1.5  *** ****************************** *****  +2.3                  |     +2.8
    src.nH          :     +20.0|*********************************************************************************|    +26.0
    src.softscatnorm:      -7.0|******************************************************** ************************|     -1.0
    pca1.lognorm    :      -2.2|******************** ********************************* ******************** *****|     +1.8

    Z=-9978548.5(0.00%) | Like=-9923310.86..-2028.74 [-2.967e+11..-2604] | it/evals=160/596 eff=81.6327% N=400 0 

    Mono-modal Volume: ~exp(-3.81)   Expected Volume: exp(-0.45) Quality: ok

    src.level       :      -8.0|*********************************************************** ****  +0.6           |     +3.0
    torus.phoindex  :      +1.2|            +1.6  ** ****************************** *****  +2.3                  |     +2.8
    src.nH          :     +20.0|*********************************************************************************|    +26.0
    src.softscatnorm:      -7.0| ******************************************************* ************************|     -1.0
    pca1.lognorm    :      -2.2|**************************************************** ****************************|     +1.8

    Z=-594817.6(0.00%) | Like=-586915.40..-2028.74 [-2.967e+11..-2604] | it/evals=265/765 eff=72.6027% N=400 0 

    Mono-modal Volume: ~exp(-4.47) * Expected Volume: exp(-0.67) Quality: ok

    src.level       :      -8.0|************************************************* *****  -0.6                    |     +3.0
    torus.phoindex  :      +1.2|            +1.6  ** ****************************** *****  +2.3                  |     +2.8
    src.nH          :     +20.0|********* ***********************************************************************|    +26.0
    src.softscatnorm:      -7.0|**************************************** ****************************************|     -1.0
    pca1.lognorm    :      -2.2|**************************************************** ************************    |     +1.8

    Z=-173190.1(0.00%) | Like=-160428.37..-2028.74 [-2.967e+11..-2604] | it/evals=353/918 eff=68.1467% N=400 

    Mono-modal Volume: ~exp(-4.72) * Expected Volume: exp(-0.90) Quality: ok

    src.level       :      -8.0|********************************************** ** *  -1.1                        |     +3.0
    torus.phoindex  :      +1.2|            +1.6  ** * **************************** *****  +2.3                  |     +2.8
    src.nH          :     +20.0|*********************************************************************************|    +26.0
    src.softscatnorm:      -7.0|**************************************** ** *********************** *************|     -1.0
    pca1.lognorm    :      -2.2|********************************************************************  +1.1       |     +1.8

    Z=-59053.5(0.00%) | Like=-58881.01..-2028.74 [-2.967e+11..-2604] | it/evals=440/1072 eff=65.4762% N=400  

    Mono-modal Volume: ~exp(-4.99) * Expected Volume: exp(-1.12) Quality: ok

    src.level       :      -8.0|**********************************************  -1.8                             |     +3.0
    torus.phoindex  :      +1.2|            +1.6  *  ****************************** *****  +2.3                  |     +2.8
    src.nH          :     +20.0|**** *********************************************** ****************************|    +26.0
    src.softscatnorm:      -7.0|******************************************************************* *************|     -1.0
    pca1.lognorm    :      -2.2|************************************************************  +0.7               |     +1.8

    Z=-35508.0(0.00%) | Like=-35436.48..-2028.74 [-2.967e+11..-2604] | it/evals=520/1218 eff=63.5697% N=400 

    Mono-modal Volume: ~exp(-4.99)   Expected Volume: exp(-1.35) Quality: ok

    src.level       :      -8.0|*********************************************  -1.9                              |     +3.0
    torus.phoindex  :      +1.2|            +1.6  ** ****************************** ** **  +2.3                  |     +2.8
    src.nH          :     +20.0|*********************************************************************************|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :      -2.2|*********************************************************  +0.6                  |     +1.8

    Z=-25985.5(0.00%) | Like=-25963.87..-2028.74 [-2.967e+11..-2604] | it/evals=626/1443 eff=60.0192% N=400 

    Mono-modal Volume: ~exp(-4.99)   Expected Volume: exp(-1.57) Quality: ok

    src.level       :      -8.0|******************************************** *  -1.8                             |     +3.0
    torus.phoindex  :      +1.2|            +1.6  ** ***********************************  +2.3                   |     +2.8
    src.nH          :     +20.0|*********************************************************************************|    +26.0
    src.softscatnorm:      -7.0|***************************************************************** ***************|     -1.0
    pca1.lognorm    :      -2.2|        ** *********************************************  +0.5                   |     +1.8

    Z=-19777.5(0.00%) | Like=-19690.19..-2028.74 [-2.967e+11..-2604] | it/evals=714/1689 eff=55.3918% N=400 

    Mono-modal Volume: ~exp(-4.99)   Expected Volume: exp(-1.80) Quality: ok

    src.level       :      -8.0|********************************************  -2.1                               |     +3.0
    torus.phoindex  :      +1.2|            +1.6  *  ******************************* ***  +2.3                   |     +2.8
    src.nH          :     +20.0|*************************************************************************** *****|    +26.0
    src.softscatnorm:      -7.0|********************************************************* ***********************|     -1.0
    pca1.lognorm    :      -2.2|         -1.4  ***************************************  +0.4                     |     +1.8

    Z=-15401.1(0.00%) | Like=-15359.21..-1674.24 [-2.967e+11..-2604] | it/evals=800/1903 eff=53.2269% N=400 

    Mono-modal Volume: ~exp(-5.44) * Expected Volume: exp(-2.02) Quality: ok

    src.level       :      -8.0|***************************************** **  -2.1                               |     +3.0
    torus.phoindex  :      +1.2|            +1.6  *  ******************************* ***  +2.3                   |     +2.8
    src.nH          :     +20.0|*************************************************************************** *****|    +26.0
    src.softscatnorm:      -7.0|********************************************************* ******* ***************|     -1.0
    pca1.lognorm    :      -2.2|            -1.3  * *********************************  +0.4                      |     +1.8

    Z=-12325.4(0.00%) | Like=-12258.25..-1674.24 [-2.967e+11..-2604] | it/evals=880/2085 eff=52.2255% N=400 

    Mono-modal Volume: ~exp(-5.59) * Expected Volume: exp(-2.25) Quality: ok

    src.level       :      -8.0|***************************************** *  -2.2                                |     +3.0
    torus.phoindex  :      +1.2|            +1.6  *  ******************************* ***  +2.3                   |     +2.8
    src.nH          :     +20.0|*********************************************************************************|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :      -2.2|                -1.1  *****************************  +0.3                        |     +1.8

    Z=-9408.8(0.00%) | Like=-9399.06..-1674.24 [-2.967e+11..-2604] | it/evals=988/2343 eff=50.8492% N=400 0 

    Mono-modal Volume: ~exp(-6.22) * Expected Volume: exp(-2.47) Quality: ok

    src.level       :      -8.0|*****************************************  -2.4                                  |     +3.0
    torus.phoindex  :      +1.2|               +1.6  ***********************************  +2.3                   |     +2.8
    src.nH          :     +20.0|*********************************************************************************|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :      -1.0|   ** ********************************************  +0.2                         |     +1.0

    Z=-7834.1(0.00%) | Like=-7815.01..-1674.24 [-2.967e+11..-2604] | it/evals=1069/2510 eff=50.6635% N=400 

    Mono-modal Volume: ~exp(-6.25) * Expected Volume: exp(-2.70) Quality: ok

    src.level       :      -8.0|*****************************************  -2.4                                  |     +3.0
    torus.phoindex  :      +1.2|            +1.6  *  ***********************************  *  +2.4                |     +2.8
    src.nH          :     +20.0|************************** ******************************************************|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :      -1.0|        * ***************************************  +0.2                          |     +1.0

    Z=-6716.3(0.00%) | Like=-6695.76..-1674.24 [-2.967e+11..-2604] | it/evals=1160/2702 eff=50.3910% N=400 

    Mono-modal Volume: ~exp(-6.25)   Expected Volume: exp(-2.92) Quality: ok

    src.level       :      -8.0|*****************************************  -2.4                                  |     +3.0
    torus.phoindex  :      +1.2|            +1.6  ** ************************************ **  +2.4               |     +2.8
    src.nH          :     +20.0|* ************************ ******************************************************|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :      -1.0|          * ************************************  +0.2                           |     +1.0

    Z=-6084.1(0.00%) | Like=-6075.22..-1666.27 [-2.967e+11..-2604] | it/evals=1240/2898 eff=49.6397% N=400 

    Mono-modal Volume: ~exp(-6.62) * Expected Volume: exp(-3.15) Quality: ok

    src.level       :      -8.0|*****************************************  -2.4                                  |     +3.0
    torus.phoindex  :      +1.2|           +1.5  **************************************** **  +2.4               |     +2.8
    src.nH          :     +20.0|* *******************************************************************************|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :      -1.0|       -0.7  **********************************  +0.1                            |     +1.0

    Z=-5625.1(0.00%) | Like=-5603.01..-1666.27 [-2.967e+11..-2604] | it/evals=1338/3177 eff=48.1815% N=400 

    Mono-modal Volume: ~exp(-6.62)   Expected Volume: exp(-3.37) Quality: ok

    src.level       :      -8.0|*****************************************  -2.5                                  |     +3.0
    torus.phoindex  :      +1.2|           +1.5  *** ************************************ **  +2.4               |     +2.8
    src.nH          :     +20.0|*********************************************************************************|    +26.0
    src.softscatnorm:      -7.0|******************** ******** ********************************** ****************|     -1.0
    pca1.lognorm    :      -1.0|      -0.7  * *********************************  +0.1                            |     +1.0

    Z=-5348.2(0.00%) | Like=-5337.89..-1666.27 [-2.967e+11..-2604] | it/evals=1435/3538 eff=45.7298% N=400 

    Mono-modal Volume: ~exp(-6.62)   Expected Volume: exp(-3.60) Quality: ok

    src.level       :      -8.0|  **** **********************************  -2.5                                  |     +3.0
    torus.phoindex  :      +1.2|           +1.5  *** ************************************ **  +2.4               |     +2.8
    src.nH          :     +20.0|****************************************** **************************************|    +26.0
    src.softscatnorm:      -7.0|**************************************************************** ****************|     -1.0
    pca1.lognorm    :      -1.0|        -0.6  ********************************  +0.1                             |     +1.0

    Z=-5057.7(0.00%) | Like=-5041.99..-1664.55 [-2.967e+11..-2604] | it/evals=1520/3827 eff=44.3537% N=400 

    Mono-modal Volume: ~exp(-6.80) * Expected Volume: exp(-3.82) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.79
    src.level       :      -8.0|       **********************************  -2.5                                  |     +3.0
    torus.phoindex  :      +1.2|           +1.5  *** ************************************ **  +2.4               |     +2.8
    src.nH          :     +20.0|*********************************************************************************|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :      -1.0|         -0.6  *******************************  +0.1                             |     +1.0

    Z=-4648.4(0.00%) | Like=-4631.08..-1664.55 [-2.967e+11..-2604] | it/evals=1600/4128 eff=42.9185% N=400 

    Mono-modal Volume: ~exp(-6.80)   Expected Volume: exp(-4.05) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.82
    src.level       :      -8.0|         *******************************  -2.6                                   |     +3.0
    torus.phoindex  :      +1.2|           +1.5  ************************************ ** **  +2.4                |     +2.8
    src.nH          :     +20.0|*********************************************************************************|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :     -1.00|        -0.61  * ****************************  +0.10                             |    +1.00

    Z=-4286.3(0.00%) | Like=-4268.66..-1664.55 [-2.967e+11..-2604] | it/evals=1700/4431 eff=42.1732% N=400 

    Mono-modal Volume: ~exp(-6.95) * Expected Volume: exp(-4.27) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.84
    src.level       :      -8.0|     -6.4  ******************************  -2.5                                  |     +3.0
    torus.phoindex  :      +1.2|           +1.5  ************************************ ** **  +2.4                |     +2.8
    src.nH          :     +20.0|*********************************************************************************|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :     -1.00|         -0.58  * **************************  +0.08                              |    +1.00

    Z=-3849.9(0.00%) | Like=-3839.24..-1664.55 [-2.967e+11..-2604] | it/evals=1796/4792 eff=40.8925% N=400 

    Mono-modal Volume: ~exp(-6.95)   Expected Volume: exp(-4.50) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.84
    src.level       :      -8.0|       -6.2  ****************************  -2.5                                  |     +3.0
    torus.phoindex  :      +1.2|           +1.5  ************************************ ** **  +2.4                |     +2.8
    src.nH          :     +20.0|*********************************************************** *********************|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :     -1.00|           -0.53  **************************  +0.07                              |    +1.00

    Z=-3599.9(0.00%) | Like=-3588.20..-1664.55 [-2.967e+11..-2604] | it/evals=1880/5224 eff=38.9718% N=400 

    Mono-modal Volume: ~exp(-6.95)   Expected Volume: exp(-4.73) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.83
    src.level       :      -8.0|       -6.2  ****************************  -2.5                                  |     +3.0
    torus.phoindex  :      +1.2|           +1.5  ************************************ ** **  +2.4                |     +2.8
    src.nH          :     +20.0|**************************************************** ****************************|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :     -1.00|            -0.52  ************************  +0.06                               |    +1.00

    Z=-3331.9(0.00%) | Like=-3317.44..-1664.55 [-2.967e+11..-2604] | it/evals=1971/5680 eff=37.3295% N=400 

    Mono-modal Volume: ~exp(-6.95)   Expected Volume: exp(-4.95) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.82
    src.level       :      -8.0|      -6.2  ****************************  -2.7                                   |     +3.0
    torus.phoindex  :      +1.2|           +1.5  ************************************ **  +2.3                   |     +2.8
    src.nH          :     +20.0|*********************************************  ****  ****************************|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :     -1.00|              -0.48  *********************  +0.03                                |    +1.00

    Z=-3126.5(0.00%) | Like=-3115.87..-1587.90 [-2.967e+11..-2604] | it/evals=2063/6274 eff=35.1209% N=400 

    Mono-modal Volume: ~exp(-8.08) * Expected Volume: exp(-5.18) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.82
    src.level       :      -8.0|        -6.1  **************************  -2.7                                   |     +3.0
    torus.phoindex  :      +1.2|           +1.5  ***************************************  +2.3                   |     +2.8
    src.nH          :     +20.0|******************************************* * *** *  ** ****************** ******|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :     -1.00|              -0.47  *********************  +0.02                                |    +1.00

    Z=-2950.6(0.00%) | Like=-2939.53..-1587.90 [-2.967e+11..-2604] | it/evals=2147/6645 eff=34.3795% N=400 

    Mono-modal Volume: ~exp(-8.08)   Expected Volume: exp(-5.40) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.83
    src.level       :      -8.0|         -5.9  *************************  -2.7                                   |     +3.0
    torus.phoindex  :      +1.2|            +1.6  **************************************    *  +2.4              |     +2.8
    src.nH          :     +20.0|******************************************  * *** *   * *** *********************|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :    -1.000|             -0.461  ********************  +0.004                                |   +1.000

    Z=-2743.1(0.00%) | Like=-2730.97..-1587.90 [-2.967e+11..-2604] | it/evals=2240/7157 eff=33.1508% N=400 

    Mono-modal Volume: ~exp(-8.08)   Expected Volume: exp(-5.63) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.82
    src.level       :      -8.0|         -5.8  ************* ************  -2.5                                  |     +3.0
    torus.phoindex  :      +1.2|            +1.6  ***************************************   *  +2.4              |     +2.8
    src.nH          :     +20.0|******************************************     *      * *** *********************|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :     -1.00|                -0.43  *****************  -0.01                                  |    +1.00

    Z=-2613.0(0.00%) | Like=-2600.30..-1587.90 [-2603.9145..-1664.5521] | it/evals=2331/7782 eff=31.5768% N=400 

    Mono-modal Volume: ~exp(-8.89) * Expected Volume: exp(-5.85) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.80
    src.level       :      -8.0|          -5.8  *************************  -2.5                                  |     +3.0
    torus.phoindex  :      +1.2|            +1.6  ***************************************   *  +2.4              |     +2.8
    src.nH          :     +20.0|**************************************** *            ***** *********** *********|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :     -1.00|                -0.43  *****************  -0.01                                  |    +1.00

    Z=-2470.2(0.00%) | Like=-2457.99..-1587.90 [-2603.9145..-1664.5521] | it/evals=2427/8467 eff=30.0855% N=400 

    Mono-modal Volume: ~exp(-8.89)   Expected Volume: exp(-6.08) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.80
    src.level       :      -8.0|          -5.8  ************ ************  -2.5                                  |     +3.0
    torus.phoindex  :      +1.2|         +1.5  ** ***************************************   *  +2.4              |     +2.8
    src.nH          :     +20.0|******************************************            * *************** *** *****|    +26.0
    src.softscatnorm:      -7.0|******************* ** **********************************************************|     -1.0
    pca1.lognorm    :     -1.00|                 -0.39  ****************  -0.03                                  |    +1.00

    Z=-2374.8(0.00%) | Like=-2362.86..-1587.90 [-2603.9145..-1664.5521] | it/evals=2512/9047 eff=29.0505% N=400 

    Mono-modal Volume: ~exp(-8.89)   Expected Volume: exp(-6.30) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.84
    src.level       :      -8.0|          -5.8  ************ **********  -2.7                                    |     +3.0
    torus.phoindex  :      +1.2|         +1.5  ** **************************************    *  +2.4              |     +2.8
    src.nH          :     +20.0|**************************************** *              *************** *********|    +26.0
    src.softscatnorm:      -7.0|************* *************************************************** ***************|     -1.0
    pca1.lognorm    :     -1.00|                 -0.39  ***************  -0.04                                   |    +1.00

    Z=-2292.2(0.00%) | Like=-2280.42..-1587.90 [-2603.9145..-1664.5521] | it/evals=2609/9756 eff=27.8858% N=400 

    Mono-modal Volume: ~exp(-8.89)   Expected Volume: exp(-6.53) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.84
    src.level       :      -8.0|          -5.8  ************ *********  -2.9                                     |     +3.0
    torus.phoindex  :      +1.2|        +1.5  *** ********************************  ****  +2.3                   |     +2.8
    src.nH          :     +20.0|****************************************                *************************|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :     -1.00|                  -0.38  **************  -0.04                                   |    +1.00

    Z=-2213.4(0.00%) | Like=-2200.91..-1587.90 [-2603.9145..-1664.5521] | it/evals=2699/10432 eff=26.9039% N=400 

    Mono-modal Volume: ~exp(-8.89)   Expected Volume: exp(-6.75) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.85
    src.level       :      -8.0|          -5.8  ************ *********  -2.9                                     |     +3.0
    torus.phoindex  :      +1.2|        +1.5  *** ******************************** *** *  +2.3                   |     +2.8
    src.nH          :     +20.0|****************************************                * ********* *** *********|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :     -1.00|                  -0.37  **************  -0.05                                   |    +1.00

    Z=-2154.3(0.00%) | Like=-2142.24..-1587.90 [-2603.9145..-1664.5521] | it/evals=2777/11170 eff=25.7846% N=400 

    Mono-modal Volume: ~exp(-8.89)   Expected Volume: exp(-6.98) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.87
    src.level       :      -8.0|          -5.8  ************ *********  -2.9                                     |     +3.0
    torus.phoindex  :      +1.2|         +1.5  ****** ******************************** **  +2.3                  |     +2.8
    src.nH          :     +20.0|****************************************                ************ ** *********|    +26.0
    src.softscatnorm:      -7.0|********************** ****************************************** ***************|     -1.0
    pca1.lognorm    :     -1.00|                   -0.36  *************  -0.06                                   |    +1.00

    Z=-2087.4(0.00%) | Like=-2074.70..-1587.90 [-2603.9145..-1664.5521] | it/evals=2876/12296 eff=24.1762% N=400 

    Mono-modal Volume: ~exp(-9.84) * Expected Volume: exp(-7.20) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.87
    src.level       :      -8.0|           -5.7  **********  *********  -2.9                                     |     +3.0
    torus.phoindex  :      +1.2|         +1.5  ************************************* * **  +2.3                  |     +2.8
    src.nH          :     +20.0| ********* ****************************                 ******* **** ************|    +26.0
    src.softscatnorm:      -7.0|********************** **********************************************************|     -1.0
    pca1.lognorm    :     -1.00|                   -0.35  ************  -0.06                                    |    +1.00

    Z=-2028.9(0.00%) | Like=-2016.01..-1587.90 [-2603.9145..-1664.5521] | it/evals=2960/13307 eff=22.9333% N=400 

    Mono-modal Volume: ~exp(-9.84)   Expected Volume: exp(-7.43) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.86
    src.level       :      -8.0|           -5.6  **********  *********  -2.9                                     |     +3.0
    torus.phoindex  :      +1.2|         +1.5  ****** ****************************** * **  +2.3                  |     +2.8
    src.nH          :     +20.0| ***** *** ****************************               *** ********** ************|    +26.0
    src.softscatnorm:      -7.0|********************** ********************************** ***********************|     -1.0
    pca1.lognorm    :     -1.00|                   -0.34  ************  -0.08                                    |    +1.00

    Z=-1985.8(0.00%) | Like=-1973.22..-1575.73 [-2603.9145..-1664.5521] | it/evals=3054/14321 eff=21.9381% N=400 

    Mono-modal Volume: ~exp(-9.84)   Expected Volume: exp(-7.65) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.82
    src.level       :      -8.0|           -5.6  *********   *********  -2.9                                     |     +3.0
    torus.phoindex  :      +1.2|         +1.5  *************************************** ***  +2.3                 |     +2.8
    src.nH          :     +20.0|  ** * * ** **** *********************                 ** ************ **********|    +26.0
    src.softscatnorm:      -7.0|********************** **********************************************************|     -1.0
    pca1.lognorm    :     -1.00|                   -0.34  ************  -0.08                                    |    +1.00

    Z=-1950.5(0.00%) | Like=-1938.08..-1575.73 [-2603.9145..-1664.5521] | it/evals=3139/15245 eff=21.1452% N=400 

    Mono-modal Volume: ~exp(-9.84)   Expected Volume: exp(-7.88) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.82
    src.level       :      -8.0|           -5.6  *********   *********  -2.9                                     |     +3.0
    torus.phoindex  :      +1.2|         +1.5  *************************************** ***  +2.3                 |     +2.8
    src.nH          :     +20.0| *** *        ************************                 ** ******** *** ******  **|    +26.0
    src.softscatnorm:      -7.0|********************** **********************************************************|     -1.0
    pca1.lognorm    :     -1.00|                    -0.32  ***********  -0.08                                    |    +1.00

    Z=-1909.4(0.00%) | Like=-1896.02..-1575.73 [-2603.9145..-1664.5521] | it/evals=3237/16462 eff=20.1532% N=400 

    Mono-modal Volume: ~exp(-9.84)   Expected Volume: exp(-8.10) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.80
    src.level       :      -8.0|            -5.5  ********   *********  -2.9                                     |     +3.0
    torus.phoindex  :      +1.2|          +1.5  ************************************** ***  +2.3                 |     +2.8
    src.nH          :     +20.0|   *       ** ************************                  * ******** *** ******  **|    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :     -1.00|                    -0.32  **********  -0.09                                     |    +1.00

    Z=-1873.0(0.00%) | Like=-1859.18..-1565.16 [-2603.9145..-1664.5521] | it/evals=3329/18036 eff=18.8762% N=400 

    Mono-modal Volume: ~exp(-9.84)   Expected Volume: exp(-8.33) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.79
    src.level       :      -8.0|            -5.5  *********  ********  -3.1                                      |     +3.0
    torus.phoindex  :      +1.2|          +1.5  ************************************** ***       *  +2.5         |     +2.8
    src.nH          :     +20.0|   *    *   *   **********************                  * ********  ***** ** * **|    +26.0
    src.softscatnorm:      -7.0|****************************************************************** * ************|     -1.0
    pca1.lognorm    :     -1.00|                     -0.31  *********  -0.10                                     |    +1.00

    Z=-1840.8(0.00%) | Like=-1826.57..-1565.16 [-2603.9145..-1664.5521] | it/evals=3419/20101 eff=17.3544% N=400 

    Mono-modal Volume: ~exp(-9.84)   Expected Volume: exp(-8.55) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.77
    src.level       :      -8.0|            -5.5  ********    ******  -3.1                                       |     +3.0
    torus.phoindex  :      +1.2|           +1.5  * ******************************** **  **       *  +2.5         |     +2.8
    src.nH          :     +20.0|     +20.9  * * *** ******************                    ** ****  ****** *  *  *|    +26.0
    src.softscatnorm:      -7.0|********************** **********************************************************|     -1.0
    pca1.lognorm    :      -1.0|                      -0.3  *********  -0.1                                      |     +1.0

    Z=-1815.0(0.00%) | Like=-1801.26..-1565.16 [-2603.9145..-1664.5521] | it/evals=3505/21751 eff=16.4161% N=400 

    Mono-modal Volume: ~exp(-9.84)   Expected Volume: exp(-8.78) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.78
    src.level       :      -8.0|            -5.5  *********    *****  -3.2                                       |     +3.0
    torus.phoindex  :      +1.2|           +1.5  ************************************* ***       *  +2.5         |     +2.8
    src.nH          :     +20.0|     +20.9  * * * *  ******************                   ** *  *  *****        *|    +26.0
    src.softscatnorm:      -7.0|********************** **********************************************************|     -1.0
    pca1.lognorm    :      -1.0|                      -0.3  *********  -0.1                                      |     +1.0

    Z=-1785.7(0.00%) | Like=-1771.13..-1565.16 [-2603.9145..-1664.5521] | it/evals=3596/23869 eff=15.3223% N=400 

    Mono-modal Volume: ~exp(-9.84)   Expected Volume: exp(-9.00) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.77
    src.level       :      -8.0|             -5.4  *******     ***  -3.4                                         |     +3.0
    torus.phoindex  :      +1.2|           +1.5  ************************************* ***       *  +2.5         |     +2.8
    src.nH          :     +20.0|            +21.5  * *****************                    **       *   *         |    +26.0
    src.softscatnorm:      -7.0|****************************************** ****** *******************************|     -1.0
    pca1.lognorm    :      -1.0|                      -0.3  *********  -0.1                                      |     +1.0

    Z=-1760.5(0.00%) | Like=-1746.68..-1564.50 [-2603.9145..-1664.5521] | it/evals=3688/25859 eff=14.4860% N=400 

    Mono-modal Volume: ~exp(-9.84)   Expected Volume: exp(-9.23) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.76
    src.level       :      -8.0|             -5.4  *******    **  -3.7                                           |     +3.0
    torus.phoindex  :      +1.2|*                * *********************************** ***       *  +2.5         |     +2.8
    src.nH          :     +20.0|              +21.6  *****************                    *       *  +25.0       |    +26.0
    src.softscatnorm:      -7.0|****************************************** **************************************|     -1.0
    pca1.lognorm    :      -1.0|                      -0.3  ********  -0.1                                       |     +1.0

    Z=-1737.9(0.00%) | Like=-1724.21..-1564.50 [-2603.9145..-1664.5521] | it/evals=3774/28135 eff=13.6074% N=400 

    Mono-modal Volume: ~exp(-9.84)   Expected Volume: exp(-9.45) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.76
    src.level       :      -8.0|             -5.4  *******    *  -3.9                                            |     +3.0
    torus.phoindex  :      +1.2|*                ************************************* ***       *  +2.5         |     +2.8
    src.nH          :     +20.0|               +21.6  ****************                            *  +25.0       |    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :      -1.0|                      -0.3  ********  -0.1                                       |     +1.0

    Z=-1717.0(0.00%) | Like=-1703.15..-1564.50 [-2603.9145..-1664.5521] | it/evals=3869/32066 eff=12.2182% N=400 

    Mono-modal Volume: ~exp(-12.71) * Expected Volume: exp(-9.68) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.76
    src.level       :      -8.0|             -5.4  *******  -4.5                                                 |     +3.0
    torus.phoindex  :      +1.2|           +1.5  ********************************* *** ***       *  +2.5         |     +2.8
    src.nH          :     +20.0|               +21.6  * **************  +22.8                                    |    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :      -1.0|                       -0.3  *******  -0.1                                       |     +1.0

    Z=-1700.2(0.00%) | Like=-1686.12..-1564.50 [-2603.9145..-1664.5521] | it/evals=3952/32430 eff=12.3384% N=400 

    Mono-modal Volume: ~exp(-12.71)   Expected Volume: exp(-9.90) Quality: ok

       positive degeneracy between src.nH and src.level: rho=0.76
    src.level       :      -8.0|             -5.4  *******  -4.5                                                 |     +3.0
    torus.phoindex  :      +1.2|           +1.6  ********************************* *******       *  +2.5         |     +2.8
    src.nH          :     +20.0|               +21.6  * **************  +22.8                                    |    +26.0
    src.softscatnorm:      -7.0|**************** ****************************************************************|     -1.0
    pca1.lognorm    :      -1.0|                       -0.3  *******  -0.1                                       |     +1.0

    Z=-1685.9(0.00%) | Like=-1671.48..-1563.17 [-2603.9145..-1664.5521] | it/evals=4040/32889 eff=12.4350% N=400 

    Mono-modal Volume: ~exp(-13.07) * Expected Volume: exp(-10.13) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.75
       positive degeneracy between src.nH and src.level: rho=0.77
    src.level       :      -8.0|             -5.4  *******  -4.5                                                 |     +3.0
    torus.phoindex  :      +1.2|          *      ***************************************** **    *  +2.5         |     +2.8
    src.nH          :     +20.0|                 +21.8  **************  +22.8                                    |    +26.0
    src.softscatnorm:      -7.0|**************** ****************************************************************|     -1.0
    pca1.lognorm    :      -1.0|                       -0.3  ******  -0.1                                        |     +1.0

    Z=-1672.4(0.00%) | Like=-1657.80..-1563.17 [-1664.5027..-1569.9864] | it/evals=4135/33285 eff=12.5741% N=400 

    Mono-modal Volume: ~exp(-13.32) * Expected Volume: exp(-10.35) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.77
       positive degeneracy between src.nH and src.level: rho=0.77
    src.level       :      -8.0|             -5.4  *******  -4.5                                                 |     +3.0
    torus.phoindex  :      +1.2|          *      ***************************************** *     *  +2.5         |     +2.8
    src.nH          :     +20.0|                 +21.8  *************  +22.7                                     |    +26.0
    src.softscatnorm:      -7.0|* *******************************************************************************|     -1.0
    pca1.lognorm    :      -1.0|                       -0.3  ******  -0.1                                        |     +1.0

    Z=-1662.5(0.00%) | Like=-1648.08..-1563.17 [-1664.5027..-1569.9864] | it/evals=4214/33643 eff=12.6764% N=400 

    Mono-modal Volume: ~exp(-13.32)   Expected Volume: exp(-10.58) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.80
    src.level       :      -8.0|             -5.3  *******  -4.5                                                 |     +3.0
    torus.phoindex  :      +1.2|          *    * ************************************** ** *  +2.4               |     +2.8
    src.nH          :     +20.0|                 +21.8  *************  +22.7                                     |    +26.0
    src.softscatnorm:      -7.0|* ******** **********************************************************************|     -1.0
    pca1.lognorm    :      -1.0|                       -0.3  ******  -0.1                                        |     +1.0

    Z=-1651.0(0.00%) | Like=-1636.39..-1563.17 [-1664.5027..-1569.9864] | it/evals=4315/34202 eff=12.7655% N=400 

    Mono-modal Volume: ~exp(-13.32)   Expected Volume: exp(-10.80) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.82
       positive degeneracy between src.nH and src.level: rho=0.76
    src.level       :      -8.0|             -5.3  *******  -4.5                                                 |     +3.0
    torus.phoindex  :      +1.2|          *    ************************************** * ** *  +2.4               |     +2.8
    src.nH          :     +20.0|                 +21.8  * **********  +22.7                                      |    +26.0
    src.softscatnorm:      -7.0|* *******************************************************************************|     -1.0
    pca1.lognorm    :      -1.0|                       -0.3  ******  -0.1                                        |     +1.0

    Z=-1642.1(0.00%) | Like=-1627.18..-1561.61 [-1664.5027..-1569.9864] | it/evals=4400/34699 eff=12.8284% N=400 

    Mono-modal Volume: ~exp(-13.32)   Expected Volume: exp(-11.02) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.83
    src.level       :      -8.0|             -5.4  *******  -4.5                                                 |     +3.0
    torus.phoindex  :      +1.2|          *   *************************************** *  * *  +2.4               |     +2.8
    src.nH          :     +20.0|                 +21.8  * **********  +22.7                                      |    +26.0
    src.softscatnorm:      -7.0|************************************ ********************************************|     -1.0
    pca1.lognorm    :      -1.0|                        -0.3  *****  -0.1                                        |     +1.0

    Z=-1634.0(0.00%) | Like=-1619.31..-1561.61 [-1664.5027..-1569.9864] | it/evals=4489/35443 eff=12.8100% N=400 

    Mono-modal Volume: ~exp(-13.32)   Expected Volume: exp(-11.25) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.82
    src.level       :      -8.0|             -5.4  *******  -4.5                                                 |     +3.0
    torus.phoindex  :      +1.2|          *   *********************************** *** *  * *  +2.4               |     +2.8
    src.nH          :     +20.0|                   +22.0  **********  +22.6                                      |    +26.0
    src.softscatnorm:      -7.0|************************** ********* ********************************************|     -1.0
    pca1.lognorm    :      -1.0|                        -0.3  *****  -0.2                                        |     +1.0

    Z=-1627.5(0.00%) | Like=-1612.63..-1557.21 [-1664.5027..-1569.9864] | it/evals=4584/36151 eff=12.8220% N=400 

    Mono-modal Volume: ~exp(-13.32)   Expected Volume: exp(-11.47) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.85
    src.level       :      -8.0|             -5.4  *******  -4.5                                                 |     +3.0
    torus.phoindex  :      +1.2|          *   *************************************** *    *  +2.4               |     +2.8
    src.nH          :     +20.0|                   +22.0  **********  +22.6                                      |    +26.0
    src.softscatnorm:      -7.0|********** **********************************************************************|     -1.0
    pca1.lognorm    :     -1.00|                       -0.25  *****  -0.15                                       |    +1.00

    Z=-1621.8(0.00%) | Like=-1607.06..-1557.21 [-1664.5027..-1569.9864] | it/evals=4676/36891 eff=12.8141% N=400 

    Mono-modal Volume: ~exp(-13.32)   Expected Volume: exp(-11.70) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.87
       positive degeneracy between src.nH and src.level: rho=0.76
    src.level       :      -8.0|             -5.4  *******  -4.5                                                 |     +3.0
    torus.phoindex  :      +1.2|          *    ************************************** *    *  +2.4               |     +2.8
    src.nH          :     +20.0|                   +22.0  **********  +22.6                                      |    +26.0
    src.softscatnorm:      -7.0|********** **********************************************************************|     -1.0
    pca1.lognorm    :     -1.00|                       -0.25  *****  -0.15                                       |    +1.00

    Z=-1617.8(0.00%) | Like=-1602.92..-1557.21 [-1664.5027..-1569.9864] | it/evals=4760/37607 eff=12.7933% N=400 

    Mono-modal Volume: ~exp(-13.32)   Expected Volume: exp(-11.92) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.88
       positive degeneracy between src.nH and src.level: rho=0.76
    src.level       :      -8.0|             -5.4  *******  -4.5                                                 |     +3.0
    torus.phoindex  :      +1.2|          *    ************************************** *    *  +2.4               |     +2.8
    src.nH          :     +20.0|                   +22.0  **********  +22.6                                      |    +26.0
    src.softscatnorm:      -7.0|***************************************************************** ***************|     -1.0
    pca1.lognorm    :     -1.00|                       -0.24  ****  -0.16                                        |    +1.00

    Z=-1611.6(0.00%) | Like=-1596.33..-1557.21 [-1664.5027..-1569.9864] | it/evals=4859/38531 eff=12.7429% N=400 

    Mono-modal Volume: ~exp(-13.32)   Expected Volume: exp(-12.15) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.89
       positive degeneracy between src.nH and src.level: rho=0.78
    src.level       :      -8.0|             -5.4  *******  -4.5                                                 |     +3.0
    torus.phoindex  :      +1.2|          *    ************************************        *  +2.4               |     +2.8
    src.nH          :     +20.0|                   +22.0  **********  +22.6                                      |    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :     -1.00|                       -0.24  ****  -0.16                                        |    +1.00

    Z=-1606.9(0.00%) | Like=-1591.79..-1557.21 [-1664.5027..-1569.9864] | it/evals=4947/39540 eff=12.6392% N=400 

    Mono-modal Volume: ~exp(-13.40) * Expected Volume: exp(-12.37) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.91
       positive degeneracy between src.nH and src.level: rho=0.78
    src.level       :      -8.0|             -5.3  ******  -4.7                                                  |     +3.0
    torus.phoindex  :      +1.2|          *     *********************************  +2.2                          |     +2.8
    src.nH          :     +20.0|                    +22.0  *********  +22.6                                      |    +26.0
    src.softscatnorm:      -7.0|*********** *********************************************************************|     -1.0
    pca1.lognorm    :     -1.00|                       -0.24  ****  -0.17                                        |    +1.00

    Z=-1603.2(0.00%) | Like=-1588.00..-1557.21 [-1664.5027..-1569.9864] | it/evals=5039/40505 eff=12.5645% N=400 

    Mono-modal Volume: ~exp(-14.16) * Expected Volume: exp(-12.60) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.91
       positive degeneracy between src.nH and src.level: rho=0.81
    src.level       :      -8.0|             -5.3  ******  -4.7                                                  |     +3.0
    torus.phoindex  :      +1.2|          *     ********************************  +2.1                           |     +2.8
    src.nH          :     +20.0|                    +22.0  *********  +22.6                                      |    +26.0
    src.softscatnorm:      -7.0|********************** **********************************************************|     -1.0
    pca1.lognorm    :     -1.00|                       -0.24  ****  -0.17                                        |    +1.00

    Z=-1600.5(0.00%) | Like=-1585.37..-1557.21 [-1664.5027..-1569.9864] | it/evals=5126/41358 eff=12.5153% N=400 

    Mono-modal Volume: ~exp(-14.16)   Expected Volume: exp(-12.82) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.91
       positive degeneracy between src.nH and src.level: rho=0.81
    src.level       :      -8.0|             -5.3  ******  -4.7                                                  |     +3.0
    torus.phoindex  :      +1.2|          +1.5  *********************************  +2.2                          |     +2.8
    src.nH          :     +20.0|                    +22.0  *********  +22.6                                      |    +26.0
    src.softscatnorm:      -7.0|********************** **********************************************************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.23  ***  -0.17                                        |    +1.00

    Z=-1597.8(0.00%) | Like=-1582.26..-1557.21 [-1664.5027..-1569.9864] | it/evals=5217/42394 eff=12.4232% N=400 

    Mono-modal Volume: ~exp(-14.16)   Expected Volume: exp(-13.05) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.92
       positive degeneracy between src.nH and src.level: rho=0.83
    src.level       :      -8.0|             -5.3  ******  -4.7                                                  |     +3.0
    torus.phoindex  :      +1.2|          +1.5  ****************************** * *  +2.2                         |     +2.8
    src.nH          :     +20.0|                    +22.0  *********  +22.6                                      |    +26.0
    src.softscatnorm:      -7.0|********************** **********************************************************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.23  ***  -0.17                                        |    +1.00

    Z=-1595.3(0.00%) | Like=-1579.82..-1556.41 [-1664.5027..-1569.9864] | it/evals=5308/43204 eff=12.4007% N=400 

    Mono-modal Volume: ~exp(-14.16)   Expected Volume: exp(-13.27) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.93
       positive degeneracy between src.nH and src.level: rho=0.81
    src.level       :      -8.0|             -5.3  ******  -4.6                                                  |     +3.0
    torus.phoindex  :      +1.2|          +1.5  ** *************************** *  *  *  +2.3                     |     +2.8
    src.nH          :     +20.0|                    +22.0  *********  +22.6                                      |    +26.0
    src.softscatnorm:      -7.0|******************************************************* *************************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.23  ***  -0.17                                        |    +1.00

    Z=-1593.4(0.00%) | Like=-1577.83..-1556.41 [-1664.5027..-1569.9864] | it/evals=5397/44719 eff=12.1776% N=400 

    Mono-modal Volume: ~exp(-14.16)   Expected Volume: exp(-13.50) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.94
       positive degeneracy between src.nH and src.level: rho=0.82
    src.level       :      -8.0|             -5.3  ******  -4.6                                                  |     +3.0
    torus.phoindex  :      +1.2|          +1.5  ** ****************************   ** *  +2.3                     |     +2.8
    src.nH          :     +20.0|                    +22.0  *********  +22.6                                      |    +26.0
    src.softscatnorm:      -7.0|******************************************************* *************************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.23  ***  -0.17                                        |    +1.00

    Z=-1591.8(0.00%) | Like=-1576.21..-1556.41 [-1664.5027..-1569.9864] | it/evals=5489/46123 eff=12.0049% N=400 

    Mono-modal Volume: ~exp(-14.16)   Expected Volume: exp(-13.72) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.94
       positive degeneracy between src.nH and src.level: rho=0.82
    src.level       :      -8.0|              -5.3  *****  -4.6                                                  |     +3.0
    torus.phoindex  :      +1.2|          +1.5  ** ****************************   ** *  +2.3                     |     +2.8
    src.nH          :     +20.0|                    +22.0  *********  +22.6                                      |    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.23  ***  -0.17                                        |    +1.00

    Z=-1590.2(0.00%) | Like=-1574.28..-1556.41 [-1664.5027..-1569.9864] | it/evals=5579/47164 eff=11.9301% N=400 

    Mono-modal Volume: ~exp(-15.03) * Expected Volume: exp(-13.95) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.94
       positive degeneracy between src.nH and src.level: rho=0.82
    src.level       :      -8.0|              -5.3  *****  -4.6                                                  |     +3.0
    torus.phoindex  :      +1.2|          +1.5  *******************************   *  *  +2.3                     |     +2.8
    src.nH          :     +20.0|                    +22.0  *********  +22.6                                      |    +26.0
    src.softscatnorm:      -7.0|************** ******************************************************************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.23  ***  -0.17                                        |    +1.00

    Z=-1588.8(0.00%) | Like=-1572.79..-1556.41 [-1664.5027..-1569.9864] | it/evals=5664/48269 eff=11.8323% N=400 

    Mono-modal Volume: ~exp(-15.36) * Expected Volume: exp(-14.17) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.95
       positive degeneracy between src.nH and src.level: rho=0.82
    src.level       :      -8.0|              -5.3  *****  -4.7                                                  |     +3.0
    torus.phoindex  :      +1.2|          +1.5  ******************************** *   *  +2.3                     |     +2.8
    src.nH          :     +20.0|                     +22.1  *******  +22.6                                       |    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.23  ***  -0.17                                        |    +1.00

    Z=-1587.3(0.00%) | Like=-1571.04..-1556.41 [-1664.5027..-1569.9864] | it/evals=5756/49283 eff=11.7751% N=400 

    Mono-modal Volume: ~exp(-15.36)   Expected Volume: exp(-14.40) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.95
       positive degeneracy between src.nH and src.level: rho=0.84
    src.level       :      -8.0|              -5.3  *****  -4.7                                                  |     +3.0
    torus.phoindex  :      +1.2|         +1.5  *********************************     *  +2.3                     |     +2.8
    src.nH          :     +20.0|                     +22.1  *******  +22.6                                       |    +26.0
    src.softscatnorm:      -7.0|******************************************************* *************************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.23  ***  -0.18                                        |    +1.00

    Z=-1585.9(0.00%) | Like=-1569.60..-1556.41 [-1569.9552..-1562.1643] | it/evals=5846/50379 eff=11.6969% N=400 

    Mono-modal Volume: ~exp(-15.92) * Expected Volume: exp(-14.62) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.95
       positive degeneracy between src.nH and src.level: rho=0.85
    src.level       :      -8.0|              -5.3  *****  -4.7                                                  |     +3.0
    torus.phoindex  :      +1.2|         +1.5  *****************************  **     *  +2.3                     |     +2.8
    src.nH          :     +20.0|                     +22.1  *******  +22.6                                       |    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.23  ***  -0.18                                        |    +1.00

    Z=-1584.8(0.01%) | Like=-1568.21..-1555.91 [-1569.9552..-1562.1643] | it/evals=5938/51466 eff=11.6281% N=400 

    Mono-modal Volume: ~exp(-15.92)   Expected Volume: exp(-14.85) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.95
       positive degeneracy between src.nH and src.level: rho=0.84
    src.level       :      -8.0|              -5.3  *****  -4.7                                                  |     +3.0
    torus.phoindex  :      +1.2|         +1.5  *****************************   *     *  +2.3                     |     +2.8
    src.nH          :     +20.0|                     +22.1  *******  +22.6                                       |    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  ***  -0.18                                        |    +1.00

    Z=-1583.6(0.03%) | Like=-1566.95..-1555.91 [-1569.9552..-1562.1643] | it/evals=6029/53159 eff=11.4274% N=400 

    Mono-modal Volume: ~exp(-15.92)   Expected Volume: exp(-15.07) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.95
       positive degeneracy between src.nH and src.level: rho=0.85
       positive degeneracy between src.nH and torus.phoindex: rho=0.75
    src.level       :      -8.0|              -5.3  *****  -4.7                                                  |     +3.0
    torus.phoindex  :      +1.2|         +1.5  *****************************   *    **  +2.3                     |     +2.8
    src.nH          :     +20.0|                     +22.1  ********  +22.6                                      |    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  ***  -0.18                                        |    +1.00

    Z=-1582.6(0.07%) | Like=-1566.02..-1555.91 [-1569.9552..-1562.1643] | it/evals=6117/54814 eff=11.2416% N=400 

    Mono-modal Volume: ~exp(-15.92)   Expected Volume: exp(-15.30) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.95
       positive degeneracy between src.nH and src.level: rho=0.86
       positive degeneracy between src.nH and torus.phoindex: rho=0.77
    src.level       :      -8.0|              -5.3  *****  -4.7                                                  |     +3.0
    torus.phoindex  :      +1.2|        +1.5  ******************************   *    *  +2.2                      |     +2.8
    src.nH          :     +20.0|                    +22.1  *********  +22.6                                      |    +26.0
    src.softscatnorm:      -7.0|*********************************************************************************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  ***  -0.18                                        |    +1.00

    Z=-1581.9(0.11%) | Like=-1565.27..-1555.35 [-1569.9552..-1562.1643] | it/evals=6206/56873 eff=10.9893% N=400 

    Mono-modal Volume: ~exp(-16.11) * Expected Volume: exp(-15.52) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.95
       positive degeneracy between src.nH and src.level: rho=0.88
       positive degeneracy between src.nH and torus.phoindex: rho=0.79
    src.level       :      -8.0|              -5.3  *****  -4.7                                                  |     +3.0
    torus.phoindex  :      +1.2|        +1.5  ******************************   *    *  +2.2                      |     +2.8
    src.nH          :     +20.0|                    +22.1  *********  +22.6                                      |    +26.0
    src.softscatnorm:      -7.0|********************************************************************** **********|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  ***  -0.18                                        |    +1.00

    Z=-1581.2(0.24%) | Like=-1564.32..-1555.35 [-1569.9552..-1562.1643] | it/evals=6298/58887 eff=10.7682% N=400 

    Mono-modal Volume: ~exp(-16.11)   Expected Volume: exp(-15.75) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.95
       positive degeneracy between src.nH and src.level: rho=0.89
       positive degeneracy between src.nH and torus.phoindex: rho=0.80
    src.level       :      -8.0|              -5.3  *****  -4.7                                                  |     +3.0
    torus.phoindex  :      +1.2|         +1.5  *****************************   *    *  +2.2                      |     +2.8
    src.nH          :     +20.0|                    +22.1  *********  +22.6                                      |    +26.0
    src.softscatnorm:      -7.0|************** ******************************************************************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  ***  -0.18                                        |    +1.00

    Z=-1580.6(0.48%) | Like=-1563.67..-1555.35 [-1569.9552..-1562.1643] | it/evals=6389/61590 eff=10.4412% N=400 

    Mono-modal Volume: ~exp(-16.11)   Expected Volume: exp(-15.97) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.96
       positive degeneracy between src.nH and src.level: rho=0.90
       positive degeneracy between src.nH and torus.phoindex: rho=0.83
    src.level       :      -8.0|              -5.3  *****  -4.7                                                  |     +3.0
    torus.phoindex  :      +1.2|        +1.5  *******************************  *  +2.1                           |     +2.8
    src.nH          :     +20.0|                    +22.1  ********  +22.6                                       |    +26.0
    src.softscatnorm:      -7.0|***************************** ******************************** ******************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  ***  -0.18                                        |    +1.00

    Z=-1580.0(0.60%) | Like=-1562.94..-1555.22 [-1569.9552..-1562.1643] | it/evals=6478/63946 eff=10.1942% N=400 

    Mono-modal Volume: ~exp(-16.72) * Expected Volume: exp(-16.20) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.96
       positive degeneracy between src.nH and src.level: rho=0.89
       positive degeneracy between src.nH and torus.phoindex: rho=0.82
    src.level       :      -8.0|              -5.3  ****  -4.8                                                   |     +3.0
    torus.phoindex  :      +1.2|        +1.5  *************************** ***  +2.1                              |     +2.8
    src.nH          :     +20.0|                     +22.1  ******  +22.5                                        |    +26.0
    src.softscatnorm:      -7.0|******* ********************* ***************************************************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  ***  -0.18                                        |    +1.00

    Z=-1579.5(0.98%) | Like=-1562.37..-1555.07 [-1569.9552..-1562.1643] | it/evals=6568/65759 eff=10.0491% N=400 

    Mono-modal Volume: ~exp(-16.72)   Expected Volume: exp(-16.42) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.96
       positive degeneracy between src.nH and src.level: rho=0.90
       positive degeneracy between src.nH and torus.phoindex: rho=0.84
    src.level       :      -8.0|              -5.3  ****  -4.8                                                   |     +3.0
    torus.phoindex  :      +1.2|         +1.5  ************************** ***  +2.1                              |     +2.8
    src.nH          :     +20.0|                     +22.1  *******  +22.5                                       |    +26.0
    src.softscatnorm:      -7.0|***************************** ***************************************************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  ***  -0.18                                        |    +1.00

    Z=-1579.1(1.50%) | Like=-1561.74..-1555.07 [-1562.1619..-1559.8406] | it/evals=6654/67999 eff=9.8433% N=400  

    Mono-modal Volume: ~exp(-16.88) * Expected Volume: exp(-16.65) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.96
       positive degeneracy between src.nH and src.level: rho=0.91
       positive degeneracy between src.nH and torus.phoindex: rho=0.85
    src.level       :      -8.0|             -5.3  *****  -4.8                                                   |     +3.0
    torus.phoindex  :      +1.2|      +1.5  *  **************************  **  +2.1                              |     +2.8
    src.nH          :     +20.0|                    +22.1  ********  +22.5                                       |    +26.0
    src.softscatnorm:      -7.0|******** ******************** ***************************************************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  ***  -0.18                                        |    +1.00

    Z=-1578.7(1.71%) | Like=-1561.22..-1553.53 [-1562.1619..-1559.8406] | it/evals=6747/70297 eff=9.6528% N=400 

    Mono-modal Volume: ~exp(-17.05) * Expected Volume: exp(-16.87) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.96
       positive degeneracy between src.nH and src.level: rho=0.91
       positive degeneracy between src.nH and torus.phoindex: rho=0.86
    src.level       :      -8.0|              -5.3  ****  -4.8                                                   |     +3.0
    torus.phoindex  :      +1.2|         +1.5  **************************  **  +2.1                              |     +2.8
    src.nH          :     +20.0|                     +22.1  *******  +22.5                                       |    +26.0
    src.softscatnorm:      -7.0|******** **************************************** ********** ********************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  ***  -0.18                                        |    +1.00

    Z=-1578.3(2.07%) | Like=-1560.64..-1553.53 [-1562.1619..-1559.8406] | it/evals=6836/72814 eff=9.4402% N=400 

    Mono-modal Volume: ~exp(-17.05)   Expected Volume: exp(-17.10) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.96
       positive degeneracy between src.nH and src.level: rho=0.91
       positive degeneracy between src.nH and torus.phoindex: rho=0.85
    src.level       :      -8.0|             -5.3  *****  -4.8                                                   |     +3.0
    torus.phoindex  :      +1.2|       +1.5  *************************** *  +2.0                                 |     +2.8
    src.nH          :     +20.0|                     +22.1  ******  +22.5                                        |    +26.0
    src.softscatnorm:      -7.0|************************************************************ ****** *************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  ***  -0.18                                        |    +1.00

    Z=-1577.9(3.29%) | Like=-1560.14..-1553.53 [-1562.1619..-1559.8406] | it/evals=6929/76201 eff=9.1410% N=400 

    Mono-modal Volume: ~exp(-17.05)   Expected Volume: exp(-17.32) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.96
       positive degeneracy between src.nH and src.level: rho=0.92
       positive degeneracy between src.nH and torus.phoindex: rho=0.87
    src.level       :      -8.0|             -5.3  *****  -4.8                                                   |     +3.0
    torus.phoindex  :      +1.2|       +1.5  *************************** *  +2.0                                 |     +2.8
    src.nH          :     +20.0|                     +22.1  ******  +22.5                                        |    +26.0
    src.softscatnorm:      -7.0|*********************************** ******  **************** ********************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  ***  -0.18                                        |    +1.00

    Z=-1577.6(4.67%) | Like=-1559.76..-1553.53 [-1559.8397..-1558.4448] | it/evals=7019/79336 eff=8.8920% N=400 

    Mono-modal Volume: ~exp(-17.23) * Expected Volume: exp(-17.55) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.97
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.89
    src.level       :      -8.0|             -5.3  *****  -4.8                                                   |     +3.0
    torus.phoindex  :      +1.2|       +1.5  *************************** *  +2.0                                 |     +2.8
    src.nH          :     +20.0|                     +22.1  ******  +22.5                                        |    +26.0
    src.softscatnorm:      -7.0|***** ** ******************** ************* **** ***** **************************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  **  -0.19                                         |    +1.00

    Z=-1577.3(5.72%) | Like=-1559.38..-1553.36 [-1559.8397..-1558.4448] | it/evals=7109/81518 eff=8.7638% N=400 

    Mono-modal Volume: ~exp(-17.27) * Expected Volume: exp(-17.77) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.97
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.89
    src.level       :      -8.0|             -5.3  *****  -4.9                                                   |     +3.0
    torus.phoindex  :      +1.2|       +1.5  ***************************  +2.0                                   |     +2.8
    src.nH          :     +20.0|                     +22.1  ******  +22.5                                        |    +26.0
    src.softscatnorm:      -7.0|************************** ** * **********  **** ***** **************************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  **  -0.19                                         |    +1.00

    Z=-1577.0(7.21%) | Like=-1558.87..-1553.36 [-1559.8397..-1558.4448] | it/evals=7198/84998 eff=8.5085% N=400 

    Mono-modal Volume: ~exp(-17.84) * Expected Volume: exp(-18.00) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.90
    src.level       :      -8.0|              -5.3  ****  -4.9                                                   |     +3.0
    torus.phoindex  :      +1.2|       +1.5  ***************************  +2.0                                   |     +2.8
    src.nH          :     +20.0|                     +22.1  ******  +22.5                                        |    +26.0
    src.softscatnorm:      -7.0|*** * ******** * ******** *** ************* **** ***** ***** ********************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  **  -0.19                                         |    +1.00

    Z=-1576.8(8.11%) | Like=-1558.52..-1552.95 [-1559.8397..-1558.4448] | it/evals=7287/87763 eff=8.3411% N=400 

    Mono-modal Volume: ~exp(-18.04) * Expected Volume: exp(-18.23) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.91
       positive degeneracy between src.softscatnorm and src.nH: rho=0.77
    src.level       :      -8.0|              -5.3  ****  -4.9                                                   |     +3.0
    torus.phoindex  :      +1.2|       +1.5  ***************************  +2.0                                   |     +2.8
    src.nH          :     +20.0|                     +22.1  ******  +22.5                                        |    +26.0
    src.softscatnorm:      -7.0|*** * ********** ******** *** ************* **** ***** *** **********************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  **  -0.19                                         |    +1.00

    Z=-1576.6(10.54%) | Like=-1558.11..-1552.95 [-1558.4392..-1557.5018] | it/evals=7379/90194 eff=8.2177% N=400 

    Mono-modal Volume: ~exp(-18.57) * Expected Volume: exp(-18.45) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.92
       positive degeneracy between src.softscatnorm and src.nH: rho=0.77
    src.level       :      -8.0|             -5.3  *****  -4.9                                                   |     +3.0
    torus.phoindex  :      +1.2|       +1.5  ***************************  +2.0                                   |     +2.8
    src.nH          :     +20.0|                     +22.1  ******  +22.5                                        |    +26.0
    src.softscatnorm:      -7.0|****** ********* ** ***** *** ******* *** * **** ***** *** **********************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  **  -0.19                                         |    +1.00

    Z=-1576.3(12.76%) | Like=-1557.78..-1552.95 [-1558.4392..-1557.5018] | it/evals=7468/93284 eff=8.0401% N=400 

    Mono-modal Volume: ~exp(-18.61) * Expected Volume: exp(-18.68) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.90
       positive degeneracy between src.softscatnorm and src.nH: rho=0.76
    src.level       :      -8.0|             -5.3  *****  -4.9                                                   |     +3.0
    torus.phoindex  :      +1.2|       +1.5  **************************  +2.0                                    |     +2.8
    src.nH          :     +20.0|                     +22.1  ******  +22.5                                        |    +26.0
    src.softscatnorm:      -7.0|**  ** * ******* ** ** ** *** **** ****** ****** ** ** *** **********************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  **  -0.19                                         |    +1.00

    Z=-1576.1(14.63%) | Like=-1557.39..-1552.83 [-1557.4972..-1556.9304] | it/evals=7559/96755 eff=7.8449% N=400 

    Mono-modal Volume: ~exp(-18.61)   Expected Volume: exp(-18.90) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.92
       positive degeneracy between src.softscatnorm and src.nH: rho=0.76
    src.level       :      -8.0|             -5.3  *****  -4.9                                                   |     +3.0
    torus.phoindex  :      +1.2|       +1.5  **************************  +2.0                                    |     +2.8
    src.nH          :     +20.0|                     +22.1  ******  +22.5                                        |    +26.0
    src.softscatnorm:      -7.0|**  *    *******  * *****  ** ********************* **  ** ***** ****************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  **  -0.19                                         |    +1.00

    Z=-1576.0(16.77%) | Like=-1557.09..-1551.92 [-1557.4972..-1556.9304] | it/evals=7647/100684 eff=7.6253% N=400 

    Mono-modal Volume: ~exp(-18.61)   Expected Volume: exp(-19.13) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.91
       positive degeneracy between src.softscatnorm and src.nH: rho=0.75
    src.level       :      -8.0|             -5.3  *****  -4.9                                                   |     +3.0
    torus.phoindex  :      +1.2|       +1.5  **************************  +2.0                                    |     +2.8
    src.nH          :     +20.0|                     +22.1  ******  +22.5                                        |    +26.0
    src.softscatnorm:      -7.0|*** * *   *****   *  ****  ** ********************* ****** ** **  * *************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  **  -0.19                                         |    +1.00

    Z=-1575.8(19.94%) | Like=-1556.76..-1551.92 [-1556.9302..-1556.5382] | it/evals=7738/105087 eff=7.3916% N=400 

    Mono-modal Volume: ~exp(-18.61)   Expected Volume: exp(-19.35) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.91
    src.level       :      -8.0|              -5.3  ****  -4.9                                                   |     +3.0
    torus.phoindex  :      +1.2|       +1.5  **************************  +2.0                                    |     +2.8
    src.nH          :     +20.0|                     +22.1  ******  +22.5                                        |    +26.0
    src.softscatnorm:      -7.0|*** * *** *****      ** *  ** ** ** *********** *** ****** ** **  *  ************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  **  -0.19                                         |    +1.00

    Z=-1575.6(22.45%) | Like=-1556.46..-1551.92 [-1556.5371..-1556.2426] | it/evals=7829/111277 eff=7.0610% N=400 

    Mono-modal Volume: ~exp(-18.61)   Expected Volume: exp(-19.58) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.91
    src.level       :      -8.0|              -5.3  ****  -4.9                                                   |     +3.0
    torus.phoindex  :      +1.2|       +1.5  **************************  +2.0                                    |     +2.8
    src.nH          :     +20.0|                     +22.1  ******  +22.5                                        |    +26.0
    src.softscatnorm:      -7.0| **   *** *****     *** ** *   **** * ** *** **  ** * ******* **  ** ************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  **  -0.19                                         |    +1.00

    Z=-1575.5(25.17%) | Like=-1556.14..-1551.92 [-1556.2404..-1556.0691] | it/evals=7918/117786 eff=6.7453% N=400 

    Mono-modal Volume: ~exp(-18.61)   Expected Volume: exp(-19.80) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.89
    src.level       :      -8.0|              -5.3  ****  -4.9                                                   |     +3.0
    torus.phoindex  :      +1.2|       +1.5  ************************ *  +2.0                                    |     +2.8
    src.nH          :     +20.0|                     +22.1  ******  +22.5                                        |    +26.0
    src.softscatnorm:      -7.0|**    **  *****     **  **     ***  * *  ***  *  ** *   *  *  **   **************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.22  **  -0.19                                         |    +1.00

    Z=-1575.3(28.17%) | Like=-1555.84..-1551.87 [-1555.8381..-1555.7736]*| it/evals=8009/129235 eff=6.2165% N=400 

    Mono-modal Volume: ~exp(-18.96) * Expected Volume: exp(-20.03) Quality: correlation length: 4 (+)

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.89
    src.level       :      -8.0|              -5.3  ***  -4.9                                                    |     +3.0
    torus.phoindex  :      +1.2|       +1.5  ***********************  +1.9                                       |     +2.8
    src.nH          :     +20.0|                     +22.1  *****  +22.4                                         |    +26.0
    src.softscatnorm:      -7.0|**     *  * * *     *   **     ***  * *   *   *   * *   *  *  **   **************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.21  **  -0.19                                         |    +1.00

    Z=-1575.2(31.36%) | Like=-1555.54..-1551.87 [-1555.5437..-1555.5419]*| it/evals=8099/142743 eff=5.6898% N=400 

    Mono-modal Volume: ~exp(-19.01) * Expected Volume: exp(-20.25) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.89
    src.level       :      -8.0|              -5.3  ***  -4.9                                                    |     +3.0
    torus.phoindex  :      +1.2|       +1.5  **********************  +1.9                                        |     +2.8
    src.nH          :     +20.0|                     +22.1  *****  +22.4                                         |    +26.0
    src.softscatnorm:      -7.0| *      *  **       *   **     *      *   *   *   **       *  **   **************|     -1.0
    pca1.lognorm    :     -1.00|                        -0.21  **  -0.19                                         |    +1.00

    Z=-1575.1(35.17%) | Like=-1555.29..-1551.87 [-1555.2946..-1555.2931]*| it/evals=8189/157441 eff=5.2146% N=400 

    Mono-modal Volume: ~exp(-19.78) * Expected Volume: exp(-20.48) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.97
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.88
    src.level       :      -8.0|              -5.3  ***  -5.0                                                    |     +3.0
    torus.phoindex  :      +1.2|        +1.5  *********************  +1.9                                        |     +2.8
    src.nH          :     +20.0|                     +22.1  *****  +22.4                                         |    +26.0
    src.softscatnorm:      -7.0|         *  *       *    ** *  *      *   *     * **       *       **** *********|     -1.0
    pca1.lognorm    :     -1.00|                        -0.21  **  -0.19                                         |    +1.00

    Z=-1575.0(39.34%) | Like=-1555.06..-1551.87 [-1555.0551..-1555.0517]*| it/evals=8279/170357 eff=4.8712% N=400 

    Mono-modal Volume: ~exp(-19.78)   Expected Volume: exp(-20.70) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.87
    src.level       :      -8.0|              -5.3  ***  -5.0                                                    |     +3.0
    torus.phoindex  :      +1.2|        +1.5  *********************  +1.9                                        |     +2.8
    src.nH          :     +20.0|                     +22.1  *****  +22.4                                         |    +26.0
    src.softscatnorm:      -7.0|         *                *    *      *   *     *          *       **** *********|     -1.0
    pca1.lognorm    :     -1.00|                        -0.21  **  -0.19                                         |    +1.00

    Z=-1574.9(43.32%) | Like=-1554.82..-1551.87 [-1554.8210..-1554.8210]*| it/evals=8369/183052 eff=4.5819% N=400 

    Mono-modal Volume: ~exp(-19.78)   Expected Volume: exp(-20.93) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.88
    src.level       :      -8.0|              -5.3  ***  -5.0                                                    |     +3.0
    torus.phoindex  :      +1.2|        +1.5  ******************* *  +1.9                                        |     +2.8
    src.nH          :     +20.0|                     +22.1  *****  +22.4                                         |    +26.0
    src.softscatnorm:      -7.0|         *                *          **                    *     * *  * *********|     -1.0
    pca1.lognorm    :     -1.00|                        -0.21  **  -0.19                                         |    +1.00

    Z=-1574.8(47.39%) | Like=-1554.58..-1551.59 [-1554.5798..-1554.5769]*| it/evals=8459/192463 eff=4.4043% N=400 

    Mono-modal Volume: ~exp(-19.78)   Expected Volume: exp(-21.15) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.92
       positive degeneracy between src.nH and torus.phoindex: rho=0.87
    src.level       :      -8.0|             -5.3  ****  -5.0                                                    |     +3.0
    torus.phoindex  :      +1.2|          *   *******************  +1.9                                          |     +2.8
    src.nH          :     +20.0|                      +22.2  ****  +22.4                                         |    +26.0
    src.softscatnorm:      -7.0|                                                           -2.1  *       ********|     -1.0
    pca1.lognorm    :     -1.00|                        -0.21  **  -0.19                                         |    +1.00

    Z=-1574.7(51.01%) | Like=-1554.37..-1551.59 [-1554.3701..-1554.3676]*| it/evals=8549/202006 eff=4.2404% N=400 

    Mono-modal Volume: ~exp(-20.87) * Expected Volume: exp(-21.38) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.88
    src.level       :      -8.0|             -5.3  ****  -5.0                                                    |     +3.0
    torus.phoindex  :      +1.2|          *   ******************  +1.8                                           |     +2.8
    src.nH          :     +20.0|                      +22.2  ****  +22.4                                         |    +26.0
    src.softscatnorm:      -7.0|                                                                 -1.7  * ********|     -1.0
    pca1.lognorm    :     -1.00|                        -0.21  **  -0.19                                         |    +1.00

    Z=-1574.6(54.68%) | Like=-1554.15..-1551.59 [-1554.1479..-1554.1422]*| it/evals=8638/205659 eff=4.2083% N=400 

    Mono-modal Volume: ~exp(-20.87)   Expected Volume: exp(-21.60) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.89
    src.level       :      -8.0|             -5.3  ****  -5.0                                                    |     +3.0
    torus.phoindex  :      +1.2|          *   ******************  +1.8                                           |     +2.8
    src.nH          :     +20.0|                      +22.2  ****  +22.4                                         |    +26.0
    src.softscatnorm:      -7.0|                                                                 -1.7  *  *******|     -1.0
    pca1.lognorm    :     -1.00|                        -0.21  **  -0.19                                         |    +1.00

    Z=-1574.6(58.99%) | Like=-1553.94..-1551.59 [-1553.9423..-1553.9392]*| it/evals=8727/210178 eff=4.1601% N=400 

    Mono-modal Volume: ~exp(-22.50) * Expected Volume: exp(-21.83) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.88
    src.level       :      -8.0|              -5.3  ***  -5.0                                                    |     +3.0
    torus.phoindex  :      +1.2|        +1.5  ******************  +1.8                                           |     +2.8
    src.nH          :     +20.0|                      +22.2  ****  +22.4                                         |    +26.0
    src.softscatnorm:      -7.0|                                                                     -1.4  ******|     -1.0
    pca1.lognorm    :     -1.00|                        -0.21  **  -0.19                                         |    +1.00

    Z=-1574.5(63.37%) | Like=-1553.75..-1551.59 [-1553.7459..-1553.7455]*| it/evals=8819/211888 eff=4.1700% N=400 

    Mono-modal Volume: ~exp(-22.50)   Expected Volume: exp(-22.05) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.89
    src.level       :      -8.0|              -5.3  ***  -5.0                                                    |     +3.0
    torus.phoindex  :      +1.2|        +1.5  ******************  +1.8                                           |     +2.8
    src.nH          :     +20.0|                      +22.2  ****  +22.4                                         |    +26.0
    src.softscatnorm:      -7.0|                                                                     -1.4  ******|     -1.0
    pca1.lognorm    :     -1.00|                        -0.21  **  -0.19                                         |    +1.00

    Z=-1574.4(67.79%) | Like=-1553.55..-1551.59 [-1553.5544..-1553.5517]*| it/evals=8909/213905 eff=4.1727% N=400 

    Mono-modal Volume: ~exp(-22.63) * Expected Volume: exp(-22.28) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.89
    src.level       :      -8.0|              -5.3  ***  -5.0                                                    |     +3.0
    torus.phoindex  :      +1.2|        +1.5  ******************  +1.8                                           |     +2.8
    src.nH          :     +20.0|                      +22.2  ****  +22.4                                         |    +26.0
    src.softscatnorm:      -7.0|                                                                     -1.4  ******|     -1.0
    pca1.lognorm    :     -1.00|                        -0.21  **  -0.19                                         |    +1.00

    Z=-1574.4(71.84%) | Like=-1553.39..-1551.59 [-1553.3907..-1553.3904]*| it/evals=8999/216150 eff=4.1710% N=400 

    Mono-modal Volume: ~exp(-22.63)   Expected Volume: exp(-22.50) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.90
    src.level       :      -8.0|             -5.3  ****  -5.0                                                    |     +3.0
    torus.phoindex  :      +1.2|      +1.5  * ******************  +1.8                                           |     +2.8
    src.nH          :     +20.0|                      +22.2  ****  +22.4                                         |    +26.0
    src.softscatnorm:      -7.0|                                                                      -1.3  *****|     -1.0
    pca1.lognorm    :     -1.00|                         -0.21  *  -0.19                                         |    +1.00

    Z=-1574.3(74.76%) | Like=-1553.25..-1551.59 [-1553.2478..-1553.2465]*| it/evals=9089/218373 eff=4.1698% N=400 

    Mono-modal Volume: ~exp(-22.63)   Expected Volume: exp(-22.73) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.90
    src.level       :      -8.0|             -5.3  ***  -5.0                                                     |     +3.0
    torus.phoindex  :      +1.2|      +1.5  * ****************  +1.8                                             |     +2.8
    src.nH          :     +20.0|                      +22.2  ****  +22.4                                         |    +26.0
    src.softscatnorm:      -7.0|                                                                      -1.3  *****|     -1.0
    pca1.lognorm    :     -1.00|                         -0.21  *  -0.19                                         |    +1.00

    Z=-1574.3(77.99%) | Like=-1553.11..-1551.59 [-1553.1059..-1553.1031]*| it/evals=9179/220699 eff=4.1666% N=400 

    Mono-modal Volume: ~exp(-22.90) * Expected Volume: exp(-22.95) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.90
    src.level       :      -8.0|             -5.3  ***  -5.0                                                     |     +3.0
    torus.phoindex  :      +1.2|      +1.5  * ****************  +1.8                                             |     +2.8
    src.nH          :     +20.0|                      +22.2  ****  +22.4                                         |    +26.0
    src.softscatnorm:      -7.0|                                                                      -1.3  *****|     -1.0
    pca1.lognorm    :     -1.00|                         -0.21  *  -0.19                                         |    +1.00

    Z=-1574.3(80.72%) | Like=-1552.98..-1551.53 [-1552.9756..-1552.9731]*| it/evals=9266/223137 eff=4.1601% N=400 

    Mono-modal Volume: ~exp(-22.90)   Expected Volume: exp(-23.18) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.89
    src.level       :      -8.0|             -5.3  ***  -5.0                                                     |     +3.0
    torus.phoindex  :      +1.2|      +1.5  *  ***************  +1.8                                             |     +2.8
    src.nH          :     +20.0|                      +22.2  ****  +22.4                                         |    +26.0
    src.softscatnorm:      -7.0|                                                                        -1.2  ***|     -1.0
    pca1.lognorm    :     -1.00|                         -0.21  *  -0.19                                         |    +1.00

    Z=-1574.2(83.31%) | Like=-1552.88..-1551.53 [-1552.8772..-1552.8767]*| it/evals=9354/224790 eff=4.1686% N=400 

    Mono-modal Volume: ~exp(-23.18) * Expected Volume: exp(-23.40) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.88
    src.level       :      -8.0|             -5.3  ***  -5.0                                                     |     +3.0
    torus.phoindex  :      +1.2|      +1.5  * ****************  +1.8                                             |     +2.8
    src.nH          :     +20.0|                      +22.2  ***  +22.4                                          |    +26.0
    src.softscatnorm:      -7.0|                                                                        -1.2  ***|     -1.0
    pca1.lognorm    :     -1.00|                         -0.21  *  -0.19                                         |    +1.00

    Z=-1574.2(85.47%) | Like=-1552.76..-1551.41 [-1552.7619..-1552.7619]*| it/evals=9448/226892 eff=4.1714% N=400 

    Mono-modal Volume: ~exp(-23.31) * Expected Volume: exp(-23.63) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.87
    src.level       :      -8.0|             -5.3  ***  -5.0                                                     |     +3.0
    torus.phoindex  :      +1.2|      +1.5  * ****************  +1.8                                             |     +2.8
    src.nH          :     +20.0|                      +22.2  ***  +22.4                                          |    +26.0
    src.softscatnorm:      -7.0|                                                                        -1.2  ***|     -1.0
    pca1.lognorm    :     -1.00|                         -0.21  *  -0.19                                         |    +1.00

    Z=-1574.2(87.39%) | Like=-1552.65..-1551.41 [-1552.6486..-1552.6479]*| it/evals=9538/229325 eff=4.1664% N=400 

    Mono-modal Volume: ~exp(-23.32) * Expected Volume: exp(-23.85) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.89
    src.level       :      -8.0|             -5.3  ***  -5.0                                                     |     +3.0
    torus.phoindex  :      +1.2|      +1.5  * ***************  +1.8                                              |     +2.8
    src.nH          :     +20.0|                      +22.2  ***  +22.4                                          |    +26.0
    src.softscatnorm:      -7.0|                                                                        -1.2  ***|     -1.0
    pca1.lognorm    :     -1.00|                         -0.21  *  -0.20                                         |    +1.00

    Z=-1574.2(89.23%) | Like=-1552.57..-1551.41 [-1552.5707..-1552.5678]*| it/evals=9626/232205 eff=4.1526% N=400 

    Mono-modal Volume: ~exp(-24.74) * Expected Volume: exp(-24.08) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.88
    src.level       :      -8.0|             -5.3  ***  -5.0                                                     |     +3.0
    torus.phoindex  :      +1.2|      +1.5  * ***************  +1.8                                              |     +2.8
    src.nH          :     +20.0|                      +22.2  ***  +22.4                                          |    +26.0
    src.softscatnorm:      -7.0|                                                                        -1.2  ***|     -1.0
    pca1.lognorm    :     -1.00|                         -0.21  *  -0.20                                         |    +1.00

    Z=-1574.1(90.80%) | Like=-1552.45..-1551.41 [-1552.4544..-1552.4532]*| it/evals=9717/234184 eff=4.1564% N=400 

    Mono-modal Volume: ~exp(-24.94) * Expected Volume: exp(-24.30) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.89
    src.level       :      -8.0|             -5.3  ***  -5.0                                                     |     +3.0
    torus.phoindex  :      +1.2|      +1.5  * ***************  +1.8                                              |     +2.8
    src.nH          :     +20.0|                      +22.2  ***  +22.3                                          |    +26.0
    src.softscatnorm:      -7.0|                                                                         -1.1  **|     -1.0
    pca1.lognorm    :     -1.00|                         -0.21  *  -0.20                                         |    +1.00

    Z=-1574.1(92.08%) | Like=-1552.37..-1551.40 [-1552.3716..-1552.3709]*| it/evals=9804/235548 eff=4.1693% N=400 

    Mono-modal Volume: ~exp(-25.28) * Expected Volume: exp(-24.53) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.89
    src.level       :      -8.0|             -5.3  ***  -5.0                                                     |     +3.0
    torus.phoindex  :      +1.2|      +1.5  * ***************  +1.8                                              |     +2.8
    src.nH          :     +20.0|                      +22.2  ***  +22.3                                          |    +26.0
    src.softscatnorm:      -7.0|                                                                         -1.1  **|     -1.0
    pca1.lognorm    :     -1.00|                         -0.21  *  -0.20                                         |    +1.00

    Z=-1574.1(93.30%) | Like=-1552.28..-1551.40 [-1552.2766..-1552.2766]*| it/evals=9895/236970 eff=4.1827% N=400 

    Mono-modal Volume: ~exp(-25.52) * Expected Volume: exp(-24.75) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.89
    src.level       :      -8.0|              -5.3  **  -5.0                                                     |     +3.0
    torus.phoindex  :      +1.2|        +1.5  ***************  +1.8                                              |     +2.8
    src.nH          :     +20.0|                      +22.2  ***  +22.3                                          |    +26.0
    src.softscatnorm:      -7.0|                                                                         -1.1  **|     -1.0
    pca1.lognorm    :     -1.00|                         -0.21  *  -0.20                                         |    +1.00

    Z=-1574.1(94.40%) | Like=-1552.21..-1551.40 [-1552.2052..-1552.2048]*| it/evals=9987/238449 eff=4.1954% N=400 

    Mono-modal Volume: ~exp(-25.52)   Expected Volume: exp(-24.98) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.90
    src.level       :      -8.0|              -5.3  **  -5.1                                                     |     +3.0
    torus.phoindex  :      +1.2|        +1.5  ***************  +1.8                                              |     +2.8
    src.nH          :     +20.0|                      +22.2  ***  +22.3                                          |    +26.0
    src.softscatnorm:      -7.0|                                                                         -1.1  **|     -1.0
    pca1.lognorm    :     -1.00|                         -0.21  *  -0.20                                         |    +1.00

    Z=-1574.1(95.31%) | Like=-1552.15..-1551.39 [-1552.1456..-1552.1439]*| it/evals=10077/240066 eff=4.2046% N=400 

    Mono-modal Volume: ~exp(-25.52)   Expected Volume: exp(-25.20) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.89
    src.level       :      -8.0|              -5.3  **  -5.1                                                     |     +3.0
    torus.phoindex  :      +1.2|        +1.5  ***************  +1.8                                              |     +2.8
    src.nH          :     +20.0|                      +22.2  ***  +22.3                                          |    +26.0
    src.softscatnorm:      -7.0|                                                                         -1.1  **|     -1.0
    pca1.lognorm    :     -1.00|                         -0.21  *  -0.20                                         |    +1.00

    Z=-1574.1(96.12%) | Like=-1552.08..-1551.39 [-1552.0780..-1552.0775]*| it/evals=10169/241859 eff=4.2115% N=400 

    Mono-modal Volume: ~exp(-25.52)   Expected Volume: exp(-25.43) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.89
    src.level       :      -8.0|              -5.3  **  -5.1                                                     |     +3.0
    torus.phoindex  :      +1.2|        +1.5  ***************  +1.8                                              |     +2.8
    src.nH          :     +20.0|                      +22.2  ***  +22.3                                          |    +26.0
    src.softscatnorm:      -7.0|                                                                         -1.1  **|     -1.0
    pca1.lognorm    :     -1.00|                         -0.21  *  -0.20                                         |    +1.00

    Z=-1574.1(96.75%) | Like=-1552.02..-1551.39 [-1552.0210..-1552.0194]*| it/evals=10258/244611 eff=4.2005% N=400 

    Mono-modal Volume: ~exp(-26.59) * Expected Volume: exp(-25.65) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.88
    src.level       :      -8.0|              -5.3  **  -5.1                                                     |     +3.0
    torus.phoindex  :      +1.2|        +1.5  **************  +1.8                                               |     +2.8
    src.nH          :     +20.0|                      +22.2  ***  +22.3                                          |    +26.0
    src.softscatnorm:      -7.0|                                                                         -1.1  **|     -1.0
    pca1.lognorm    :    -1.000|                        -0.207  *  -0.197                                        |   +1.000

    Z=-1574.1(97.29%) | Like=-1551.97..-1551.39 [-1551.9659..-1551.9658]*| it/evals=10345/246068 eff=4.2110% N=400 

    Mono-modal Volume: ~exp(-26.59)   Expected Volume: exp(-25.88) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.92
       positive degeneracy between src.nH and torus.phoindex: rho=0.87
    src.level       :      -8.0|              -5.3  **  -5.1                                                     |     +3.0
    torus.phoindex  :      +1.2|        +1.5  **************  +1.7                                               |     +2.8
    src.nH          :     +20.0|                      +22.2  ***  +22.3                                          |    +26.0
    src.softscatnorm:      -7.0|                                                                         -1.1  **|     -1.0
    pca1.lognorm    :    -1.000|                        -0.206  *  -0.197                                        |   +1.000

    Z=-1574.1(97.76%) | Like=-1551.91..-1551.35 [-1551.9109..-1551.9102]*| it/evals=10436/247800 eff=4.2183% N=400 

    Mono-modal Volume: ~exp(-26.59)   Expected Volume: exp(-26.10) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.91
       positive degeneracy between src.nH and torus.phoindex: rho=0.85
    src.level       :      -8.0|              -5.3  **  -5.1                                                     |     +3.0
    torus.phoindex  :      +1.2|        +1.5  **************  +1.7                                               |     +2.8
    src.nH          :     +20.0|                      +22.2  ***  +22.3                                          |    +26.0
    src.softscatnorm:      -7.0|                                                                         -1.1  **|     -1.0
    pca1.lognorm    :    -1.000|                        -0.206  *  -0.197                                        |   +1.000

    Z=-1574.1(98.17%) | Like=-1551.86..-1551.35 [-1551.8639..-1551.8639]*| it/evals=10528/249800 eff=4.2213% N=400 

    Mono-modal Volume: ~exp(-26.63) * Expected Volume: exp(-26.33) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.93
       positive degeneracy between src.nH and torus.phoindex: rho=0.89
    src.level       :      -8.0|              -5.3  **  -5.1                                                     |     +3.0
    torus.phoindex  :      +1.2|        +1.5  **************  +1.7                                               |     +2.8
    src.nH          :     +20.0|                      +22.2  ***  +22.3                                          |    +26.0
    src.softscatnorm:      -7.0|                                                                          -1.1  *|     -1.0
    pca1.lognorm    :    -1.000|                        -0.206  *  -0.197                                        |   +1.000

    Z=-1574.1(98.48%) | Like=-1551.83..-1551.35 [-1551.8282..-1551.8280]*| it/evals=10617/251253 eff=4.2324% N=400 

    Mono-modal Volume: ~exp(-27.74) * Expected Volume: exp(-26.55) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.98
       positive degeneracy between src.nH and src.level: rho=0.94
       positive degeneracy between src.nH and torus.phoindex: rho=0.90
    src.level       :      -8.0|              -5.3  **  -5.1                                                     |     +3.0
    torus.phoindex  :      +1.2|        +1.5  **************  +1.7                                               |     +2.8
    src.nH          :     +20.0|                      +22.2  ***  +22.3                                          |    +26.0
    src.softscatnorm:      -7.0|                                                                          -1.1  *|     -1.0
    pca1.lognorm    :    -1.000|                        -0.206  *  -0.197                                        |   +1.000

    Z=-1574.1(98.76%) | Like=-1551.78..-1551.35 [-1551.7806..-1551.7802]*| it/evals=10708/252264 eff=4.2515% N=400 

    Mono-modal Volume: ~exp(-27.74)   Expected Volume: exp(-26.78) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.99
       positive degeneracy between src.nH and src.level: rho=0.95
       positive degeneracy between src.nH and torus.phoindex: rho=0.91
    src.level       :      -8.0|              -5.3  **  -5.1                                                     |     +3.0
    torus.phoindex  :      +1.2|        +1.5  **************  +1.7                                               |     +2.8
    src.nH          :     +20.0|                      +22.2  ***  +22.3                                          |    +26.0
    src.softscatnorm:      -7.0|                                                                          -1.1  *|     -1.0
    pca1.lognorm    :    -1.000|                        -0.205  *  -0.197                                        |   +1.000

    Z=-1574.1(98.98%) | Like=-1551.75..-1551.35 [-1551.7514..-1551.7510]*| it/evals=10798/253662 eff=4.2636% N=400 

    Mono-modal Volume: ~exp(-27.74)   Expected Volume: exp(-27.00) Quality: ok

       positive degeneracy between torus.phoindex and src.level: rho=0.99
       positive degeneracy between src.nH and src.level: rho=0.95
       positive degeneracy between src.nH and torus.phoindex: rho=0.91
    src.level       :      -8.0|              -5.3  **  -5.1                                                     |     +3.0
    torus.phoindex  :      +1.2|        +1.5  **************  +1.7                                               |     +2.8
    src.nH          :     +20.0|                      +22.2  ***  +22.3                                          |    +26.0
    src.softscatnorm:      -7.0|                                                                          -1.1  *|     -1.0
    pca1.lognorm    :    -1.000|                        -0.205  *  -0.197                                        |   +1.000

    [ultranest] Explored until L=-2e+03  551.35 [-1551.7492..-1551.7487]*| it/evals=10806/253825 eff=4.2640% N=400 
    [ultranest INFO]: Explored until L=-2e+03  
    [ultranest] Likelihood function evaluations: 253825
    [ultranest INFO]: Likelihood function evaluations: 253825
    [ultranest] Writing samples and results to disk ...
    [ultranest INFO]: Writing samples and results to disk ...
    [ultranest] Writing samples and results to disk ... done
    [ultranest INFO]: Writing samples and results to disk ... done
    [ultranest]   logZ = -1574 +- 0.1586
    [ultranest INFO]:   logZ = -1574 +- 0.1586
    [ultranest] Posterior uncertainty strategy is satisfied (KL: 0.46+-0.06 nat, need <0.50 nat)
    [ultranest INFO]: Posterior uncertainty strategy is satisfied (KL: 0.46+-0.06 nat, need <0.50 nat)
    [ultranest] Evidency uncertainty strategy is satisfied (dlogz=0.36, need <0.5)
    [ultranest INFO]: Evidency uncertainty strategy is satisfied (dlogz=0.36, need <0.5)
    [ultranest]   logZ error budget: single: 0.22 bs:0.16 tail:0.01 total:0.16 required:<0.50
    [ultranest INFO]:   logZ error budget: single: 0.22 bs:0.16 tail:0.01 total:0.16 required:<0.50
    [ultranest] done iterating.
    [ultranest INFO]: done iterating.

    logZ = -1574.044 +- 0.363
      single instance: logZ = -1574.044 +- 0.219
      bootstrapped   : logZ = -1574.033 +- 0.363
      tail           : logZ = +- 0.010
    insert order U test : converged: False correlation: 10667.0 iterations

        src.level           -5.106 +- 0.071
        torus.phoindex      1.684 +- 0.091
        src.nH              22.292 +- 0.060
        src.softscatnorm    -1.5 +- 1.2
        pca1.lognorm        -0.2012 +- 0.0048
    plotting spectrum ...
    9221/11207 (82.29%)
    calculating intrinsic fluxes and distribution of model spectra
    WARNING: Clearing convolved model
    '(apply_rmf(apply_arf((3746510.0 * (xstablemodel.torus + xstablemodel.scat)))) + (apply_rmf(apply_arf(pca1)) * 0.03082443021040756))'
    for dataset 1
    [sherpa.ui.utils WARNING]: Clearing convolved model
    '(apply_rmf(apply_arf((3746510.0 * (xstablemodel.torus + xstablemodel.scat)))) + (apply_rmf(apply_arf(pca1)) * 0.03082443021040756))'
    for dataset 1
    saving distribution plot data
    

This produces the following output files::

    $ find multiple_out_zspec_*
    multiple_out_zspec_
    multiple_out_zspec_/debug.log
    multiple_out_zspec_/plots
    multiple_out_zspec_/plots/corner.pdf
    multiple_out_zspec_/plots/trace.pdf
    multiple_out_zspec_/plots/run.pdf
    multiple_out_zspec_/info
    multiple_out_zspec_/info/post_summary.csv
    multiple_out_zspec_/info/results.json
    multiple_out_zspec_/results
    multiple_out_zspec_/results/points.hdf5
    multiple_out_zspec_/extra
    multiple_out_zspec_/chains
    multiple_out_zspec_/chains/run.txt
    multiple_out_zspec_/chains/weighted_post_untransformed.txt
    multiple_out_zspec_/chains/equal_weighted_post.txt
    multiple_out_zspec_/chains/weighted_post.txt
    multiple_out_zspec_bkg_1.txt.gz
    multiple_out_zspec_intrinsic_photonflux.dist.gz
    multiple_out_zspec_src_1.txt.gz

"multiple_out_zspec_" is the prefix used when a .z redshift file is provided and it contains a single number.

The most important files are:

* plots/corner.pdf: plot of the parameter constraints and uncertainties and their correlations
* info/results.json: summary of all parameters, their uncertainties and estimated lnZ
* info/post_summary.csv: summary of all parameters and their uncertainties as CSV
* chains/equal_weighted_post.txt: contains posterior samples: each row is a model parameter vector. You can iterate through these, set up the model in pyxspec, and then do something with it (compute fluxes and luminosities, for example).
* multiple_out_zspec_intrinsic_photonflux.dist.gz: contains the posterior distribution of redshifts, photon and energy fluxes (see step 9 in the script code)
