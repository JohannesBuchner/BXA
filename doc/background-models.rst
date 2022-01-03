Empirical background models
=======================================

The advantages of using background spectral models is that more information 
can be extracted from low-count data, as correlations between bins and instrument behaviours are known.

The :py:mod:`bxa.sherpa.background` module includes hand-crafted models to 
empirically describe the background spectra
for Chandra/ACIS, XMM/EPIC, Swift/XRT. 
This requires that you extracted a background spectrum (they are not ab initio predictions).

A mixture of powerlaws, gaussian lines and mekals are fitted to the background.
The best-fit model can then be used to fit the source. Optionally,
background parameters (such as the overall normalisation) can be varied with the source fit.

You may also be interested in the `PCA models <pca-background-models>`_ for Chandra/ACIS, XMM/EPIC, Swift/XRT, NuSTAR/FPMA, RXTE observations.


Empirical models for XMM/EPIC
--------------------------------

An example for XMM is available at
https://github.com/JohannesBuchner/BXA/blob/master/examples/sherpa/xmm/fit.py

.. autofunction:: bxa.sherpa.background.xmm::get_pn_bkg_model
	:noindex:
.. autofunction:: bxa.sherpa.background.xmm::get_mos_bkg_model
	:noindex:

The XMM model was developed by Richard Sturm at MPE.
The citation is `Maggi P., et al., 2014, A&A, 561, AA76 <https://ui.adsabs.harvard.edu/abs/2012A&A...546A.109M/abstract>`_.

Empirical models for Swift/XRT and Chandra/ACIS
------------------------------------------------

An example for Swift/XRT is available at
https://github.com/JohannesBuchner/BXA/blob/master/examples/sherpa/swift/fit.py

First define which background you want to use and where you want to store intermediate results:
::
	
	# where to store intermediary fit information
	# usually the name of the spectral file
	filename = 'mybackgroundspecfile'
	
	# create a fitter for the desired type of spectrum
	from bxa.sherpa.background.models import SwiftXRTBackground, ChandraBackground
	from bxa.sherpa.background.fitter import SingleFitter
	fitter = SingleFitter(id, filename, SwiftXRTBackground)
	# or 
	fitter = SingleFitter(id, filename, ChandraBackground)

Finally, run the background fit::

	fitter.fit(plot=True)

The Chandra model was developed by Johannes Buchner at MPE. 
The citation is `Buchner et al., 2014, A&A, 564A, 125 <https://ui.adsabs.harvard.edu/abs/2014A%26A...564A.125B/abstract>`_.

The Swift/XRT model was developed by Johannes Buchner at PUC. 
The citation is `Buchner et al., 2017, MNRAS, 464, 4545 <https://ui.adsabs.harvard.edu/abs/2017MNRAS.464.4545B/abstract>`_.

.. autoclass:: bxa.sherpa.background.models.SwiftXRTBackground
	:noindex:
.. autoclass:: bxa.sherpa.background.models.SwiftXRTWTBackground
	:noindex:
.. autoclass:: bxa.sherpa.background.models.ChandraBackground
	:noindex:

If the fit is bad
------------------

Try another method (e.g., PCA models, or fall back to Wstat statistics).
