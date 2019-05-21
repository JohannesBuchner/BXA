
# run like so:
# docker run --rm -v $PWD/examples/xspec:/opt/script/ -v $PWD:/opt/BXA -ti giacomov/xspec-docker bash /opt/script/test-docker.sh

export HEADAS=/heasoft/build/x86_64-unknown-linux-gnu-libc2.23-0/
. $HEADAS/headas-init.sh

cd /opt/
apt-get -y update
apt-get -y install -qq libblas{3,-dev} liblapack{3,-dev} libatlas{3-base,-dev} cmake build-essential gfortran python-numpy python-scipy python-matplotlib

git clone https://github.com/JohannesBuchner/MultiNest
mkdir -p MultiNest/build; pushd MultiNest/build; cmake .. && make && popd
#pip uninstall requests
#python -m pip install --upgrade pip requests urllib3
# upgrade pip ...
sudo apt-get -y purge python-pip
#curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | sudo python2.7
sudo apt-get install python-setuptools python-dev 
sudo easy_install pip 
pip install pip --upgrade 

pip install pymultinest tqdm astropy==2.0 corner
#git clone https://github.com/JohannesBuchner/BXA
pushd BXA; python setup.py install --user; popd

ls /opt/MultiNest/lib/libmultinest.so
export LD_LIBRARY_PATH=/opt/MultiNest/lib/:$LD_LIBRARY_PATH
export PYTHONPATH=/usr/local/lib/python2.7/dist-packages/:$PYTHONPATH
# avoid error without X server
echo "backend: Agg" > matplotlibrc
echo "backend: Agg" > /opt/script/matplotlibrc
python -c 'import pymultinest';
python -c 'import xspec';
python -c 'import bxa.xspec as bxa';
pushd /opt/script/ && bash -v runall.sh && popd;


