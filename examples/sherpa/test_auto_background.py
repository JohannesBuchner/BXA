import json
import numpy as np
import sherpa.astro.ui as shp

from bxa.sherpa.background.pca import auto_background


def test_chandra_pcabkg():
    _reset_sherpa()
    _load_chandra_data(emin=0.5, emax=8)

    filename = "chandra/179_pcabkg.json"
    bkgmodel = auto_background(1, max_lines=0)
    # _save_pca_params(bkgmodel, filename)
    _test_pca_params(filename, bkgmodel)

def test_chandra_detect_line():
    _reset_sherpa()
    bkgdata = _load_chandra_data(emin=0.5, emax=8)
    channel = _inject_count_excess(bkgdata)
    bkgmodel = auto_background(1, max_lines=1)

    _check_injected_line(bkgdata, bkgmodel, channel)

def _load_chandra_data(emin, emax):
    shp.load_pha("chandra/179.pi")
    _ungroup_and_ignore_bkg(emin, emax)

    return shp.get_bkg()


def test_swift_pcabkg():
    _reset_sherpa()
    _load_swift_data(emin=0.5, emax=5.0)

    filename = "swift/interval0pc_pcabkg.json"
    bkgmodel = auto_background(1, max_lines=0)
    # _save_pca_params(bkgmodel, filename)
    _test_pca_params(filename, bkgmodel)

def test_swift_detect_line():
    _reset_sherpa()
    bkgdata = _load_swift_data(emin=0.5, emax=5.0)
    channel = _inject_count_excess(bkgdata)
    bkgmodel = auto_background(1, max_lines=1)

    _check_injected_line(bkgdata, bkgmodel, channel)

def _load_swift_data(emin, emax):
    shp.load_pha("swift/interval0pc.pi")
    _ungroup_and_ignore_bkg(emin, emax)

    return shp.get_bkg()


def test_xmmpn_pcabkg():
    _reset_sherpa()
    _load_xmmpn_data(emin=0.2, emax=10.0)

    filename = "xmm/pn_pcabkg.json"
    bkgmodel = auto_background(1, max_lines=0)
    # _save_pca_params(bkgmodel, filename)
    _test_pca_params(filename, bkgmodel)

def test_xmmpn_detect_line():
    _reset_sherpa()
    bkgdata = _load_xmmpn_data(emin=0.2, emax=10.0)
    channel = _inject_count_excess(bkgdata)
    bkgmodel = auto_background(1, max_lines=1)

    _check_injected_line(bkgdata, bkgmodel, channel)

def _load_xmmpn_data(emin, emax):
    shp.load_pha("xmm/pn_spec.fits")
    shp.load_bkg("xmm/pn_backspec.fits")
    shp.load_rmf("xmm/pn.rmf")
    shp.load_arf("xmm/pn.arf")
    shp.load_bkg_rmf("xmm/pn.rmf")
    shp.load_bkg_arf("xmm/pn.arf")
    _ungroup_and_ignore_bkg(emin, emax)

    return shp.get_bkg()


def test_xmmmos_pcabkg():
    _reset_sherpa()
    _load_xmmmos_data(emin=0.2, emax=10.0)

    filename = "xmm/mos_pcabkg.json"
    bkgmodel = auto_background(1, max_lines=0)
    # _save_pca_params(bkgmodel, filename)
    _test_pca_params(filename, bkgmodel)

def test_xmmmos_detect_line():
    _reset_sherpa()
    bkgdata = _load_xmmmos_data(emin=0.2, emax=10.0)
    channel = _inject_count_excess(bkgdata)
    bkgmodel = auto_background(1, max_lines=1)

    _check_injected_line(bkgdata, bkgmodel, channel)

def _load_xmmmos_data(emin, emax):
    shp.load_pha("xmm/mos_spec.fits")
    shp.load_bkg("xmm/mos_backspec.fits")
    shp.load_rmf("xmm/mos.rmf")
    shp.load_arf("xmm/mos.arf")
    shp.load_bkg_rmf("xmm/mos.rmf")
    shp.load_bkg_arf("xmm/mos.arf")
    _ungroup_and_ignore_bkg(emin, emax)

    return shp.get_bkg()


def test_nustar_pcabkg():
    _reset_sherpa()
    _load_nustar_data(emin=5.0, emax=77.0)

    filename = "nustar/nu60360003002A01_pcabkg.json"
    bkgmodel = auto_background(1, max_lines=0)
    # _save_pca_params(bkgmodel, filename)
    _test_pca_params(filename, bkgmodel)

def test_nustar_detect_line():
    _reset_sherpa()
    bkgdata = _load_nustar_data(emin=5.0, emax=77.0)
    channel = _inject_count_excess(bkgdata)
    bkgmodel = auto_background(1, max_lines=1)

    _check_injected_line(bkgdata, bkgmodel, channel)

