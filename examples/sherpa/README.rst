BXA/Sherpa example scripts
==========================

This folder contains simple and complex examples
how BXA can be invoked for spectral analysis.

Please refer to https://johannesbuchner.github.io/BXA/
for full documentation, including how to install BXA.


Test data
-------------------

As test data, this includes the spectral file example-file.fak
representing a ATHENA observation of an absorbed AGN, and the corresponding 
response.

The spectrum looks something like this:

.. image:: ../xspec/reference-output/data.gif

Simple analysis
-----------------

Have a look at the file example_simplest.py. It contains:

* Loading data
* setting up a model and its parameter ranges
* running a BXA fit with specified priors

See https://johannesbuchner.github.io/BXA/ to understand the code.
See https://johannesbuchner.github.io/UltraNest/ to understand the output of the
fitting engine (for example, its `FAQ page <https://johannesbuchner.github.io/UltraNest/issues.html>`_).

Expected output::

	$ python3 example_simplest.py
	read RMF file athenapp_ir_b4c_wfi_withfilter_fov40.0arcmin_avg.rsp
	[ultranest] Sampling 400 live points from prior ...


	Mono-modal Volume: ~exp(-4.18) * Expected Volume: exp(0.00) Quality: ok

	mypow.PhoIndex:      +1.0|***********************************************************************************|     +3.0
	mypow.norm    :  +1.0e-10|********** *** * ***   *** * * *    * *   *  *    *  *         *    *     *    *   | +1.0e+01

	Z=-1751856.9(0.00%) | Like=-1618084.55..-4292.98 [-1.69e+08..-4793] | it/evals=80/487 eff=91.9540% N=400 0 

	Mono-modal Volume: ~exp(-4.47) * Expected Volume: exp(-0.23) Quality: ok

	mypow.PhoIndex:      +1.0|***********************************************************************************|     +3.0
	mypow.norm    :  +1.0e-10|****************** *** *   * *  *  *   *   *****  **  **  *             *  +8.7e-02| +1.0e-01

	Z=-35380.7(0.00%) | Like=-35235.95..-4292.98 [-1.69e+08..-4793] | it/evals=160/575 eff=91.4286% N=400 0 

	Mono-modal Volume: ~exp(-4.47)   Expected Volume: exp(-0.45) Quality: ok

	mypow.PhoIndex:      +1.0|***********************************************************************************|     +3.0
	mypow.norm    :  +1.0e-10|****************    ***  +2.8e-03                                                  | +1.0e-02

	Z=-27187.5(0.00%) | Like=-27051.37..-4292.98 [-1.69e+08..-4793] | it/evals=240/670 eff=88.8889% N=400 

	Mono-modal Volume: ~exp(-4.72) * Expected Volume: exp(-0.67) Quality: ok

	mypow.PhoIndex:      +1.0|**************************************************************************** ******|     +3.0
	mypow.norm    :  +1.0e-10|****************    **  +2.6e-03                                                   | +1.0e-02

	Z=-22433.1(0.00%) | Like=-22407.73..-4292.98 [-1.69e+08..-4793] | it/evals=320/764 eff=87.9121% N=400 

	Mono-modal Volume: ~exp(-4.97) * Expected Volume: exp(-0.90) Quality: ok

	mypow.PhoIndex:      +1.0|****************************************************************************  *****|     +3.0
	mypow.norm    :  +1.0e-10|****************  +1.9e-03                                                         | +1.0e-02

	Z=-17389.5(0.00%) | Like=-17315.87..-4089.86 [-1.69e+08..-4793] | it/evals=440/902 eff=87.6494% N=400 

	Mono-modal Volume: ~exp(-5.42) * Expected Volume: exp(-1.12) Quality: ok

	mypow.PhoIndex:      +1.0|************************************************************************** **  ****|     +3.0
	mypow.norm    :  +1.0e-10|***************  +1.8e-03                                                          | +1.0e-02

	Z=-14930.7(0.00%) | Like=-14920.84..-4089.86 [-1.69e+08..-4793] | it/evals=520/996 eff=87.2483% N=400 

	Mono-modal Volume: ~exp(-5.61) * Expected Volume: exp(-1.35) Quality: ok

	mypow.PhoIndex:      +1.0|**************************************************************************** * ****|     +3.0
	mypow.norm    :  +1.0e-10|*************  +1.5e-03                                                            | +1.0e-02

	Z=-13003.7(0.00%) | Like=-12933.49..-4036.29 [-1.69e+08..-4793] | it/evals=600/1091 eff=86.8307% N=400 

	Mono-modal Volume: ~exp(-5.90) * Expected Volume: exp(-1.57) Quality: ok

	mypow.PhoIndex:      +1.0|*************************************************************** ********** *** ****|     +3.0
	mypow.norm    :  +1.0e-10|***********  +1.3e-03                                                              | +1.0e-02

	Z=-11638.1(0.00%) | Like=-11629.24..-4014.22 [-1.69e+08..-4793] | it/evals=680/1185 eff=86.6242% N=400 

	Mono-modal Volume: ~exp(-5.90)   Expected Volume: exp(-1.80) Quality: ok

	mypow.PhoIndex:      +1.0|**************************************************************************** *** * |     +3.0
	mypow.norm    :  +1.0e-10|**********  +1.2e-03                                                               | +1.0e-02

	Z=-10056.7(0.00%) | Like=-10045.44..-4014.22 [-1.69e+08..-4793] | it/evals=800/1335 eff=85.5615% N=400 

	Mono-modal Volume: ~exp(-6.35) * Expected Volume: exp(-2.02) Quality: ok

	mypow.PhoIndex:      +1.0|*******************************************************************  **  +2.7      |     +3.0
	mypow.norm    :  +1.0e-10|*********  +1.0e-03                                                                | +1.0e-02

	Z=-9145.1(0.00%) | Like=-9114.83..-4014.22 [-1.69e+08..-4793] | it/evals=880/1445 eff=84.2105% N=400 

	Mono-modal Volume: ~exp(-6.40) * Expected Volume: exp(-2.25) Quality: ok

	mypow.PhoIndex:      +1.0|**************************************************************  +2.5               |     +3.0
	mypow.norm    :  +1.0e-10|*********************************** * *************  * * * * *    ***** *  +8.8e-04| +1.0e-03

	Z=-8511.7(0.00%) | Like=-8496.13..-4014.22 [-1.69e+08..-4793] | it/evals=960/1546 eff=83.7696% N=400 

	Mono-modal Volume: ~exp(-7.13) * Expected Volume: exp(-2.47) Quality: ok

	mypow.PhoIndex:      +1.0|*****************************************************  +2.3                        |     +3.0
	mypow.norm    :  +1.0e-10|************************************* ***** ******** *****   * *  ** **  +8.5e-04  | +1.0e-03

	Z=-7851.9(0.00%) | Like=-7837.07..-4014.22 [-1.69e+08..-4793] | it/evals=1040/1643 eff=83.6685% N=400 

	Mono-modal Volume: ~exp(-7.13)   Expected Volume: exp(-2.70) Quality: ok

	mypow.PhoIndex:      +1.0|************************************************  +2.1                             |     +3.0
	mypow.norm    :  +1.0e-10| ************************************ ***** ***** *   ** **  *    **  +8.2e-04     | +1.0e-03

	Z=-7136.3(0.00%) | Like=-7127.15..-4014.22 [-1.69e+08..-4793] | it/evals=1160/1798 eff=82.9757% N=400 

	Mono-modal Volume: ~exp(-7.13)   Expected Volume: exp(-2.92) Quality: ok

	mypow.PhoIndex:      +1.0|******************************************  +2.0                                   |     +3.0
	mypow.norm    :  +1.0e-10| ************************************ ***** ***** * *  * **   *  +7.5e-04          | +1.0e-03

	Z=-6681.7(0.00%) | Like=-6672.54..-4014.22 [-1.69e+08..-4793] | it/evals=1240/1903 eff=82.5017% N=400 

	Mono-modal Volume: ~exp(-7.13)   Expected Volume: exp(-3.15) Quality: ok

	mypow.PhoIndex:      +1.0|************************************  +1.9                                         |     +3.0
	mypow.norm    :  +1.0e-10| ****************************************** *** * * *  * *  +7.0e-04               | +1.0e-03

	Z=-6273.8(0.00%) | Like=-6263.88..-4014.22 [-1.69e+08..-4793] | it/evals=1320/1996 eff=82.7068% N=400 

	Mono-modal Volume: ~exp(-7.17) * Expected Volume: exp(-3.37) Quality: ok

	mypow.PhoIndex:      +1.0|*******************************  +1.7                                              |     +3.0
	mypow.norm    :  +1.0e-10|  ***************************************** **      *  +6.3e-04                    | +1.0e-03

	Z=-6007.6(0.00%) | Like=-5978.42..-4014.22 [-1.69e+08..-4793] | it/evals=1400/2101 eff=82.3045% N=400 

	Mono-modal Volume: ~exp(-7.54) * Expected Volume: exp(-3.60) Quality: ok

	mypow.PhoIndex:      +1.0|***************************  +1.6                                                  |     +3.0
	mypow.norm    :  +1.0e-10|   **************************************** **  +5.5e-04                           | +1.0e-03

	Z=-5601.9(0.00%) | Like=-5591.90..-4014.22 [-1.69e+08..-4793] | it/evals=1520/2267 eff=81.4140% N=400 

	Mono-modal Volume: ~exp(-7.98) * Expected Volume: exp(-3.82) Quality: ok

	mypow.PhoIndex:      +1.0|************************  +1.6                                                     |     +3.0
	mypow.norm    :  +1.0e-10|   *******************************************  +5.5e-04                           | +1.0e-03

	Z=-5365.4(0.00%) | Like=-5354.72..-3983.52 [-1.69e+08..-4793] | it/evals=1600/2370 eff=81.2183% N=400 

	Mono-modal Volume: ~exp(-8.47) * Expected Volume: exp(-4.05) Quality: ok

	mypow.PhoIndex:      +1.0|********************  +1.5                                                         |     +3.0
	mypow.norm    :  +1.0e-10|   ************************************  +4.6e-04                                  | +1.0e-03

	Z=-5203.1(0.00%) | Like=-5193.15..-3983.52 [-1.69e+08..-4793] | it/evals=1680/2465 eff=81.3559% N=400 

	Mono-modal Volume: ~exp(-8.58) * Expected Volume: exp(-4.27) Quality: ok

	mypow.PhoIndex:      +1.0|******************  +1.4                                                           |     +3.0
	mypow.norm    :  +1.0e-10|    ***********************************  +4.6e-04                                  | +1.0e-03

	Z=-5038.9(0.00%) | Like=-5029.07..-3983.52 [-1.69e+08..-4793] | it/evals=1760/2566 eff=81.2558% N=400 

	Mono-modal Volume: ~exp(-8.58)   Expected Volume: exp(-4.50) Quality: ok

	mypow.PhoIndex:      +1.0|****************  +1.4                                                             |     +3.0
	mypow.norm    :  +1.0e-10|     ********************************  +4.4e-04                                    | +1.0e-03

	Z=-4851.6(0.00%) | Like=-4840.10..-3983.52 [-1.69e+08..-4793] | it/evals=1880/2732 eff=80.6175% N=400 

	Mono-modal Volume: ~exp(-8.86) * Expected Volume: exp(-4.73) Quality: ok

	mypow.PhoIndex:      +1.0|**************  +1.3                                                               |     +3.0
	mypow.norm    :  +1.0e-10|     ******************************  +4.2e-04                                      | +1.0e-03

	Z=-4738.8(0.00%) | Like=-4728.77..-3971.79 [-4792.1998..-3996.6500] | it/evals=1960/2840 eff=80.3279% N=400 

	Mono-modal Volume: ~exp(-9.17) * Expected Volume: exp(-4.95) Quality: ok

	mypow.PhoIndex:      +1.0|************  +1.3                                                                 |     +3.0
	mypow.norm    :  +1.0e-10|      ****************************  +4.0e-04                                       | +1.0e-03

	Z=-4641.1(0.00%) | Like=-4628.17..-3971.79 [-4792.1998..-3996.6500] | it/evals=2040/2944 eff=80.1887% N=400 

	Mono-modal Volume: ~exp(-9.50) * Expected Volume: exp(-5.18) Quality: ok

	mypow.PhoIndex:      +1.0|**********  +1.2                                                                   |     +3.0
	mypow.norm    :  +1.0e-10|      ***************************  +3.9e-04                                        | +1.0e-03

	Z=-4550.0(0.00%) | Like=-4539.21..-3964.70 [-4792.1998..-3996.6500] | it/evals=2120/3047 eff=80.0907% N=400 

	Mono-modal Volume: ~exp(-9.98) * Expected Volume: exp(-5.40) Quality: ok

	mypow.PhoIndex:      +1.0|*********  +1.2                                                                    |     +3.0
	mypow.norm    :  +1.0e-10|       ************************  +3.6e-04                                          | +1.0e-03

	Z=-4446.3(0.00%) | Like=-4434.45..-3963.07 [-4792.1998..-3996.6500] | it/evals=2240/3201 eff=79.9714% N=400 

	Mono-modal Volume: ~exp(-9.98)   Expected Volume: exp(-5.63) Quality: ok

	mypow.PhoIndex:      +1.0|********  +1.2                                                                     |     +3.0
	mypow.norm    :  +1.0e-10|       **********************  +3.5e-04                                            | +1.0e-03

	Z=-4385.8(0.00%) | Like=-4374.52..-3963.07 [-4792.1998..-3996.6500] | it/evals=2320/3300 eff=80.0000% N=400 

	Mono-modal Volume: ~exp(-9.98)   Expected Volume: exp(-5.85) Quality: ok

	mypow.PhoIndex:      +1.0|*******  +1.2                                                                      |     +3.0
	mypow.norm    :  +1.0e-10|        *********************  +3.4e-04                                            | +1.0e-03

	Z=-4336.2(0.00%) | Like=-4324.51..-3963.07 [-4792.1998..-3996.6500] | it/evals=2400/3403 eff=79.9201% N=400 

	Mono-modal Volume: ~exp(-10.07) * Expected Volume: exp(-6.08) Quality: ok

	mypow.PhoIndex:      +1.0|******  +1.1                                                                       |     +3.0
	mypow.norm    :   +0.0000|        ********************  +0.0003                                              |  +0.0010

	Z=-4293.3(0.00%) | Like=-4281.53..-3957.55 [-4792.1998..-3996.6500] | it/evals=2480/3508 eff=79.7941% N=400 

	Mono-modal Volume: ~exp(-10.38) * Expected Volume: exp(-6.30) Quality: ok

	mypow.PhoIndex:      +1.0|*****  +1.1                                                                        |     +3.0
	mypow.norm    :   +0.0000|         *****************  +0.0003                                                |  +0.0010

	Z=-4228.9(0.00%) | Like=-4217.46..-3957.55 [-4792.1998..-3996.6500] | it/evals=2600/3662 eff=79.7057% N=400 

	Mono-modal Volume: ~exp(-10.63) * Expected Volume: exp(-6.53) Quality: ok

	mypow.PhoIndex:      +1.0|*****  +1.1                                                                        |     +3.0
	mypow.norm    :   +0.0000|         *****************  +0.0003                                                |  +0.0010

	Z=-4195.0(0.00%) | Like=-4182.98..-3957.55 [-4792.1998..-3996.6500] | it/evals=2680/3770 eff=79.5252% N=400 

	Mono-modal Volume: ~exp(-11.36) * Expected Volume: exp(-6.75) Quality: ok

	mypow.PhoIndex:      +1.0|****  +1.1                                                                         |     +3.0
	mypow.norm    :   +0.0000|         ****************  +0.0003                                                 |  +0.0010

	Z=-4166.7(0.00%) | Like=-4155.08..-3957.55 [-4792.1998..-3996.6500] | it/evals=2760/3875 eff=79.4245% N=400 

	Mono-modal Volume: ~exp(-11.36)   Expected Volume: exp(-6.98) Quality: ok

	mypow.PhoIndex:      +1.0|****  +1.1                                                                         |     +3.0
	mypow.norm    :   +0.0000|          ***************  +0.0003                                                 |  +0.0010

	Z=-4143.4(0.00%) | Like=-4129.42..-3951.45 [-4792.1998..-3996.6500] | it/evals=2840/3970 eff=79.5518% N=400 

	Mono-modal Volume: ~exp(-11.36)   Expected Volume: exp(-7.20) Quality: ok

	mypow.PhoIndex:      +1.0|***  +1.1                                                                          |     +3.0
	mypow.norm    :   +0.0000|          **************  +0.0003                                                  |  +0.0010

	Z=-4111.1(0.00%) | Like=-4099.43..-3951.45 [-4792.1998..-3996.6500] | it/evals=2960/4133 eff=79.2928% N=400 

	Mono-modal Volume: ~exp(-11.54) * Expected Volume: exp(-7.43) Quality: ok

	mypow.PhoIndex:      +1.0|***  +1.1                                                                          |     +3.0
	mypow.norm    :   +0.0000|  +0.0001  ************  +0.0003                                                   |  +0.0010

	Z=-4097.6(0.00%) | Like=-4085.70..-3951.45 [-4792.1998..-3996.6500] | it/evals=3040/4233 eff=79.3112% N=400 

	Mono-modal Volume: ~exp(-11.77) * Expected Volume: exp(-7.65) Quality: ok

	mypow.PhoIndex:     +1.00|***  +1.05                                                                         |    +3.00
	mypow.norm    :   +0.0000|  +0.0001  ************  +0.0003                                                   |  +0.0010

	Z=-4081.9(0.00%) | Like=-4069.83..-3951.45 [-4792.1998..-3996.6500] | it/evals=3120/4330 eff=79.3893% N=400 

	Mono-modal Volume: ~exp(-12.28) * Expected Volume: exp(-7.88) Quality: ok

	mypow.PhoIndex:     +1.00|**  +1.04                                                                          |    +3.00
	mypow.norm    :   +0.0000|  +0.0001  ***********  +0.0003                                                    |  +0.0010

	Z=-4064.9(0.00%) | Like=-4052.76..-3951.45 [-4792.1998..-3996.6500] | it/evals=3200/4431 eff=79.3848% N=400 

	Mono-modal Volume: ~exp(-12.39) * Expected Volume: exp(-8.10) Quality: ok

	mypow.PhoIndex:     +1.00|**  +1.04                                                                          |    +3.00
	mypow.norm    :   +0.0000|  +0.0001  ***********  +0.0003                                                    |  +0.0010

	Z=-4046.8(0.00%) | Like=-4034.00..-3951.45 [-4792.1998..-3996.6500] | it/evals=3320/4578 eff=79.4639% N=400 

	Mono-modal Volume: ~exp(-12.73) * Expected Volume: exp(-8.33) Quality: ok

	mypow.PhoIndex:     +1.00|**  +1.03                                                                          |    +3.00
	mypow.norm    :   +0.0000|   +0.0001  **********  +0.0003                                                    |  +0.0010

	Z=-4036.1(0.00%) | Like=-4023.75..-3951.45 [-4792.1998..-3996.6500] | it/evals=3400/4677 eff=79.4950% N=400 

	Mono-modal Volume: ~exp(-12.73)   Expected Volume: exp(-8.55) Quality: ok

	mypow.PhoIndex:     +1.00|**  +1.03                                                                          |    +3.00
	mypow.norm    :  +0.00000|  +0.00015  *********  +0.00025                                                    | +0.00100

	Z=-4028.1(0.00%) | Like=-4015.62..-3951.45 [-4792.1998..-3996.6500] | it/evals=3480/4781 eff=79.4339% N=400 

	Mono-modal Volume: ~exp(-13.13) * Expected Volume: exp(-8.78) Quality: ok

	mypow.PhoIndex:     +1.00|*  +1.02                                                                           |    +3.00
	mypow.norm    :  +0.00000|  +0.00015  *********  +0.00024                                                    | +0.00100

	Z=-4020.5(0.00%) | Like=-4008.05..-3951.45 [-4792.1998..-3996.6500] | it/evals=3560/4878 eff=79.4998% N=400 

	Mono-modal Volume: ~exp(-13.31) * Expected Volume: exp(-9.00) Quality: ok

	mypow.PhoIndex:     +1.00|*  +1.02                                                                           |    +3.00
	mypow.norm    :  +0.00000|   +0.00016  *******  +0.00024                                                     | +0.00100

	Z=-4010.1(0.00%) | Like=-3997.18..-3951.45 [-4792.1998..-3996.6500] | it/evals=3680/5020 eff=79.6537% N=400 

	Mono-modal Volume: ~exp(-13.31)   Expected Volume: exp(-9.23) Quality: ok

	mypow.PhoIndex:     +1.00|*  +1.02                                                                           |    +3.00
	mypow.norm    :  +0.00000|   +0.00016  *******  +0.00024                                                     | +0.00100

	Z=-4004.0(0.00%) | Like=-3990.83..-3951.45 [-3996.5018..-3957.5958] | it/evals=3760/5130 eff=79.4926% N=400 

	Mono-modal Volume: ~exp(-13.47) * Expected Volume: exp(-9.45) Quality: ok

	mypow.PhoIndex:     +1.00|*  +1.01                                                                           |    +3.00
	mypow.norm    :  +0.00000|   +0.00016  *******  +0.00023                                                     | +0.00100

	Z=-3998.1(0.00%) | Like=-3985.07..-3951.45 [-3996.5018..-3957.5958] | it/evals=3840/5231 eff=79.4866% N=400 

	Mono-modal Volume: ~exp(-13.87) * Expected Volume: exp(-9.68) Quality: ok

	mypow.PhoIndex:     +1.00|*  +1.01                                                                           |    +3.00
	mypow.norm    :  +0.00000|   +0.00017  *******  +0.00023                                                     | +0.00100

	Z=-3993.5(0.00%) | Like=-3980.50..-3951.45 [-3996.5018..-3957.5958] | it/evals=3920/5337 eff=79.4004% N=400 

	Mono-modal Volume: ~exp(-14.06) * Expected Volume: exp(-9.90) Quality: ok

	mypow.PhoIndex:     +1.00|*  +1.01                                                                           |    +3.00
	mypow.norm    :  +0.00000|   +0.00017  *******  +0.00023                                                     | +0.00100

	Z=-3988.5(0.00%) | Like=-3975.65..-3951.42 [-3996.5018..-3957.5958] | it/evals=4040/5496 eff=79.2779% N=400 

	Mono-modal Volume: ~exp(-14.45) * Expected Volume: exp(-10.13) Quality: ok

	mypow.PhoIndex:    +1.000|*  +1.009                                                                          |   +3.000
	mypow.norm    :  +0.00000|    +0.00017  *****  +0.00023                                                      | +0.00100

	Z=-3985.3(0.00%) | Like=-3972.21..-3951.42 [-3996.5018..-3957.5958] | it/evals=4120/5601 eff=79.2155% N=400 

	Mono-modal Volume: ~exp(-14.45)   Expected Volume: exp(-10.35) Quality: ok

	mypow.PhoIndex:    +1.000|*  +1.008                                                                          |   +3.000
	mypow.norm    :  +0.00000|    +0.00017  *****  +0.00022                                                      | +0.00100

	Z=-3982.7(0.00%) | Like=-3969.75..-3951.42 [-3996.5018..-3957.5958] | it/evals=4200/5701 eff=79.2303% N=400 

	Mono-modal Volume: ~exp(-14.45)   Expected Volume: exp(-10.58) Quality: ok

	mypow.PhoIndex:    +1.000|*  +1.007                                                                          |   +3.000
	mypow.norm    :  +0.00000|    +0.00017  *****  +0.00022                                                      | +0.00100

	Z=-3980.4(0.00%) | Like=-3967.22..-3951.42 [-3996.5018..-3957.5958] | it/evals=4280/5801 eff=79.2446% N=400 

	Mono-modal Volume: ~exp(-14.59) * Expected Volume: exp(-10.80) Quality: ok

	mypow.PhoIndex:    +0.000|                   +1.000  *  +1.006                                               |   +3.000
	mypow.norm    :  +0.00000|    +0.00017  *****  +0.00022                                                      | +0.00100

	Z=-3977.2(0.00%) | Like=-3963.98..-3951.42 [-3996.5018..-3957.5958] | it/evals=4400/5982 eff=78.8248% N=400 

	Mono-modal Volume: ~exp(-15.69) * Expected Volume: exp(-11.02) Quality: ok

	mypow.PhoIndex:    +1.000|*  +1.005                                                                          |   +3.000
	mypow.norm    :  +0.00000|    +0.00018  *****  +0.00022                                                      | +0.00100

	Z=-3975.6(0.00%) | Like=-3962.46..-3951.42 [-3996.5018..-3957.5958] | it/evals=4480/6082 eff=78.8455% N=400 

	Mono-modal Volume: ~exp(-15.69)   Expected Volume: exp(-11.25) Quality: ok

	mypow.PhoIndex:    +1.000|*  +1.004                                                                          |   +3.000
	mypow.norm    :  +0.00000|    +0.00018  ****  +0.00022                                                       | +0.00100

	Z=-3974.3(0.02%) | Like=-3961.07..-3951.42 [-3996.5018..-3957.5958] | it/evals=4560/6182 eff=78.8654% N=400 

	Mono-modal Volume: ~exp(-15.79) * Expected Volume: exp(-11.47) Quality: ok

	mypow.PhoIndex:    +1.000|*  +1.004                                                                          |   +3.000
	mypow.norm    :  +0.00000|    +0.00018  ****  +0.00021                                                       | +0.00100

	Z=-3973.1(0.05%) | Like=-3959.76..-3951.42 [-3996.5018..-3957.5958] | it/evals=4640/6279 eff=78.9250% N=400 

	Mono-modal Volume: ~exp(-15.79)   Expected Volume: exp(-11.70) Quality: ok

	mypow.PhoIndex:    +1.000|*  +1.003                                                                          |   +3.000
	mypow.norm    :  +0.00000|    +0.00018  ****  +0.00021                                                       | +0.00100

	Z=-3971.6(0.27%) | Like=-3958.21..-3951.42 [-3996.5018..-3957.5958] | it/evals=4760/6439 eff=78.8210% N=400 

	Mono-modal Volume: ~exp(-16.30) * Expected Volume: exp(-11.92) Quality: ok

	mypow.PhoIndex:    +1.000|*  +1.003                                                                          |   +3.000
	mypow.norm    :  +0.00000|     +0.00018  ***  +0.00021                                                       | +0.00100

	Z=-3970.7(0.61%) | Like=-3957.32..-3951.42 [-3957.5844..-3954.9980] | it/evals=4840/6549 eff=78.7120% N=400 

	Mono-modal Volume: ~exp(-16.54) * Expected Volume: exp(-12.15) Quality: correlation length: 776 (-)

	mypow.PhoIndex:    +1.000|*  +1.002                                                                          |   +3.000
	mypow.norm    :  +0.00000|     +0.00018  ***  +0.00021                                                       | +0.00100

	Z=-3970.0(1.32%) | Like=-3956.53..-3951.42 [-3957.5844..-3954.9980] | it/evals=4920/6648 eff=78.7452% N=400 

	Mono-modal Volume: ~exp(-16.92) * Expected Volume: exp(-12.37) Quality: correlation length: 776 (-)

	mypow.PhoIndex:    +0.000|                   +1.000  *  +1.002                                               |   +3.000
	mypow.norm    :  +0.00000|     +0.00018  ***  +0.00021                                                       | +0.00100

	Z=-3969.4(2.56%) | Like=-3955.73..-3951.42 [-3957.5844..-3954.9980] | it/evals=5000/6761 eff=78.6040% N=400 

	Mono-modal Volume: ~exp(-17.01) * Expected Volume: exp(-12.60) Quality: correlation length: 776 (-)

	mypow.PhoIndex:    +0.000|                   +1.000  *  +1.002                                               |   +3.000
	mypow.norm    :  +0.00000|     +0.00018  ***  +0.00021                                                       | +0.00100

	Z=-3968.6(5.35%) | Like=-3955.08..-3951.42 [-3957.5844..-3954.9980] | it/evals=5120/6904 eff=78.7208% N=400 

	Mono-modal Volume: ~exp(-17.21) * Expected Volume: exp(-12.82) Quality: correlation length: 776 (-)

	mypow.PhoIndex:    +0.000|                   +1.000  *  +1.001                                               |   +3.000
	mypow.norm    :  +0.00000|     +0.00019  ***  +0.00021                                                       | +0.00100

	Z=-3968.2(8.05%) | Like=-3954.52..-3951.35 [-3954.9942..-3954.3317] | it/evals=5200/7012 eff=78.6449% N=400 

	Mono-modal Volume: ~exp(-17.59) * Expected Volume: exp(-13.05) Quality: correlation length: 776 (-)

	mypow.PhoIndex:    +0.000|                   +1.000  *  +1.001                                               |   +3.000
	mypow.norm    :  +0.00000|     +0.00019  ***  +0.00021                                                       | +0.00100

	Z=-3967.8(11.87%) | Like=-3954.02..-3951.35 [-3954.0245..-3954.0104]*| it/evals=5280/7115 eff=78.6299% N=400 

	Mono-modal Volume: ~exp(-17.85) * Expected Volume: exp(-13.27) Quality: correlation length: 776 (-)

	mypow.PhoIndex:    +0.000|                   +1.000  *  +1.001                                               |   +3.000
	mypow.norm    :  +0.00000|     +0.00019  ***  +0.00021                                                       | +0.00100

	Z=-3967.5(16.31%) | Like=-3953.67..-3951.27 [-3953.6724..-3953.6656]*| it/evals=5360/7215 eff=78.6500% N=400 

	Mono-modal Volume: ~exp(-17.85)   Expected Volume: exp(-13.50) Quality: correlation length: 776 (-)

	mypow.PhoIndex:   +0.0000|                  +1.0000  *  +1.0009                                              |  +3.0000
	mypow.norm    :  +0.00000|     +0.00019  ***  +0.00021                                                       | +0.00100

	Z=-3967.1(24.15%) | Like=-3953.27..-3951.24 [-3953.2674..-3953.2585]*| it/evals=5480/7371 eff=78.6114% N=400 

	Mono-modal Volume: ~exp(-17.85)   Expected Volume: exp(-13.72) Quality: correlation length: 776 (-)

	mypow.PhoIndex:   +0.0000|                  +1.0000  *  +1.0008                                              |  +3.0000
	mypow.norm    :  +0.00000|     +0.00019  **  +0.00020                                                        | +0.00100

	Z=-3966.9(29.91%) | Like=-3953.02..-3951.24 [-3953.0237..-3953.0113]*| it/evals=5560/7472 eff=78.6199% N=400 

	Mono-modal Volume: ~exp(-18.15) * Expected Volume: exp(-13.95) Quality: correlation length: 776 (-)

	mypow.PhoIndex:   +0.0000|                  +1.0000  *  +1.0007                                              |  +3.0000
	mypow.norm    :  +0.00000|     +0.00019  **  +0.00020                                                        | +0.00100

	Z=-3966.7(35.97%) | Like=-3952.76..-3951.24 [-3952.7565..-3952.7551]*| it/evals=5640/7579 eff=78.5625% N=400 

	Mono-modal Volume: ~exp(-18.15)   Expected Volume: exp(-14.17) Quality: correlation length: 776 (-)

	mypow.PhoIndex:   +0.0000|                  +1.0000  *  +1.0006                                              |  +3.0000
	mypow.norm    :  +0.00000|     +0.00019  **  +0.00020                                                        | +0.00100

	Z=-3966.6(42.29%) | Like=-3952.55..-3951.24 [-3952.5506..-3952.5480]*| it/evals=5720/7679 eff=78.5822% N=400 

	Mono-modal Volume: ~exp(-18.73) * Expected Volume: exp(-14.40) Quality: correlation length: 776 (-)

	mypow.PhoIndex:   +0.0000|                  +1.0000  *  +1.0005                                              |  +3.0000
	mypow.norm    :  +0.00000|     +0.00019  **  +0.00020                                                        | +0.00100

	Z=-3966.4(51.36%) | Like=-3952.29..-3951.24 [-3952.2937..-3952.2909]*| it/evals=5840/7844 eff=78.4524% N=400 

	Mono-modal Volume: ~exp(-18.98) * Expected Volume: exp(-14.62) Quality: correlation length: 776 (-)

	mypow.PhoIndex:   +0.0000|                  +1.0000  *  +1.0004                                              |  +3.0000
	mypow.norm    :  +0.00000|     +0.00019  **  +0.00020                                                        | +0.00100

	Z=-3966.2(57.40%) | Like=-3952.17..-3951.24 [-3952.1668..-3952.1662]*| it/evals=5920/7949 eff=78.4210% N=400 

	Mono-modal Volume: ~exp(-19.29) * Expected Volume: exp(-14.85) Quality: correlation length: 776 (-)

	mypow.PhoIndex:   +0.0000|                  +1.0000  *  +1.0004                                              |  +3.0000
	mypow.norm    :  +0.00000|     +0.00019  **  +0.00020                                                        | +0.00100

	Z=-3966.2(62.63%) | Like=-3952.05..-3951.24 [-3952.0465..-3952.0465]*| it/evals=6000/8050 eff=78.4314% N=400 

	Mono-modal Volume: ~exp(-19.55) * Expected Volume: exp(-15.07) Quality: correlation length: 776 (-)

	mypow.PhoIndex:   +0.0000|                  +1.0000  *  +1.0003                                              |  +3.0000
	mypow.norm    :  +0.00000|     +0.00019  **  +0.00020                                                        | +0.00100

	Z=-3966.1(67.38%) | Like=-3951.93..-3951.23 [-3951.9281..-3951.9278]*| it/evals=6080/8150 eff=78.4516% N=400 

	Mono-modal Volume: ~exp(-19.56) * Expected Volume: exp(-15.30) Quality: correlation length: 776 (-)

	mypow.PhoIndex:   +0.0000|                  +1.0000  *  +1.0003                                              |  +3.0000
	mypow.norm    : +0.000000|    +0.000191  **  +0.000201                                                       |+0.001000

	Z=-3966.0(73.98%) | Like=-3951.81..-3951.22 [-3951.8081..-3951.8074]*| it/evals=6200/8297 eff=78.5108% N=400 

	Mono-modal Volume: ~exp(-19.93) * Expected Volume: exp(-15.52) Quality: correlation length: 776 (-)

	mypow.PhoIndex:   +0.0000|                  +1.0000  *  +1.0002                                              |  +3.0000
	mypow.norm    : +0.000000|    +0.000192  **  +0.000201                                                       |+0.001000

	Z=-3965.9(77.78%) | Like=-3951.72..-3951.22 [-3951.7221..-3951.7218]*| it/evals=6280/8404 eff=78.4608% N=400 

	Mono-modal Volume: ~exp(-19.93)   Expected Volume: exp(-15.75) Quality: correlation length: 776 (-)

	mypow.PhoIndex:   +0.0000|                  +1.0000  *  +1.0002                                              |  +3.0000
	mypow.norm    : +0.000000|    +0.000192  **  +0.000201                                                       |+0.001000

	Z=-3965.9(81.11%) | Like=-3951.66..-3951.21 [-3951.6627..-3951.6619]*| it/evals=6360/8507 eff=78.4507% N=400 

	Mono-modal Volume: ~exp(-20.42) * Expected Volume: exp(-15.97) Quality: correlation length: 776 (-)

	mypow.PhoIndex:   +0.0000|                  +1.0000  *  +1.0002                                              |  +3.0000
	mypow.norm    : +0.000000|    +0.000193  **  +0.000200                                                       |+0.001000

	Z=-3965.9(84.04%) | Like=-3951.60..-3951.21 [-3951.5972..-3951.5946]*| it/evals=6440/8620 eff=78.3455% N=400 

	Mono-modal Volume: ~exp(-20.67) * Expected Volume: exp(-16.20) Quality: correlation length: 776 (-)

	mypow.PhoIndex:   +0.0000|                  +1.0000  *  +1.0001                                              |  +3.0000
	mypow.norm    : +0.000000|     +0.000193  *  +0.000200                                                       |+0.001000

	Z=-3965.8(87.64%) | Like=-3951.51..-3951.19 [-3951.5065..-3951.5064]*| it/evals=6560/8772 eff=78.3564% N=400 

	Mono-modal Volume: ~exp(-21.00) * Expected Volume: exp(-16.42) Quality: correlation length: 776 (-)

	mypow.PhoIndex:   +0.0000|                  +1.0000  *  +1.0001                                              |  +3.0000
	mypow.norm    : +0.000000|     +0.000193  *  +0.000200                                                       |+0.001000

	Z=-3965.8(89.67%) | Like=-3951.47..-3951.19 [-3951.4659..-3951.4654]*| it/evals=6640/8877 eff=78.3296% N=400 

	Mono-modal Volume: ~exp(-21.00)   Expected Volume: exp(-16.65) Quality: correlation length: 776 (-)

	mypow.PhoIndex:   +0.0000|                  +1.0000  *  +1.0001                                              |  +3.0000
	mypow.norm    : +0.000000|     +0.000193  *  +0.000200                                                       |+0.001000

	Z=-3965.8(91.36%) | Like=-3951.43..-3951.19 [-3951.4342..-3951.4340]*| it/evals=6720/8985 eff=78.2761% N=400 

	Mono-modal Volume: ~exp(-21.33) * Expected Volume: exp(-16.87) Quality: correlation length: 776 (-)

	mypow.PhoIndex:  +0.00000|                 +1.00000  *  +1.00009                                             | +3.00000
	mypow.norm    : +0.000000|     +0.000193  *  +0.000199                                                       |+0.001000

	Z=-3965.8(92.80%) | Like=-3951.40..-3951.19 [-3951.4049..-3951.4047]*| it/evals=6800/9096 eff=78.1969% N=400 

	Mono-modal Volume: ~exp(-21.87) * Expected Volume: exp(-17.10) Quality: correlation length: 776 (-)

	mypow.PhoIndex:  +0.00000|                 +1.00000  *  +1.00008                                             | +3.00000
	mypow.norm    : +0.000000|     +0.000194  *  +0.000199                                                       |+0.001000

	Z=-3965.7(94.55%) | Like=-3951.37..-3951.19 [-3951.3653..-3951.3652]*| it/evals=6920/9244 eff=78.2451% N=400 

	Mono-modal Volume: ~exp(-22.01) * Expected Volume: exp(-17.32) Quality: correlation length: 776 (-)

	mypow.PhoIndex:  +0.00000|                 +1.00000  *  +1.00007                                             | +3.00000
	mypow.norm    : +0.000000|     +0.000194  *  +0.000199                                                       |+0.001000

	Z=-3965.7(95.47%) | Like=-3951.34..-3951.19 [-3951.3446..-3951.3444]*| it/evals=7000/9340 eff=78.2998% N=400 

	Mono-modal Volume: ~exp(-22.11) * Expected Volume: exp(-17.55) Quality: correlation length: 776 (-)

	mypow.PhoIndex:  +0.00000|                 +1.00000  *  +1.00006                                             | +3.00000
	mypow.norm    : +0.000000|     +0.000194  *  +0.000199                                                       |+0.001000

	Z=-3965.7(96.25%) | Like=-3951.33..-3951.19 [-3951.3285..-3951.3285]*| it/evals=7080/9445 eff=78.2753% N=400 

	Mono-modal Volume: ~exp(-22.18) * Expected Volume: exp(-17.77) Quality: correlation length: 776 (-)

	mypow.PhoIndex:  +0.00000|                 +1.00000  *  +1.00005                                             | +3.00000
	mypow.norm    : +0.000000|     +0.000194  *  +0.000199                                                       |+0.001000

	Z=-3965.7(96.90%) | Like=-3951.31..-3951.19 [-3951.3115..-3951.3115]*| it/evals=7160/9549 eff=78.2599% N=400 

	Mono-modal Volume: ~exp(-22.60) * Expected Volume: exp(-18.00) Quality: correlation length: 776 (-)

	mypow.PhoIndex:  +0.00000|                 +1.00000  *  +1.00005                                             | +3.00000
	mypow.norm    : +0.000000|     +0.000194  *  +0.000198                                                       |+0.001000

	Z=-3965.7(97.67%) | Like=-3951.29..-3951.19 [-3951.2901..-3951.2901]*| it/evals=7280/9699 eff=78.2880% N=400 

	Mono-modal Volume: ~exp(-22.87) * Expected Volume: exp(-18.23) Quality: correlation length: 776 (-)

	mypow.PhoIndex:  +0.00000|                 +1.00000  *  +1.00004                                             | +3.00000
	mypow.norm    : +0.000000|     +0.000195  *  +0.000198                                                       |+0.001000

	[ultranest] Explored until L=-4e+03  951.19 [-3951.2890..-3951.2883]*| it/evals=7290/9710 eff=78.3029% N=400 
	[ultranest] Likelihood function evaluations: 9715
	[ultranest] Writing samples and results to disk ...
	[ultranest] Writing samples and results to disk ... done
	[ultranest]   logZ = -3966 +- 0.163
	[ultranest] Posterior uncertainty strategy is satisfied (KL: 0.46+-0.07 nat, need <0.50 nat)
	[ultranest] Evidency uncertainty strategy is satisfied (dlogz=0.36, need <0.5)
	[ultranest]   logZ error budget: single: 0.18 bs:0.16 tail:0.02 total:0.16 required:<0.50
	[ultranest] done iterating.

	logZ = -3965.690 +- 0.360
	  single instance: logZ = -3965.690 +- 0.180
	  bootstrapped   : logZ = -3965.647 +- 0.360
	  tail           : logZ = +- 0.022
	insert order U test : converged: True correlation: inf iterations

		mypow.PhoIndex      1.00038 +- 0.00038
		mypow.norm          0.0001964 +- 0.0000044


