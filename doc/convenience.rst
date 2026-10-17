Convenience features
=======================================

.. contents:: :local:

Fixing FITS keywords
----------------------------

Source, background, ARF and RMF files should reference each other
by FITS header keywords.

The `fixkeywords.py <https://github.com/JohannesBuchner/BXA/blob/master/fixkeywords.py>`_
script adjusts the keywords::

	fixkeywords.py src.pi bkg.pi rmf.rmf arf.arf

This also fixes ARF/RMF that start the energy bounds at zero (which is invalid)
instead of a small number.

Combining spectra
----------------------------

The ``addspec.py`` script sums source and background spectra with compatible
channel and response energy grids::

	python addspec.py sum observation1.pha observation2.pha

This creates ``sum.pha`` and ``sum_bkg.pha``. For identical RMF files with
separate ARFs, it retains ``.arf`` and ``.rmf`` outputs. Otherwise, it multiplies
each RMF by its corresponding ARF with ``marfrmf`` before averaging with
``addrmf``.
The resulting ``.rsp`` contains the effective area, so the output spectrum
references it with ``RESPFILE`` and sets ``ANCRFILE=NONE``. Source and
background responses are handled independently. Inputs with ``ANCRFILE=NONE``
are used as complete responses without an additional ARF multiplication.

Response weights are proportional to exposure times AREASCAL. The output
exposure is the sum of the input exposures, and the output AREASCAL is their
exposure-weighted mean. This preserves the summed forward-folded prediction
for a common incident spectrum. It does not retain all the information of a
joint fit, and source/background extraction scaling must also be compatible.


Galactic absorption
----------------------------

The galactic column density in the direction of the source is often needed.
https://www.swift.ac.uk/analysis/nhtot/donhtot.php provides a look-up service.

The `gal.py <https://github.com/JohannesBuchner/BXA/blob/master/gal.py>`_
script fetches the value from there::

	gal.py src.pi

and stores it in src.pi.nh.

You can also give this script multiple spectral files and it avoids duplicate requests.


Accelerating slow models
----------------------------

Some models are very slow (such as convolutions).
It is worthwhile to cache them or produce interpolation grids.

For Sherpa, caching of arbitrary models is provided by CachedModel, which you can use as a wrapper:

.. autoclass:: bxa.sherpa.cachedmodel.CachedModel
	:noindex:


Automatic production of an interpolation model is possible with the RebinnedModel:

.. autoclass:: bxa.sherpa.rebinnedmodel.RebinnedModel
	:noindex:


Xspec chain files
----------------------------

BXA, when run from pyxspec, also provides chain fits file compatible with the
mcmc feature in xspec/pyxspec. xspec error propagation tools can thus be used
after a BXA fit. In xspec, one can load it with::

	XSPEC12> chain load path/to/mychain.fits


Parallelisation
---------------------------

BXA supports parallelisation with MPI (Message Passing Interface).
This allows scaling the inference from laptops all the way to computing clusters.

To use it, install mpi4py and run your python script with mpiexec::

	$ mpiexec -np 4 python3 myscript.py

No modifications of your scripts are needed. However, you may want to 
run plotting and other post-analysis only on rank 0.

Analysis of many data sets, or of many models are trivial to parallelise.
If your script accepts a command line argument, unix tools such as
"make -j 10" and "xargs --max-args 1 --max-procs 10" 
can help run your code in parallel.


Verbosity
--------------------------

If you want to make the fitting more quiet, set `verbose=False` when calling `run()`.

You can find more instructions 
`how to reduce the output of the UltraNest fitting engine here <https://johannesbuchner.github.io/UltraNest/issues.html#how-do-i-suppress-the-output>`_.

Code inside a XSilence container disables Xspec chatter::

	from bxa.xspec.solver import XSilence
	
	with XSilence():
		# do something here
