#
# Example script to make use of BXA's built-in MPI support
# --------------------------------------------------------
#
# David Homan; 01.08.2023
#
# NOTE: although it is required to have mpi4py installed, we do not call it
# explicitly in this script. In fact, doing so would cause an error. The use
# of MPI is 'under the hood' in the BXA implementation. 
#
# ---
# This script:
#
# In the example below we define a model that would require a particularly
# long time to run: it is an alternative version of the 'mod2' used in the
# notebook 'example_usage_plotbxa', where the redshifts of the power law and
# the intrinsic absorber are left free to vary. We will use the same example
# data as in Section 1 of the noteboook. 
#
# As can be seen below, the setup for the run is identical to that presented
# in the tutorial notebook. We set up XSpec, define a model, create priors 
# and a solver, and then run the fit. The division of the run into multiple
# processes is taken care of within BXA. The only reason we take this analysis
# out of the notebook and into a separate script, is that it is far more 
# convenient to launch an MPI run from the CL for an individual script, than
# it is to set up a Jupyter session for this purpose.
#
# ---
# A few notes on multi-processing:
#
# With regard to OpenMP and MPI configuration: we recommend setting 
# OMP_NUM_THREADS=1 and limiting the number of processes to at most the number
# of physical cores. If you are unsure how many (physical) cores your system
# has, try e.g. the lscpu (Linux) command to investigate. 
#
# Explicitly binding either processes or threads (for example using the OMP_PLACES
# environment variable) to specific cores, was found to have little impact on
# performance. However, experimentation on any particular system could still be
# worthwhile if speed is a concern (also note that OpenMPI binds processes to 
# either cores or sockets by default, depending on the number of cores & processes).
# ---
#
# An example command to launch this script:
# 
# OMP_NUM_THREADS=1  mpirun -n 4 python mpi_example_bxa.py > mpi_run_output.log
#
# In the above command we set the environment variable for the run only (one can
# of course also set this for shell), we limit the number of processes to 4, and
# we store the output in the .log file.
#
# => To see the effect of the parallel processing on performance, try running
#    this script with different numbers of processes.
# => It can sometimes happen that the script falters on the first run, throwing
#    an error about creating the output directory for the BXA results. Simply 
#    relaunching the mpirun often works in this case.
# 

import xspec
import bxa.xspec as bxa
import os,sys
from bxa.xspec.solver import XSilence
import time

wd = os.path.join(os.path.dirname(__file__),'../example_data/athena/')
os.chdir(wd)

start_time = time.time()

with XSilence():
    # initial setup
    xspec.Fit.statMethod = "cstat"
    xspec.Xset.abund = 'wilm' # Wilms et al. '00'   
    xspec.Xset.xsect = 'vern' # Verner et al. '96'
    xspec.Xset.cosmo = '70 0 0.73'

    # load data
    xspec.AllData.clear()
    epicfn = 'example-file.fak'
    xspec.AllData(f"{epicfn}")

    # Spectral range
    xspec.AllData.notice('all')
    xspec.AllData.ignore('bad')
    xspec.AllData(1).ignore('**-1.0 10.0-**')

    # define model
    model_name = 'mod3'
    xspec.AllModels += ("wabs*powerlaw + gauss",model_name)
    mod = xspec.AllModels(1,model_name)

    mod.wabs.nH.values  = (1., 0.01, 1e-3, 1e-3, 50., 50.)

    mod.powerlaw.PhoIndex.values = (1.7, 0.1, 0., 0., 3., 3.)
    mod.powerlaw.norm.values = (1.e-1, 0.01, 1.e-3, 1.e-3, 5e-1, 5e-1)

    mod.gaussian.LineE.values = (6.4, -1)  #<= Fix as K-alpha
    mod.gaussian.Sigma.values = (0.1, 0.01, 0.01, 0.01, 2., 2.)
    mod.gaussian.norm.values  = (1e-4, 0.01, 1e-6, 1e-6, 1e-1, 1e-1)
    
    # define priors and solver
    mp1 = bxa.create_loguniform_prior_for(mod, mod.wabs.nH)
    mp2 = bxa.create_uniform_prior_for(mod, mod.powerlaw.PhoIndex)
    mp3 = bxa.create_loguniform_prior_for(mod, mod.powerlaw.norm)
    mp4 = bxa.create_uniform_prior_for(mod, mod.gaussian.Sigma)
    mp5 = bxa.create_loguniform_prior_for(mod, mod.gaussian.norm)

    solver = bxa.BXASolver(transformations=[mp1,mp2,mp3,mp4,mp5],
                                outputfiles_basename="mod3_wabs-bb-g_MPI")

    # run the model                      
    results = solver.run(resume=False)

print('#########################')
print(f'finished in {time.time()-start_time:7.1f} seconds')
print('#########################')
