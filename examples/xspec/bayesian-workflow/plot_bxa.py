#
# Class to support plotting with BXA & PyXspec
#
# David Homan 11.07.2023
#
#

import xspec
import bxa.xspec as bxa
import ultranest.plot as upl
from plot_xspec import PlotXspec
import numpy as np

import os
import json
from natsort import natsorted 

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
plt.rc('font', family='serif')

class PlotBXA(PlotXspec):
    '''
    Provides basic plotting and inspection functions when using BXA & PyXspec.
    ---
    The following public methods are defined:

    plot_model_instances:
    Show predictive power of model, by plotting a number of instances of
    the model (as set by the priors) in combination with the data
    
    plot_overview_priors:
    Show the distributions of the parameter priors (historgrams)
    
    plot_data_and_predictionbands:
    An visualisation of the fitting results, indlucding the uncertainty
    set by the posterior distribution
    
    plot_overview_posteriors:
    Show the distributions of the parameter posteriors (historgrams),
    after the model fitting with BXA has been completed
    
    plot_qq:
    Quantile-Quantile plot, showing the cumulative distribution functions
    of model and data plotted against eachother
    
    plot_qq_difference:
    Difference of normalised cumulative distributions of model and data, 
    plotted against the energy
    
    plot_posterior_flux:
    The posterior distribution of the model flux
    
    plot_posterior_mc_likelihood:
    The posterior distribution of the likelihood, based on simulated data,
    under the assumption that the fitted model was correct. This can be 
    compared with the likelihood of the best-fit model
    
    plot_false_positive_test:
    Quantify significance of Bayesian evidence: create a simulated dataset
    based on the assumption that one of two models is correct and fit two
    models to all spectra in this dataset using BXA. The distribution of
    Bayesian evidence is plotted (histogram), as well as the cumulative 
    distribution function. This can be used to estimate the significance of
    the Bayesian evidence for the best-fit models.
    
    plot_false_negative_test:
    Convenience function, similar to plot_false_positive_test, only now
    testing the assumption that the other of the two models passed to it
    is the 'true' one 
   
    print_bayes_statistics:
    Prints an overview of fitting statistics (including Bayesian evidence)
    to screen
    '''
    
    def __init__(self):
        return None
        
    #####################################
    #                                   #
    #      (0) Helper Functions         #
    #                                   #
    #####################################
    
    def _create_fake_spectra(self,solver,
                             model_name=None,
                             idsp=None,
                             nsample=100,
                             return_plot_data=False,
                             plot_data_idsp=1,
                             store_spec=False,
                             spec_prefix='',
                             savedir='fakeit_spectra',
                             start_from_iter=0):
        '''
        Use XSPEC's fakeit to create simulated spectra, using the
        best-fit model from a BXA solver. This method requires the
        active XSPEC model to match the model used in the solver.
        
        Positional arguments
        solver           --- BXA solver; after solver.run() has completed
        
        Keyword arguments
        model_name       --- string; name of model to use, if named model is 
                             required (default is None)
        idsp             --- int; ID for loaded spectral data in XSPEC to use as 
                             input for fakeit (default is to make one fake spectrum
                             for each spectrum loaded) 
        nsample          --- int; number of fake spectra to create (default=100)
        return_plot_data --- bool; set to True if the method should also return
                             the simulated counts for each iteration
        plot_data_idsp   --- int; ID of simulated spectrum to return plot data for.
                             The default value is 1; this should only be changed if
                             more than one spectrum is loaded (and therefore more 
                             than one spectrum simulated) and data from these
                             simulated spectra are required
        store_spec       --- boolean; set to True if spectral files need to be stored
        spec_prefix      --- string; prefix to add to name under which simulated 
                             spectra are stored
        savedir          --- string; name of the directory where the simulated spectra
                             are stored
        start_from_iter  --- int; this value is only relevant when storing data. It
                             sets the lowest value in the labelling of stored spectra
                             (for cases where it is useful to keep some of the faked 
                             spectra in place -- e.g. for reproducibility). This value
                             should be lower than nsample.
        
        Returns
        fitstat_best     --- float; fit statistic for best-fit model
        fitstat          --- list of floats; fit statistics for simulated data
        sim_data         --- dict; contains the simulated data as well as the model
        '''
        # if required: check whether simulation directory exists
        if store_spec:
            if not os.path.exists(savedir):
                os.makedirs(savedir)
        # if required: check whether start_from_iter < nsample
        assert start_from_iter<nsample, 'start_from_iter should be smaller than nsample'
        # Check the correct model is active
        solver_model_cmp = solver.transformations[1]['model'].componentNames
        if model_name is None:
            model_name = ''  # empty string to call unnamed XSPEC model
        assert xspec.AllModels(1,model_name).componentNames == solver_model_cmp
        # read currently loaded xpspec data (these will be restored at the end)
        orig_data = self._find_loaded_data_format()
        # set model parameters to best-fit values
        params = solver.results['posterior']['mean']
        bxa.solver.set_parameters(values=params,transformations=solver.transformations)
        fitstat_best = 0.5*xspec.Fit.statistic
        # create fake spectra based on best-fit model
        fakeit_kw = []
        for ii,d in enumerate(orig_data):
            # check ARF & RMF file name lengths (fakeit has a built-in
            # character limit for the RESPFILE and ANCRFILE header entries)
            if len(d['rmf'])>68 or len(d['arf'])>68:
                print('The RMF and/or ARF file names are too long, these')
                print('will not be linked properly for the faked spectra.')
            fakeit_kw.append( dict([("response", d['rmf']),
                                    ("arf", d['arf']),
                                    ("background", d['bkg']),
                                    ("exposure", d['exp']),
                                    ("correction", "1."),
                                    ("backExposure", d['exp']),
                                    ("fileName", f"fakeit_tmp_{ii}.pha")]) )
        if idsp is None:
            nsim   = len(orig_data)
            fks    = [xspec.FakeitSettings(**kwd) for kwd in fakeit_kw]
            fk_ign = [d['ign'] for d in orig_data]
        else:
            nsim   = 1
            fks    = [xspec.FakeitSettings(**fakeit_kw[idsp])]
            fk_ign = [ orig_data[idsp]['ign'] ]
            for ii in range(1,len(orig_data)+1):
                if ii != idsp:
                    xspec.AllData -= ii
        fitstat  = []
        if return_plot_data:
            data = []
            bins, _, binw, _, model, _, _, _  = self._get_xspec_data(idsp=plot_data_idsp)
        xspec.Plot.xAxis = "keV"
        # when storing spectra: adjust filenames to prevent overwriting files
        if store_spec:
            fnames = []
            for fksetting in fks:
                fnames += [os.path.join(savedir,spec_prefix + '_{}_' + fksetting.fileName)]
        for ii in range(nsample-start_from_iter):
            # specify the filename if storing spectra
            if store_spec:
                for jj,fksetting in enumerate(fks):
                    fksetting.fileName = fnames[jj].format(ii+start_from_iter)
            # create fake spectra
            xspec.AllData.fakeit(nsim,fks)
            for jj in range(nsim):
                xspec.AllData(jj+1).ignore(fk_ign[jj])
            fitstat += [0.5*xspec.Fit.statistic]
            if return_plot_data:
                xspec.Plot('counts')
                data += [xspec.Plot.y(plotGroup=plot_data_idsp)]

        # clean up
        splist = [f"{d['dg']}:{d['ind']} {d['sp']}" for d in orig_data]
        xspec.AllData(' '.join(splist))
        xspec.AllData.notice('all')
        xspec.AllData.ignore('bad')
        for ii,d in enumerate(orig_data):
            xspec.AllData(ii+1).ignore(d['ign'])
        if not store_spec:
            for fname in [f for f in os.listdir() if f.startswith('fakeit_tmp')]:
                os.remove(fname)

        # define datasets to return
        if return_plot_data:
            sim_data = dict([('bins',bins),
                             ('binw',binw),
                             ('model',model),
                             ('data',data)])
            return fitstat_best, fitstat, sim_data
        else:           
            return fitstat_best, fitstat
            
    def _activate_models_for_solver(self,solver,fmodel):
        '''
        For a given solver, (re-)activate the model it uses and point
        the solver's transformations to this model. In case the the 
        transformations point to multiple models (i.e. in the case the 
        data are loaded into different XSPEC data groups), the 'fmodel'
        argument passed to this method should account for this and included
        all required model activation functions.
        
        NOTE: when multiple models are activated by the same function, it is 
              assumed that the order in which the priors (transformations) were
              passed tot the solver is the same order as the models as returned
              by the activation functions. i.e.: the first N priors are associated
              with model 1, the next M priors are associated with model 2, etc.
              (typically this means that the priors are in order of data group)
        
        Positional arguments:
        solver   --- BXA solver
        fmodel   --- list of functions; these functions should activate the 
                     necessary XSPEC models (all with the same name) and return
                     the PyXSPEC model objects associated with each.
                     
        Returns:
        mname    --- string; the name of the model (in case of multiple models 
                     associated with multiple data groups, the same name applies
                     to each model).
        '''
        mod,mname = fmodel()
        if type(mod) != list:
            # every transformation should point to the same model
            for t in solver.transformations:
                t['model'] = mod
        else:
            # the correct model needs to be matched to the correct transformation
            # (see note in docstring about matching)
            ii = 0
            for m in mod:
                nP = 0
                for v in self._find_var_params_model(m).values():
                    if v:
                        nP += len(v)
                for t in solver.transformations[ii:ii+nP]:
                    t['model'] = m
                ii += nP
        return mname

    def _find_var_params_solver(self,solver):
        '''
        Find all variable parameters included in a BXA solver
        
        Positional arguments:
        solver   --- BXA solver
        
        Returns:
        cmp_var  --- dict; keys are model component names, items are
                     lists of the variable parameters per component. 
                     Components belonging to a model other than AllModels
                     group element 1 are lablelled with a prefix M{ii}, with
                     ii the model group ID in XSPEC.
        '''
        # identify different XSPEC models (e.g. for different Data Groups)
        idms   = []
        st_ind = []
        mod_cmp   = None
        for idm,t in enumerate(solver.transformations):
            if t['model'] != mod_cmp:
                idms   += [idm]
                st_ind += [t['model'].startParIndex]
                mod_cmp = t['model']
        # sort model IDs to match order in XSPEC
        idms = [idm for _,idm in sorted(zip(st_ind, idms))]
        # loop over all different models
        cp_var = {}
        for ii,idm in enumerate(idms):
            cp = self._find_var_params_model(solver.transformations[idm]['model'])
            # add prefix for all models other than the first one in the group
            if ii>0:
                keys = list(cp.keys())
                for k in keys:
                    cp[f'M{ii+1}_'+k] = cp.pop(k)
            cp_var = {**cp_var, **cp}
        return(cp_var)
        
    def _assign_colors_to_model_params(self,solvers,models=None,colors=None):
        '''
        Create a list of colours, such that identical component-parameter
        combinations in different models (associated with the solvers) have
        the same colour.
        
        Positional arguments
        solvers  --- BXA solver or list of BXA solvers
        
        Keyword arguments:
        models   --- list of functions to activate models; NOTE: this kwarg
                     is ONLY required the data are loaded into more than one
                     data group (in this case de-activating a named model in
                     XSPEC removes the models associated with data groups with
                     index>1; to access them, the named model needs to be re-
                     activated)        
        colors   --- list of colours to assign to parameters. NOTE: this list
                     must be as least as long as the number of variable
                     parameters. If None (the default), a list of colours
                     will be generated.
        '''
        # check input format
        if type(solvers) is not list:
            solvers = [solvers]
        if models is not None and type(models) is not list:
            models = [models]
        if colors is None:
            colors = [plt.cm.Set1(ii) for ii in range(20)]
        assert type(colors) is list
        # find all combinations of model & component & parameter
        cmp_par,cmp_par_u = [],[]
        for ii,s in enumerate(solvers):
            # re-activate model and point solver to new instance
            # NOTE: only required when using more than one data group
            if models is not None:
                assert len(models)==len(solvers)
                self._activate_models_for_solver(s,models[ii])
            cp = self._find_var_params_solver(s)
            cmp_par   += [cp]
            cmp_par_u += [(k,v) for k in cp.keys() for v in cp[k]]
        # assign a colour to each unique component
        colmap = dict(zip(set(cmp_par_u),colors[:len(set(cmp_par_u))]))
        # create a list of assigned colours, matching the 'paramnames'
        # attribute of the solvers
        parcolors = []
        for m in cmp_par:
            modelc = []
            for c in m.keys():
                if len(m[c])!=0:
                    for p in m[c]:
                        modelc += [colmap[(c,p)]]
            parcolors += [modelc]
        return parcolors
        
    def _print_model_active_warning(self):
        '''
        Print warning concerning the use of multiple solvers without 
        re-activating the associated models in XSPEC.
        '''
        msg = '''
        PLEASE NOTE:
        Multiple solvers are used, however there are no functions provided
        to re-activate the models in XSPEC. Please verify that the parameters
        in all models are indeed altered as expected. If one or more of the
        models appears static, please include functions to redefine the models
        using the 'models' kwarg. The list of these functions should match the
        order of the list of solvers.
        '''
        print(msg)


    #################################
    #                               #
    #     (1) Plot the spectra      #
    #                               #
    #################################
    
    def plot_data_and_predictionbands(self,solvers,
                                      models=None,
                                      idsp=None,
                                      quantile=0.485,
                                      npost = 400,
                                      subplot='ratio',
                                      colors=None,
                                      ymin=None,ymax=None,
                                      xlog=True,ylog=True,
                                      rebinsig=None,
                                      rebinbnum=10,
                                      setxminorticks=None,
                                      savename=None):
        '''
        Plot data and model, including predictionbands. One band
        is set to one sigma, the other is set by the 'quantile' 
        kwarg.
        
        Positional arguments
        solvers        --- BXA solver or list of solvers; the solvers can be used 
                           after solver.run() has completed

        Keyword arguments
        models         --- list of functions; the functions should contain the 
                           XSPEC model definitions for each of the models (in 
                           order matching the list of solvers) and activate the
                           models when called. This approach is necessary to access
                           the XSPEC data for each of the models in turn
        idsp           --- int or list of ints; ID of spectra to plot 
                           (in plotGroup; default is all loaded spectra)
        quantile       --- float; quantile to set width of outer
                           prediction band (default = 0.48 -> 99%)
        npost          --- int; number of fit iterations included in the 
                           posterior distribution to sample.
        subplot        --- string; 'res' or 'ratio', setting the content of
                           the residuals plot
        colors         --- list of matplotlib colours to use for the plotted
                           spectra (default is None -> automatic)
        ymin           --- float; lower limit on y-axis
        ymax           --- float; upper limit on y-axis
        xlog           --- bool; set x-axis logscale (default is True)
        ylog           --- bool; set y-axis logscale (default is True)
        rebinsig       --- int; minimum sigma per bin (plotting only)
        rebinbnum      --- int; maximum number of bins to combine when
                           rebinning (plotting only)
        setxminorticks --- list; explicitly set minor ticks for x-axis
        savename       --- string; filename to store results (default is None)
        '''
        # Check input data
        if type(solvers) is not list:
            solvers = [solvers]
        if models is not None and type(models) is not list:
            models = [models]
        if len(solvers)>1 and models is None:
            self._print_model_active_warning()
        if idsp is None:
            idsp = [ii+1 for ii in range(xspec.AllData.nSpectra)]
        elif type(idsp) is int:
            idsp = [idsp]
        # define colors to use
        if colors is None:
            colors  = ['k']+[plt.cm.Set1(ii) for ii in range(len(idsp)-1)]
        if len(idsp)>1:
            mcolors = [[c]*len(idsp) for c in colors]
        else:
            mcolors = [None]
        # set up figure
        fig = plt.figure(constrained_layout=False,figsize=(12*len(solvers),9))
        gs = fig.add_gridspec(nrows=7, ncols=len(solvers), wspace=0.06, hspace=0)
        axs = []
        for ii in range(len(solvers)):
            axs += [(fig.add_subplot(gs[0:5,ii]), fig.add_subplot(gs[5:,ii]))]
        # loop over the models and create a plot for each
        for ii,s in enumerate(solvers):
            # re-activate model and point solver to new instance
            if models is not None:
                assert len(models)==len(solvers)
                self._activate_models_for_solver(s,models[ii])
            # plot the data, model, and residuals
            for jj,idsp_jj in enumerate(idsp):
                self._plot_data_prediction_single_model(axs[ii],s,
                                                        idsp=idsp_jj,
                                                        quantile=quantile,
                                                        npost=npost,
                                                        clr=colors[jj],mclr=mcolors[jj],
                                                        ymin=ymin,ymax=ymax,
                                                        xlog=xlog,ylog=ylog,
                                                        rebinsig=rebinsig,
                                                        rebinbnum=rebinbnum,
                                                        setxminorticks=setxminorticks)
            # label models
            m = s.transformations[0]['model'].expression
            axs[ii][0].text(0.05,1.02,f'Model {m}',
                            fontsize=20,fontweight='bold',
                            transform=axs[ii][0].transAxes)
            # settings for subplots other that left-most
            if ii!=0:
                for kk in [0,1]:
                    #axs[ii][jj].set_yticklabels([])
                    axs[ii][kk].set_ylabel('')
        # show and possibly store plot
        if savename:
            plt.savefig(savename)
        else:
            plt.show()
            
    def _plot_data_prediction_single_model(self,axs,solver,
                                           idsp=1,
                                           quantile=0.48,
                                           npost = 400,
                                           subplot='ratio',
                                           clr='k',mclr=None,
                                           ymin=None,ymax=None,
                                           rebinsig=None,
                                           rebinbnum=10,
                                           setxminorticks=None,
                                           xlog=True,ylog=True):
        '''
        Plot data and model, including predictionbands. One band
        is set to one sigma, the other is set by the 'quantile' 
        kwarg.
        
        Positional arguments
        axs            --- tuple of two Matplotlib Axes objects; the objects 
                           should represent the main plot and the residuals
                           plot, respectively
        solver         --- BXA solver; solver after running the fit
        
        Keyword arguments:
        idsp           --- int; ID of spectrum to plot (in plotGroup)    
        quantile       --- float; quantile to set width of outer
                           prediction band (default = 0.48 -> 99%)
        npost          --- int; number of fit iterations included in the 
                           posterior distribution to sample.
        subplot        --- string; 'res' or 'ratio', setting the content of
                           the residuals plot (default is 'ratio')
        clr            --- matplotlib color; colour used to plot the data
        mclr           --- list; if set colours will be used for the model
                           and predictionbands. Otherwise the standard colours 
                           for will be used (default is None)
        ymin           --- float; lower limit on y-axis
        ymax           --- float; upper limit on y-axis
        xlog           --- bool; set x-axis logscale (default is True)
        ylog           --- bool; set y-axis logscale (default is True)
        rebinsig       --- int; minimum sigma per bin (plotting only)
        rebinbnum      --- int; maximum number of bins to combine when
                           rebinning (plotting only)
        setxminorticks --- list; explicitly set minor ticks for x-axis<
        savename       --- string; filename to store results (default is None)
        '''
        # define subplots
        ax, ax_res = axs
        # get data from XSPEC plot (using the best-fit parameters)
        params = solver.results['posterior']['mean']
        bxa.solver.set_parameters(values=params,transformations=solver.transformations)
        x,y,xerr,yerr,mbest,res,ratio,_ = self._get_xspec_data(idsp=idsp,
                                                               rebinsig=rebinsig,
                                                               rebinbnum=rebinbnum)
        # specify data to be used in subplot
        if subplot=='res': 
            sp_data    = res
            sp_dataerr = yerr
            res_norm   = np.ones(len(yerr))
        elif subplot=='ratio':
            sp_data    = ratio
            sp_dataerr = np.ones(len(sp_data))
            res_norm   = np.array(yerr)
            res_norm[res_norm==0] = np.nan
        # get bxa results and store
        band_main = upl.PredictionBand(x)
        band_res  = upl.PredictionBand(x)
        xspec.Plot.background = True
        mbest = np.array(mbest)
        if npost > len(solver.posterior):
            npost = len(solver.posterior)
        for row in solver.posterior[:npost]:
            bxa.solver.set_parameters(values=row,transformations=solver.transformations)
            _,_,_,_,model,_,_,_ = self._get_xspec_data(idsp=idsp,
                                                       rebinsig=rebinsig,
                                                       rebinbnum=rebinbnum)
            band_main.add(model)
            band_res.add((np.array(model)-mbest)/res_norm)
        # plot data
        self._make_spec_plot_main(ax,x,y,xerr,yerr,
                                  xlabel=False,
                                  ymin=ymin,ymax=ymax,
                                  xlog=xlog,ylog=ylog,
                                  clr=clr,
                                  setxminorticks=setxminorticks)
        # plot residuals
        self._make_spec_plot_residuals(ax_res,
                                       x,sp_data,xerr,sp_dataerr,
                                       xlog=True,ylog=False,
                                       subplot=subplot,
                                       clr=clr,
                                       setxminorticks=setxminorticks,
                                       zeroline=False)
        # plot model & posterior bands (and set the colours)
        if mclr is not None:
            assert len(mclr)==3,'mclr must list three colours: best-fit model, 1-sigma band, and quantile band'
            lineclr = mclr[0]
            sigclr  = mclr[1]
            qclr    = mclr[2]
        else:
            lineclr = 'k'
            sigclr  = 'red'
            qclr    = 'orange'
        for a,b in zip(axs,[band_main,band_res]):
            plt.sca(a)
            b.line(color=lineclr)
            # add 1 sigma quantile
            b.shade(color=sigclr, alpha=0.65)
            # add wider quantile (0.01 .. 0.99)
            b.shade(q=quantile, color=qclr, alpha=0.4)

    ###############################
    #                             #
    # (2) Print results to screen #
    #                             #
    ###############################
    
    def _calc_aic(self,solver):
        '''
        --- uses BXA ---
        Calculate the Akaike Information Criterion based on the best-fit 
        likelihood for one BXA solver.
        
        Positional arguments:
        solver --- BXA solver
        
        Returns
        aic    --- float; Akaike Information Criterion
        '''
        npar = len(solver.paramnames)
        aic  = 2*npar-2*solver.results['maximum_likelihood']['logl']
        return aic

    def print_bayes_statistics(self,solvers):
        '''
        --- uses BXA ---
        Print comparison of fit-statistics, based on Bayesian evidence and log
        -likelihood to screen. The results will be printed as the difference
        between two models, for Sum(N-1) pairs of models in an array of N solvers.
        
        Positional arguments:
        solvers   --- list of BXA solvers
        
        Returns:
        None
        '''
        if type(solvers) is not list:
            print('At least two solvers are required (format is list)')
        for ii in range(len(solvers)):
            for jj in range(len(solvers)):
                if ii>=jj:
                    continue
                z1   = solvers[ii].results['logz']
                z2   = solvers[jj].results['logz']
                l1   = solvers[ii].results['maximum_likelihood']['logl']
                l2   = solvers[jj].results['maximum_likelihood']['logl']
                aic1 = self._calc_aic(solvers[ii])
                aic2 = self._calc_aic(solvers[jj])
                print('For {}/{} = ({})/({}):'.format(solvers[ii].transformations[0]['model'].name,
                                                      solvers[jj].transformations[0]['model'].name,
                                                      solvers[ii].transformations[0]['model'].expression,
                                                      solvers[jj].transformations[0]['model'].expression))
                print(f'{"Bayes factor:":<13} log(Z_1/Z_2) = {z1: 7.2f} - {z2: 7.2f} = {z1-z2: 5.2f}')
                print(f'{"Likelihood:":<13} log(L_1/L_2) = {l1: 7.2f} - {l2: 7.2f} = {l1-l2: 5.2f}')
                print(f'{"AIC:":<13} AIC_1-AIC_2  = {aic1: 7.2f} - {aic2: 7.2f} = {aic1-aic2: 5.2f}')
                print('###########')
 
    ######################################################
    #                                                    #
    # (3) Plot model instances (prior predictive checks) #
    #                                                    #
    ######################################################
    
    def plot_model_instances(self,solvers,
                             models = None,
                             nsample=100,
                             idsp=1,msize=5,
                             ymin=None,ymax=None,
                             rebinsig=None,
                             rebinbnum=10,
                             savename=None,
                             print_values=False):
        '''
        Plot the result of creating multiple instances of the same model
        with the parameters drawn from the specified priors. Can be used
        as a check on the predictive power of the priors.
        
        Positional arguments:
        solvers       --- BXA solver or list of solvers; matching the models to 
                          explore

        Keyword arguments:
        models        --- list of functions to activate models; NOTE: this kwarg
                          is required if more than one solver is passed to this 
                          method
        nsample       --- int; number of model instances to create
        idsp          --- int; ID of spectrum to plot (in plotGroup; default is 1)
        msize         --- int; size of the data markers in the plot (default is 5)
        ymin          --- float; lower limit of y-axis (default is None; automatic)
        ymax          --- float; upper limit of y-axis (default is None; automatic)
        rebinsig      --- int; minimum sigma per bin (plotting only)
        rebinbnum     --- int; maximum number of bins to combine when
                          rebinning (plotting only)
        savename      --- string; filename for output plot, if it should be saved
                          (default is None)
        print_values  --- boolean; print the maximum and minimum values per parameter
                          (per model) to screen (default is False)
        '''
        # Check input data
        if type(solvers) is not list:
            solvers = [solvers]
        if models is not None and type(models) is not list:
            models = [models]
        if len(solvers)>1 and models is None:
            self._print_model_active_warning()
        # set up figure
        fig,axs = plt.subplots(1,len(solvers),figsize=(8*len(solvers),8))
        # loop over the models and create a predictive plot for each
        if type(axs) is not np.ndarray:
            axs = (axs,)
        for ii,s in enumerate(solvers):
            # re-activate model and point solver to new instance
            if models is not None:
                assert len(models)==len(solvers)
                mname = self._activate_models_for_solver(s,models[ii])
            else:
                mname = None
            # plot the model instances
            self._instances_single_model(axs[ii],s,
                                         nsample=nsample,
                                         idsp=idsp,msize=5,
                                         ymin=ymin,ymax=ymax,
                                         rebinsig=rebinsig,
                                         rebinbnum=rebinbnum,
                                         print_values=print_values)
            # label models
            m = s.transformations[0]['model'].expression
            fsize = np.minimum(24,int(28/len(m) * 24))
            axs[ii].set_title(f' Model: {m}',loc='left',pad=15,
                                 fontsize=fsize,fontweight='bold')
            # settings for subplots other than left-most
            if ii!=0:
                axs[ii].set_yticklabels([])
                axs[ii].set_ylabel('')
        # final plot settings
        plt.subplots_adjust(wspace=0.03)
        # show and possibly store plot
        plt.tight_layout()
        if savename:
            plt.savefig(savename)
        else:
            plt.show()
            
    def _instances_single_model(self,ax,
                                solver,nsample=100,
                                idsp=1,msize=5,
                                ymin=None,ymax=None,
                                rebinsig=None,
                                rebinbnum=10,
                                print_values=False):
        '''
        Plot the prior predictions for a single model. This method works on 
        a single Matplotlib Axes.
        '''
        # intitial setup for xspec
        xspec.Plot.xAxis = "keV"
        # generate the xspec model data
        mod_iter = []
        values   = []
        rnd      = np.random.uniform(size=(nsample,len(solver.paramnames)))
        for ii in range(nsample):
            values += [solver.prior_function(rnd[ii])]
            bxa.solver.set_parameters(transformations=solver.transformations,
                                      values=values[-1])
            if rebinsig:
                xspec.Plot.setRebin(minSig=rebinsig,
                                    maxBins=rebinbnum,
                                    groupNum=-1)
            else:
                xspec.Plot.setRebin(minSig=0,maxBins=None,groupNum=None)
            xspec.Plot('data')
            mod_iter += [xspec.Plot.model(plotGroup=idsp)]
        # get the xspec spectral data
        bins,rates,binw,ratese = self._get_xspec_data(model=False,
                                                      idsp=idsp,
                                                      rebinsig=rebinsig,
                                                      rebinbnum=rebinbnum)
        # set up figure and plot data & models
        for m in mod_iter:
            x,y = self._extrapolate_model_log(bins,binw,m)
            ax.plot(x,y,c='red',lw='2',alpha=0.55)
        self._make_spec_plot_main(ax,
                                     bins,rates,binw,ratese,
                                     ymin=ymin,ymax=ymax,
                                     extend=True)
        ax.grid(False)
        # summarise parameter distribution
        if print_values:
            print(f"Model: {solver.transformations[0]['model'].expression}")
            print('{:<10s}{:<10s}{:<10s}'.format('param','min','max'))
            values = np.array(values)
            for ii in range(len(solver.paramnames)):
                par  = solver.paramnames[ii]
                minv = np.amin(values[:,ii])
                maxv = np.amax(values[:,ii])
                print('{:<10s}{:<10.4f}{:<10.4}'.format(par,minv,maxv)) 
                
    ############################
    #                          #
    #  (4) Plot QQ overviews   #
    #                          #
    ############################    
        
    def plot_qq(self,solvers,
                models=None,
                idsp=1,
                npost = 100,
                xlog = False, ylog = False,
                quantile=0.495,
                savename=None):
        '''
        Create Q-Q plot (i.e. the cumulative distributions of the data and 
        model, respectively), including indication of posterior distribution.
        The plot will show a 1:1 relation as a blue dashed line, the measured
        quantile distribution in black, and two bands indicating the scatter
        in the posterior distribution (1-sigma in red, and a user-
        specified width in light orange).
        
        Positional arguments:
        solvers    --- list of BXA solvers
        
        Keyword arguments:
        models     --- list of functions to activate XSPEC models
        idsp       --- int; ID of spectrum to plot (default is 1)
        npost      --- int; sample size to draw from posterior distribution
        xlog       --- boolean; set logscale on horizontal axis (default is False)
        ylog       --- boolean; set logscale on vertical axis (default is False)
        quantile   --- float; quantile of the posterior distribution to include
                       (based on a one-tailed distribution). This is in addition
                       to the 1-sigma band, which is always shown (default is 0.48)
        savename   --- string; file name for saving plot, if required 
                       (default is None)
        '''
        # Check input data
        if type(solvers) is not list:
            solvers = [solvers]
        if models is not None and type(models) is not list:
            models = [models]
        if len(solvers)>1 and models is None:
            self._print_model_active_warning()
        # set up figure
        fig,axs = plt.subplots(1,len(solvers),figsize=(8*len(solvers),8))
        # loop over the models and create a QQ plot for each
        if type(axs) is not np.ndarray:
            axs = (axs,)
        for ii,s in enumerate(solvers):
            # re-activate model and point solver to new instance
            if models is not None:
                assert len(models)==len(solvers)
                self._activate_models_for_solver(s,models[ii])
            # generate the QQ plot in the Axes instance
            self._plot_qq_single_model(axs[ii],s,
                                       idsp=idsp,
                                       npost=npost,
                                       xlog=xlog, ylog=ylog,
                                       quantile=quantile)
            # label models
            m = s.transformations[0]['model'].expression
            fsize = np.minimum(24,int(28/len(m) * 24))
            axs[ii].set_title(f' Model: {m}',loc='left',pad=15,
                                 fontsize=fsize,fontweight='bold')
            # settings for subplots other than left-most
            if ii!=0:
                axs[ii].set_yticklabels([])
                axs[ii].set_ylabel('')
        # final plot settings
        plt.subplots_adjust(wspace=0.03)
        axs[0].legend(loc='upper left',fontsize=18)
        # show and possibly store plot
        plt.tight_layout()
        if savename:
            plt.savefig(savename)
        else:
            plt.show()
            
    def _plot_qq_single_model(self,ax,solver,
                              idsp=1,
                              npost = 100,
                              xlog = False, ylog = False,
                              quantile=0.48):
        '''
        Create Q-Q plot for a single Axes object.
        '''
        # best-fit model data
        bins, data, binw, _, model, _, _, _ = self._get_xspec_data(model=True,idsp=idsp,
                                                                      plottype='counts')
        data  = np.array(data)
        datac = data.cumsum()

        # models generated from posterior distributions
        band = upl.PredictionBand(datac)
        if npost > len(solver.posterior):
            npost = len(solver.posterior)
        for row in solver.posterior[:npost]:
            bxa.solver.set_parameters(values=row, transformations=solver.transformations)
            xspec.Plot('counts')
            band.add(np.array(xspec.Plot.model(plotGroup=idsp)).cumsum())

        ax.plot(datac,datac,linestyle='--',color='blue',lw=2,label='1:1')
        plt.sca(ax)
        band.line(color='k',label='data')    
        band.shade(color='r', alpha=0.8,label='68.2%')
        qstr = f'{(2*quantile)*100:.1f}%'
        band.shade(q=quantile, color='orange', alpha=0.5,label=qstr)

        # plot details
        xmin, ymin = 0,0
        if xlog:
            ax.set_xscale('log')
            xmin = np.amin(datac)
        if ylog:
            ax.set_yscale('log')
            ymin = datac[0]
        ax.set_xlim(xmin,np.amax(datac))
        ax.set_ylim(bottom=ymin)
        textkwargs = dict( (('fontsize',18),('fontweight','bold')) )
        ax.set_xlabel('Cumulative Data (Counts)',**textkwargs)
        ax.set_ylabel('Cumulative Model (Counts)',**textkwargs)

        # ticks and ticklabels
        plt.setp(ax.get_xticklabels(), fontsize=13)
        plt.setp(ax.get_yticklabels(), fontsize=13)
        ax.tick_params(top=True, right=True, which='both')
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.tick_params(axis='both', which='major',
                       direction='in', length=6, width=1.5)
        ax.tick_params(axis='both', which='minor',
                       direction='in', length=3, width=1.2)

    def plot_qq_difference(self,solvers,
                           models=None,
                           idsp=1,
                           npost = 100,
                           xlog = True, ylog = False,
                           ymin = None, ymax = None,
                           quantile=0.48,
                           sim_data=False,nsample=100,
                           savename=None):
        '''
        Plot the difference between the normalised cumulative distributions
        of the model and the data, against the energy. The plot will show the
        measured difference between the distributions in black, as well as two
        shaded bands. These bands indicate the scatter in the posterior 
        distribution: 1-sigma in red, and a user-specified width in light orange.

        The method also includes the option (set sim_data=True) to give an 
        indication of the intrinsic scatter of these data. This is performed by
        using the best-fit model to create simulated spectra; in other words:
        this shows the scatter in the data for the case that the model is
        a perfect representation of the real spectrum.
       
        Positional arguments:
        solvers    --- list of BXA solvers
        
        Keyword arguments:
        models     --- list of functions to activate XSPEC models
        idsp       --- int; ID of spectrum to plot (default is 1)
        npost      --- int; sample size to draw from posterior distribution
        xlog       --- boolean; set logscale on horizontal axis (default is False)
        ylog       --- boolean; set logscale on vertical axis (default is False)
        ymin       --- float; lower limit of y-axis (default is None -> automatic)
        ymax       --- float; upper limit of y-axis (default is None -> automatic)
        quantile   --- float; quantile of the posterior distribution to include
                       (based on a one-tailed distribution). This is in addition
                       to the 1-sigma band, which is always shown (default is 0.48)
        sim_data   --- boolean; include a shaded region showing the distribution
                       of the difference of the normalised cumulative distributions,
                       __under the assumption__ that model represents the true 
                       spectrum (i.e. using simulated spectra based on the best-
                       fit model)
        n_sample   --- int; number of spectra to simulate (if sim_data is True)
        savename   --- string; file name for saving plot, if required 
                       (default is None)
        ''' 
        # Check input data
        if type(solvers) is not list:
            solvers = [solvers]
        if models is not None and type(models) is not list:
            models = [models]
        if len(solvers)>1 and models is None:
            self._print_model_active_warning()
        # set up figure
        fig,axs = plt.subplots(1,len(solvers),figsize=(8*len(solvers),8))
        # loop over the models and create a QQ-difference plot for each
        if type(axs) is not np.ndarray:
            axs = (axs,)
        for ii,s in enumerate(solvers):
            # re-activate model and point solver to new instance
            if models is not None:
                assert len(models)==len(solvers)
                mname = self._activate_models_for_solver(s,models[ii])
            else:
                mname = None
            # generate the QQ-difference plot in the Axes instance
            self._plot_qq_diff_single_model(axs[ii],s,
                                            model_name=mname,
                                            idsp=idsp,
                                            npost=npost,
                                            xlog=xlog, ylog=ylog,
                                            quantile=quantile,
                                            sim_data=sim_data,nsample=nsample)
            # label models
            m = s.transformations[0]['model'].expression
            fsize = np.minimum(24,int(28/len(m) * 24))
            axs[ii].set_title(f' Model: {m}',loc='left',pad=15,
                                 fontsize=fsize,fontweight='bold')
            # settings for subplots other than left-most
            if ii!=0:
                axs[ii].set_yticklabels([])
                axs[ii].set_ylabel('')
        # final plot settings
        plt.subplots_adjust(wspace=0.03)
        ymn, ymx = np.array([ax.get_ylim() for ax in axs]).T
        if ymin is None:
            ymin = np.amin(ymn)*1.05
        if ymax is None:
            ymax = np.amax(ymx)*1.05
        for ax in axs:
            ax.set_ylim((ymin,ymax))
        axs[0].legend(loc='best',fontsize=18)
        # show and possibly store plot
        plt.tight_layout()
        if savename:
            plt.savefig(savename)
        else:
            plt.show()

    def _plot_qq_diff_single_model(self,ax,solver,
                                   model_name = None,
                                   idsp=1,
                                   npost = 100,
                                   xlog = True, ylog = False,
                                   quantile=0.48,
                                   sim_data=False,nsample=100):
        '''
        Plot the difference between the normalised cumulative 
        distributions of the model and the data, against the 
        energy.
        ''' 

        # get data
        bins, data, binw, _ = self._get_xspec_data(model=False,plottype='counts',idsp=idsp)
        ndatac  = np.array(data).cumsum()/np.sum(data)

        # models generated from posterior distributions
        band = upl.PredictionBand(bins)
        if npost > len(solver.posterior):
            npost = len(solver.posterior)
        for row in solver.posterior[:npost]:
            bxa.solver.set_parameters(values=row, transformations=solver.transformations)
            xspec.Plot('counts')
            m = np.array(xspec.Plot.model(plotGroup=idsp))
            band.add(ndatac-m.cumsum()/m.sum())

        # plot the data
        xmin = bins[0] - binw[0]/3
        xmax = bins[-1] + binw[-1]
        ax.hlines(0,xmin,xmax,ls='--',color='grey')
        plt.sca(ax)
        band.line(color='k',label='data')    
        band.shade(color='r', alpha=0.8,label='68.2%')
        qstr = f'{(2*quantile)*100:.1f}%'
        band.shade(q=quantile, color='orange', alpha=0.5,label=qstr)
        
        # include simulated data (if required)
        if sim_data:
            _,_,sdata = self._create_fake_spectra(solver,
                                                  model_name=model_name,
                                                  nsample=nsample,
                                                  return_plot_data=True,
                                                  plot_data_idsp=idsp)
            assert bins == sdata['bins']
            nmodelc = np.array(sdata['model']).cumsum()/np.sum(sdata['model'])
            band_sim = upl.PredictionBand(bins)
            for d in sdata['data']:
                band_sim.add(np.array(d).cumsum()/np.sum(d) - nmodelc)
            band_sim.shade(color='grey',alpha=0.7)

        # plot details
        if xlog:
            ax.set_xscale('log')
        if ylog:
            ax.set_yscale('log')
            ymin = ndatac[0]
        ax.set_xlim(xmin,xmax)
        textkwargs = dict( (('fontsize',22),('fontweight','bold')) )
        ax.set_xlabel('Energy (keV)',**textkwargs)
        ax.set_ylabel(r'Q$_d$/N$_d$ $-$ Q$_m$/N$_m$',**textkwargs)
        # ticks and ticklabels
        plt.setp(ax.get_xticklabels(), fontsize=15)
        plt.setp(ax.get_yticklabels(), fontsize=15)
        ax.tick_params(top=True, right=True, which='both')
        ax.yaxis.set_minor_locator(MultipleLocator(0.01))
        ax.tick_params(axis='both', which='major',
                       direction='in', length=6, width=1.5)
        ax.tick_params(axis='both', which='minor',
                       direction='in', length=3, width=1.2)


    #######################################
    #                                     #
    #  (5) Plot parameter distributions   #
    #                                     #
    #######################################

    def plot_overview_priors(self,solvers,
                             models=None,
                             nsample=10000,nbins=30,
                             convert_log=False,
                             colors = None,
                             savename=None):
        '''
        Plot an overview of the prior distributions for each variable 
        model component, for one or multiple (as associated with the 
        solver or solvers passed to this method).
        
        Positional arguments:
        solvers       --- BXA solver or list of BXA solvers
        
        Keyword arguments:
        models        --- list of functions to activate models; NOTE: this kwarg
                          is ONLY required the data are loaded into more than one
                          data group (in this case de-activating a named model in
                          XSPEC removes the models associated with data groups with
                          index>1; to access them, the named model needs to be re-
                          activated)
        nsample       --- int; number of random draws from the prior to use to create
                          the plot (default is 'prior')
        nbins         --- int; number of bins used in the histogram (default is 30)
        convert_log   --- boolean; convert log-uniform paramteres to linear space
                          (default is False)
        colors        --- list of PyPlot.matplotlib colours to be used for plotting 
                          (see PlotBXA._assign_colors_to_model_params(); default is
                          None)
        savename      --- string; name of output file, if required (default is None)
        '''
        self._plot_overview_parameters(solvers,
                                       models=models,
                                       distribution='prior',
                                       nsample=nsample,nbins=nbins,
                                       convert_log=convert_log,
                                       colors=colors,
                                       savename=savename)
                                       
    def plot_overview_posteriors(self,solvers,
                                 models=None,
                                 nbins=30,convert_log=False,
                                 quantile=0.341,colors=None,
                                 printq=False,
                                 return_val=False,
                                 savename=None):
        '''
        Plot an overview of the posterior distributions for each variable
        model component, as accessible through the BXA solvers passed to this
        method.
        
        Positional arguments:
        solvers       --- BXA solver or list of BXA solvers
        
        Keyword arguments:
        models        --- list of functions to activate models; NOTE: this kwarg
                          is ONLY required if the data are loaded into more than one
                          data group (in this case de-activating a named model in
                          XSPEC removes the models associated with data groups with
                          index>1; to access them, the named model needs to be re-
                          activated)
        nbins         --- int; number of bins used in the histogram (default is 30)
        convert_log   --- boolean; convert log-uniform paramteres to linear space
                          (default is False)
        quantile      --- float; quantile to be plotted as vertical line in the
                          distribution, on either side of the mean. Value applies to
                          a one-tailed distribution (default is 0.341= 1 sigma)
        colors        --- list of PyPlot.matplotlib colours to be used for plotting 
                          (see PlotBXA._assign_colors_to_model_params(); default is
                          None)
        printq        --- boolean; if True, print the mean and the uncertainties, as
                          specified by the quantiles, to screen for each of the
                          parameters
        return_val    --- boolean; if True, the mean paramater values and uncertainties
                          will be returned as a list (default is False)
        savename      --- string; name of output file, if required (default is None)
        '''
        self._plot_overview_parameters(solvers,
                                       models=models,
                                       distribution='posterior',
                                       nbins=nbins,convert_log=convert_log,
                                       q=quantile,colors=colors,
                                       printq=printq,
                                       savename=savename)
        if return_val:
            return self.posterior_par_unc
                                     
    def _plot_overview_parameters(self,solvers,
                                  models=None,
                                  distribution='prior',
                                  nsample=10000,nbins=30,
                                  convert_log = False,q=0.341,
                                  colors = None,
                                  printq=False,
                                  savename = None):
        '''
        Plot overview of parameter distributions for one or multiple models.
        Based on a single BXA solver, or a list of solvers, plot the probability
        distribution of each varying parameter.
        
        Most arguments are defined in the docstring for PlotBXA._plot_overview_priors().
        Additional keyword arguments:
        
        distribution  --- string; 'prior' or 'posterior'; sets plot type

        '''
        # check input
        if type(solvers) is not list:
            solvers = [solvers]
        if models is not None and type(models) is not list:
            models = [models]
        # set up plot
        npar_max = 1
        for s in solvers:
            npar_max = np.maximum(npar_max,len(s.paramnames))
        fig, axs = plt.subplots(len(solvers),npar_max,
                                figsize=(npar_max*8,len(solvers)*8))
        # identifify identical component parameters and give them the same colour
        colors = self._assign_colors_to_model_params(solvers,models=models)
        # loop over models (solvers) and create overview of parameters for each
        if len(solvers) == 1:
            if npar_max == 1:
                axs = ((axs,),)
            else:
                axs = (axs,)
        if distribution=='posterior':
            self.posterior_par_unc = [] # set for first use or clear for new use
        for ii,s in enumerate(solvers):
            # re-activate model and point solver to new instance
            # NOTE: only required when using more than one data group
            if models is not None:
                assert len(models)==len(solvers)
                self._activate_models_for_solver(s,models[ii])
            # create plot(s) for a single model
            self._distribution_single_model(s,axs[ii],
                                            dist=distribution,
                                            nsample=nsample,nbins=nbins,
                                            convert_log=convert_log,q=q,
                                            colors=colors[ii],
                                            printq=printq)
            # label each model
            m = s.transformations[0]['model'].expression
            axs[ii][0].set_title(f' Model: {m}',loc='left',pad=15,
                                 fontsize=24,fontweight='bold')
        # plot details                                      
        plt.subplots_adjust(wspace=0.03,hspace=0.25)

        # set legend in top right plot
        if axs[0][0].get_legend_handles_labels() != ([],[]):
            axs[0][0].legend(loc='upper right',fontsize=18)
    
        # show and possibly store plot
        plt.tight_layout()
        if savename:
            plt.savefig(savename)
        else:
            plt.show()

    def _distribution_single_model(self,solver,axs,
                                   dist='prior',
                                   nsample=10000,nbins=30,
                                   convert_log = False,q=0.341,
                                   colors = ['b','g','r','y'],
                                   printq=False):
        '''
        Overview plot of the parameter distributions for a single model. Modifies
        objects from an array of Matplotlib Axes.
        
        For an overview of the parameter definitions, see 
        PlotBXA._plot_overview_priors() & PlotBXA._plot_overview_parameters().
        '''
        npar = len(solver.paramnames)
        par_v = self._find_var_params_solver(solver)
        cmp_names = []
        for k in par_v.keys():
            if len(par_v[k])!=0:
                cmp_names += [k]*len(par_v[k])
        # collect data for histograms
        if dist=='prior':
            # generate prior distribution from random uniform sample
            priors = []
            rnd = np.random.uniform(size=(nsample,npar))
            for r in rnd:
                priors.append(solver.prior_function(r))
            data = np.array(priors).T
        elif dist=='posterior':
            # collect posteriors (even-weighted sampling)
            data = solver.posterior.copy().T
        # convert log-distributed parameters to linear space
        parnames = solver.paramnames.copy()
        if convert_log:
            for ii,pn in enumerate(solver.paramnames):
                if pn.startswith('log'):
                   data[ii] = solver.transformations[ii]['aftertransform'](data[ii])
                   parnames[ii] = pn[pn.find('(')+1:pn.find(')')]
        # plot histograms
        lblkw = dict( (('fontsize',20),('fontweight','bold')) )
        ymax = []
        mname = solver.transformations[1]['model'].expression
        if printq and dist=='posterior':
            print(f'\nFor model {mname}, with uncertainties estimated for +/- {q*100:.1f}%:')
        for ii,d in enumerate(data):
            ax = axs[ii]
            c,b = np.histogram(d,bins=nbins)
            ax.stairs(c,b,fill=True,color=colors[ii],alpha=0.5)
            xl = f'{parnames[ii]} [{cmp_names[ii]}]'
            ax.set_xlabel(xl,**lblkw)
            # find the y-range upper limit
            ymax += [np.amax(c)]
            ax.set_yticklabels([])
            # set x-range
            xmin = b[0]  - (b[-1] - b[0])*0.2 
            xmax = b[-1] + (b[-1] - b[0])*0.2 
            ax.set_xlim((xmin,xmax))
            # ticks
            ax.tick_params(top=True, right=True, which='both')
            ax.yaxis.set_minor_locator(AutoMinorLocator())
            ax.xaxis.set_minor_locator(AutoMinorLocator())
            ax.tick_params(axis='both', which='major',
                           direction='in', length=6, width=1.5)
            ax.tick_params(axis='both', which='minor',
                           direction='in', length=3, width=1.2)
            plt.setp(ax.get_xticklabels(), fontsize=15)
            if dist=='posterior':
                # mark mean and q-quantile limits
                ax.vlines(np.mean(d),0,len(d),
                          colors=colors[ii],ls='-',lw=3,
                          zorder=100,label='Mean')
                q_mean = np.count_nonzero(d<np.mean(d))/d.size
                wrnstr = 'Reached {} end of posterior distribution for {}: '
                wrnstr += '{} uncertainty is an approximation'
                if q_mean-q < 0:
                    print(wrnstr.format('lower',parnames[ii],'lower'))
                    qlim = 0
                else:
                    qlim = q_mean-q
                q_low  = np.quantile(d,qlim)
                if q_mean+q > 1:
                    print(wrnstr.format('upper',parnames[ii],'upper'))
                    qlim = 1
                else:
                    qlim = q_mean+q
                q_high = np.quantile(d,qlim)
                qstr = f'{(2*q)*100:.1f}%'
                ax.vlines(q_low,0,len(d),
                          colors=colors[ii],ls='--',lw=3,zorder=100,label=qstr)
                ax.vlines(q_high,0,len(d),
                          colors=colors[ii],ls='--',lw=3,zorder=100)
                # store values to return them and print to screen if required
                if dist=='posterior':
                    self.posterior_par_unc += [[mname,cmp_names[ii],parnames[ii],
                                                np.mean(d),q_high,q_low]]
                if printq:
                    print(f'{xl:20}: Mean={np.mean(d): .3e} (+){q_high: .3e} (-){q_low: .3e}')
        # remove unused axes
        if len(axs)>len(data):
            for ax in axs[len(data):]:
                ax.axis('off')
        # Final details
        axs[0].set_ylabel('Probability Distribution',**lblkw)
        plt.setp(axs[0].get_yticklabels(), fontsize=15)
        for ax in axs:
            ax.set_ylim(0,np.amax(ymax)*1.05)


    ##################################################
    #                                                #
    #  (6) Check on fit results and statistics (MC)  #
    #                                                #
    ##################################################

    def plot_posterior_flux(self,solvers,
                            models=None,
                            fluxrange=(0.2,2.0),
                            npost=-1,colors='k',
                            quantile=0.341,
                            printq=False,
                            return_val=True,
                            ymax=None,
                            savename=None):
        '''
        Plot an overview of the posterior distribution of the fluxes for 
        each solver. This flux is calculated for the fluxrange specfied, 
        using each set of parameters from the solver's posterior 
        distributions.
        
        Positional arguments
        solvers    --- BXA solver or list of solvers; the solvers can be used 
                       after solver.run() has completed

        Keyword arguments
        models     --- list of functions; the functions should contain the 
                       XSPEC model definitions for each of the models (in 
                       order matching the list of solvers). This approach is 
                       necessary to access the XSPEC data for each of the 
                       models in turn
        fluxrange  --- tuple or list of length 2; start and stop for energy 
                       range, in keV, over which to calculate the flux (default
                       is 0.2-2.0 keV)
        npost      --- int; number of sets of parameters (single model instances)
                       to draw from the posterior distribution (default is all)
        color      --- string or list of strings; color ID(s) matching 
                       Matplotlib's name colours
        quantile   --- float; quantile to be plotted as vertical line in the
                       distribution, on either side of the mean. Value applies to
                       a one-tailed distribution (default is 0.341 = 1 sigma)
        printq     --- boolean; if True, print the mean flux and the uncertainties, 
                       as specified by the quantiles, to screen (default is False)
        return_val --- boolean; if True, the mean flux and uncertainties will be
                       returned as a list (default is False)        
        ymax       --- float; cut-off level for y-axis of plot
        savename   --- string; filename to store results (default is None)
        '''
        self._plot_posterior_statistic(solvers,
                                       models=models,
                                       stat='flux',
                                       nsample=npost,
                                       fluxrange=fluxrange,
                                       colors=colors,
                                       q=quantile,
                                       printq=printq,
                                       ymax=ymax,
                                       savename=savename)
        if return_val:
            return self.posterior_flux_unc

    def plot_posterior_mc_likelihood(self,solvers,
                                     models=None,
                                     nsample=100,
                                     idsp=None,colors='k',
                                     ymax=None,
                                     savename=None):
        '''
        Simulate data with XSPEC's fakeit, based on the best-fit model. Create an
        overview of fit statistics (posterior predictive check).
        
        Positional arguments
        solvers  --- BXA solver or list of solvers; the solvers can be used 
                     after solver.run() has completed

        Keyword arguments
        models   --- list of functions; the functions should contain the 
                     XSPEC model definitions for each of the models (in 
                     order matching the list of solvers). This approach is 
                     necessary to access the XSPEC data for each of the 
                     models in turn.
        nsample  --- int; number of MC iterations (default=100)
        idsp     --- int; group ID for loaded spectrum in XSPEC (default is to
                     use all loaded spectra)
        colors   --- string or list of strings; color ID(s) matching 
                     Matplotlib's name colours
        ymax     --- float; upper limit for the y-axis of the plot(s)
                     (default is None -> automatic)
        savename --- string; name for the file to be saved (default is None)
        '''
        self._plot_posterior_statistic(solvers,
                                       models=models,
                                       stat='mc_likelihood',
                                       nsample=nsample,
                                       idsp=idsp,colors=colors,
                                       ymax=ymax,
                                       savename=savename)

    def _plot_posterior_statistic(self,solvers,
                                       models=None,
                                       stat='flux',
                                       nsample=100,
                                       fluxrange=(0.2,2.0),
                                       idsp=None,colors='k',
                                       q=0.341,
                                       printq=False,
                                       ymax=None,
                                       savename=None):
        '''
        Plot an overview of a single statistic for a model, as specified
        by the 'stat' kwarg. The supported options are 'flux' and 
        'mc_likelihood'. This is a plotting method that is used for 
        methods that require the same format of plot.
        
        Positional arguments
        solvers    --- BXA solver or list of solvers; the solvers can be used 
                       after solver.run() has completed

        Keyword arguments
        models     --- list of functions; the functions should contain the 
                       XSPEC model definitions for each of the models (in 
                       order matching the list of solvers). This approach is 
                       necessary to access the XSPEC data for each of the 
                       models in turn
        stat       --- string; 'flux' (default) or 'mc_likelihood'. This sets
                       the method to be called to create the dataset to be
                       plotted
        nsample    --- int; number of objects to draw from the posterior
                       distributions for the fluxes or the  number of MC
                       iterations used to calculated the likelihood distribution.
        fluxrange  --- tuple or list of length 2; start and stop for energy range
                       over which to calculate the flux (default is 0.2-2.0 keV)
        idsp       --- int; group ID for loaded spectrum in XSPEC (default is to
                       use all loaded spectra)
        colors     --- string or list of strings; color ID(s) matching 
                       Matplotlib's name colours
        q          --- float; quantile to be plotted as vertical line in the
                       distribution, on either side of the mean. Value applies to
                       a one-tailed distribution (default is 0.341 = 1 sigma)
        printq     --- boolean; if True, print the mean statistic and the 
                       uncertainties, as specified by the quantiles, to screen
        ymax       --- float; upper limit for the y-axis of the plot(s)
                       (default is None -> automatic)
        savename   --- string; filename to store results (default is None)
        '''
        # Check input data
        if type(solvers) is not list:
            solvers = [solvers]
        if models is not None and type(models) is not list:
            models = [models]
        if len(solvers)>1 and models is None:
            self._print_model_active_warning()
        # set up figure
        fig,axs = plt.subplots(1,len(solvers),figsize=(8*len(solvers),8))
        # define colors
        if type(colors) is not list:
            colors = [colors]
        if len(colors)<len(solvers):
            for jj in range(len(solvers)-len(colors)):
                colors.append(colors[-1])
        # loop over the models and create a predictive plot for each
        if type(axs) is not np.ndarray:
            axs = (axs,)
        for ii,s in enumerate(solvers):
            # re-activate model and point solver to new instance
            if models is not None:
                assert len(models)==len(solvers)
                mname = self._activate_models_for_solver(s,models[ii])
            else:
                mname = None
            if stat == 'flux':
                self.posterior_flux_unc = [] # define for first use or clear for new use
                # plot the flux distributions based on the posteriors
                self._posterior_flux_single_model(axs[ii],s,
                                                  npost=nsample,
                                                  fluxrange=fluxrange,
                                                  color=colors[ii],
                                                  q=q,printq=printq)
            elif stat == 'mc_likelihood':
                # plot the log-L distributions based on MC data
                self._posterior_mc_L_single_model(axs[ii],s,
                                                  model_name=mname,
                                                  nsample=nsample,
                                                  idsp=idsp,
                                                  color=colors[ii])
            # label models
            m = s.transformations[0]['model'].expression
            fsize = np.minimum(22,int(24/len(m) * 24))
            axs[ii].set_title(f' Model: {m}',loc='left',pad=15,
                                 fontsize=fsize,fontweight='bold')
            # settings for subplots other than the left-most
            if ii!=0:
                axs[ii].set_yticklabels([])
                axs[ii].set_ylabel('')
        # final plot settings
        plt.subplots_adjust(wspace=0.03)
        ymn, ymx = np.array([ax.get_ylim() for ax in axs]).T
        if ymax is None:
            ymax = np.amax(ymx)*1.05
        for ax in axs:
            ax.set_ylim((0,ymax))
        axs[0].legend(loc='best',fontsize=18).set_zorder(101)
        # show and possibly store plot
        if savename:
            plt.tight_layout()
            plt.savefig(savename)
        else:
            plt.show()
    
    def _posterior_flux_single_model(self,ax,solver,
                                     npost=-1,
                                     fluxrange=(0.2,2.0),
                                     color='k',
                                     q=0.341,printq=False):
        '''
        Plot an overview of the posterior distribution of the fluxes for 
        a single solver. This flux is calculated for the specified flux
        range.
        
        For an overview of the parameters, see plot_posterior_flux().
        '''
        if npost!=-1 and npost<10:
            print('npost must be >=10; using npost=10')
            npost=10
        # calculate flux for each set of parameters in the solver's posteriors
        d = []
        frange = f'{fluxrange[0]:.2},{fluxrange[1]:.2f}'
        for row in solver.posterior[:npost]:
            bxa.solver.set_parameters(values=row,transformations=solver.transformations)
            xspec.AllModels.calcFlux(frange)
            d += [xspec.AllData(1).flux[0]*1e12] # in units of 10^12 erg cm^-2 s^-1
        # plot the data
        c,b = np.histogram(d,bins=np.minimum(int(len(d)/10),20),
                           density=True)
        ax.stairs(c,b,fill=True,color=color,alpha=0.3)
        yl = ax.get_ylim()
        # mark mean and q-quantile limits
        ax.vlines(np.mean(d),0,yl[1]*1e4,
                  colors=color,ls='-',lw=3,
                  zorder=100,label='Mean')
        q_mean = np.count_nonzero(d<np.mean(d))/len(d)        
        q_low  = np.quantile(d,np.maximum(0,q_mean-q))
        q_high = np.quantile(d,np.minimum(q_mean+q,1))
        qstr = f'{(2*q)*100:.1f}%'
        ax.vlines(q_low,0,yl[1]*1e4,
                  colors=color,ls='--',lw=3,zorder=100,label=qstr)
        ax.vlines(q_high,0,yl[1]*1e4,
                  colors=color,ls='--',lw=3,zorder=100)
        mname = solver.transformations[1]['model'].expression
        if printq:
            print(f'For model {mname}:')
            print(f'Mean={np.mean(d):.3f} (+){q_high:.3f} (-){q_low:.3f} (10^12 erg cm^-2 s^-1)')
            print(f'With uncertainties estimated for +/- {q*100:.1f}%\n')
        self.posterior_flux_unc += [[mname,fluxrange,np.mean(d),q_high,q_low]]
        # plot details
        lblkw   = dict( (('fontsize',20),('fontweight','bold')) )
        rngstr  = f'Flux {fluxrange[0]:.1f}-{fluxrange[1]:.1f} keV'
        unitstr = r' ($10^{12}$ erg cm$^{-2}$ s$^{-1}$)'
        ax.set_xlabel(rngstr+unitstr,**lblkw)
        ax.set_ylabel('Probability Density',**lblkw)
        ax.set_ylim(yl)
        ax.tick_params(top=True, right=True, which='both')
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.tick_params(axis='both', which='major',
                       direction='in', length=6, width=1.5)
        ax.tick_params(axis='both', which='minor',
                       direction='in', length=3, width=1.2)
        plt.setp(ax.get_xticklabels(), fontsize=15)
        plt.setp(ax.get_yticklabels(), fontsize=15)
                           

    def _posterior_mc_L_single_model(self,ax,solver,
                                     model_name=None,
                                     nsample=100, idsp=None,
                                     color='k'):
        '''
        Simulate data with XSPEC's fakeit, based on a best-fit model. Create an
        overview of fit statistics (posterior predictive check).
        
        Positional arguments
        ax      --- Matplotlib Axes object; the Axes object that will
                    contain the plot
        solver  --- BXA solver; after solver.run() has completed

        Keyword arguments
        nsample --- int; number of MC iterations (default=100)
        idsp    --- int; group ID for loaded spectrum in XSPEC (default is to
                    use all loaded spectra)
        color   --- string or tuple; color ID matching Matplotlib's color
                    definitions
        '''
        # simulate data
        fitstat_best, fitstat = self._create_fake_spectra(solver,
                                                          model_name=model_name,
                                                          nsample=nsample,
                                                          idsp=idsp)
        # plot results
        if nsample<10:
            print('nsample must be >=10; using nsample=10')
            nsample=10
        c,b = np.histogram(fitstat,bins=np.minimum(int(nsample/10),20),
                           density=True)
        ax.stairs(c,b,fill=True,color=color,alpha=0.3)
        yl = ax.get_ylim()
        ax.vlines(fitstat_best,0,1,color=color,ls='--',lw=3,label='Best fit')
        # plot details
        lblkw = dict( (('fontsize',20),('fontweight','bold')) )
        ax.set_xlabel('-ln(L)',**lblkw)
        ax.set_ylabel('Probability Density',**lblkw)
        ax.set_ylim(yl)
        ax.tick_params(top=True, right=True, which='both')
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.tick_params(axis='both', which='major',
                       direction='in', length=6, width=1.5)
        ax.tick_params(axis='both', which='minor',
                       direction='in', length=3, width=1.2)
        plt.setp(ax.get_xticklabels(), fontsize=15)
        plt.setp(ax.get_yticklabels(), fontsize=15)
        
        
    
    ###################################
    #                                 #    
    #   (7) Checks on Bayes Factors   #
    #                                 #
    ###################################

    def _run_bxa_on_multiple_spectra(self,solver,model,filelist,
                                     bxa_dir,spec_prefix='',
                                     npoints=200):
        '''
        Run a single solver for different datasets. The results will
        be stored in the bxa_dir directory, with a different subdirectory
        for each run
        
        Positional arguments:
        solver      --- BXA solver
        model       --- function to activate XSPEC model
        filelist    --- nested list of filenames for X-ray spectra
                        each sublist should contain all files to be 
                        loaded at once (grouping of data will match 
                        the grouping of the currently loaded data)
        bxa_dir     --- string; name of the parent output directory
                        for the BXA fitting results
        
        Keyword arguments:
        spec_prefix --- string; identifying prefix (e.g. the model name) for
                        files containing the simulated spectra
        npoints     --- int; number of live points to be used in BXA fitting
        
        Returns:
        logz        --- list of floats; the logZ values for the BXA runs
        '''
        # check directory exists to store multiple versions of BXA output
        if not os.path.exists(bxa_dir):
            os.makedirs(bxa_dir)
        # store current data format
        orig_data = self._find_loaded_data_format()    
        # re-activate the model and point solver to new instance
        mod,mname = model()
        for t in solver.transformations:
            t['model'] = mod
        # a) check format of currently loaded data (the faked spectra should match this)
        solver_orig_basename = solver.outputfiles_basename
        nG = xspec.AllData.nGroups
        nS = xspec.AllData.nSpectra
        if nG==nS:
            # there is one file per group
            load_format = [f'{g+1}:{g+1}' for g in range(nG)]
        else:
            # just load everything into a single group
            # (more complicated configurations are currently not possible)
            load_format = ['']*nS
        # b) loop over the fake spectra
        logz = []
        for ii,flist in enumerate(filelist):
            print('#######')
            print(f'Iteration {ii+1} for model {mname}; performing BXA fitting')
            print('#######')
            # load data & ignore the same bins as for the real data
            xspec.AllData.clear()
            xspec.AllData(' '.join([f'{fmt} {f}' for fmt,f in zip(load_format,flist)]))
            for jj in range(len(flist)):
                xspec.AllData(jj+1).ignore(orig_data[jj]['ign'])
            # fit fake spectrum with BXA
            solver.outputfiles_basename = os.path.join(bxa_dir,mname+f'_{ii}/')
            solver.run(n_live_points=npoints,resume=True)
            logz += [solver.results['logz']]
        # c) restore solver's basename to original setting
        solver.outputfiles_basename = solver_orig_basename
        # d) restore original data
        splist = [f"{d['dg']}:{d['ind']} {d['sp']}" for d in orig_data]
        xspec.AllData(' '.join(splist))
        xspec.AllData.notice('all')
        xspec.AllData.ignore('bad')
        for ii,d in enumerate(orig_data):
            xspec.AllData(ii+1).ignore(d['ign'])
        
        return logz

    def _run_bayes_factor_test_sim(self,solvers,models,
                                   nsample,spec_prefix,
                                   fakeit_model=0,
                                   gen_new_spec=True,
                                   start_from_iter=0,
                                   bxa_dir='test_sim',npoints=400):
        '''
        Create data for use in false positive tests (decision on Bayes factor)
        Simulated spectra will be created using the assumption that the first
        of the two supplied models is correct. BXA fitting will be performed
        on the simulated data, using the first and the second model and the
        evidence for each model will be returned.
        
        Positional arguments:
        solvers         --- list of two BXA solvers
        models          --- list of two functions; the functions should contain the 
                            XSPEC model definitions for each of the models (in 
                            order matching the list of solvers). This approach is 
                            necessary to access the XSPEC data for each of the 
                            models in turn
        nsample         --- int; number of spectra to simulate
        spec_prefix     --- string; identifying prefix (e.g. the model name) for
                            files containing the simulated spectra
        
        Keyword arguments:
        fakeit_model    --- int; index in 'solvers' and 'models' of the model that 
                            will be used as the baseline for the creation of new 
                            spectra using XSpec's fakeit
        gen_new_spec    --- boolean; generate new fake spectra (True). Set to False
                            if the aim is to use existing fake spectra, e.g. to
                            resume a previous run of BXA fitting that was
                            interrupted
        start_from_iter --- int; if previous results are in place but more can be
                            added set this value to the number of iterations
                            completed. The fake spectra for iterations below this
                            value will be kept (so that the BXA results can be
                            reloaded)
        bxa_dir         --- string; name of the directory to store BXA fitting results
        npoints         --- int; number of live points to be used in BXA fitting
        '''
        if gen_new_spec:
            # re-activate first model and point solver to new instance
            assert len(models)==len(solvers)
            mod,mname = models[fakeit_model]()
            for t in solvers[fakeit_model].transformations:
                t['model'] = mod
            # simulate data based on 1st model
            _,_ = self._create_fake_spectra(solvers[fakeit_model],mname,
                                            nsample=nsample,store_spec=True,
                                            start_from_iter=start_from_iter,
                                            spec_prefix=spec_prefix,
                                            savedir='fakeit_spectra')
        # create a list of all files in 'savedir', to be loaded for BXA fitting
        filelist = []
        assert os.path.exists('fakeit_spectra'), 'No fake spectra exist, please set kwarg gen_new_spec=True'
        dirlist = os.listdir('fakeit_spectra')
        dirlist = natsorted(dirlist) # lexicographical sorting does not match the fakeit naming settings
        for ii in range(nsample):
            flist = []
            for jj in range(xspec.AllData.nSpectra):
                for kk,f in enumerate(dirlist):
                    if f.startswith(f'{spec_prefix}_{ii}') and f.endswith(f'{jj}.pha'):
                        flist += [os.path.join('fakeit_spectra',dirlist.pop(kk))]
                        break
            filelist += [flist]
        # generate logz values for the first model
        logz1 = self._run_bxa_on_multiple_spectra(solvers[0],models[0],filelist,
                     	                          bxa_dir=bxa_dir,
                          	                      spec_prefix=spec_prefix,
                              	                  npoints=npoints)
        # generate logz values for the second model
        logz2 = self._run_bxa_on_multiple_spectra(solvers[1],models[1],filelist,
                 		                          bxa_dir=bxa_dir,
                          	                      spec_prefix=spec_prefix,
                               	                  npoints=npoints)

        return logz1,logz2

    def plot_false_positive_test(self,
                                 existing_data=False,
                                 datadir='test_type1',
                                 solvers=None,models=None,
                                 nsample=None,spec_prefix=None,
                                 gen_new_spec=True,
                                 start_from_iter=0,
                                 mnames=None,
                                 npoints=400,
                                 quantile=0.99,
                                 color='g',
                                 filter_logz=True,
                                 print_removed=False,
                                 savename=None):
        '''
        Create plot showing the probability density of the Bayes
        factors for models 1 & 2 (log(Z2/Z1)), under the assumption
        that model 1 is correct.
        
        For description of arguments, see _plot_bayes_factor_test()
        '''
        qval, logz = self._plot_bayes_factor_test(existing_data=existing_data,
                                                  datadir=datadir,
                                                  solvers=solvers,
                                                  nsample=nsample,
                                                  spec_prefix=spec_prefix,
                                                  gen_new_spec=gen_new_spec,
                                                  fakeit_model=0,
                                                  start_from_iter=start_from_iter,
                                                  npoints=npoints,
                                                  mnames=mnames,
                                                  quantile=quantile,
                                                  color=color,
                                                  filter_logz=filter_logz,
                                                  print_removed=print_removed,
                                                  savename=savename)
       
        return qval,logz

    def plot_false_negative_test(self,
                                 existing_data=False,
                                 datadir='test_type2',
                                 solvers=None,models=None,
                                 nsample=None,spec_prefix=None,
                                 gen_new_spec=True,
                                 start_from_iter=0,
                                 mnames=None,
                                 npoints=400,
                                 quantile=0.99,
                                 color='r',
                                 filter_logz=True,
                                 print_removed=False,
                                 savename=None):
        '''
        Create plot showing the probability density of the Bayes
        factors for models 1 & 2 (log(Z2/Z1)), under the assumption
        that model 2 is correct.
        
        For description of arguments, see _plot_bayes_factor_test()
        '''
        qval, logz = self._plot_bayes_factor_test(existing_data=existing_data,
                                                  datadir=datadir,
                                                  solvers=solvers,
                                                  nsample=nsample,
                                                  spec_prefix=spec_prefix,
                                                  fakeit_model=1,
                                                  gen_new_spec=gen_new_spec,
                                                  start_from_iter=start_from_iter,
                                                  mnames=mnames,
                                                  npoints=npoints,
                                                  quantile=quantile,
                                                  color=color,
                                                  filter_logz=filter_logz,
                                                  print_removed=print_removed,
                                                  savename=savename)
                                                  
        return qval,logz

    def _plot_bayes_factor_test(self,
                                existing_data=False,
                                datadir=None,
                                solvers=None,
                                nsample=None,
                                spec_prefix=None,
                                fakeit_model=0,
                                gen_new_spec=None,
                                start_from_iter=0,
                                mnames=None,
                                npoints=400,
                                quantile=0.99,
                                color='g',
                                filter_logz=True,
                                print_removed=False,
                                savename=None):
        '''
        Keyword arguments:
        existing_data   --- boolean; load existing dataset (True) or create new
                            simulated data (False)
        datadir         --- string; directory where previous BXA fitting results are
                            stored
        solvers         --- list of two BXA solvers
        mnames          --- list of two strings; the names of the two models. These
                            should be the names used to store the models (typically,
                            this is the name of the model in XSpec). This only needs
                            to be specified if existing_data is set to True
        nsample         --- int; number of spectra to simulate
        spec_prefix     --- string; identifying prefix (e.g. the model name) for
                            files containing the simulated spectra
        fakeit_model    --- int; index in 'solvers' and 'models' of the model that 
                            will be used as the baseline for the creation of new 
                            spectra using XSpec's fakeit
        gen_new_spec    --- boolean; generate new fake spectra (True). Set to False
                            if the aim is to use existing fake spectra, e.g. to
                            resume a previous run of BXA fitting that was interrupted
        start_from_iter --- int; if previous results are in place but more can be
                            added set this value to the number of iterations
                            completed. The fake spectra for iterations below this
                            value will be kept (so that the BXA results can be
                            reloaded). nsample new spectra will be created and
                            fitted, after which _all_ BXA results in the datadir
                            will be loaded (i.e. including the pre-existing ones)
        npoints         --- int; number of live points to be used in BXA fitting
        quantile        --- float; limit to mark in the plot, setting a cut-off
                            criterion for the distribution in log(z1/z2). Default
                            is 0.99
        color           --- matplotlib.pyplot colour; sets colour of the histogram
        filter_logz     --- boolean; filter out clearly erroneous results from the
                            logZ results (True). This option is included for the
                            cases where during prolongend runs (high 'nsample') some
                            of the BXA fitting may fail. Filter settings exclude any
                            logZ that is smaller than 1e-6. Default is True
        print_removed   --- boolean; only applies when filter_logz==True. If set to
                            True, the method will print the directory names (solver
                            outputfiles_basename) for those entries that were
                            filtered out for containing erroneous logZ values.
                            Default is False
        savename        --- string; filename for saving the plot (optional)
                           
        Returns:
        qval            --- The Bayes factor associated with the specified quantile
                            of the distribution
        logz            --- 2D list; contains two lists of logZ values, belonging to
                            model 1 & 2, respectively.
        '''
        if existing_data:
            if not os.path.exists(datadir):
                wrn_str = '''
                Using standard output directory "test_type1" to locate previous
                results. If this directory is not correct, please specify kwarg
                "datadir"; otherwise, if no previous fits exist, please run with
                existing_data=False to generate a simulated dataset.
                '''
                print(wrn_str)
                return
            if mnames is None:
                print('If loading existing data, please specify the model names')
                return
            m1name,m2name = mnames
            logz1, logz2 = [], []
            fitd1, fitd2 = [], []
            for d in os.listdir(datadir):
                if d.startswith(m1name):
                    fitd1 += [d]
                    logz1 += [json.load(open(f'{datadir}/{d}/info/results.json'))['logz']]
                elif d.startswith(m2name):
                    fitd2 += [d]
                    logz2 += [json.load(open(f'{datadir}/{d}/info/results.json'))['logz']]
            nsample = len(logz1)
        else:
            # verify required variables are defined
            for var in (solvers,models,nsample,spec_prefix):
                if var is None:
                    print('Please specify the following kwargs to run BXA fitting:')
                    print(' solvers, models, nsample, and spec_prefix')
                    return
            # create new simulated spectra & perform BXA fitting
            logz1,logz2 = self._run_bayes_factor_test_sim(solvers,models,
                                                          nsample,spec_prefix,
                                                          fakeit_model=fakeit_model,
                                                          gen_new_spec=gen_new_spec,
                                                          start_from_iter=start_from_iter,
                                                          bxa_dir=datadir,
                                                          npoints=npoints)
            m1name = solvers[0].transformations[0]['model'].name
            m2name = solvers[1].transformations[0]['model'].name
        # filter logz if necessary
        if filter_logz:
            if print_removed:
                for mn,fitd,logz in zip((m1name,m2name),(fitd1,fitd2),(logz1,logz2)):
                    print(f'The following entries were problematic for model {mn} and have been removed:')
                    for ii in range(len(fitd)):
                        if abs(logz[ii])<=1e-6:
                            print(fitd.pop(ii))
                    else:
                        print('-- None --')
                    print(f'Total entries used for model {mn} = {len(fitd)}\n')
            logz1 = [lz for lz in logz1 if abs(lz)>1e-6]
            logz2 = [lz for lz in logz2 if abs(lz)>1e-6]

        # create sample of Bayes factors
        bf = [z2-z1 for z1 in logz1 for z2 in logz2]

        # create plot
        fig, axs = plt.subplots(1,2,figsize=(16,8))
        # subplot 1: PDF
        c,b = np.histogram(bf,bins=np.minimum(nsample*nsample,20),
                           density=True)
        axs[0].stairs(c,b,fill=True,color=color,alpha=0.4)
        # subplot 2: quantile
        ctot = np.sum(c)
        c_quant = c.cumsum()/ctot
        axs[1].stairs(np.append(c_quant,1),np.append(b,axs[0].get_xlim()[1]+1),
                       fill=False,linestyle='--',
                       color=color,alpha=0.7,lw=3)
        axs[1].set_xlim(axs[0].get_xlim())
        # identify limit and mark it in both plots
        qval = np.quantile(bf,quantile)
        for ax in axs:
            ylims = ax.get_ylim()
            ax.vlines(qval,*ylims,color='grey',linestyle='--',lw=3)
            ax.set_ylim(ylims)
        # final details
        plt.subplots_adjust(wspace=0.03)
        lblkw = dict( (('fontsize',22),('fontweight','bold')) )
        axs[0].set_ylabel('Probability Density',**lblkw)
        axs[1].yaxis.set_label_position('right')
        axs[1].yaxis.tick_right()
        axs[1].set_ylabel('Quantile',rotation=-90,labelpad=25,**lblkw)
        for ax in axs:
            ax.set_xlabel(r'log(Z$_{{ {} }}$/Z$_{{ {} }}$)'.format(m2name,m1name),**lblkw)
            ax.tick_params(top=True, right=True, left=True, which='both')
            ax.yaxis.set_minor_locator(AutoMinorLocator())
            ax.xaxis.set_minor_locator(AutoMinorLocator())
            ax.tick_params(axis='both', which='major',
                           direction='in', length=6, width=1.5)
            ax.tick_params(axis='both', which='minor',
                           direction='in', length=3, width=1.2)
            plt.setp(ax.get_xticklabels(), fontsize=15)
            plt.setp(ax.get_yticklabels(), fontsize=15)
            
        # save plot if necesarry
        if savename:
            plt.tight_layout()
            plt.savefig(savename)
        else:
            plt.show()

        return qval,[logz1,logz2]        



