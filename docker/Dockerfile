# Fitting X-ray point sources like obscured AGN

FROM ldouchy/bxa_ciao:latest

MAINTAINER johannesbuchner

LABEL description="BXA for AGN https://johannesbuchner.github.io/BXA"

ENV	LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/MultiNest/lib:/opt/npyinterp/ \
	MULTINEST=$MULTINEST:/opt/MultiNest \
	PYTHONPATH=$PYTHONPATH:/opt/custom/complex_pymultinest/LF_modules/configuration:/opt/custom/complex_pymultinest/LF_modules/models:/opt/BXA:/opt/npyinterp/ 

RUN sed --in-place 's,archive\.,old-releases\.,g' /etc/apt/sources.list
RUN apt-get update; apt-get -y install python-setuptools python-progressbar python-astropy python-pip
RUN cd /opt/BXA && git pull && python setup.py install
COPY sphere0708.fits torus1006.fits uxclumpy-cutoff.fits uxclumpy-cutoff-omni.fits /opt/models/

RUN cd /opt/ && git clone https://github.com/JohannesBuchner/npyinterp && cd /opt/npyinterp && make

COPY testsrc/fitagn.py /opt/scripts/

WORKDIR /opt/example

CMD . /opt/ciao-4.8/bin/ciao.sh; sherpa /opt/scripts/fitagn.py


