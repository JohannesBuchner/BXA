# X-ray Spectral fitting with PyXspec and BXA

This directory is centred on two Python classes, PlotXspec and PlotBXA, that provide additional plotting functionality for X-ray spectral fitting with PyXspec and BXA, as well as methods to assist with Bayesian analysis of the fitted models. The repository contains the following files:

- *plot_xspec.py*: the class definition for PlotXspec
- *plot_bxa.py*: the class definition for PlotBXA

In the subdirectory `tutorials`:
- *tutorial_usage_plotxspec.ipynb*: a tutorial notebook for using PlotXspec
- *tutorial_usage_plotbxa.ipynb*: a tutorial notebook for using PlotBXA
- *mp_scripts/parallel_bxa_tt1.py*: a Python script to illustrate launching multiple BXA processes simultaneously (the explanation is part of *tutorial_usage_plotbxa.ipynb*)
- *mp_scripts/mpi_bxa_example.py*: a Python script used to help illustrate how to use MPI & OpenMP in speeding up BXA fitting

## Using this repository

The tutorial notebooks provide an introduction to both of the classes. Users are encouraged to make use of these notebooks to familiarise themselves with the usage of the class methods. PlotXspec transports some of the basic XSpec plotting options to Python. PlotBXA includes BXA fitting results in these plotting options. 

PlotBXA also provides the possibility for additional analysis, with further tests and visualisations. These methods follow the examples set out in [Statistical Aspects of X-ray Spectral Analysis](https://ui.adsabs.harvard.edu/abs/2023hxga.book..150B/abstract). The *tutorial_usage_plotbxa* notebook provides an overview of how to apply the functionalities of PlotBXA to construct a Bayesian workflow for fitting with XSpec; both for fitting a single model and for model comparison.

For more experienced users, the methods (both public and private) provided in the PlotXspec and PlotBXA classes can also serve as a template or guide on how to access and manipulate the data in PyXspec and BXA, and how to use them to create plots.

### Requirements

In addition to the requirements for BXA, the classes defined here make use of the natsort package. If this is not yet installed on the system, it can be installed via pip or conda, e.g.:

```
$ pip install natsort
```

## Running the examples

Before running any of the scripts in the tutorial directory, it will be necessary to generate the test datasets. This can be done either by running `create_simdata.sh`, or by running `run_all.sh`. The latter script will also create a series of test fits and plots, using the basic methods of PlotXspec and PlotBXA. Once the files are generated, they will be stored in the directory `tutorials/example_data`, in the `athena` and `xmm` subdirectories.

---
**Contact**

David Homan
dshoman@gmail.com

Please note: *all bug reports, suggestions, and contributions are welcome*.

---
