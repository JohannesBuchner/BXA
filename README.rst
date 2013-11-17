BXA - Bayesian X-ray Analysis
==============================

Sherpa with MultiNest
----------------------

BXA is a statistical analysis package for the `sherpa`_ X-ray spectral analysis environment. Sherpa is partially based on XSPEC and contains all its models, but is much nicer to work with.

BXA does:

  * parameter estimation in arbitrary dimensions, which involves:
     * finding the best fit
     * computing error bars
     * computing marginal probability distributions
  * plotting of spectral fits vs. the data:
     * for the best fit
     * for each of the solutions
     * for each component
  * model selection:
     * computing the evidence for the considered model, 
       ready for use in computing Bayes factors


Installation
-------------

You need to have `sherpa`_ running and working.

You need to have pymultinest and MultiNest installed and working.

Install bxa as a python package::

   $ python setup.py install

Or if you only want to install it for the current user::

   $ python setup.py install --user

In sherpa, load the package::

	jbuchner@ds42 ~ $ sherpa
	-----------------------------------------------------
	Welcome to Sherpa: CXC's Modeling and Fitting Package
	-----------------------------------------------------
	CIAO 4.4 Sherpa version 2 Tuesday, June 5, 2012

	sherpa-1> import bxa
	sherpa-2> bxa.run_model?

Now you can use bxa.


Usage
------

Define your background model and source model as usual in sherpa.
Freeze the parameters you do not want to investigate. Make sure you set the parameter minimum and maximum values to appropriate (a priori reasonable) values.

Define Priors::

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

Run the evaluation::

   # see the pymultinest documentation for all options
   bxa.nested_run(prior = priorfunction, parameters = parameters,
		resume = True, verbose = True, 
		outputfiles_basename = "testbxa_")

Plot and analyse the results. PyMultiNest comes in handy at this point to 
produce a number of plots and summaries::

   # on the shell, run
   $ multinest_marginals.py "testbxa_"
   # this utility is installed with PyMultiNest.

You can also access the output directly and compute other quantities, like the flux::

   import pymultinest
   a = pymultinest.analyse.Analyzer(n_params = len(parameters), outputfiles_basename = 'testbxa_')
   markov_chain = a.get_equal_weighted_posterior()
   
   dist = bxa.get_distribution_with_fluxes(parameters = parameters, outputfiles_basename = 'testbxa_')
  
BXA also allows you to compute the fluxes corresponding to the 
parameter estimation, giving the correct probability distribution on the flux.
With distance information (fixed value or distribution), you can later infer
the correct luminosity distribution.

::

	dist = pyblocxs.mn.get_distribution_with_fluxes(lo=2, hi=10,
		parameters = parameters, outputfiles_basename = 'testbxa_')
	numpy.savetxt(out + prefix + "dist.txt", dist)

Recommendations for X-ray spectral analysis
--------------------------------------------

For good and valid results, experienced users of XSpec or Sherpa will already do these:

* Using a continuous background model (parameteric, albeit not necessarily physical),
 instead of "subtracting" or using bin-wise backgrounds (XSpec default).
* Use C-stat (poisson likelihood) instead of Chi^2 (gaussian likelihood)
* Use unbinned spectra (except perhaps for visualization, albeit you can use QQ-plots there without loss of resolution)

Beyond these already-standard practices, we suggest:

* Estimating the values with uncertainties using nested sampling (this software)
** instead of Contour-search, Fisher matrix, stepping, or other approximations
* Comparing models using the computed evidence (this software)
** instead of Likelihood ratio tests (which are invalid for non-nested models)

See the accompaning paper for a detailed discussion and comparison! 
Buchner et al. (in prep)

Citing BXA correctly
---------------------

We suggest giving credit to the developers of Sherpa, MultiNest and of this software.
As an example::

  For analysing X-ray spectra, we use the analysis software BXA (\ref{Buchner2014}),
  which connects the nested sampling algorithm MultiNest (\ref{FerozHobson2010})
  with the fitting environment CIAO/Sherpa (\ref{Fruscione2006}).

Where the BibTex entries are:

* for BXA: Buchner et al. (in prep)
* for MultiNest: see `multinest`_
* for Sherpa: see `sherpa`_


.. _sherpa: http://cxc.cfa.harvard.edu/sherpa/
.. _multinest: http://ccpforge.cse.rl.ac.uk/gf/project/multinest/ 




