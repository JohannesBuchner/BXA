
# run like so:
# docker run --rm -v $PWD/examples/xspec:/opt/script/ -v $PWD:/opt/BXA -ti giacomov/xspec-docker bash /opt/script/test-docker.sh

export HEADAS=/heasoft/build/x86_64-unknown-linux-gnu-libc2.23-0/
. $HEADAS/headas-init.sh

cd /opt/
apt-get -y update
apt-get -y install -qq python-numpy python-scipy python-matplotlib

# upgrade pip ...
sudo apt-get -y purge python-pip
#curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | sudo python2.7
sudo apt-get install python-setuptools python-dev 
sudo easy_install pip 
pip install pip --upgrade 

pip install requests tqdm astropy==2.0 corner cython h5py
pip install ultranest
#git clone https://github.com/JohannesBuchner/BXA
pushd BXA; python setup.py install --user; popd

# avoid error without X server
echo "backend: Agg" > matplotlibrc
echo "backend: Agg" > /opt/script/matplotlibrc
python -c 'import ultranest';
python -c 'import xspec';
python -c 'import bxa.xspec as bxa';

pushd /opt/script/ && sed --in-place s/python3/python/g runall.sh && bash -v runall.sh && popd;
