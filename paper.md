---
title: 'Bayesian X-ray Analysis (BXA) v4.0'
tags:
  - X-rays
  - Python
  - Bayesian inference
  - Nested Sampling
  - Spectroscopy
  - Bayes factors
authors:
  - name: Johannes Buchner
    orcid: 0000-0003-0872-7098
    affiliation: "1, 2, 3, 4"
affiliations:
 - name: Max Planck Institute for Extraterrestrial Physics, Giessenbachstrasse, 85741 Garching, Germany. 
   index: 1
 - name: Millenium Institute of Astrophysics, Vicuña MacKenna 4860, 7820436 Macul, Santiago, Chile . . . 
   index: 2
 - name: Pontificia Universidad Católica de Chile, Instituto de Astrofísica, Casilla 306, Santiago 22, Chile. 
   index: 3
 - name: Excellence Cluster Universe, Boltzmannstr. 2, D-85748, Garching, Germany  
   index: 4

date: 22 January 2021
bibliography: paper.bib

---

# Summary

BXA connects the X-ray specral analysis environments Xspec 
[@XSPEC] and Sherpa [@Freeman2001]
with modern Bayesian inference algorithms based on nested sampling.
This allows estimation of parameter probability distributions and
model comparison with Bayes factors. Because BXA is a plugin,
users can build and fit the full range of models 
available in Xspec and Sherpa. 
BXA also comes with convenience functionality for backgrounds 
of many X-ray missions, which allow extracting more information from low-count data.

# Statement of need

In X-ray spectroscopy, the instrument responses are often not trivial,
which means that forward folding is required to test models against data.
Judging realistic physical models, which can be degenerate, 
against data, which sometimes consist of few photon counts, is a challenge.
Bayesian inference provides a good solution in this setting.

For parameter estimation, Bayesian inference updates an initial state of information 
using the data and a model into a new state (posterior probability distribution).
In practice, Bayesian inference algorithms perform an approximation using sampling.
Before BXA, Bayesian X-ray spectral analyses have been limited to 
versions of Markov Chain Monte Carlo (MCMC) [e.g., @Dyk2001]
that were difficult to initialise and tune.
MCMC also has limitations when models have multiple parameter peaks, which is
common in the additive models typically considered in X-ray astronomy.

BXA uses nested sampling [@Skilling2004] to efficiently generate posterior samples.
BXA does not require custom initialisation and proposal tuning,
as nested sampling performs a global scan of the parameter space.
This makes it robust and easy to use in large X-ray surveys with many objects,
and in cases where many models should be compared.
BXA can also be substantially more efficient than MCMC
in low-dimensional settings ($d<10$).
With Bayesian inference and advanced sampling algorithms,
low count data is also not a difficult special case anymore.

Comparing astrophysical models is currently primarily performed either
using likelihood ratio tests (F-test) or Monte Carlo simulations to evaluate
goodness-of-fit measures. The former are often invalid [@Protassov2002], 
while the latter are computationally very expensive. 
Bayesian model comparison provides an 
alternative approach, which is natural in Bayesian inference.
BXA (via nested sampling) makes Bayesian model comparison computationally
feasible.

# Features

BXA connects the X-ray spectral analysis environments Xspec/Sherpa
to the nested sampling algorithm UltraNest 
for Bayesian parameter estimation and model comparison.

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
   * unlike likelihood-ratios, not limited to nested and linear models 
* model discovery:
   * visualize deviations between model and data with binning-independent Quantile-Quantile (QQ) plots.
* empirical background models
   * for getting more information out of low-count spectra

BXA shines especially

* when systematically analysing a large data-set, or
* when comparing multiple models, or
* when analysing low counts data-set
* for unsupervised, automated fitting

# Methods

The methods and limitations of BXA were presented in more detail in
 [@Buchner2014].
Until v3.0, BXA employed the Fortran package MultiNest [@Feroz2009] to
perform Bayesian inference. 
Since v4.0, BXA uses the Python package UltraNest [@ultranest], 
which is easier to install.

# Documentation

[Extensive documentation](https://johannesbuchner.github.io/BXA/) is available.



# Acknowledgements

I thank Antonis Georgakakis, Charlotte Simmonds, J. Michael Burgess and Kirpal Nandra
for insightful conversations.

Early versions of BXA for Sherpa were based on pyblocxs code [@pyblocxs].

# References
