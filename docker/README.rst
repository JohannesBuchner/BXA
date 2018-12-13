================================
Fitting with BXA & XAGNFitter
================================

With this tool you can automatically fit X-ray spectra of AGN.

What it does
---------------

* Fit the source spectrum with 

  * Obscured AGN component (powerlaw reprocessed by a torus structure)
  * Warm mirror component (powerlaw, Thompson scattering within the opening angle)
  * Stellar process component (apec whose luminosity remains below 1e42 erg/s)
  * All three are absorbed by Milky Way absorption.

* Additional features:

  * Uses the MultiNest global parameter space exploration algorithm, which can deal with many parameters and does not get stuck in local minima.
  * If the redshift is uncertain, these uncertainties are propagated through. Or you can give a fixed value.
  * The background spectrum is approximated automatically with an empirical model. This extracts more information compared to default xspec wstat, even for very few source counts (see e.g., Simmonds+18).

* Produces parameter posterior distributions, which describe the uncertainties in:

  * AGN Luminosity           (log-uniform uninformative prior)
  * Column density N_H       (log-uniform uninformative prior)
  * Powerlaw photon index    (1.95+-0.15 informative prior)
  * Redshift (if not fixed)  (user-supplied)
  * apec temperature         (log-uniform uninformative prior)
  * apec normalisation       (log-uniform uninformative prior)
  * torus opening angle parameters (CTKcover, TORtheta, uniform uninformative priors) 


Preparing your data
---------------------

* You only need your spectrum as a .pi/.pha file and the associated RMF, ARF and background files.
* Check that the keywords are set correctly:

  * You can use the fixkeywords.py script (see BXA repository) to make sure the src points to the ARF, RMF and background files
  * python fixkeywords.py pn_src.fits pn_bgd.fits pn_rmf.fits pn_arf.fits

* Set the galactic N_H

  * Create a file next to your spectrum file with the extention .nh and put in the galactic column density to the source. For example:
  * $ echo 1e21 > combined_src.pi.nh
  * You can also use the gal.py script (see BXA repository). It automatically fetches the nhtot value from http://www.swift.ac.uk/analysis/nhtot/ if RA/DEC are set:
  * python gal.py pn_src.fits

* Give redshift information

  * Create a file next to your spectrum file with the extention .z and put in the source redshift. For example:
  * $ echo 6.31 > combined_src.pi.z
  * If you do not know the redshift, don't create this file.
  * If you have redshift uncertainties as a probability distribution, store here two columns: cumulative probability (from 0 to 1, uniformly sampled) and corresponding redshift. For example, for a redshift 1.1+-0.2, you could do::

	cdfsteps = numpy.linspace(0, 1, 100)
	z = scipy.stats.norm(1.1, 0.2).cdf(cdfsteps)
	numpy.savetxt("combined_src.pi.z", numpy.transpose([cdfsteps, z]))


Finally, you should have files like in the testsrc/ folder:

* combined_src.pi
* combined_src.pi.nh (galactic NH)
* combined_src.pi.z  (redshift information)
* combined_src.arf
* combined_src.rmf
* combined_bkg.arf  (optional)
* combined_bkg.pi 
* combined_bkg.rmf  (optional)


How to use
---------------

You only need to **install docker** on your computer. 

All the necessary software (ciao, sherpa, multinest, BXA) is in a container image that will be automatically downloaded for you.

First, go to the directory where your spectrum is::

	$ cd testsrc

Optionally, allow docker containers to show stuff on your screen::

	$ xhost +local:`docker inspect --format='{{ .Config.Hostname }}' johannesbuchner/bxa_absorbed` 
	$ XDOCKERARGS="-v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY"

Then, run docker::

	$ docker run $XDOCKERARGS -v $PWD:/opt/example/ -e FILENAME=combined_src.pi -e ELO=0.5 -e EHI=8 -ti johannesbuchner/bxa_absorbed 

The arguments mean the following:

* -v arguments mount local directories into the virtual machine:

  * -v $PWD:/opt/example/ -- This connects the /opt/example folder inside the container, to your host machines folder $PWD (the folder you are currently in). Otherwise the container cannot read your files.

* -e arguments set environment variables

  * -e FILENAME=combined_src.pi sets the file to analyse
  * -e ELO=0.5 -e EHI=8 sets the energy range (in keV) to use

* -ti -- Get a interactive terminal
* johannesbuchner/bxa_absorbed -- name of the container image to run


What it will do internally
----------------------------

1. Initialises the container. It is similar to a virtual machine, with a completely separated Ubuntu Linux installation inside.
2. Inside, it run the command ". /opt/ciao-4.8/bin/ciao.sh; sherpa /opt/scripts/fitagn.py". This loads ciao and runs sherpa. 

  * If you want to replace or edit the fitting script, add  in the docker run command "-v mydirectory/scripts:/opt/scripts/" before "-ti" to replace the /opt/scripts folder with your own scripts folder.

3. The sherpa script sets up the source model, parameters and priors. The background is fitted. Finally, multinest is run to constrain the parameters. 

4. Output files are combined_src.pi_out_*. The most important ones are

  * params.json -- contains the parameter names 
  * post_equal_weights.dat -- contains the posterior samples, each column is a parameter

What you can do with the results
-------------------------------------

* Plot the parameter distribution. The multinest_marginals.py tool in the pymultinest repository can help::

  $ python pymultinest/multinest_marginals.py combined_src.piout_withapec_

Alternatively, you can also use corner.py or any other plotting tool.

Modify the behaviour
-------------------------

* to change redshift, alter the .z file (see above)
* to disable apec component, set the environment variable "-e WITHAPEC=0"
* to change the fitagn.py script altogether, edit it in the scripts/ folder and pass "-v mydirectory/scripts:/opt/scripts/". You have to give the absolute path to your scripts/ directory.






