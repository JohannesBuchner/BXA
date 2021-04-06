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
 - name: Millenium Institute of Astrophysics, Vicuña MacKenna 4860, 7820436 Macul, Santiago, Chile
   index: 2
 - name: Pontificia Universidad Católica de Chile, Instituto de Astrofísica, Casilla 306, Santiago 22, Chile.
   index: 3
 - name: Excellence Cluster Universe, Boltzmannstr. 2, D-85748, Garching, Germany
   index: 4

date: 22 January 2021
bibliography: paper.bib

---

# Summary

BXA connects the X-ray spectral analysis environments Xspec
[@XSPEC] and Sherpa [@Freeman2001]
with modern Bayesian inference algorithms based on nested sampling.
This allows estimation of parameter probability distributions and
model comparison with Bayes factors. Because BXA is a plug-in,
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
In practice, Bayesian inference algorithms approximate the posterior by Monte Carlo sampling.
Before BXA, Bayesian X-ray spectral analyses have been implemented with
Markov Chain Monte Carlo (MCMC).
The variants include Metropolis random walks [e.g., @Dyk2001] and
affine-invariant ensembles [@GoodmanWeare].
These can be difficult to initialise and/or tune, and require complicated
checks of the chain convergence to determine when to terminate the computation,
and how to select good posterior samples from the chain.
MCMC tends to be computationally costly, and difficult to parallelise.
MCMC has limitations when models have multiple posterior peaks. These are
common in the additive models typically considered in X-ray astronomy
when combined with data sets of low spectral quality.
For these reasons, Bayesian X-ray analyses, as implemented in existing
popular packages, can be unsatisfying.

BXA uses nested sampling [@Skilling2004] to efficiently generate posterior samples.
Nested sampling performs a global scan of the parameter space,
without requiring a user-defined starting point.
This makes it robust and easy to use in large X-ray surveys with many objects,
and in situations where many models should be compared.
Nested sampling can be substantially more efficient than MCMC
in low-dimensional settings ($d<10$) [@Speagle2020].

Comparing astrophysical models is currently primarily performed either
using likelihood ratio tests (F-test) or Monte Carlo simulations to evaluate
goodness-of-fit measures. The former are often invalid [@Protassov2002],
while the latter are computationally very expensive.
Bayesian model comparison with posterior odds ratios, provides an
alternative approach, which is natural in Bayesian inference.
BXA (via nested sampling) makes Bayesian model comparison computationally
feasible to apply and calibrate with simulated data [see e.g., @Buchner2014].

# Features

BXA connects the X-ray spectral analysis environments Xspec/Sherpa
to the nested sampling algorithm UltraNest
for Bayesian parameter estimation and model comparison.

BXA provides the following features:

* parameter estimation in arbitrary dimensions, which involves:
   * finding the best fit
   * computing error bars
   * computing marginal probability distributions
   * parallelisation with MPI
* plotting of spectral model vs. the data:
   * for the best fit
   * for each of the solutions (posterior samples)
   * for each component
* model selection:
   * computing the Bayesian evidence for the considered model,
     ready for use in Bayes factors
   * unlike likelihood-ratios, not limited to nested and linear models
* model discovery:
   * visualize deviations between model and data with binning-independent Quantile-Quantile (QQ) plots.
* empirical background models:
   * for getting more information out of low-count spectra

BXA shines especially

* when systematically analysing a large data-set, or
* when comparing multiple models
* when analysing low counts data-set with realistic models

because its robust and unsupervised fitting algorithm explores
even complicated parameter spaces in an automated fashion.
The user does not need to initialise to good starting points.
The algorithm automatically runs until convergence, and slows down to sample
carefully if complicated parameter spaces are encountered.
This allows building automated analysis pipelines.


# Methods

The methods and limitations of BXA were presented in more detail in
 [@Buchner2014].
Until v3.0, BXA employed the Fortran package MultiNest [@Feroz2009] to
perform Bayesian inference.
Since v4.0, BXA uses the Python package UltraNest [@ultranest],
which is easier to install.

# Documentation

[Extensive documentation](https://johannesbuchner.github.io/BXA/) is available.



# Acknowledgments

I thank Antonis Georgakakis, Charlotte Simmonds, J. Michael Burgess and Kirpal Nandra
for insightful conversations.
I thank Liu Zhu for implementing empirical background models for XMM,
and Liu Teng for implementing the export of PCA-based background models as table models.

Early versions of BXA for Sherpa were based on pyblocxs code [@pyblocxs].

# References
