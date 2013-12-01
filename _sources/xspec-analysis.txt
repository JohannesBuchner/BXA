BXA/Xspec
=======================================

Load your data, define your background model and source model as usual.
This, you have to do using calls to `PyXSpec`_ functions. 
Look at the file *examples/example_simplest.py* for an instructive example on 
how to do the simplest analysis.

.. _PyXspec: https://heasarc.gsfc.nasa.gov/xanadu/xspec/python/html/

.. literalinclude:: ../examples/example_simplest.py

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

For plotting the model parameters found against the data, use these functions.

.. autofunction:: bxa.xspec.posterior_predictions_unconvolved
.. autofunction:: bxa.xspec.posterior_predictions_convolved
.. autofunction:: bxa.xspec.set_best_fit
.. automodule:: bxa.xspec.sinning
	:members: binning

Refer to the *standard_analysis* function as an example of how to use them.

Error propagation
---------------------

:py:func:`pymultinest.Analyzer.equal_weighted_posterior` provides access to the posterior samples (similar to a Markov Chain).
Use these to propagate errors:
* For every row in the chain, compute the quantity of interest
* Then, make a histogram of the results, or compute mean and standard deviations.
This preserves the structure of the errors (multiple modes, degeneracies, etc.)

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


