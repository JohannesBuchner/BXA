BXA/Xspec example scripts
==========================

This folder contains simple and complex examples
how BXA can be invoked for spectral analysis.

Please refer to https://johannesbuchner.github.io/BXA/
for full documentation, including how to install BXA.


Generate test data
-------------------

Generate test data with xspec using the commands in gen.xspec
This will produce a spectral file example-file.fak
representing a ATHENA observation of an absorbed AGN.

Expected output::

	$ < gen.xspec xspec

The spectrum looks something like this:

.. image:: reference-output/data.gif

Simple analysis
-----------------

Have a look at the file example_simplest.py. It contains:

* Loading data
* setting up a model and its parameter ranges
* running a BXA fit with specified priors
* plotting the posterior predictions (convolved with the response)
* plotting the model (posterior predictions, not convolved)
* making a Q-Q plot

See https://johannesbuchner.github.io/BXA/ to understand the code.
See https://johannesbuchner.github.io/UltraNest/ to understand the output of the
fitting engine (for example, its `FAQ page <https://johannesbuchner.github.io/UltraNest/issues.html>`_).

Expected output::

	$ python3 example_simplest.py
	Default fit statistic is set to: C-Statistic
	   This will apply to all current and newly loaded spectra.

	1 spectrum  in use
	 
	Spectral Data File: example-file.fak  Spectrum 1
	Net count rate (cts/s) for Spectrum:1  4.224e+00 +/- 9.191e-02
	 Assigned to Data Group 1 and Plot Group 1
	  Noticed Channels:  1-4096
	  Telescope: ATHENA+ Instrument: WFI  Channel Type: PI
	  Exposure Time: 500 sec
	 Using fit statistic: cstat
	 Using Response (RMF) File            athenapp_ir_b4c_wfi_withfilter_fov40.0arcmin_avg.rsp for Source 1

	  4096 channels (1,4096) ignored in spectrum #     1

	   801 channels (11-811) noticed in spectrum #     1


	========================================================================
	Model powerlaw<1> Source No.: 1   Active/On
	Model Model Component  Parameter  Unit     Value
	 par  comp
	   1    1   powerlaw   PhoIndex            1.00000      +/-  0.0          
	   2    1   powerlaw   norm                1.00000      +/-  0.0          
	________________________________________________________________________


	Fit statistic  : C-Statistic              2.056191e+07     using 801 bins.

	Test statistic : Chi-Squared              4.197601e+11     using 801 bins.

	***Warning: Chi-square may not be valid due to bins with zero variance
				in spectrum number(s): 1 

	 Null hypothesis probability of 0.000000e+00 with 799 degrees of freedom
	 Current data and model not fit yet.

	Fit statistic  : C-Statistic              2.056191e+07     using 801 bins.

	Test statistic : Chi-Squared              4.197601e+11     using 801 bins.

	***Warning: Chi-square may not be valid due to bins with zero variance
				in spectrum number(s): 1 

	 Null hypothesis probability of 0.000000e+00 with 799 degrees of freedom
	 Current data and model not fit yet.

	Fit statistic  : C-Statistic              2.056191e+07     using 801 bins.

	Test statistic : Chi-Squared              4.197601e+11     using 801 bins.

	***Warning: Chi-square may not be valid due to bins with zero variance
				in spectrum number(s): 1 

	 Null hypothesis probability of 0.000000e+00 with 799 degrees of freedom
	 Current data and model not fit yet.
	  uniform prior for PhoIndex between 1.000000 and 3.000000 
	  jeffreys prior for norm between 1.000000e-10 and 1.000000e+01 
	   note: this parameter spans *many* dex. Double-check the limits are reasonable.
	running analysis ...
	[ultranest] Resuming from 7774 stored points


	Mono-modal Volume: ~exp(-4.24) * Expected Volume: exp(0.00) Quality: ok

	PhoIndex :      +1.0|*** ****************************** ****************************************************** **************|     +3.0
	log(norm):     -10.0|********************************************************************************************************|     +1.0

	Z=-1199206.7(0.00%) | Like=-1089578.51..-4277.72 [-1.045e+08..-4464] | it/evals=80/9998 eff=inf% N=400 

	Mono-modal Volume: ~exp(-4.24)   Expected Volume: exp(-0.23) Quality: correlation length: 3 (+)

	PhoIndex :      +1.0|********************************** ************* *******************************************************|     +3.0
	log(norm):     -10.0|************************************************************************************  -1.2              |     +1.0

	Z=-24616.1(0.00%) | Like=-24611.37..-4277.72 [-1.045e+08..-4464] | it/evals=160/9998 eff=inf% N=400 0 

	...
	...
	...

	Mono-modal Volume: ~exp(-22.05) * Expected Volume: exp(-18.00) Quality: correlation length: 1913 (+)

	PhoIndex :  +0.00000|                        +1.00000  *  +1.00005                                                           | +3.00000
	log(norm):   -10.000|                                                   -3.709  *  -3.699                                    |   +1.000

	Z=-3996.5(96.93%) | Like=-3981.81..-3981.70 [-3981.8147..-3981.8146]*| it/evals=7280/9998 eff=inf% N=400 

	Mono-modal Volume: ~exp(-22.35) * Expected Volume: exp(-18.23) Quality: correlation length: 1913 (+)

	PhoIndex :  +0.00000|                        +1.00000  *  +1.00004                                                           | +3.00000
	log(norm):   -10.000|                                                   -3.709  *  -3.700                                    |   +1.000

	[ultranest] Explored until L=-4e+03  981.70 [-3981.7988..-3981.7987]*| it/evals=7360/9998 eff=inf% N=400 
	[ultranest] Likelihood function evaluations: 9998
	[ultranest] Writing samples and results to disk ...
	[ultranest] Writing samples and results to disk ... done
	[ultranest]   logZ = -3996 +- 0.1528
	[ultranest] Posterior uncertainty strategy is satisfied (KL: 0.46+-0.08 nat, need <0.50 nat)
	[ultranest] Evidency uncertainty strategy is satisfied (dlogz=0.39, need <0.5)
	[ultranest]   logZ error budget: single: 0.18 bs:0.15 tail:0.02 total:0.15 required:<0.50
	[ultranest] done iterating.

	logZ = -3996.484 +- 0.389
	  single instance: logZ = -3996.484 +- 0.183
	  bootstrapped   : logZ = -3996.490 +- 0.389
	  tail           : logZ = +- 0.024
	insert order U test : converged: False correlation: 3.0 iterations

		PhoIndex            1.00038 +- 0.00038
		log(norm)           -3.7043 +- 0.0094
	running analysis ... done!
	creating plot of posterior predictions against data ...
	100%|████████████████████████████████████████████████████████████████████████████████████████████████| 100/100 [00:00<00:00, 107.90it/s]
	binning for plot...
	100%|█████████████████████████████████████████████████████████████████████████████████████████████████| 100/100 [00:01<00:00, 85.53it/s]
	saving plot...
	creating plot of posterior predictions ...
	100%|████████████████████████████████████████████████████████████████████████████████████████████████| 100/100 [00:00<00:00, 117.24it/s]
	saving plot...
	creating quantile-quantile plot ...
	saving plot...


