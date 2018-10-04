
# run like so:
# docker run --rm -v $PWD/examples/xspec:/opt/script/ -v $PWD:/opt/BXA -ti giacomov/xspec-docker bash /opt/script/test-docker.sh

export HEADAS=/heasoft/build/x86_64-unknown-linux-gnu-libc2.23-0/
. $HEADAS/headas-init.sh

cd /opt/
apt-get update
apt-get install -qq libblas{3,-dev} liblapack{3,-dev} libatlas{3-base,-dev} cmake build-essential gfortran python-numpy python-scipy python-matplotlib

git clone https://github.com/JohannesBuchner/MultiNest
mkdir -p MultiNest/build; pushd MultiNest/build; cmake .. && make && popd
#pip install --upgrade pip
pip install pymultinest progressbar-latest astropy==2.0
#git clone https://github.com/JohannesBuchner/BXA
pushd BXA; python setup.py install --user; popd

ls /opt/MultiNest/lib/libmultinest.so
export LD_LIBRARY_PATH=/opt/MultiNest/lib/:$LD_LIBRARY_PATH
export PYTHONPATH=/usr/local/lib/python2.7/dist-packages/:$PYTHONPATH
# avoid error without X server
echo "backend: Agg" > matplotlibrc
python -c 'import pymultinest';
python -c 'import xspec';
python -c 'import bxa.xspec as bxa';
pushd /opt/script/ && bash -v runall.sh && popd;


