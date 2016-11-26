# for running inside the docker container

. /opt/ciao-4.8/bin/ciao.bash 
export PYTHONPATH=/opt/example/:/opt/pymultinest/:$PYTHONPATH:/usr/lib/python2.7/dist-packages/:/opt/example/npyinterp/
export LD_LIBRARY_PATH=/opt/MultiNest/lib/:/opt/example/npyinterp/:$LD_LIBRARY_PATH
sherpa fit.py

