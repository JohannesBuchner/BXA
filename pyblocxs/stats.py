#!/usr/bin/env python

from sherpa.models import ArithmeticModel, Parameter
import numpy

__all__ = ['Normal']

###############################################################################
#
# Statistics
#
###############################################################################

class Normal(ArithmeticModel):

    def __init__(self, name='normal'):

        self.sigma = Parameter(name, 'sigma', 1., alwaysfrozen=True)
        self.x0 = Parameter(name, 'x0', 1., alwaysfrozen=True)
        self.norm = Parameter(name, 'norm', 1., alwaysfrozen=True)

        ArithmeticModel.__init__(self, name, (self.sigma, self.x0, self.norm))

    def calc(self, x):
        return self.pdf(x)

    def pdf(self, x):
        norm = self.norm.val
        sigma = self.sigma.val
        x0 = self.x0.val
        return norm/numpy.sqrt(2*numpy.pi*sigma*sigma)*numpy.exp(-0.5*(x-x0)*(x-x0)/sigma/sigma)
