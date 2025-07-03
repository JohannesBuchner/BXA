Welcome to BXA's documentation!
=======================================

.. include:: ../README.rst

Usage
--------

* We start with some notes on :doc:`best practice <best-practise>` in currently common 
  Maximum Likelihood analysis (fitting) and Bayesian analysis.

The usage is similar in Sherpa and Xspec conceptionally:

* Define **priors** as transformations from the unit cube to the parameter space
	* :ref:`In Sherpa <sherpa-priors>`
	* :ref:`In Xspec <xspec-priors>`
* **Run** the analysis
	* :ref:`In Sherpa <sherpa-run>`
	* :ref:`In Xspec <xspec-run>`
* **Analyse** the results: Get marginal distributions and computed evidence for the model
	* :ref:`In Sherpa <sherpa-analyse>`
	* :ref:`In Xspec <xspec-analyse>`
* **Model comparison**
	* :ref:`In Sherpa <sherpa-models>`
	* :ref:`In Xspec <xspec-models>`
* **Experiment design**
	* :ref:`In Sherpa <sherpa-design>`
	* :ref:`In Xspec <xspec-design>`
* **Model discovery**: Quantile-Quantile (QQ) plots
	* :ref:`In Sherpa <sherpa-qq>`
	* :ref:`In Xspec <xspec-qq>`

.. toctree::
   :maxdepth: 1
   :caption: Documentation

   sherpa-analysis
   xspec-analysis
   contributing
   history
   modules

.. toctree::
   :maxdepth: 1
   :caption: Learn more

   visualisations
   engine
   tutorials
   convenience
   background-models
   pca-background-models

.. toctree::
   :maxdepth: 1
   :caption: Examples

   examples
   xagnfitter
   tutorial_usage_plotbxa.ipynb
   tutorial_usage_plotxspec.ipynb

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