def _load_nustar_data(emin, emax):
    shp.load_pha("nustar/nu60360003002A01_sr_grp.pha")
    _ungroup_and_ignore_bkg(emin, emax)

    return shp.get_bkg()


def test_erosita_pcabkg():
    _reset_sherpa()
    _load_erosita_data(emin=0.2, emax=8.0)

    filename = "erosita/em01_182117_020_pcabkg.json"
    bkgmodel = auto_background(1, max_lines=0)
    _test_pca_params(filename, bkgmodel)
    # _save_pca_params(bkgmodel, filename)

def test_erosita_detect_line():
    _reset_sherpa()
    bkgdata = _load_erosita_data(emin=0.2, emax=8.0)
    channel = _inject_count_excess(bkgdata)
    bkgmodel = auto_background(1, max_lines=1)

    _check_injected_line(bkgdata, bkgmodel, channel)

def _load_erosita_data(emin, emax):
    shp.load_pha("erosita/em01_182117_020_SourceSpec_00005_c010.fits")
    _ungroup_and_ignore_bkg(emin, emax)

    return shp.get_bkg()


def test_suzaku_pcabkg():
    _reset_sherpa()
    _load_suzaku_data(emin=0.2, emax=8.0)

    filename = "suzaku/ae900001010xi0_0_3x3n000a_pcabkg.json"
    bkgmodel = auto_background(1, max_lines=0)
    _test_pca_params(filename, bkgmodel)
    # _save_pca_params(bkgmodel, filename)

def test_suzaku_detect_line():
    _reset_sherpa()
    bkgdata = _load_suzaku_data(emin=0.2, emax=8.0)
    channel = _inject_count_excess(bkgdata)
    bkgmodel = auto_background(1, max_lines=1)

    _check_injected_line(bkgdata, bkgmodel, channel)

def _load_suzaku_data(emin, emax):
    shp.load_pha("suzaku/ae900001010xi0_0_3x3n000a_sr.pi")
    _ungroup_and_ignore_bkg(emin, emax)

    return shp.get_bkg()


def _reset_sherpa():
    shp.clean()
    shp.set_stat("cstat")

def _ungroup_and_ignore_bkg(emin, emax):
    shp.ungroup(bkg_id=1)
    shp.notice(bkg_id=1)
    shp.ignore(lo=None, hi=emin, bkg_id=1)
    shp.ignore(lo=emax, hi=None, bkg_id=1)
    
    # Set dummy source model for auto_background
    shp.set_model("powlaw1d.dummy")


def _save_pca_params(bkgmodel, filename):
    pca_params = {p.name: p.val for p in bkgmodel.pars}

    with open(filename, "w") as fp:
        json.dump(pca_params, fp, indent=2)

def _load_pca_params(filename):
    with open(filename, "r") as fp:
        return json.load(fp)


def _test_pca_params(filename, bkgmodel):
    test_pca_params = _load_pca_params(filename)
    bkgdata = shp.get_bkg()

    assert len(bkgdata.channel) == bkgmodel.rmf.detchans
    assert len(bkgmodel.pars) == len(test_pca_params)
    
    for p in bkgmodel.pars:
        assert p.name in test_pca_params
        assert np.isclose(p.val, test_pca_params[p.name], rtol=0.05, atol=0.02), (p.name, p.val, test_pca_params[p.name])


def _inject_count_excess(bkgdata):
    # Insert a high excess of counts in the middle
    # of the noticed energy range
    cmin = bkgdata.channel[bkgdata.mask][0]
    cmax = bkgdata.channel[bkgdata.mask][-1]
    c = int((cmin + cmax) / 2)
    c0 = int(bkgdata.channel[0])
    bkgdata.counts[c - c0] = 100 * bkgdata.counts.max()
    print(f"Injecting {bkgdata.counts[c - c0]:.0f} counts at {bkgdata.x[c - c0]:.2f} keV [channel {c}]")

    return c

def _check_injected_line(bkgdata, bkgmodel, channel_injected):
    for p in bkgmodel.pars:
        if p.name == "LineE":
            first_line_energy = p.val
            break

    first_line_channel = bkgdata.channel[0] + np.argmin(np.absolute(bkgdata.x - first_line_energy))
    assert int(first_line_channel) == channel_injected



def run_tests():
    instruments = [
        "chandra",
        "swift",
        "xmmpn",
        "xmmmos",
        # "nustar",
        # "erosita",
        # "suzaku",
        # "rxtepca",
        # "rxtehexa",
        # "rxtehexb",
    ]

    for instrument in instruments:
        test_continuum = globals()[f"test_{instrument}_pcabkg"]
        test_continuum()

        test_lines = globals()[f"test_{instrument}_detect_line"]
        test_lines()


if __name__ == "__main__":
    run_tests()
