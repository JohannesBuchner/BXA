BXA/Xspec
=======================================

Load your data, define your background model and source model as usual.
This, you have to do using calls to `PyXSpec`_ functions. 
Look at the file *examples/example_simplest.py* for an instructive example on 
how to do the simplest analysis.

.. _PyXspec: https://heasarc.gsfc.nasa.gov/xanadu/xspec/python/html/

.. literalinclude:: ../examples/xspec/example_simplest.py

.. _xspec-priors:

Defining priors
---------------------

Create a list of prior transformations like in the example above, one line for each variable.
These functions will help you with that.

.. automodule:: bxa.xspec
      :members: create_uniform_prior_for, create_jeffreys_prior_for, create_custom_prior_for

See *examples/example_simplest.py* for a simple example. 
*examples/example_advanced_priors.py* introduces more complex and custom priors.

.. _xspec-run:

Running the analysis
---------------------

A convencience method is provided for you, called *standard_analysis*, which does everything.
You need to specify a prefix, called *outputfiles_basename* where the files are stored.

.. autofunction:: bxa.xspec.standard_analysis
.. autofunction:: bxa.xspec.nested_run

Both method return a *pymultinest.Analyzer* object, which provides access to the results.

The example *examples/example_custom_run.py* shows how to customize the analysis (other plots)

This will allow you to create marginal plots, qq plots, plots of the spectra, etc.

.. _xspec-analyse:

Marginal plots
----------------------

For histograms (1d and 2d) of the marginal parameter distributions, use *plot.marginal_plots*.

.. automodule:: bxa.xspec.plot
	:members: marginal_plots

.. figure:: absorbed-corner.*
	:scale: 50%
	
	For each parameter and each pair (not shown here), the marginal probability distribution is plotted.
	This is presented in three forms:
	
	* Grey histogram, for the probability density
	* Blue curve, for the cumulative distribution (summing up the grey histogram from left to right)
	* As a summarizing error bar with the error corresponding to the quantiles of 1-sigma of a Gaussian.
	  (i.e. the 16%, 50% and 84% quantiles are shown).

For plotting the model parameters found against the data, use these functions.

.. autofunction:: bxa.xspec.posterior_predictions_unconvolved
.. autofunction:: bxa.xspec.posterior_predictions_convolved
.. autofunction:: bxa.xspec.set_best_fit
.. automodule:: bxa.xspec.sinning
	:members: binning

Refer to the *standard_analysis* function as an example of how to use them.


.. figure:: absorbed-convolved_posterior.*
	
	Example of the convolved spectrum with data.
	For each posterior sample (solution), the parameters are taken and put
	through the model. All such lines are plotted. Where the region is darker,
	more lines ended up, and thus it is more likely.
	
	The data points are adaptively binned to contain at least 20 counts.
	The error bars are created by asking: which model count rate can produce
	this amount of counts. 
	In a Poisson process, the inverse incomplete gamma
	function provides this answer. The 10%-90% probability range is used.
	
	For all intents and purposes, you can ignore the colors.
	
	The colors are intended to aid the discovery of discrepancies, by using
	a custom Goodness of Fit measure. In this procedure (gof module), 
	a tree of the bins is built, i.e. in the first layer, every 2 bins 
	are merged, in the second, every 4 bins are merged, etc.
	Then, the counts in the bins are compared against with 
	the poisson process of the model. The worst case, i.e. the least likely 
	probability over the whole tree is considered. That is, for each bin,
	the lowest probability of all its merges is kept. Finally, this is multiplied
	by the number of nodes in the tree (as more comparisons lead to more 
	random chances).
	
	Then, if the probability for the bin is below :math:`10^{-2}`, the point is marked orange,
	and if it reaches below :math:`10^{-6}`, it is marked red.
	
	It is ok to ignore the colors, this computation is not used otherwise.

.. figure:: absorbed-unconvolved_posterior.pdf
	
	Example of the unconvolved spectrum with data.
	For each posterior sample (solution), the parameters are taken and put
	through the model. All such lines are plotted. Where the region is darker,
	more lines ended up, and thus it is more likely.
	
Error propagation
---------------------

:py:func:`pymultinest.Analyzer.equal_weighted_posterior` provides access to the posterior samples (similar to a Markov Chain).
Use these to propagate errors:

* For every row in the chain, compute the quantity of interest
* Then, make a histogram of the results, or compute mean and standard deviations.

This preserves the structure of the uncertainty (multiple modes, degeneracies, etc.)

*Continuing in Xspec*: A chain file, compatible with Xspec chain commands is 
written for you into *<outputfiles_basename>chain.fits*. In Xspec, load it using `"chain load" <https://heasarc.gsfc.nasa.gov/xanadu/xspec/manual/XSchain.html>`_.
This should set parameters, and compute flux estimates.

.. _xspec-models:

.. include:: model_comparison.rst

.. _xspec-design:

.. include:: experiment_design.rst

.. _xspec-qq:

.. include:: model_discovery.rst

For Xspec, the *qq* function in the *qq* module allows you to create such plots easily.

.. autofunction:: bxa.xspec.qq.qq

Refer to the :ref:`accompaning paper <cite>`, which gives an introduction and 
detailed discussion on the methodology.


