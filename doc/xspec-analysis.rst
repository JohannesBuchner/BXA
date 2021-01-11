Xspec with BXA
=======================================

This documentation shows how to use BXA with `PyXSpec`_.

Begin by importing bxa in a python session with heasoft loaded:

.. literalinclude:: ../examples/xspec/example_simplest.py
   :lines: 4-5

Load your data, define your background model and source model as usual
with `PyXSpec`_. 

.. _PyXspec: https://heasarc.gsfc.nasa.gov/xanadu/xspec/python/html/

.. _xspec-priors:

Defining priors
---------------------

Create a list of prior transformations like in the example above, one line for each variable.
These functions will help you with that.

.. autofunction:: bxa.xspec.create_uniform_prior_for
.. autofunction:: bxa.xspec.create_loguniform_prior_for
.. autofunction:: bxa.xspec.create_gaussian_prior_for
.. autofunction:: bxa.xspec.create_custom_prior_for

For example:

.. literalinclude:: ../examples/xspec/example_simplest.py
   :lines: 13-27

See `examples/xspec/example_simplest.py <https://github.com/JohannesBuchner/BXA/blob/master/examples/xspec/example_simplest.py>`_ for a simple example. 
`examples/xspec/example_advanced_priors.py <https://github.com/JohannesBuchner/BXA/blob/master/examples/xspec/example_advanced_priors.py>`_ introduces more complex and custom priors.

.. _xspec-run:

Running the analysis
---------------------

This runs the fit and stores the result in the specified output folder:

.. literalinclude:: ../examples/xspec/example_simplest.py
   :lines: 30-32

.. autoclass:: bxa.xspec.BXASolver
   :noindex:

The returned results contain posterior samples and the Bayesian evidence.
These are also reported on the screen for you.

.. _xspec-analyse:

Parameter posterior plots
--------------------------

Credible intervals of the model parameters, and histograms 
(1d and 2d) of the marginal parameter distributions are plotted
in 'myoutputs/plots/corner.pdf' for you.

.. figure:: absorbed-corner.*
	:scale: 50%

You can also plot them yourself using corner, triangle and getdist, by
passing `results['samples']` to them.

For more information on the corner library used here, 
see https://corner.readthedocs.io/en/latest/.

Model checking
-----------------------

The following code creates a plot of the convolved posterior model:

.. literalinclude:: ../examples/xspec/example_simplest.py
   :lines: 37-60

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
	
	On the colors of the data points:
	
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

The following code creates a plot of the unconvolved posterior:

.. literalinclude:: ../examples/xspec/example_simplest.py
   :lines: 65-79

.. figure:: absorbed-unconvolved_posterior.*
	
	Example of the unconvolved spectrum.
	For each posterior sample (solution), the parameters are taken and put
	through the model. All such lines are plotted. Where the region is darker,
	more lines ended up, and thus it is more likely.

For plotting the model parameters found against the data, use these functions.

.. automethod:: bxa.xspec.BXASolver.posterior_predictions_unconvolved
.. automethod:: bxa.xspec.BXASolver.posterior_predictions_convolved
.. automethod:: bxa.xspec.sinning.binning
    :noindex:


Error propagation
---------------------

`results['samples']` provides access to the posterior samples (similar to a Markov Chain).
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

For Xspec, the *qq* function in the *qq* module allows you to create such plots easily:

.. literalinclude:: ../examples/xspec/example_simplest.py
   :lines: 83-90

.. autofunction:: bxa.xspec.qq.qq

Refer to the :ref:`accompaning paper <cite>`, which gives an introduction and 
detailed discussion on the methodology.
