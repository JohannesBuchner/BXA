"""FITS-chain regressions for issue #65, using real PyXspec models and chains.

After initializing HEASoft, run from the repository root with:
    python -m unittest discover -s tests -p test_xspec_chain.py -v

The run regression uses deterministic sampler results. XSPEC evaluates the
reference likelihoods and loads the exported FITS files. All products are temporary.
"""

import contextlib
import io
import os
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import numpy as np
from astropy.io import fits

try:
    import xspec
except ImportError:
    xspec = None
else:
    from bxa.xspec import priors
    from bxa.xspec import solver as solver_module


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipIf(xspec is None, "PyXspec is required; initialize HEASoft")
class XspecChainTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="bxa-chain-test-")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        previous_directory = Path.cwd()
        self.addCleanup(os.chdir, previous_directory)
        os.chdir(self.directory)
        # The example uses relative paths to its background and response files.
        for name in ("interval0pc.pi", "interval0pcback.pi",
                     "interval0pc.rmf", "interval0pc.arf"):
            shutil.copyfile(ROOT / "examples" / "sherpa" / "swift" / name,
                            self.directory / name)
        self.old_chatter = xspec.Xset.chatter, xspec.Xset.logChatter
        self.old_statistic = xspec.Fit.statMethod
        self.addCleanup(self.clear_xspec)
        xspec.Xset.chatter = xspec.Xset.logChatter = 0
        xspec.AllChains.clear()
        xspec.AllData.clear()
        xspec.AllModels.clear()
        xspec.Spectrum("interval0pc.pi")
        self.model = xspec.Model("powerlaw")
        self.model.powerlaw.PhoIndex.values = (2, 0.1, 1, 1, 4, 4)
        self.model.powerlaw.norm.values = (0.001, 0.1, 1e-5, 1e-5, 100, 100)
        xspec.Fit.statMethod = "cstat"
        with contextlib.redirect_stdout(io.StringIO()):
            self.transformations = [
                priors.create_uniform_prior_for(self.model, self.model.powerlaw.PhoIndex),
                priors.create_loguniform_prior_for(self.model, self.model.powerlaw.norm),
            ]
        self.chain = self.directory / "chain.fits"

    def clear_xspec(self):
        xspec.AllChains.clear()
        xspec.AllData.clear()
        xspec.AllModels.clear()
        xspec.Fit.statMethod = self.old_statistic
        xspec.Xset.chatter, xspec.Xset.logChatter = self.old_chatter

    def test_mixed_priors_in_either_parameter_order(self):
        posterior = np.array([[2.0, 0.0], [3.0, 1.0]])
        for order in ([0, 1], [1, 0]):
            with self.subTest(order=order):
                xspec.AllChains.clear()
                solver_module.store_chain(
                    self.chain, [self.transformations[i] for i in order],
                    posterior[:, order], [20.0, 40.0])
                with fits.open(self.chain) as hdus:
                    table = hdus["CHAIN"].data
                    self.assertEqual(table.names, ["PhoIndex__1", "norm__2", "FIT_STATISTIC"])
                    np.testing.assert_array_equal(table["PhoIndex__1"], [2.0, 3.0])
                    np.testing.assert_array_equal(table["norm__2"], [1.0, 10.0])
                    np.testing.assert_array_equal(table["FIT_STATISTIC"], [20.0, 40.0])
                xspec.AllChains += str(self.chain)
                self.assertEqual(xspec.AllChains(1).totalLength, 2)
                np.testing.assert_allclose(xspec.AllChains.best(), [2.0, 1.0, 20.0])

    def test_run_preserves_complete_sample_statistic_alignment(self):
        solver = solver_module.BXASolver(
            self.transformations, outputfiles_basename=str(self.directory / "run"))
        # Different rows share coordinates; one full row is also duplicated.
        points = np.array([[2.0, -3.0], [2.0, -2.0], [3.0, -3.0],
                           [3.0, -2.0], [2.0, -3.0]])
        logls = np.array([solver.log_likelihood(point) for point in points])
        self.assertEqual(len(np.unique(logls)), 4)
        order = [3, 1, 1, 2, 0]
        posterior = points[order].copy()
        results = {
            "samples": posterior,
            "weighted_samples": {"points": points, "logl": logls,
                                 "weights": np.full(len(points), 1.0 / len(points))},
            "logz": -123.0,
        }
        sampler = SimpleNamespace(results=results, run=Mock(),
                                  print_results=Mock(), plot=Mock())
        # Export should reuse the stored likelihoods, not rerun the likelihood.
        with patch.object(solver_module, "ReactiveNestedSampler", return_value=sampler), \
                patch.object(solver, "log_likelihood", side_effect=AssertionError(
                    "Chain export must not re-evaluate the likelihood")):
            returned = solver.run(sampler_kwargs={}, run_kwargs={})
        self.assertIs(returned, results)
        self.assertIs(solver.posterior, posterior)
        np.testing.assert_array_equal(posterior, points[order])
        np.testing.assert_array_equal(results["weighted_samples"]["logl"], logls)
        self.assertEqual(returned["logz"], -123.0)
        expected_statistic = -2.0 * logls[order]
        with fits.open(self.directory / "run" / "chain.fits") as hdus:
            table = hdus["CHAIN"].data
            np.testing.assert_array_equal(table["PhoIndex__1"], posterior[:, 0])
            np.testing.assert_allclose(table["norm__2"], 10.0 ** posterior[:, 1])
            np.testing.assert_array_equal(table["FIT_STATISTIC"], expected_statistic)
        self.assertEqual(xspec.AllChains(1).totalLength, len(posterior))
        best = posterior[expected_statistic.argmin()]
        np.testing.assert_allclose(
            xspec.AllChains.best(), [best[0], 10.0 ** best[1], expected_statistic.min()],
            rtol=1e-5)
        # run() must still leave the model at the best weighted-sample fit.
        best = points[logls.argmax()]
        np.testing.assert_allclose(
            [self.model.powerlaw.PhoIndex.values[0], self.model.powerlaw.norm.values[0]],
            [best[0], 10.0 ** best[1]])

    def test_rejects_missing_or_misaligned_fit_statistics(self):
        posterior = np.array([[2.0, 0.0], [3.0, 1.0]])
        for statistic in ([], [20.0], [20.0, 40.0, 60.0], [[20.0], [40.0]]):
            with self.subTest(statistic=statistic):
                with self.assertRaisesRegex(ValueError, "one value per posterior sample"):
                    solver_module.store_chain(
                        self.chain, self.transformations, posterior, statistic)
                self.assertFalse(self.chain.exists())

    def test_rejects_incompatible_posterior_shape(self):
        for posterior in (np.ones(2), np.ones((2, 1)), np.ones((2, 3))):
            with self.subTest(shape=posterior.shape):
                with self.assertRaisesRegex(ValueError, "one column per parameter"):
                    solver_module.store_chain(
                        self.chain, self.transformations, posterior, [20.0, 40.0])
                self.assertFalse(self.chain.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
