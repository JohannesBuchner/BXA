BXA/Xspec
=======================================

Begin by loading bxa in a session with xspec loaded:

.. code-block:: python

   import xspec
   import bxa.xspec as bxa

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

.. code-block:: python

	m = Model("pow")
	m.powerlaw.norm.values = ",,1e-10,1e-10,1e1,1e1" # 10^-10 .. 10
	m.powerlaw.PhoIndex.values = ",,1,1,3,3"       #     1 .. 3

	# define prior
	transformations = [
		# uniform prior for Photon Index
		bxa.create_uniform_prior_for( m, m.powerlaw.PhoIndex),
		# jeffreys prior for scale variable
		bxa.create_jeffreys_prior_for(m, m.powerlaw.norm),
		# and possibly many more parameters here
	]


See *examples/example_simplest.py* for a simple example. 
*examples/example_advanced_priors.py* introduces more complex and custom priors.

.. _xspec-run:

Running the analysis
---------------------

This runs the fit and stores the result in the myoutputs folder:

.. code-block:: python

	outputfiles_basename = 'myoutputs/'
	solver = BXASolver(transformations=transformations, outputfiles_basename=outputfiles_basename)
	results = solver.run(resume=True)

.. autoclass:: bxa.xspec.BXASolver

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

The following code creates a plot of the unconvolved posterior:

.. code-block:: python

	print('creating plot of posterior predictions against data ...')
	plt.figure()
	data = solver.posterior_predictions_convolved(outputfiles_basename, transformations, nsamples = 100)
	# plot data
	#plt.errorbar(x=data['bins'], xerr=data['width'], y=data['data'], yerr=data['error'],
	#	label='data', marker='o', color='green')
	# bin data for plotting
	print('binning for plot...')
	binned = binning(outputfiles_basename=outputfiles_basename, 
		bins = data['bins'], widths = data['width'], 
		data = data['data'], models = data['models'])
	for point in binned['marked_binned']:
		plt.errorbar(marker='o', zorder=-1, **point)
	plt.xlim(binned['xlim'])
	plt.ylim(binned['ylim'][0], binned['ylim'][1]*2)
	plt.gca().set_yscale('log')
	if Plot.xAxis == 'keV':
		plt.xlabel('Energy [keV]')
	elif Plot.xAxis == 'channel':
		plt.xlabel('Channel')
	plt.ylabel('Counts/s/cm$^2$')
	print('saving plot...')
	plt.savefig(outputfiles_basename + 'convolved_posterior.pdf', bbox_inches='tight')
	plt.close()

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

The following code creates a plot of the unconvolved posterior:

.. code-block:: python

	print('creating plot of posterior predictions ...')
	plt.figure()
	solver.posterior_predictions_unconvolved(transformations, nsamples = 100)
	ylim = plt.ylim()
	# 3 orders of magnitude at most
	plt.ylim(max(ylim[0], ylim[1] / 1000), ylim[1])
	plt.gca().set_yscale('log')
	if Plot.xAxis == 'keV':
		plt.xlabel('Energy [keV]')
	elif Plot.xAxis == 'channel':
		plt.xlabel('Channel')
	plt.ylabel('Counts/s/cm$^2$')
	print('saving plot...')
	plt.savefig(outputfiles_basename + 'unconvolved_posterior.pdf', bbox_inches='tight')
	plt.close()

.. figure:: absorbed-unconvolved_posterior.pdf
	
	Example of the unconvolved spectrum with data.
	For each posterior sample (solution), the parameters are taken and put
	through the model. All such lines are plotted. Where the region is darker,
	more lines ended up, and thus it is more likely.

For plotting the model parameters found against the data, use these functions.

.. automethod:: bxa.xspec.BXASolver.posterior_predictions_unconvolved
.. automethod:: bxa.xspec.BXASolver.posterior_predictions_convolved
.. automodule:: bxa.xspec.sinning
	:members: binning


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

For Xspec, the *qq* function in the *qq* module allows you to create such plots easily::

	print('creating quantile-quantile plot ...')
	solver.set_best_fit()
	plt.figure(figsize=(7,7))
	bxa.qq.qq(prefix=outputfiles_basename, markers = 5, annotate = True)
	print('saving plot...')
	plt.savefig(outputfiles_basename + 'qq_model_deviations.pdf', bbox_inches='tight')
	plt.close()

.. autofunction:: bxa.xspec.qq.qq

Refer to the :ref:`accompaning paper <cite>`, which gives an introduction and 
detailed discussion on the methodology.
