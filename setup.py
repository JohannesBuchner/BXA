#!/usr/bin/env python
import setuptools
from distutils.core import setup

try:
	with open('README.rst') as f:
		long_description = f.read()
except IOError:
	long_description = ''

setup(name='bxa',
	version='4.0.0',
	author='Johannes Buchner',
	url='https://github.com/JohannesBuchner/BXA/',
	author_email='johannes.buchner.acad@gmx.com',
	description='Bayesian X-ray spectral analysis',
	long_description=long_description,
	packages=['bxa.xspec', 'bxa.sherpa', 'bxa.sherpa.background', 'bxa'],
	requires=['ultranest','numpy', 'tqdm', 'corner', 'h5py', 'matplotlib'],
	include_package_data=True,
)
