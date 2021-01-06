pip install cython
pip install ultranest
pushd /opt/BXA && python setup.py install 
mkdir -p models
wget -nc https://zenodo.org/record/1169181/files/uxclumpy-cutoff.fits https://zenodo.org/record/1169181/files/uxclumpy-cutoff-omni.fits
popd
export MODELDIR=/opt/BXA/models
pushd /opt/examples/
sherpa /opt/BXA/examples/sherpa/xagnfitter.py
