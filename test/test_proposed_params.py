import sherpa.all
import sherpa.astro.all
from pyblocxs.mh import MH, LimitError
import numpy
import unittest

_tol = numpy.finfo(numpy.float32).eps

class TestParameterProposal(unittest.TestCase):

    _min     = [0.001, 0.1, 0.0]
    _max     = [10., 10., 10.]
    _initial = [1., 1., 1.]
    _bad     = [1.e+40, 1.e+40, 1.e+40]
    _good    = [5., 5., 5.]
    _above   = [20., 20., 20.]
    _below   = [0.0001, 0.01, -1.0 ]

    def setUp(self):
        xlo, xhi, y = sherpa.utils.dataspace1d(0.1, 10.1, 0.1)
        data = sherpa.data.Data1D('dataspace1d', xlo, y)
        g1 = sherpa.models.Gauss1D('g1')
        g1.thawedpars     = self._initial
        g1.thawedparmins  = self._min
        g1.thawedparmaxes = self._max    
        fit = sherpa.fit.Fit(data, g1, stat=sherpa.stats.Cash())
        thawedparmins = numpy.array(fit.model.thawedparhardmins)
        thawedparmaxes = numpy.array(fit.model.thawedparhardmaxes)
        def calc_stat(proposal):
            prop = numpy.atleast_1d(proposal)
            mins  = sherpa.utils.sao_fcmp(prop, thawedparmins, _tol)
            maxes = sherpa.utils.sao_fcmp(thawedparmaxes, prop, _tol)
            if -1 in mins or -1 in maxes:
                raise LimitError('Sherpa parameter hard limit exception')
            fit.model.thawedpars = proposal
            return -0.5*fit.calc_stat()

        sigma = g1.thawedpars
        dof = len(xlo) - len(sigma)
        mu = numpy.random.rand(3)
        self.mh = MH(calc_stat, sigma, mu, dof)
        current, stat = self.mh.init()


    def test_bad_proposal(self):
        self.assertRaises(LimitError, self.mh.calc_stat, self._bad)

    def test_good_proposal(self):
        stat = self.mh.calc_stat(self._good)

    def test_good_proposal_above_softlimits(self):
        stat = self.mh.calc_stat(self._above)

    def test_good_proposal_below_softlimits(self):
        stat = self.mh.calc_stat(self._below)


if __name__ == '__main__':
    unittest.main()
