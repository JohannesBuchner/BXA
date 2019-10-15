==========================================
Machine-learned Background Spectral Model
==========================================

Builds a paramtric spectral model for the background of any instrument
from a large number of example background spectra.


Uses PCA to learn average spectral shape and features and their correlations.

Works on the detector-level, completely empirical (does not go through the response).
See Simmonds, Buchner et al. 2018.


Create a model
--------------

If you have a new instrument or survey, create a model with:

`python autobackgroundmodel/__init__.py bkg1.pha bkg2.pha bkg3.pha`

The resulting file is telescope.json or telescope_instrument.json.


Fitting a model
----------------

Once you want to fit a specific sources, you can obtain its background model
in two different ways:

**For use in xspec**, you can precompute a background model:

`python autobackgroundmodel/fitbkg.py bkg1.pha [src1.pha]`

This will make a file bkg1.pha.bstat.out with the estimated per-channel count rate.

**For use in sherpa**, use the autobackground feature.
see `examples/sherpa/example_automatic_background.py`

If you have a new model (json file), it needs to be installed in the BXA folder,
probably at `~/.local/lib/python*/site-packages//bxa/sherpa/background/`.

