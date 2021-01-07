Sherpa with BXA
=======================================

Begin by loading bxa in a session with sherpa loaded::

   import bxa.sherpa as bxa

.. _sherpa-priors:

Defining priors
---------------------

Define your background model and source model as usual in sherpa.
Then define the priors over the free parameters, for example::

   # three parameters we want to vary
   param1 = xsapec.myapec.norm
   param2 = xspowerlaw.mypowerlaw.norm
   param3 = xspowerlaw.mypowerlaw.PhoIndex

   # list of parameters
   parameters = [param1, param2, param3]
   # list of prior transforms
   priors = [
      bxa.create_uniform_prior_for(param1),
      bxa.create_loguniform_prior_for(param2),
      bxa.create_gaussian_prior_for(param3, 1.95, 0.15),
      # and more priors
   ]

Make sure you set the parameter minimum and maximum values to appropriate (a priori reasonable) values.
The limits are used to define the uniform and loguniform priors.

You can freeze the parameters you do not want to investigate, but BXA only modifies the parameters specified.
As a hint, you can find all thawed parameters of a model with::

   parameters = [for p in get_model().pars if not p.frozen and p.link is None]

.. autofunction:: bxa.sherpa.create_jeffreys_prior_for
.. autofunction:: bxa.sherpa.create_uniform_prior_for
.. autofunction:: bxa.sherpa.create_gaussian_prior_for
.. autofunction:: bxa.sherpa.create_prior_function

.. _sherpa-run:

Running the analysis
---------------------

You need to specify a prefix, called *outputfiles_basename* where the files are stored.

::

   # see the pymultinest documentation for all options
   priorfunction = bxa.create_prior_function(parameters)
   solver = bxa.BXASolver(prior=priorfunction, parameters=parameters,
		outputfiles_basename = "myoutputs/")
   results = solver.run(resume=True)

.. autoclass:: bxa.sherpa.BXASolver

.. _sherpa-analyse:

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

Error propagation
---------------------

`results['samples']` provides access to the posterior samples (similar to a Markov Chain).
Use these to propagate errors:

* For every row in the chain, compute the quantity of interest
* Then, make a histogram of the results, or compute mean and standard deviations.

This preserves the structure of the uncertainty (multiple modes, degeneracies, etc.)

BXA also allows you to compute the fluxes corresponding to the 
parameter estimation, giving the correct probability distribution on the flux.
With distance information (fixed value or distribution), you can later infer
the correct luminosity distribution.

::

     dist = solver.get_distribution_with_fluxes(lo=2, hi=10)
     numpy.savetxt(out + prefix + "dist.txt", dist)

.. automethod:: bxa.sherpa.BXASolver.get_distribution_with_fluxes

This does nothing more than::

    r = []
    for row in results['samples']:
	    # set the parameter values to the current sample
	    for p, v in zip(parameters, row):
		    p.val = v
	    r.append(list(row) + [calc_photon_flux(lo=elo, hi=ehi), 
		    calc_energy_flux(lo=elo, hi=ehi)])

Such loops can be useful for computing obscuration-corrected, rest-frame luminosities,
(modifying the nH parameter and the energy ranges before computing the fluxes).

.. _sherpa-models:

.. include:: model_comparison.rst

.. _sherpa-design:

.. include:: experiment_design.rst

.. _sherpa-qq:

.. include:: model_discovery.rst

The *qq* function in the *qq* module allows you to create such plots easily, by
exporting the cumulative functions into a file.

.. autofunction:: bxa.sherpa.qq.qq_export
   :noindex:

Refer to the :ref:`accompaning paper <cite>`, which gives an introduction and 
detailed discussion on the methodology.