Output files::

	$ find simplest-/
	simplest-/
	simplest-/debug.log
	simplest-/plots
	simplest-/plots/corner.pdf
	simplest-/plots/trace.pdf
	simplest-/plots/run.pdf
	simplest-/info
	simplest-/info/post_summary.csv
	simplest-/info/results.json
	simplest-/results
	simplest-/results/points.hdf5
	simplest-/extra
	simplest-/chains
	simplest-/chains/run.txt
	simplest-/chains/weighted_post_untransformed.txt
	simplest-/chains/equal_weighted_post.txt
	simplest-/chains/weighted_post.txt


"simplest-" is the `outputfiles_basename` defined in the script.

The most important files are:

* plots/corner.pdf:

	.. image:: reference-output/corner.png
	
	Plot of the parameter constraints and uncertainties and their correlations.
	The photon index parameter is hitting the edge of the parameter space,
	and its uncertainties are tiny. This can be a hint that it is a poor model.

* info/results.json: summary of all parameters, their uncertainties and estimated lnZ
* info/post_summary.csv: summary of all parameters and their uncertainties as CSV
* chains/equal_weighted_post.txt: contains posterior samples: each row is a model parameter vector. You can iterate through these, set up the model in pyxspec, and then do something with it (compute fluxes and luminosities, for example).

