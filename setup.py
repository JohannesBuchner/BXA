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
    version='4.1.4',
    author='Johannes Buchner',
    url='https://github.com/JohannesBuchner/BXA/',
    author_email='johannes.buchner.acad@gmx.com',
    description='Bayesian X-ray spectral analysis',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    license="GNU General Public License v3",
    long_description=long_description,
    packages=['bxa.xspec', 'bxa.sherpa', 'bxa.sherpa.background', 'bxa'],
    install_requires=['ultranest','numpy', 'tqdm', 'corner', 'h5py', 'matplotlib', 'astropy'],
    scripts=['gal.py', 'fixkeywords.py', 'addspec.py'],
    include_package_data=True,
)

if not sherpa_available and not xspec_available:
    warnings.warn("BXA is a plugin for xspec/sherpa, but neither xspec nor sherpa are installed in the current environment!")
