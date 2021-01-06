pushd /opt/BXA

mkdir -p models
pushd models
wget -q -nc https://zenodo.org/record/1169181/files/uxclumpy-cutoff.fits https://zenodo.org/record/1169181/files/uxclumpy-cutoff-omni.fits &
popd

apt-get -y update
apt-get -y install -qq python-numpy python-scipy python-matplotlib

pip install cython h5py tqdm corner
pip install ultranest

python setup.py install 

wait

export MODELDIR=/opt/BXA/models
pushd /opt/examples/
sherpa /opt/BXA/examples/sherpa/xagnfitter.py
