"""End-to-end checks using the spectra in examples/sherpa.

Run ``python tests/test_addspec.py`` after initializing HEASoft. Requires
NumPy, Astropy, and the HEASoft tools listed below; no XSPEC/Sherpa Python
bindings are needed. All products and task parameter files are temporary.

Swift/XRT and XMM/MOS share an incident-energy grid, but not a channel grid.
For the mixed-instrument check, rebin temporary copies of their spectra and
RMFs to common 0.02-keV channels over 0--10 keV before calling addspec.
The temporary RMFs identify redistribution-only data and disable sparse
matrix truncation, so even tiny response elements can be compared directly.
The assertions concern source and background predictions separately, not
the statistical equivalence of stacking and a joint fit.
"""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from astropy.io import fits


ROOT = Path(__file__).resolve().parents[1]
ADDSPEC = ROOT / "addspec.py"
TOOLS = ("addarf", "addrmf", "marfrmf", "mathpha", "fmodhead",
         "ftrbnpha", "ftrbnrmf")
EXAMPLES = {
    "swift": ("interval0pc.pi", "interval0pcback.pi",
              "interval0pc.arf", "interval0pc.rmf"),
    "xmm": ("mos_spec.fits", "mos_backspec.fits", "mos.arf", "mos.rmf"),
}


def require_heasoft():
    missing = [tool for tool in TOOLS if shutil.which(tool) is None]
    if missing or not os.environ.get("HEADAS"):
        raise unittest.SkipTest(
            "Initialize HEASoft before running addspec checks; missing: "
            + ", ".join(missing or ["HEADAS"]))


class AddspecIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require_heasoft()

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="bxa-addspec-test-")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        pfiles = self.directory / "pfiles"
        pfiles.mkdir()
        self.env = os.environ.copy()
        self.env["PFILES"] = str(pfiles) + ";" + str(
            Path(self.env["HEADAS"]) / "syspfiles")
        self.env["HEADASNOQUERY"] = "1"

    def run_command(self, command):
        result = subprocess.run(
            [str(arg) for arg in command], cwd=self.directory, env=self.env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            timeout=120)
        self.assertEqual(result.returncode, 0,
                         "Command failed: %s\n%s" % (command, result.stdout))

    def stage_example(self, instrument):
        names = EXAMPLES[instrument]
        for name in names:
            shutil.copyfile(ROOT / "examples" / "sherpa" / instrument / name,
                            self.directory / name)
        return names

    def set_header(self, filename, **values):
        with fits.open(self.directory / filename, mode="update") as hdus:
            hdus["SPECTRUM"].header.update(values)

    def header(self, filename):
        return fits.getheader(self.directory / filename, "SPECTRUM")

    def forward_operator(self, filename, fallback=None):
        """Independently decode t * AREASCAL * RMF * ARF from OGIP files."""
        header = self.header(filename)
        rmf, arf = header["RESPFILE"], header["ANCRFILE"]
        if fallback is not None:
            source = self.header(fallback)
            if rmf.upper() == "NONE":
                rmf = source["RESPFILE"]
            if arf.upper() == "NONE":
                arf = source["ANCRFILE"]
        with fits.open(self.directory / rmf) as hdus:
            rows = hdus["MATRIX"].data
            bounds = hdus["EBOUNDS"].data
            channels = bounds["CHANNEL"]
            np.testing.assert_array_equal(
                channels, fits.getdata(self.directory / filename, "SPECTRUM")["CHANNEL"])
            np.testing.assert_array_equal(
                channels, np.arange(channels[0], channels[0] + len(channels)))
            grid = [rows["ENERG_LO"].copy(), rows["ENERG_HI"].copy(),
                    bounds["E_MIN"].copy(), bounds["E_MAX"].copy()]
            response = np.zeros((len(rows), len(channels)))
            for index, row in enumerate(rows):
                offset = 0
                starts = np.atleast_1d(row["F_CHAN"])[:row["N_GRP"]]
                lengths = np.atleast_1d(row["N_CHAN"])[:row["N_GRP"]]
                values = np.atleast_1d(row["MATRIX"])
                for start, length in zip(starts, lengths):
                    start = int(start) - int(channels[0])
                    length = int(length)
                    self.assertGreaterEqual(start, 0)
                    self.assertLessEqual(start + length, len(channels))
                    response[index, start:start + length] = values[offset:offset + length]
                    offset += length
        if arf.upper() != "NONE":
            with fits.open(self.directory / arf) as hdus:
                area = hdus["SPECRESP"].data
                np.testing.assert_array_equal(grid[0], area["ENERG_LO"])
                np.testing.assert_array_equal(grid[1], area["ENERG_HI"])
                response *= area["SPECRESP"][:, None]
        return grid, response * header["EXPOSURE"] * header["AREASCAL"]

    def check_sum(self, inputs, prefix, full_response=False):
        self.assertEqual(self.header(prefix + ".pha")["BACKFILE"], prefix + "_bkg.pha")
        backgrounds = [self.header(name)["BACKFILE"] for name in inputs]
        for names, output, fallbacks in (
                (inputs, prefix + ".pha", [None] * len(inputs)),
                (backgrounds, prefix + "_bkg.pha", inputs)):
            with self.subTest(spectrum=output):
                headers = [self.header(name) for name in names]
                header = self.header(output)
                exposure = sum(h["EXPOSURE"] for h in headers)
                areascal = sum(h["EXPOSURE"] * h["AREASCAL"] for h in headers) / exposure
                # mathpha rounds EXPOSURE to single-precision accuracy.
                np.testing.assert_allclose(header["EXPOSURE"], exposure, rtol=1e-6)
                np.testing.assert_allclose(header["AREASCAL"], areascal, rtol=1e-10)
                counts = sum(fits.getdata(self.directory / name, "SPECTRUM")["COUNTS"]
                             .astype(np.int64) for name in names)
                np.testing.assert_array_equal(
                    fits.getdata(self.directory / output, "SPECTRUM")["COUNTS"], counts)

                grid, actual = self.forward_operator(output)
                expected = np.zeros_like(actual)
                for name, fallback in zip(names, fallbacks):
                    input_grid, operator = self.forward_operator(name, fallback)
                    for out_axis, in_axis in zip(grid, input_grid):
                        np.testing.assert_allclose(out_axis, in_axis, rtol=1e-6, atol=1e-7)
                    expected += operator
                # FITS response matrices are stored as single-precision floats.
                # Comparing every element also covers any incident spectral shape.
                np.testing.assert_allclose(actual, expected, rtol=3e-6,
                                           atol=expected.max() * 1e-10)
                if full_response:
                    self.assertEqual(header["ANCRFILE"].upper(), "NONE")
                    self.assertTrue(header["RESPFILE"].endswith(".rsp"))
                else:
                    self.assertTrue(header["ANCRFILE"].endswith(".arf"))
                    self.assertTrue(header["RESPFILE"].endswith(".rmf"))

    def test_same_file_twice(self):
        source, _, _, _ = self.stage_example("swift")
        self.run_command([sys.executable, ADDSPEC, "sum", source, source])
        self.check_sum([source, source], "sum")

    def test_exposure_weighted_areascal(self):
        source, background, _, _ = self.stage_example("swift")
        shutil.copyfile(self.directory / source, self.directory / "other.pha")
        shutil.copyfile(self.directory / background, self.directory / "other_bkg.pha")
        self.set_header("other.pha", BACKFILE="other_bkg.pha", AREASCAL=3.0)
        self.set_header(source, EXPOSURE=10.0, AREASCAL=1.0)
        self.set_header(background, EXPOSURE=4.0, AREASCAL=2.0)
        self.set_header("other_bkg.pha", EXPOSURE=8.0, AREASCAL=1.0)
        # Exercise both equal and unequal source exposures and the @list CLI.
        (self.directory / "inputs.txt").write_text(source + "\nother.pha\n")
        for second_exposure in (10.0, 30.0):
            with self.subTest(second_exposure=second_exposure):
                self.set_header("other.pha", EXPOSURE=second_exposure)
                prefix = "sum%d" % second_exposure
                self.run_command([sys.executable, ADDSPEC, prefix, "@inputs.txt"])
                self.check_sum([source, "other.pha"], prefix)

    def rebin_example(self, instrument, factor, last_channel):
        source, background, arf, rmf = self.stage_example(instrument)
        # The Swift example omits HDUCLAS3. Its RMF is redistribution-only,
        # with effective area in the separate ARF; identify it for marfrmf.
        with fits.open(self.directory / rmf, mode="update") as hdus:
            hdus["MATRIX"].header.setdefault("HDUCLAS3", "REDIST")
            hdus["MATRIX"].header["LO_THRES"] = 0.0
        prefix = instrument + "_common"
        nchan = len(fits.getdata(self.directory / rmf, "EBOUNDS"))
        binfile = prefix + ".txt"
        (self.directory / binfile).write_text(
            "0 %d %d\n%d %d -1\n" % (last_channel, factor, last_channel + 1, nchan - 1))
        response = prefix + ".rmf"
        self.run_command([
            "ftrbnrmf", "infile=" + rmf, "outfile=" + response,
            "cmpmode=binfile", "binfile=" + binfile, "ecmpmode=linear", "ebfact=1"])
        for name, suffix in ((source, ".pha"), (background, "_bkg.pha")):
            output = prefix + suffix
            self.run_command([
                "ftrbnpha", "infile=" + name, "outfile=" + output,
                "binfile=" + binfile, "properr=no", "error=poiss-0"])
            original = fits.getdata(self.directory / name, "SPECTRUM")["COUNTS"]
            expected = original[:last_channel + 1].reshape(-1, factor).sum(axis=1)
            np.testing.assert_array_equal(
                fits.getdata(self.directory / output, "SPECTRUM")["COUNTS"], expected)
        self.set_header(prefix + ".pha", RESPFILE=response, ANCRFILE=arf,
                        BACKFILE=prefix + "_bkg.pha")
        # Missing background responses deliberately exercise the source fallback.
        self.set_header(prefix + "_bkg.pha", RESPFILE="NONE", ANCRFILE="NONE")
        return prefix + ".pha"

    def test_different_instruments_and_full_response_restack(self):
        swift = self.rebin_example("swift", factor=2, last_channel=999)
        mos = self.rebin_example("xmm", factor=4, last_channel=1999)
        self.assertNotEqual(self.header(swift)["INSTRUME"], self.header(mos)["INSTRUME"])
        # The real example exposures differ; also exercise non-unit AREASCAL.
        self.set_header(mos, AREASCAL=3.0)
        self.set_header(self.header(mos)["BACKFILE"], AREASCAL=2.0)
        self.run_command([sys.executable, ADDSPEC, "sum", swift, mos])
        self.check_sum([swift, mos], "sum", full_response=True)
        self.run_command([sys.executable, ADDSPEC, "resum", "sum.pha", "sum.pha"])
        self.check_sum(["sum.pha", "sum.pha"], "resum", full_response=True)


if __name__ == "__main__":
    # Fail clearly when invoked as a script/CI job without its prerequisites;
    # unittest/pytest discovery can instead report a dependency-related skip.
    try:
        require_heasoft()
    except unittest.SkipTest as error:
        sys.exit(str(error))
    unittest.main(verbosity=2)
