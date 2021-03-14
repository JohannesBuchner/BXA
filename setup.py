#!/usr/bin/env python
import setuptools
from distutils.core import setup
import warnings

try:
	with open('README.rst') as f:
		long_description = f.read()
except IOError:
	long_description = ''

xspec_available = True
try:
	import xspec
except ImportError:
	xspec_available = False

sherpa_available = True
try:
	import sherpa
except ImportError:
	sherpa_available = False

if not sherpa_available and not xspec_available:
	warnings.warn("BXA is a plugin for xspec/sherpa, but neither xspec nor sherpa are installed in the current environment!")

setup(name='bxa',
	version='4.0.3',
	author='Johannes Buchner',
	url='https://github.com/JohannesBuchner/BXA/',
	author_email='johannes.buchner.acad@gmx.com',
	description='Bayesian X-ray spectral analysis',
	long_description=long_description,
	packages=['bxa.xspec', 'bxa.sherpa', 'bxa.sherpa.background', 'bxa'],
	install_requires=['ultranest','numpy', 'tqdm', 'corner', 'h5py', 'matplotlib', 'astropy'],
	scripts=['gal.py', 'fixkeywords.py'],
	include_package_data=True,
)
