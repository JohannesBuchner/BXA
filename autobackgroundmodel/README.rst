=======================================
Machine-learned PCA Background models
=======================================

The advantages of using background spectral models is that more information 
can be extracted from low-count data, as correlations between bins and instrument behaviours are known.

This page describes the machine-learning approach to derive empirical background models
published in `Simmonds et al., 2018, A&A, 618A, 66 <https://ui.adsabs.harvard.edu/abs/2018A%26A...618A..66S/abstract>`_.
For Chandra/ACIS, XMM/EPIC, Swift/XRT, NuSTAR/FPMA, RXTE, 
Large archives of background spectra were used to derive principal components (PCA)
that empirically describe the background and its variations.

BXA includes these PCA models, which can be fitted to a specific background spectrum.

These PCA models are trained in log10(counts + 1) space to avoid negative counts.
The PCA models operate on detector channels and thus should never pass through the response.

The PCA models are limited in how well they can describe additive components such as 
gaussian emission lines. For this reason, the fitters also try adding Gaussian lines at 
the location of strongest fit mismatch.

The fits keep increasing complexity (first, the number of PCA components and then, the gaussians) as long as the AIC (Akaike information criterion) improves.

In Sherpa
-------------------------

After setting your source model (with set_model), use::

	from bxa.sherpa.background.pca import auto_background
	convmodel = get_model(id)
	bkg_model = auto_background(id)
	set_full_model(id, get_response(id)(model) + bkg_model * get_bkg_scale(id))

.. autofunction:: bxa.sherpa.background.pca.auto_background

A full example for fitting obscured Active Galactic Nuclei is available:
https://github.com/JohannesBuchner/BXA/blob/master/examples/sherpa/xagnfitter.py

In Xspec
-------------------------

In xspec, there are two steps. 

1) precompute the best-fit continuum model

   fit the background spectrum outside xspec using the autobackgroundmodel/fitbkg.py script.

   You can find it here: https://github.com/JohannesBuchner/BXA/tree/master/autobackgroundmodel
   
   It needs the json files in the same folder.
   
   It will give you instructions how to load the PCA model in xspec.

2) Use the resulting atable with a dummy unit response matrix.

   fitbkg.py in step 1 gives you instructions how to load it in xspec.

Creating a new PCA model
---------------------------

If you have a new instrument or survey, create a model with:

`python autobackgroundmodel/__init__.py bkg1.pha bkg2.pha bkg3.pha`

The resulting file is telescope.json or telescope_instrument.json.


Fitting a model
----------------

Once you want to fit a specific sources, you can obtain its background model
in two different ways:

**For use in xspec**, you can precompute a background model:

`python autobackgroundmodel/fitbkg.py bkg1.pha [src1.pha]`

This will make a file bkg1.pha.bstat.out with the estimated per-channel count rate.

**For use in sherpa**, use the autobackground feature.
see `examples/sherpa/example_automatic_background.py`

If you have a new model (json file), it needs to be installed in the BXA folder,
probably at `~/.local/lib/python*/site-packages//bxa/sherpa/background/`.
