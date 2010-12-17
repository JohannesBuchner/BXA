#!/usr/bin/env python

from distutils.core import setup

setup(name='pyblocxs',
      version='0.0.4',
      author='CHASC Astro-Statistics Collaboration',
      url='http://hea-www.harvard.edu/AstroStat/',
      description='Bayesian low-Counts X-ray spectral analysis',
      packages=['pyblocxs'
                ],
      package_data={'pyblocxs': ['test/*']},
      
      )
