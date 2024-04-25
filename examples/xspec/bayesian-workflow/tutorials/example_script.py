#
#
# Example script to making use of basic functionalities of PlotXspec and PlotBXA
# ------------------------------------------------------------------------------
#
# David Homan; 23.04.2024
#
# NOTE: This script simply creates a list of output plots using the methods of
#       PlotXspec and PlotBXA. For details and further explanations, please
#       refer to the tutorial scripts
#

# Loading the required modules
import os,sys
import xspec
import bxa.xspec as bxa
from bxa.xspec.solver import XSilence
import ultranest.plot as upl

maindir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(maindir,'..'))
from plot_xspec import PlotXspec
from plot_bxa import PlotBXA

# set paths
savedir = os.path.join(maindir,'example_output')
if not os.path.exists(savedir):
    os.mkdir(savedir)

# initial setup for XSpec
xspec.Fit.statMethod = "cstat"
xspec.Xset.abund = 'wilm' # Wilms et al. '00'
xspec.Xset.xsect = 'vern' # Verner et al. '96'
xspec.Xset.cosmo = '70 0 0.73'

# load data
with XSilence():
    # Load the data
    xspec.AllData.clear()
    xspec.AllModels.clear()
    
    # Move to the working directory
    if 'athena' not in os.getcwd():
        os.chdir(os.path.join(maindir,'example_data/athena/'))

    epicfn = 'example-file.fak'
    xspec.AllData(f"{epicfn}")

    # Spectral range
    xspec.AllData.notice('all')
    xspec.AllData.ignore('bad')
    xspec.AllData(1).ignore('**-1.0 10.0-**')

###
# PlotXpec
###
px = PlotXspec()

# 1) first look
px.first_look(ymin=-0.05,ymax=2.5,ylog=False,
              rebinsig=5,rebinbnum=40,
              savename=os.path.join(savedir,'px_first_look.png'))

## run fit in XSpec
xspec.AllModels.clear()
mod = xspec.Model("wabs*pow+gauss") 
mod.wabs.nH = 1e-2
mod.powerlaw.PhoIndex = 1.7
mod.powerlaw.norm = 1e-4
mod.gaussian.LineE = 6.4
mod.gaussian.Sigma = 0.1
mod.gaussian.norm = 2
xspec.Fit.statMethod = 'chi'
xspec.Fit.nIterations = 1000
xspec.Fit.query = 'yes'
xspec.Fit.perform()

# 2) model and data
px.plot_model_and_data(ymin=9e-7,rebinsig=5,rebinbnum=40,
                       savename=os.path.join(savedir,'px_model_and_data.png'))

# 3) steppar results
with XSilence():
    xspec.Fit.steppar('1 7.5 15.5 25 2 1.15 2.9 25')
    px.plot_chisq_contours(savename=os.path.join(savedir,'px_steppar_2d.png'))
    
    par = mod.powerlaw.PhoIndex
    xspec.Fit.steppar('2 1.2 2.9 500')
    px.calc_error_from_1Dchisq(par,level=1,
                               savename=os.path.join(savedir,'px_steppar_1d.png'))

# methods that print to screen
px.print_model_results()
px.print_errors(1.0)

###
# PlotBXA
###
pbx = PlotBXA()

xspec.Fit.statMethod = 'cstat'

# define models, set priors, and create solvers
###############################################
def activate_mod1():
    # This is the model we used in Section 1)
    model_name = 'mod1'
    xspec.AllModels += ("wabs*powerlaw",model_name)
    mod = xspec.AllModels(1,model_name)

    mod.wabs.nH.values  = (1., 0.01, 1e-3, 1e-3, 50., 50.)

    mod.powerlaw.PhoIndex.values = (1.7, 0.1, 0., 0., 3., 3.)
    mod.powerlaw.norm.values = (1.e-1, 0.01, 1.e-3, 1.e-3, 5e-1, 5e-1)
    
    return mod,model_name

def activate_mod2():
    # black-body instead of power-law
    model_name = 'mod2'
    xspec.AllModels += ("wabs*bbody",model_name)
    mod = xspec.AllModels(1,model_name)

    mod.wabs.nH.values  = (1., 0.01, 1e-3, 1e-3, 50., 50.)
    
    mod.bbody.kT.values = (20, 0.01, 1e-1,  1e-1, 200., 200.)
    mod.bbody.norm.values = (1e-3, 0.01, 1e-6,  1e-6, 1e-1, 1e-1)
    
    return mod, model_name

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

with XSilence():
    mod1,_ = activate_mod1()
    mod2,_ = activate_mod2()
    mod3,_ = activate_mod3()

