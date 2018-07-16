#!/usr/bin/env python

from distutils.core import setup

try:
	with open('README.rst') as f:
		long_description = f.read()
except IOError:
	long_description = ''

setup(name='bxa',
	version='2.3',
	author='Johannes Buchner',
	url='https://github.com/JohannesBuchner/BXA/',
	author_email='johannes.buchner.acad@gmx.com',
	description='Bayesian X-ray spectral analysis',
	long_description=long_description,
	packages=['bxa.xspec', 'bxa.sherpa'],
	)

