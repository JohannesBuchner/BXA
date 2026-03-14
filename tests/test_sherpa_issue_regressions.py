from types import SimpleNamespace

import numpy as np
import pytest

pytest.importorskip("sherpa.models.parameter")

from sherpa.models.parameter import Parameter

from bxa.sherpa.background.fitters import SingleFitter
from bxa.sherpa.priors import create_prior_function


class DummyBackgroundModel:
	def __init__(self, pars):
		self.pars = pars
		self.stagepars = list(pars)
		self.calls = []

	def set_model(self, stage=None):
		self.calls.append(stage)


def make_parameter(modelname, name, value, low, high):
	return Parameter(modelname, name, value, min=low, max=high)


def make_fitter(pars):
	fitter = SingleFitter.__new__(SingleFitter)
	fitter.id = 2
	fitter.bm = DummyBackgroundModel(pars)
	return fitter


def test_create_prior_function_uses_each_parameter_bounds():
	parameters = [
		SimpleNamespace(min=-2.0, max=2.0),
		SimpleNamespace(min=10.0, max=20.0),
	]
	cube = np.array([0.25, 0.75], dtype=float)

	prior_function = create_prior_function(parameters=parameters)
	prior_function(cube, ndim=2, nparams=2)

	np.testing.assert_allclose(cube, [-1.0, 17.5])


def test_prepare_stage_links_joint_fit_parameters():
	prev = [
		make_parameter("joint", "norm_1", 1.5, 0.0, 10.0),
		make_parameter("joint", "tilt_1", -1.0, -5.0, 5.0),
	]
	current = [
		make_parameter("joint", "norm_2", 0.5, 0.0, 10.0),
		make_parameter("joint", "tilt_2", 0.0, -5.0, 5.0),
	]
	fitter = make_fitter(current)

	fitter.prepare_stage(stage="joint", prev=prev, link=True)

	assert fitter.bm.calls == ["joint"]
	assert current[0].link is prev[0]
	assert current[1].link is prev[1]
	prev[0].val = 3.25
	prev[1].val = 1.75
	assert current[0].val == pytest.approx(3.25)
	assert current[1].val == pytest.approx(1.75)


def test_prepare_stage_unlinks_and_keeps_joint_fit_values():
	prev = [
		make_parameter("joint", "norm_1", 2.5, 0.0, 10.0),
		make_parameter("joint", "tilt_1", 1.0, -5.0, 5.0),
	]
	current = [
		make_parameter("joint", "norm_2", 0.5, 0.0, 10.0),
		make_parameter("joint", "tilt_2", 0.0, -5.0, 5.0),
	]
	fitter = make_fitter(current)

	fitter.prepare_stage(stage="joint", prev=prev, link=True)
	prev[0].val = 4.5
	prev[1].val = -2.0
	fitter.prepare_stage(stage="individual", prev=prev, link=False)

	assert fitter.bm.calls == ["joint", "individual"]
	assert current[0].link is None
	assert current[1].link is None
	assert current[0].val == pytest.approx(4.5)
	assert current[1].val == pytest.approx(-2.0)
	assert not current[0].frozen
	assert not current[1].frozen
