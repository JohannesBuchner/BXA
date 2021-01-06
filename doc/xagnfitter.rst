Obscured Active Galactic Nuclei
=======================================

A script for fitting Active Galactic Nuclei is provided at
`xagnfitter <https://github.com/JohannesBuchner/BXA/blob/master/examples/sherpa/xagnfitter.py>`_.
This is the method used in Buchner+14, Buchner+15, Simmonds+17.

Features:

* Maximum information extraction in the low count regime, by Bayesian inference and background models.
* Provides robust uncertainty estimation of all parameters, including the
  * obscuring column density NH
  * Photon index Gamma
  * rest-frame, intrinsic accretion luminosity
  * etc.
* Redshift can be fixed, unknown or come from a probability distribution (photo-z)
* Realistic nuclear obscurer model (UXCLUMPY) that fits objects in the local Universe well.
* Corrects for galactic absorption
* Optional: add an apec L<10^42erg/s contamination component (set WITHAPEC=1)
* Can fit multiple observations simultaneously

I strongly recommend using the `xagnfitter <https://github.com/JohannesBuchner/BXA/blob/master/examples/sherpa/xagnfitter.py>`_.
 script instead of hardness ratios.

It is included verbatim below:

.. literalinclude:: ../examples/sherpa/xagnfitter.py
