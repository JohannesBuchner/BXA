# for docker environment
. /opt/ciao-4.8/bin/ciao.bash 
export PYTHONPATH=/opt/example/:/opt/pymultinest/:$PYTHONPATH
export LD_LIBRARY_PATH=/opt/MultiNest/lib/:$LD_LIBRARY_PATH
sherpa fit.py