Output files::

	$ find simplest/
	simplest/
	simplest/debug.log
	simplest/convolved_posterior.pdf
	simplest/chain.fits
	simplest/plots
	simplest/plots/corner.pdf
	simplest/plots/trace.pdf
	simplest/plots/run.pdf
	simplest/unconvolved_posterior.pdf
	simplest/info
	simplest/info/post_summary.csv
	simplest/info/results.json
	simplest/qq_model_deviations.pdf
	simplest/results
	simplest/results/points.hdf5
	simplest/extra
	simplest/chains
	simplest/chains/run.txt
	simplest/chains/weighted_post_untransformed.txt
	simplest/chains/equal_weighted_post.txt
	simplest/chains/weighted_post.txt

"simplest/" is the `outputfiles_basename` defined in the script.

The most important files are:

* unconvolved_posterior.pdf : 

	.. image:: reference-output/unconvolved_posterior.png
	
	The model itself is a powerlaw, and the uncertainties are too narrow to see.

	For further explanation of this plot, see https://johannesbuchner.github.io/BXA/xspec-analysis.html

* convolved_posterior.pdf : 

	.. image:: reference-output/convolved_posterior.png
	
	The model and the data convolved through the response. 
	Red means the data are poorly fitted by this model.
	The model is clearly off -- For example, the lower energy X-rays are overpredicted.

	For further explanation of this plot, see https://johannesbuchner.github.io/BXA/xspec-analysis.html

* plots/corner.pdf:

	.. image:: reference-output/corner.png
	
	Plot of the parameter constraints and uncertainties and their correlations.
	The photon index parameter is hitting the edge of the parameter space,
	and its uncertainties are tiny. Another hint of a poor model.

	For further explanation of this plot, see https://johannesbuchner.github.io/BXA/xspec-analysis.html

* qq_model_deviations.pdf : 
	
	.. image:: reference-output/qq_model_deviations.png
	
	`Q-Q plot <https://en.wikipedia.org/wiki/Q%E2%80%93Q_plot>`_:
	The red curve is far from the 1:1 line. That it is on the bottom right
	indicates the model produces many more counts than the data.
	The tickmarks indicate that the problem is accumulating below 2keV.

	For further explanation of this plot, see https://johannesbuchner.github.io/BXA/xspec-analysis.html

* info/results.json: summary of all parameters, their uncertainties and estimated lnZ
* info/post_summary.csv: summary of all parameters and their uncertainties as CSV
* chains/equal_weighted_post.txt: contains posterior samples: each row is a model parameter vector. You can iterate through these, set up the model in pyxspec, and then do something with it (compute fluxes and luminosities, for example).

Other examples
---------------

* example_advanced_priors.py shows a absorbed powerlaw fit, which is better. It 
  also demonstrates how to specify custom prior functions.

  Run with::
	
	$ python3 example_advanced_priors.py example-file.fak absorbed/
	
  Here the spectral file and output folder are command line arguments,
  which is convenient for analysing many sources.

* example_custom_run.py finally adds a emission line. Run with::

	$ python3 example_custom_run.py example-file.fak line/

Compare the models with::

	$ python3 model_compare.py absorbed simplest line

	Model comparison
	****************

	model simplest  : log10(Z) = -1519.1  XXX ruled out
	model absorbed  : log10(Z) =    -5.6  XXX ruled out
	model line      : log10(Z) =     0.0    <-- GOOD

	The last, most likely model was used as normalization.
	Uniform model priors are assumed, with a cut of log10(30) to rule out models.

Beware of the caveats of these log10(Z) differences (log-Bayes factors),
and derive thresholds with simulated data. 

For the full documentation, see https://johannesbuchner.github.io/BXA/xspec-analysis.html

Please explore this folder for other demo scripts.
