Recommendations for X-ray spectral analysis
--------------------------------------------

For good and valid results, experienced users of XSpec or Sherpa already do these:

1. Using a continuous background model (parameteric, albeit not necessarily physical),
   instead of "subtracting" or using bin-wise backgrounds (XSpec default).
   Commonly, a extraction region near the source is used to estimate the background.
2. Use C-Stat/Cash (poisson likelihood) instead of Chi^2 (gaussian likelihood)
3. Use unbinned spectra (except perhaps for visualization, albeit you can use QQ-plots there without loss of resolution)

Beyond these already accepted practices, we recommend:

4. Estimating the values with uncertainties using Bayesian inference (this software, or MCMC methods)
   instead of Contour-search, Fisher matrix, stepping, or other approximations
   
   Instead of a local optimization, the benefit is that a global search can deal with multiples solutions.
   Error propagation is easy too when using the posterior samples (similar to a Markov chain),
   and it preserves the structure of the error (dependence between parameters, etc.)

5. Comparing models using the computed evidence (this software)
   instead of Likelihood ratio tests (which are invalid for non-nested models)
   
   Bayesian model selection based on the "evidence" Z resolves a number of limitations
   of current methods, and is easy to do with this software.

See the :ref:`accompaning paper <cite>` for a detailed discussion and comparison! 
