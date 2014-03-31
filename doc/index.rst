Welcome to BXA's documentation!
=======================================

About Bayesian X-ray Analysis (BXA)
------------------------------------

BXA connects the nested sampling algorithm MultiNest to the 
X-ray spectral analysis environments Xspec/Sherpa 
for **Bayesian Parameter Estimation** and **Model comparison**.

BXA provides the following features:

  * parameter estimation in arbitrary dimensions, which involves:
     * finding the best fit
     * computing error bars
     * computing marginal probability distributions
  * plotting of spectral model vs. the data:
     * for the best fit
     * for each of the solutions (posterior samples)
     * for each component
  * model selection:
     * computing the evidence for the considered model, 
       ready for use in computing Bayes factors
     * unlike likelihood-ratios, not limited to nested models 
  * model discovery:
     * visualize deviations between model and data with Quantile-Quantile (QQ) plots.
       QQ-plots do not require binning and are more comprehensive than residuals.
       This will give you ideas on when to introduce more complex models, which 
       may again be tested with model selection

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

Get BXA
-------------------------------

See the `code repository page <https://github.com/JohannesBuchner/BXA>`_ 

.. _cite:

Citing BXA correctly
---------------------

Refer to the `accompaning paper <http://www2011.mpe.mpg.de/heg/internal-papers/spectra_methods_obscured_AGN.pdf>`_ which gives introduction and 
detailed discussion on the methodology and its statistical footing.

We suggest giving credit to the developers of Sherpa/Xspec, MultiNest and of this software.
As an example::

	For analysing X-ray spectra, we use the analysis software BXA (\ref{Buchner2014}),
	which connects the nested sampling algorithm MultiNest (\ref{FerozHobson2010})
	with the fitting environment CIAO/Sherpa (\ref{Fruscione2006}).

Where the BibTex entries are:

* for BXA, PyMultiNest software, and the contributions to X-ray spectral analysis methodology (model comparison, model discovery, Experiment design, Model discovery through QQ-plots): 
	* Buchner et al. (2014) A&A
	* The paper is available in `MPE HEG <http://www2011.mpe.mpg.de/heg/internal-papers/spectra_methods_obscured_AGN.pdf>`_
* for MultiNest: see `MultiNest <http://ccpforge.cse.rl.ac.uk/gf/project/multinest/>`_
* for Sherpa: see `Sherpa`_
* for Xspec: see `Xspec`_


Installation
-------------

You need to have `pymultinest`_ and `MultiNest <https://github.com/JohannesBuchner/MultiNest>`_ installed and working.

* `Installation for those two packages only <http://johannesbuchner.github.io/pymultinest-tutorial/install.html#on-your-own-computer>`_
* `Extensive PyMultiNest, PyAPEMoST, PyCuba installation instructions <http://johannesbuchner.github.io/PyMultiNest/install.html>`_

You need to have `Sherpa`_ or `Xspec`_ installed and its environment loaded.

Install the needed python packages, through your package manager, through pip or easy_install. For example::

	$ yum install ipython python-matplotlib scipy numpy matplotlib
	$ apt-get install python-numpy python-scipy python-matplotlib ipython

	$ pip install progressbar --user

Then, just download and install bxa as a python package::

	$ python setup.py install

Or if you only want to install it for the current user::

	$ python setup.py install --user

In *Sherpa*, load the package::

	jbuchner@ds42 ~ $ sherpa
	-----------------------------------------------------
	Welcome to Sherpa: CXC's Modeling and Fitting Package
	-----------------------------------------------------
	CIAO 4.4 Sherpa version 2 Tuesday, June 5, 2012

	sherpa-1> import bxa.sherpa as bxa
	sherpa-2> bxa.run_model?

For *Xspec*, start python or ipython::
	
	jbuchner@ds42 ~ $ ipython
	In [1]: import xspec
	
	In [2]: import bxa.xspec as bxa
	
	In [3]:	bxa.standard_analysis?
	
Now you can use bxa.


.. _pymultinest: http://johannesbuchner.github.io/PyMultiNest/

.. _Sherpa: http://cxc.harvard.edu/sherpa/

.. _Xspec: http://heasarc.gsfc.nasa.gov/docs/xanadu/xspec/



Documentation:
-------------------------------

.. toctree::
   sherpa-analysis
   xspec-analysis
   :maxdepth: -1

Indices and tables
-------------------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

