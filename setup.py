#!/usr/bin/env python

from distutils.core import setup

long_description = ''
with open('README.rst') as f:
	long_description = f.read()

setup(name='bxa',
	version='1.0',
	author='Johannes Buchner',
	url='https://github.com/JohannesBuchner/BXA/',
	author_email='johannes.buchner.acad@gmx.com',
	description='Bayesian X-ray spectral analysis',
	long_description=open('README.rst').read(),
	packages=['bxa.xspec', 'bxa.sherpa'],
	)