# Model 1
print('Model 1')
m1p1 = bxa.create_loguniform_prior_for(mod1, mod1.wabs.nH)
m1p2 = bxa.create_uniform_prior_for(mod1, mod1.powerlaw.PhoIndex)
m1p3 = bxa.create_loguniform_prior_for(mod1, mod1.powerlaw.norm)

solver1 = bxa.BXASolver(transformations=[m1p1,m1p2,m1p3],
                        outputfiles_basename="mod1_wabs-pl")

# Model 2
print('\nModel 2')
m2p1 = bxa.create_loguniform_prior_for(mod2, mod2.wabs.nH)
m2p2 = bxa.create_loguniform_prior_for(mod2, mod2.bbody.kT)
m2p3 = bxa.create_loguniform_prior_for(mod2, mod2.bbody.norm)

solver2 = bxa.BXASolver(transformations=[m2p1,m2p2,m2p3],
                        outputfiles_basename="mod2_wabs-bb")

# Model 3
print('\nModel 3')
m3p1 = bxa.create_loguniform_prior_for(mod3, mod3.wabs.nH)
m3p2 = bxa.create_uniform_prior_for(mod3, mod3.powerlaw.PhoIndex)
m3p3 = bxa.create_loguniform_prior_for(mod3, mod3.powerlaw.norm)
m3p4 = bxa.create_uniform_prior_for(mod3, mod3.gaussian.Sigma)
m3p5 = bxa.create_loguniform_prior_for(mod3, mod3.gaussian.norm)

solver3 = bxa.BXASolver(transformations=[m3p1, m3p2, m3p3, m3p4, m3p5],
                        outputfiles_basename="mod3_wabs-bb-g")
###############################################

with XSilence():
    # 1) overview priors
    pbx.plot_overview_priors([solver1,solver2,solver3],
                             nsample=1000,nbins=25,
                             convert_log=True,
                             savename=os.path.join(savedir,'pbx_overview_priors.png'))

    # 2) prior predictive checks
    pbx.plot_model_instances([solver1,solver2,solver3],
                             models=[activate_mod1,activate_mod2,activate_mod3],
                             nsample=50,print_values=False,
                             ymin=1e-3,
                             rebinsig=5,rebinbnum=20,
                             savename=os.path.join(savedir,'pbx_model_instances.png'))

# run the fitting
#################
with XSilence():
    mod1,_ = activate_mod1()
    for t in solver1.transformations:
        t['model'] = mod1
    results1 = solver1.run(resume=True,run_kwargs={'show_status': False})

    mod2,_ = activate_mod2()
    for t in solver2.transformations:
        t['model'] = mod2

    results2 = solver2.run(resume=True,run_kwargs={'show_status': False})
    
    mod3,_ = activate_mod3()
    for t in solver3.transformations:
        t['model'] = mod3
    results3 = solver3.run(resume=True,run_kwargs={'show_status': False})
#################

with XSilence():
    # 3) fit results
    pbx.plot_data_and_predictionbands([solver1,solver2,solver3],
                                      [activate_mod1,activate_mod2,activate_mod3],
                                      setxminorticks=[1.2,2,3,4,6],
                                      ymin=1e-3,
                                      rebinsig=5,rebinbnum=10,
                                      savename=os.path.join(savedir,'pbx_data_and_predictionbands.png'))

    # 4) overview posterior distributions
    pbx.plot_overview_posteriors([solver1,solver2,solver3],
                                 convert_log=True,
                                 savename=os.path.join(savedir,'pbx_overview_posteriors.png'))

    # 5) qq plot
    pbx.plot_qq([solver1,solver2,solver3],
                models=[activate_mod1,activate_mod2,activate_mod3],
                quantile=0.49,
                savename=os.path.join(savedir,'pbx_qq.png'))

    # 6) qq diference plot
    pbx.plot_qq_difference([solver1,solver2,solver3],
                           models=[activate_mod1,activate_mod2,activate_mod3],
                           sim_data=True,nsample=150,
                           quantile=0.495,
                           savename=os.path.join(savedir,'pbx_qq_difference.png'))

    # 7) posterior MC likelihood test
    pbx.plot_posterior_mc_likelihood([solver1,solver2,solver3],
                                     models=[activate_mod1,activate_mod2,activate_mod3],
                                     nsample=250,colors=['r','g','b'],
                                     savename=os.path.join(savedir,'pbx_posterior_mc_likelihood.png'))

    # 8) fluxes
    pbx.plot_posterior_flux([solver1,solver2,solver3],
                            models=[activate_mod1,activate_mod2,activate_mod3],
                            fluxrange=(1.0,5.0),
                            colors=['r','g','b'],
                            savename=os.path.join(savedir,'pbx_flux.png'))

# method to print results
pbx.print_bayes_statistics([solver1,solver2,solver3])