You probably want to plot the fit as well (after setting to the best fit).

Try modifying the model.

For more information, see https://johannesbuchner.github.io/BXA/sherpa-analysis.html

Other examples
---------------

* Example of PCA background:

  This uses the Swift data file swift/interval0pc.pi.

  First, store the galactic NH value (1.68e+20)
  into the text file swift/interval0pc.pi.nh.

  Then run with::

	$ python3 example_pcabackground.py
	
	....

	loading nH from swift/interval0pc.pi.nh (expecting something like 1e21 in there)
	setting galactic nH to 0.0168 [units of 1e22/cm²]
	[bxa.Fitter INFO]: PCAFitter(for ID=2)
	[bxa.Fitter INFO]: loading PCA information from /home/user/bin/ciao-4.13/ots/lib/python3.7/site-packages/bxa/sherpa/background/swift_xrt_1024.json
	[bxa.Fitter INFO]: fitting background of ID=2 using PCA method
	[bxa.Fitter INFO]: have 2751 background counts for deconvolution
	[bxa.Fitter INFO]: fit: initial PCA decomposition: [ 3.43950638e+00 -2.18629410e-02  7.52750306e-03 -4.07883039e-03
	 -3.49918117e-03 -3.20861431e-03  3.52942831e-03 -5.05089198e-03
	 -9.34656625e-04 -4.86905140e-03  2.29800943e-03]
	[bxa.Fitter INFO]: fit: first full fit done
	[bxa.Fitter INFO]: fit: parameters: [-0.8139987117963805, 0.42489117817206506, 0.03088268390136437, 0.19696313135650556, 0.09137494506325541, -0.17493295963368954, -0.09507225292526847, 0.16435598097773643, -0.058544963240419884, 0.25546836854960586, 0.08241814841520864]
	[bxa.Fitter INFO]: fit: stat: 551.3592848191211
	[bxa.Fitter INFO]: fit: second full fit from zero
	[bxa.Fitter INFO]: fit: parameters: [-0.8139987117963805, 0.42489117817206506, 0.03088268390136437, 0.19696313135650556, 0.09137494506325541, -0.17493295963368954, -0.09507225292526847, 0.16435598097773643, -0.058544963240419884, 0.25546836854960586, 0.08241814841520864]
	[bxa.Fitter INFO]: fit: stat: 551.3592848191096
	[bxa.Fitter INFO]: fit: using zero-fit
	11 parameters, stat=551.36
	--> 10 parameters, stat=552.44
	--> 9 parameters, stat=582.41
	--> 8 parameters, stat=583.58
	--> 7 parameters, stat=682.99
	--> 6 parameters, stat=696.18
	--> 5 parameters, stat=698.64
	--> 4 parameters, stat=707.46
	--> 3 parameters, stat=716.11
	--> 2 parameters, stat=716.63
	--> 1 parameters, stat=1145.24

	Background PCA fitting AIC results:
	-----------------------------------

	stat Ncomp AIC
	1145.2  1 1147.2
	716.6  2 720.6
	716.1  3 722.1
	707.5  4 715.5
	698.6  5 708.6
	696.2  6 708.2
	683.0  7 697.0
	583.6  8 599.6
	582.4  9 600.4
	552.4 10 572.4
	551.4 11 573.4

	Increasing parameters again...
	11 parameters, aic=573.36
	Final choice: 10 parameters, aic=572.44

	Adding Gaussian#1
	largest remaining discrepancy at 1.855keV[185], need 5959 counts
	placing gaussian at 1.86keV, with power 0.6227582993302021
	with Gaussian: 579.3593637901457 ; change: 6.9 (negative is good)
	not significant, rejecting
	creating prior functions...
	running BXA ...
	[ultranest] Sampling 400 live points from prior ...
	[ultranest INFO]: Sampling 400 live points from prior ...


	Mono-modal Volume: ~exp(-2.94) * Expected Volume: exp(0.00) Quality: ok

	src.level   :      -8.0|*************************************************** ******************************************|     +2.0
	src.PhoIndex:      +1.0|      *                *   * *********************************                               *|     +3.0
	src.nh      :     +19.0|**********************************************************************************************|    +24.0
	src.redshift:      +0.0|                +0.2  * ********************************* *  +0.4                             |     +0.7
	pca2.lognorm:      -5.0|******************************************************************************************** *|    +20.0

	Z=-1e+18(0.00%) | Like=-1.3e+18..-7.9e+02 [-1.142e+23..-1100] | it/evals=88/505 eff=83.8095% N=400 

	....

	logZ = -356.466 +- 0.259
	  single instance: logZ = -356.466 +- 0.183
	  bootstrapped   : logZ = -356.488 +- 0.259
	  tail           : logZ = +- 0.011

		src.level           -2.404 +- 0.037
		src.PhoIndex        2.029 +- 0.045
		src.nh              19.75 +- 0.46
		src.redshift        0.302 +- 0.050
		pca2.lognorm        -0.769 +- 0.031



