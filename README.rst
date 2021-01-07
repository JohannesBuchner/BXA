About Bayesian X-ray Analysis (BXA)
------------------------------------

BXA connects the X-ray spectral analysis environments Xspec/Sherpa
to the nested sampling algorithm UltraNest 
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
     ready for use in Bayes factors
   * unlike likelihood-ratios, not limited to nested models 
* model discovery:
   * visualize deviations between model and data with Quantile-Quantile (QQ) plots.
     QQ-plots do not require binning and are more comprehensive than residuals.
     This will give you ideas on when to introduce more complex models, which 
     may again be tested with model selection

BXA shines especially

* when systematically analysing a large data-set, or
* when comparing multiple models, or
* when analysing low counts data-set
* when you don't want to babysit your fits
* when you don't want to test MCMC chains for their convergence

Who is using BXA?
-------------------------------

* Dr. Antonis Georgakakis (NOA, Athens)
* Dr. Mike Anderson (MPA, Munich)
* Dr. Franz Bauer, Charlotte Simmonds (PUC, Santiago)
* Dr. Stéphane Paltani (ISDC, Geneva)
* Dr. Zhu Liu (NAO, Beijing)
* Dr. Francesca Civano, Dr. Aneta Siemiginowska (CfA/SAO, Cambridge)
* Dr. Teng Liu, Adam Malyali, Riccardo Arcodia, Sophia Waddell, ... (MPE, Garching)
* and you?

Documentation
----------------

BXA's `documentation <http://johannesbuchner.github.io/BXA/>`_ is hosted at http://johannesbuchner.github.io/BXA/

Installation
-------------

First, you need to have `Sherpa`_ or `Xspec`_ installed and its environment loaded.

BXA itself can installed easily using pip::

	$ pip install bxa

If you want to install in your home directory, install with::

	$ pip install bxa --user

The following commands should not yield any error message::

	$ python -c 'import ultranest'
	$ python -c 'import xspec'
	$ sherpa

You may need to install required python packages through your package manager. For example::

	$ yum install ipython python-matplotlib scipy numpy matplotlib
	$ apt-get install python-numpy python-scipy python-matplotlib ipython

The source code is available from https://github.com/JohannesBuchner/BXA,
so alternatively you can download and install it::
	
	$ git clone https://github.com/JohannesBuchner/BXA
	$ cd BXA
	$ python setup.py install

Or if you only want to install it for the current user::

	$ python setup.py install --user

Running
--------------

In *Sherpa*, load the package::

	jbuchner@ds42 ~ $ sherpa
	-----------------------------------------------------
	Welcome to Sherpa: CXC's Modeling and Fitting Package
	-----------------------------------------------------
	CIAO 4.4 Sherpa version 2 Tuesday, June 5, 2012

	sherpa-1> import bxa.sherpa as bxa
	sherpa-2> bxa.BXASolver?

For *Xspec*, start python or ipython::
	
	jbuchner@ds42 ~ $ ipython
	In [1]: import xspec
	
	In [2]: import bxa.xspec as bxa
	
	In [3]:	bxa.BXASolver?

Now you can use BXA.

.. _ultranest: http://johannesbuchner.github.io/UltraNest/

.. _Sherpa: http://cxc.harvard.edu/sherpa/

.. _Xspec: http://heasarc.gsfc.nasa.gov/docs/xanadu/xspec/

Code
-------------------------------

See the `code repository page <https://github.com/JohannesBuchner/BXA>`_ 

.. _cite:

Citing BXA correctly
---------------------

Refer to the `accompaning paper Buchner et al. (2014) <http://www.aanda.org/articles/aa/abs/2014/04/aa22971-13/aa22971-13.html>`_ which gives introduction and 
detailed discussion on the methodology and its statistical footing.

We suggest giving credit to the developers of Sherpa/Xspec, UltraNest and of this software.
As an example::

	For analysing X-ray spectra, we use the analysis software BXA (\ref{Buchner2014}),
	which connects the nested sampling algorithm UltraNest (\ref{ultranest})
	with the fitting environment CIAO/Sherpa (\ref{Fruscione2006}).

Where the BibTex entries are:

* for BXA and the contributions to X-ray spectral analysis methodology (model comparison, model discovery, Experiment design, Model discovery through QQ-plots):

	- Buchner et al. (2014) A&A
	- The paper is available at `arXiv:1402.0004 <http://arxiv.org/abs/arXiv:1402.0004>`_
	- `bibtex entry <https://ui.adsabs.harvard.edu/abs/2014A%26A...564A.125B/exportcitation>`_

* for UltraNest: see https://johannesbuchner.github.io/UltraNest/issues.html#how-should-i-cite-ultranest
* for Sherpa: see `Sherpa`_
* for Xspec: see `Xspec`_
