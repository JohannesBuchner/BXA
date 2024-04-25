#
# BXA fitting script to be used in a parallel processing run
# ----------------------------------------------------------
#
# David Homan; 01.08.2023
#
# NOTE: This script is designed to be used in combination with the example
# given in section 2.1) of the Jupyter notebook 'example_usage_plotbxa'. The
# script takes command-line input in the form of a filename of an X-ray
# spectrum.
#
# ---
# This script:
#
# In this example we will use the same setup as used in the notebook: we set
# the same XSpec settings, we define the same models (*with the same names*),
# and we match the filenames for the simulated spectra to those created in the
# tutorial notebook.
#
#   => It is clear that the copy-pasting from the notebook introduces some risk
#      of errors. However, this may be greatly offset by the improved run time.
#
# Another possible source of error here is the file labelling. We are creating
# multiple files, which are all quite similar. BXA creates named output which 
# we want to be able to reload if necessary. To be able to retrace our steps,
# we sort the input data such that the simulated spectra are passed in numerical
# order and label each output model by the model name ('mod2' or 'mod3')
# followed by the iteration number that matches the number of the simulated 
# spectrum. e.g., 'mod2_11' is the label for the output of the BXA fitting of
# simulated spectrum '11' with model 'mod2'; a directory of this name will 
# be created under example_data/xmm/test_type1 and contain the BXA output files
# for this fitting process.
#
# ---
# Example command to launch this script:
#
# The example command, for a Linux system, to run this notebook (*after the
# setup in the notebook has been completed*) is as follows:
#
# ls example_data/xmm/fakeit_spectra/tt1_tb-ztb-zpl_{0..23}*_0.pha | sort -t_ -k5,5n | xargs --max-args=1 --max-procs=4 python parallel_bxa_tt1.py > tt1_run.log
#
# (note: the script is set up to run in the 'mp_examples' directory).
#
# ---
# A note regarding the use of multiple cores:
#
# We aim to match the number of processes to the configuration of the system.
# This means controlling (1) the total number of processes and (2) the number
# of threads used per process.
# 
# With regard to point (2): many HEASOFT installations are set up to use 
# multithreading (using OpenMP) and may use all available cores (including 
# virtual ones, for Intel CPUs). In combination with BXA, the use of hyper-
# threading (i.e. the use of the virtual cores) has been found to reduce
# performance. The number of extra threads available to XSpec per BXA process
# also appears to have little effect on BXA fitting execution time: the 
# overhead is the time-limiting factor. For this reason, we recommend running
# this script with the environment variable OMP_NUM_THREADS=1 (i.e. one thread
# per process). Please see the script mpi_bxa_example.py for further suggestions
# on the setup for a multi-core run.
#
# With regard to point (1): with the number of threads per process limited to
# one, this can be set as high as possible, depending on competing demands for
# CPU time on the system. In the case of Intel CPUs, we recommend that the total
# number of threads (number of processes times number of threads per process) not
# exceed the total number of _physical_ cores, to avoid the use of hyperthreading.
# If not running on a cluser: for N physical cores, it can be recommended to 
# leave at least one core free for other processes, therefore setting the 
# --max-procs argument of xargs to N-1.
# ===

import xspec
import bxa.xspec as bxa
import os,sys
from bxa.xspec.solver import XSilence
import time


##
# RUN SETTINGS
##
fname   = sys.argv[1].split('/')[-1] # strip leading directory from file path (if necessary)
specdir = 'fakeit_spectra'
datadir = 'test_type1'
it = fname.split('_')[2]
wd = os.path.join(os.path.dirname(__file__),'../example_data/athena/')
os.chdir(wd)

#
# ACTIVATION FUNCTIONS
#
def activate_mod1():
    model_name = 'mod1'
    xspec.AllModels += ("wabs*powerlaw",model_name)
    mod = xspec.AllModels(1,model_name)

    mod.wabs.nH.values  = (1., 0.01, 1e-3, 1e-3, 50., 50.)

    mod.powerlaw.PhoIndex.values = (1.7, 0.1, 0., 0., 3., 3.)
    mod.powerlaw.norm.values = (1.e-1, 0.01, 1.e-3, 1.e-3, 5e-1, 5e-1)
    
    return mod,model_name

def activate_mod3():
    # same as mod1, but with added FeK
    model_name = 'mod3'
    xspec.AllModels += ("wabs*powerlaw + gauss",model_name)
    mod = xspec.AllModels(1,model_name)

    mod.wabs.nH.values  = (1., 0.01, 1e-3, 1e-3, 50., 50.)

    mod.powerlaw.PhoIndex.values = (1.7, 0.1, 0., 0., 3., 3.)
    mod.powerlaw.norm.values = (1.e-1, 0.01, 1.e-3, 1.e-3, 5e-1, 5e-1)
    
    mod.gaussian.LineE.values = (6.4, -1)  #<= Fix as K-alpha
    mod.gaussian.Sigma.values = (0.1, 0.01, 0.01, 0.01, 2., 2.)
    mod.gaussian.norm.values  = (1e-4, 0.01, 1e-6, 1e-6, 1e-1, 1e-1)
    
    return mod, model_name


#
# XSPEC SETUP
#
xspec.Fit.statMethod = "cstat"
xspec.Xset.abund = 'wilm' # Wilms et al. '00'
xspec.Xset.xsect = 'vern' # Verner et al. '96'
xspec.Xset.cosmo = '70 0 0.73'


#
# RUN FIT
#
with XSilence():
    # Load data
    xspec.AllData.clear()
    xspec.AllData(f'{os.path.join(specdir,fname)}')
        
    # Spectral range
    xspec.AllData.notice('all')
    xspec.AllData.ignore('bad')
    xspec.AllData(1).ignore('**-1.0 10.0-**')

    # FIT FIRST MODEL
    mod1, mname = activate_mod1()
    # create prior transformations & solver
    m1p1 = bxa.create_loguniform_prior_for(mod1, mod1.wabs.nH)
    m1p2 = bxa.create_uniform_prior_for(mod1, mod1.powerlaw.PhoIndex)
    m1p3 = bxa.create_loguniform_prior_for(mod1, mod1.powerlaw.norm)

    solver1 = bxa.BXASolver(transformations=[m1p1,m1p2,m1p3],
                            outputfiles_basename=os.path.join(datadir,mname+f'_{it}'))

    solver1.run(resume=True,run_kwargs={'show_status': False})
    print(f'FINISHED FIT FOR {fname}, using model {mname}')

    # FIT SECOND MODEL (third model from the tutorial notebook)
    mod3, mname = activate_mod3()
    # create prior transformations & solver
    m3p1 = bxa.create_loguniform_prior_for(mod3, mod3.wabs.nH)
    m3p2 = bxa.create_uniform_prior_for(mod3, mod3.powerlaw.PhoIndex)
    m3p3 = bxa.create_loguniform_prior_for(mod3, mod3.powerlaw.norm)
    m3p4 = bxa.create_uniform_prior_for(mod3, mod3.gaussian.Sigma)
    m3p5 = bxa.create_loguniform_prior_for(mod3, mod3.gaussian.norm)

    solver3 = bxa.BXASolver(transformations=[m3p1, m3p2, m3p3, m3p4, m3p5],
                            outputfiles_basename=os.path.join(datadir,mname+f'_{it}'))
                            
    solver3.run(resume=True,run_kwargs={'show_status': False})
    print(f'FINISHED FIT FOR {fname}, using model {mname}')