* Example of empirical background model (and different priors). Redshift is a free parameter here:
  
  Run with::

    $ python3 example_automatic_background_model.py

	calling singlefitter...
	[bxa.Fitter INFO]: SingleFitter(for ID=2, storing to "swift/interval0pc")
	[bxa.Fitter INFO]: prepare_stage 2 of ID=2
	[bxa.Fitter INFO]: prepare_stage 2 of ID=2 done
	[bxa.Fitter INFO]: prepare_stage 2 of ID=2
	[bxa.Fitter INFO]: prepare_stage 2 of ID=2 done
	[bxa.Fitter INFO]: fit_stage 2 of ID=2
	[bxa.Fitter INFO]: fit_stage 2 of ID=2.  fine fit ...
	[bxa.Fitter INFO]: fit_stage 2 of ID=2.  fitted
	[bxa.Fitter INFO]: fit_stage 2 of ID=2.  stage done
	[bxa.Fitter INFO]: prepare_stage 3 of ID=2
	[bxa.Fitter INFO]: prepare_stage 3 of ID=2 done
	[bxa.Fitter INFO]: fit_stage 3 of ID=2
	[bxa.Fitter INFO]: fit_stage 3 of ID=2.  fine fit ...
	[bxa.Fitter INFO]: fit_stage 3 of ID=2.  fitted
	[bxa.Fitter INFO]: fit_stage 3 of ID=2.  stage done
	[bxa.Fitter INFO]: prepare_stage 4 of ID=2
	[bxa.Fitter INFO]: prepare_stage 4 of ID=2 done
	[bxa.Fitter INFO]: fit_stage 4 of ID=2
	[bxa.Fitter INFO]: fit_stage 4 of ID=2.  fine fit ...
	[bxa.Fitter INFO]: fit_stage 4 of ID=2.  fitted
	[bxa.Fitter INFO]: fit_stage 4 of ID=2.  stage done
	[bxa.Fitter INFO]: prepare_stage 5 of ID=2
	[bxa.Fitter INFO]: prepare_stage 5 of ID=2 done
	[bxa.Fitter INFO]: fit_stage 5 of ID=2
	[bxa.Fitter INFO]: fit_stage 5 of ID=2.  fine fit ...
	[bxa.Fitter INFO]: fit_stage 5 of ID=2.  fitted
	[bxa.Fitter INFO]: fit_stage 5 of ID=2.  stage done
	[bxa.Fitter INFO]: prepare_stage 6 of ID=2
	[bxa.Fitter INFO]: prepare_stage 6 of ID=2 done
	[bxa.Fitter INFO]: fit_stage 6 of ID=2
	[bxa.Fitter INFO]: fit_stage 6 of ID=2.  fine fit ...
	[bxa.Fitter INFO]: fit_stage 6 of ID=2.  fitted
	[bxa.Fitter INFO]: fit_stage 6 of ID=2.  stage done
	[bxa.Fitter INFO]: prepare_stage 7 of ID=2
	[bxa.Fitter INFO]: prepare_stage 7 of ID=2 done
	[bxa.Fitter INFO]: fit_stage 7 of ID=2
	[bxa.Fitter INFO]: fit_stage 7 of ID=2.  fine fit ...
	[bxa.Fitter INFO]: fit_stage 7 of ID=2.  fitted
	[bxa.Fitter INFO]: fit_stage 7 of ID=2.  stage done
	[bxa.Fitter INFO]: Background fit complete.

	freezing background params
	loading nH from swift/interval0pc.pi.nh (expecting something like 1e21 in there)
	setting galactic nH to 0.0168 [units of 1e22/cm²]
	apply_rmf(apply_arf((9504.67 * (((xszpowerlw.src * xszwabs.abso) * xswabs.galabso) + (0.05553358353932973 * (((1.0 - box1d.dip_2) * (((xsbknpower.pbknpl_2 + gauss1d.gauss1_2) + gauss1d.gauss2_2) + gauss1d.gauss3_2)) + gauss1d.gauss4_2))))))
	   Param        Type          Value          Min          Max      Units
	   -----        ----          -----          ---          ---      -----
	   src.PhoIndex thawed            1           -2            9           
	   src.redshift frozen            0       -0.999           10           
	   src.norm     thawed            1            0        1e+24           
	   abso.nH      thawed            1            0       100000 10^22 atoms / cm^2
	   abso.redshift frozen            0       -0.999           10           
	   galabso.nH   thawed            1            0       100000 10^22 atoms / cm^2
	   dip_2.xlow   frozen      1.76028         1.75         2.25           
	   dip_2.xhi    frozen      3.21915         2.75         3.25           
	   dip_2.ampl   frozen     0.937426        0.001        0.999           
	   pbknpl_2.PhoIndx1 frozen      1.53607          0.8            4           
	   pbknpl_2.BreakE frozen      4.10858          0.2            5        keV
	   pbknpl_2.PhoIndx2 frozen      2.71323          0.8            4           
	   pbknpl_2.norm frozen    0.0140262        1e-10            1           
	   gauss1_2.fwhm frozen     0.817724         0.01            1           
	   gauss1_2.pos frozen     0.607138          0.1          1.1           
	   gauss1_2.ampl frozen      0.01218        1e-06            1           
	   gauss2_2.fwhm frozen    0.0199524         0.01            1           
	   gauss2_2.pos frozen      2.19733            2          2.5           
	   gauss2_2.ampl frozen   0.00376109        1e-06            1           
	   gauss3_2.fwhm frozen    0.0303601         0.01            1           
	   gauss3_2.pos frozen      1.37532            1          1.4           
	   gauss3_2.ampl frozen   0.00415471        1e-06            1           
	   gauss4_2.fwhm frozen      0.93892         0.01            1           
	   gauss4_2.pos frozen        0.125            0          0.5           
	   gauss4_2.ampl frozen  0.000819252        1e-06            1           
	creating prior functions...
	running BXA ...
	[ultranest] Sampling 400 live points from prior ...
	[ultranest INFO]: Sampling 400 live points from prior ...


	Mono-modal Volume: ~exp(-3.96) * Expected Volume: exp(0.00) Quality: ok

	src.level   :      -8.0|*************************** **** ***** *************** **************************************** *************************************** |     -1.0
	src.PhoIndex:      +1.0|***** *************************** **************************************** ** ******* ********  ********** ************************* ***|     +3.0
	src.nh      :     +19.0|**************************************************** **************************** **** *********************************************** *|    +24.0
	gal.nh      :     +20.8|                                        +21.6  ************************************** * ***  +22.4                                      |    +23.2

	Z=-10118.6(0.00%) | Like=-10114.95..-778.63 [-34687.3038..-1560.0087] | it/evals=80/491 eff=87.9121% N=400 
	...

	logZ = -362.501 +- 0.288
	  single instance: logZ = -362.501 +- 0.221
	  bootstrapped   : logZ = -362.528 +- 0.288
	  tail           : logZ = +- 0.010

		src.level           -2.394 +- 0.016
		src.PhoIndex        2.200 +- 0.046
		src.nh              19.51 +- 0.35
		gal.nh              20.807 +- 0.035


Compare the models with::

	$ python3 model_compare.py superfit/ wabs_noz/

	Model comparison
	****************

	model superfit/ : log10(Z) =    -2.6  XXX ruled out
	model wabs_noz/ : log10(Z) =     0.0    <-- GOOD

	The last, most likely model was used as normalization.
	Uniform model priors are assumed, with a cut of log10(30) to rule out models.


Beware of the caveats of these log10(Z) differences (log-Bayes factors),
and derive thresholds with simulated data.

For the full documentation, see https://johannesbuchner.github.io/BXA/sherpa-analysis.html

Please explore this folder for other demo scripts.

For example, go into the chandra folder, and run the `xagnfitter.py <https://johannesbuchner.github.io/BXA/xagnfitter.html>`_ in this folder against it.
