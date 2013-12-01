BXA/Sherpa
=======================================

Define your background model and source model as usual in sherpa.
Freeze the parameters you do not want to investigate. Make sure you set the parameter minimum and maximum values to appropriate (a priori reasonable) values.

.. _sherpa-priors:

Defining priors
---------------------
::

   # you can use automatic priors (uniform priors everywhere, within the parameters range)
   # for this, all scale parameters (those with ampl or norm in their name)
   # are converted to log-parameters
   parameters = auto_reparametrize()
   prior = bxa.create_prior_function(parameters)
   
Alternatively (advanced), define priors manually::

   # get parameters
   parameters = [param1, param2, param3]
   # or just get all that are not linked or frozen
   parameters = [for p in get_model().pars if not p.frozen and p.link is None]
   
   priors = []
   priors += [bxa.create_jeffreys_prior_for(param1)]
   priors += [bxa.create_uniform_prior_for(param2)]
   priors += [lambda x: x**2] # custom prior transformation (rarely desired)
   priorfunction = bxa.create_prior_function(priors = priors)

.. autofunction:: bxa.sherpa.create_jeffreys_prior_for
.. autofunction:: bxa.sherpa.create_uniform_prior_for
.. autofunction:: bxa.sherpa.create_prior_function

.. _sherpa-run:

Running the analysis
---------------------

You need to specify a prefix, called *outputfiles_basename* where the files are stored.

::

   # see the pymultinest documentation for all options
   bxa.nested_run(prior = priorfunction, parameters = parameters,
		resume = True, verbose = True, 
		outputfiles_basename = "testbxa_")

.. autofunction:: bxa.sherpa.nested_run

.. _sherpa-analyse:

Marginal plots
----------------------

Plot and analyse the results. PyMultiNest comes in handy at this point to 
produce a number of plots and summaries. 

On the shell, run::

   $ multinest_marginals.py "testbxa_"

The `multinest_marginals.py <https://github.com/JohannesBuchner/PyMultiNest/blob/master/multinest_marginals.py>`_
utility is installed with PyMultiNest, for instance into ~/.local/bin/.

Error propagation
---------------------

:py:func:`pymultinest.Analyzer.equal_weighted_posterior` provides access to the posterior samples (similar to a Markov Chain).
Use these to propagate errors:

* For every row in the chain, compute the quantity of interest
* Then, make a histogram of the results, or compute mean and standard deviations.

This preserves the structure of the uncertainty (multiple modes, degeneracies, etc.)

You can also access the output directly and compute other quantities::

	import pymultinest
	analyzer = pymultinest.analyse.Analyzer(n_params = len(parameters), 
		outputfiles_basename = 'testbxa_')
	
	chain = analyzer.get_equal_weighted_posterior()
	
	print chain

BXA also allows you to compute the fluxes corresponding to the 
parameter estimation, giving the correct probability distribution on the flux.
With distance information (fixed value or distribution), you can later infer
the correct luminosity distribution.

::

	dist = pyblocxs.mn.get_distribution_with_fluxes(lo=2, hi=10,
		parameters = parameters, outputfiles_basename = 'testbxa_')
	numpy.savetxt(out + prefix + "dist.txt", dist)

.. autofunction:: bxa.sherpa.get_distribution_with_fluxes

.. _sherpa-models:

.. include:: model_comparison.rst

.. _sherpa-design:

.. include:: experiment_design.rst

.. _sherpa-qq:

.. include:: model_discovery.rst

The *qq* function in the *qq* module allows you to create such plots easily.

.. automodule:: bxa.xspec.qq
	:members: qq

Refer to the :ref:`accompaning paper <cite>`, which gives an introduction and 
detailed discussion on the methodology.


