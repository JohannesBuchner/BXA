==============
Release Notes
==============

5.0.0 (2024-07-03)
------------------

* potentially breaking change: xspec: in BXA v5, priors now use min/max soft parameter limits instead of hard parameter limits. That is, among "min, bottom, top, and max", BXA<5 used min and max, while BXA>=5 uses bottom and top.
* xspec: compute fluxes for multi-source and multi-spectrum cases (thanks @DaKalt)
* sherpa: smooth interpolation in CDF prior file interpolation
* add eROSITA background file

4.1.4 (2024-05-26)
------------------

* fix in BXA/sherpa PCA background fitting. Previously, emission lines were never added.

  * This means that versions before 4.1.3 and after will give different background fits
  * The old behaviour can be recovered with auto_background(max_lines=0).

* add Bayesian workflow tutorial

4.0.0 (2021-01-06)
------------------

* Make ultranest default, remove multinest.

3.4 (2019-05-26)
------------------

3.3 (2020-01-28)
------------------

3.2 (2020-01-12)
------------------

* circumvent xspec numerical interpolation issues (Lepsilon parameter)

3.1 (2019-10-21)
------------------

* Make multinest optional, allow ultranest

3.0 (2019-10-15)
------------------

2.10 (2019-06-12)
------------------

* Added PCA background models

2.9 (2019-06-11)
-----------------

2.8 (2019-05-31)
-----------------

2.7 (2019-05-31)
-----------------

2.6 (2019-05-21)
-----------------

* replace outdated progressbar with tqdm

2.5 (2019-04-08)
-----------------

* added PCA background model
* added galactic absorption fetcher
* added generic AGN fitting script

2.4 (2015-06-17)
-----------------

2.3 (2015-06-09)
-----------------

* added  Chandra background model
* added  Swift background model

2.0.0 (2015-06-05)
------------------

* Python 3 support
* added corner plots
* added more convenience functions for plotting
* added Chandra background model
* added acceleration of models

1.0.0 (2013-12-01)
------------------

* simple multinest interfaces for xspec and sherpa based on pyblocxs code
