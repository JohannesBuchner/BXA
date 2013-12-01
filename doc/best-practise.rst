Recommendations for X-ray spectral analysis
--------------------------------------------

For good and valid results, experienced users of XSpec or Sherpa already do these:

1. Using a continuous background model (parameteric, albeit not necessarily physical),
   instead of "subtracting" or using bin-wise backgrounds (XSpec default).
   Commonly, a extraction region near the source is used to estimate the background.
2. Use C-Stat/Cash (poisson likelihood) instead of Chi^2 (gaussian likelihood)
3. Use unbinned spectra (except perhaps for visualization, albeit you can use QQ-plots there without loss of resolution)

Beyond these already accepted practices, we recommend:

4. Estimating the values with uncertainties using nested sampling (this software)
   instead of Contour-search, Fisher matrix, stepping, or other approximations
5. Comparing models using the computed evidence (this software)
   instead of Likelihood ratio tests (which are invalid for non-nested models)

See the :ref:`accompaning paper <cite>` for a detailed discussion and comparison! 


