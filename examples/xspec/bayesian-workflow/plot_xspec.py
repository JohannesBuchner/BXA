#
# Class to support PyXspec usage
#
# David Homan 10.08.2022
#

import xspec
import numpy as np

from itertools import compress

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FormatStrFormatter
plt.rc('font', family='serif')


class PlotXspec:
    '''
    Provides basic plotting and inspection functions when using PyXspec.
    ---
    The following public methods are defined:
    
    first_look:
    A quick first look at the data
    
    plot_model_and_data:
    Plot the data as well as the currently active model
    
    plot_chisq_contours:
    Plot 2D steppar results, including several chi-squared contours
    
    calc_error_from_1Dchisq:
    Plot 1D steppar results and estimate a single parameter's uncertainty
    based on a specified chi-squared value
   
    print_model_results
    Print fitting results to screen
    
    print errors
    Calculate errors on model parameters (for a specified chi-squared
    value) and print to screen
    '''
    
    def __init__(self):
        return None


    #####################################
    #                                   #
    #      (0) Helper Functions         #
    #                                   #
    #####################################

    def _get_xspec_data(self,model=True,plottype='folded',
                        idsp=1,idmd=1,model_name=None,
                        backgrnd=False,
                        rebinsig=None,rebinbnum=None):
        '''
        Get data from XSPEC plot
        
        Keyword arguments:
        model      ---  boolean; True if model is included in xspec
                        plot (default is True)
        plottype   ---  string; 'folded' or 'unfolded' setting the main
                        plot type (and units of the y-axis)
        idsp       ---  int; ID of spectrum to plot
                        (in plotGroup; default is 1)
        idmd       ---  int; ID of model data group to include in plot 
                        (in AllModels; default is 1)
        model_name ---  string or list of strings; named models to
                        include in plot. This is of particular use
                        when there are multiple named models that
                        contribute to the total model (i.e. when 
                        there are multiple sources defined in XSpec
                        for the same spectrum). The data for the 
                        models will be returned under 'mc'. Default 
                        is None; in this case the method will check
                        for additive model components
        backgrnd   ---  boolean; return background data (note: this
                        is always in units of counts/s/keV, regardless
                        of plttype)
        rebinsig   ---  int; minimum sigma per bin (plotting only)
        rebinbnum  ---  int; maximum number of bins to combine when
                        rebinning using rebinsig (plotting only)
                         
        Returns:
        x   ---  list of floats; energy bins
        y   ---  list of floats; counts/flux
        xe  ---  list of floats; width of bins
        ye  ---  list of floats; error on counts/flux
        pm  ---  list of floats; model values (if model==True)
        rs  ---  NumPy array of floats; residuals (if model==True)
        rt  ---  NumPy array of floats; error-normalised residuals 
                                        (if model==True)
        mc  ---  list of lists of floats; model component values
                                         (if model==True)
        bg  ---  list of floats; counts/flux of the background
                                 (if backgrnd==True)
        '''
        # Initial setup and xspec plot
        xspec.Plot.xAxis = "keV"
        if rebinsig:
            assert rebinbnum is not None
            xspec.Plot.setRebin(minSig=rebinsig,
                                maxBins=rebinbnum,
                                groupNum=-1)
        else:
            xspec.Plot.setRebin(minSig=0,maxBins=-1,groupNum=-1)
        if plottype == 'folded':
            plttype = 'data'
        elif plottype == 'counts':
            plttype = 'counts'
        elif plottype == 'unfolded':
            plttype = 'euf'
        else: raise ValueError
        xspec.Plot(plttype)
        # Get coordinates from plot:
        x  = xspec.Plot.x(plotGroup=idsp)
        xe = xspec.Plot.xErr(plotGroup=idsp)
        y  = xspec.Plot.y(plotGroup=idsp)
        ye = xspec.Plot.yErr(plotGroup=idsp)
        results = [x,y,xe,ye]
        if model:
            # get model
            pm = xspec.Plot.model(plotGroup=idsp)
            # calculate residuals
            rs = np.array(y)-np.array(pm)
            ye_corr = [1 if v==0 else v for v in ye] # erroneous errors can occur
            rt = rs/np.array(ye_corr)
            mc = []
            if model_name is not None:
                for m in model_name:
                    mc += [xspec.AllModels(idmd,m).folded(idsp)]
                # the folded fluxes need to be adjusted such
                # that the combined flux matches that of the
                # model flux. This is a stop-gap measure, as
                # we cannot access the plotted fluxes for the
                # named models directly if there are multiple
                # models for the same source
                mtot    = [sum(mx) for mx in zip(*mc)]
                ratio_m = [mf/mcf for mcf,mf in zip(mtot,pm)]
                mc = [[mx*r for mx,r in zip(mcl,ratio_m)] for mcl in mc]
            else:
                # check for additive components in the model
                ## additive components are not included when plotting
                ## 'data' or 'counts' => if not present yet, plot 'euf'
                if xspec.Plot.nAddComps() == 0 and plttype != 'euf':
                    xspec.Plot('euf')
                if xspec.Plot.nAddComps() > 0:
                    xspec.Plot.add = True
                    xspec.Plot(plttype)  # redraw plot to include components
                    for ii in range(xspec.Plot.nAddComps()):
                        mc += [xspec.Plot.addComp(ii+1,plotGroup=idsp)]
            results += [pm,rs,rt,mc]
        if backgrnd:
            xspec.Plot('back')
            bg  = xspec.Plot.y(plotGroup=idsp)
            bge = xspec.Plot.yErr(plotGroup=idsp)
            results += [bg,bge]
        # reset rebinning if necessary
        if rebinsig:
            xspec.Plot.setRebin(minSig=0,maxBins=1,groupNum=-1)
        return results

    def _extrapolate_model_log(self,x,xw,y):
        '''
        Extend the plotted model (y), such that when displayed
        it extends the full range spanned by the data 
        (including the edges of the bins -x-).
        
        NOTE: this functionality is for display only.
        
        Positional arguments:
        x  --- list of floats; xbins
        xw --- list of floats; width of xbins
        y  --- list of floats; model values (belonging to xbins)
        
        Returns:
        x  --- list of floats; extended xbins, expanded at start and end
        y  --- list of floats; extended model values
        '''
        # lower range
        dx = np.log10(x[1]/x[0])
        x  = [ x[0]-xw[0] ] + x
        if y[0]!=0:
            dy = np.log10(y[1]/y[0])
            dlogx = np.log10(x[0]/x[1])
            y  = [ y[0] * np.power(10,dlogx*(dy/dx)) ] + y
        else:
            y  = [ y[0] ] + y
        # upper range
        dx = np.log10(x[-1]/x[-2])
        x  = x + [ x[-1]+xw[-1] ]
        if y[-2]!=0:
            dy = np.log10(y[-1]/y[-2])
            dlogx = np.log10(x[-2]/x[-1])
            y  = y + [ y[-1] * np.power(10,-dlogx*(dy/dx)) ]
        else:
            y  = y + [ y[-1] ]
        return (x,y)

    def _find_loaded_data_format(self):
        '''
        Find the format of the currently loaded XSPEC
        data and return the pertinent values in a list
        of dictionaries, one entry per loaded spectrum.
        
        Positional arguments:
        None
        
        Returns:
        orig_data  list of dicts; load settings for
                   each loaded spectrum
        '''
        orig_data = []
        for ii in range(1,xspec.AllData.nSpectra+1):
            sp  = xspec.AllData(ii).fileName
            try:
                bkg = xspec.AllData(ii).background.fileName
            except:
                bkg = ''
            try:
                rmf = xspec.AllData(ii).response.rmf
            except:
                rmf = ''
            try:
                arf = xspec.AllData(ii).response.arf
            except:
                arf = ''
            exp = xspec.AllData(ii).exposure
            ign = xspec.AllData(ii).ignoredString()
            dg  = xspec.AllData(ii).dataGroup
            ind = xspec.AllData(ii).index
            orig_data.append({'sp':sp,'bkg':bkg,
                              'rmf':rmf,'arf':arf,
                              'exp':exp,'ign':ign,
                              'dg':dg,'ind':ind})
        return orig_data

    def _find_var_params_model(self,model):
        '''
        find the variable parameters of a given XSPEC model
        
        Positional arguments:
        model   --- XSPEC model
        
        Returns:
        cmp_var --- dict; keys are model component names, items are
                    lists of the variable parameters per component
        '''
        cmp_var = {}
        # components of model
        cmp = model.componentNames
        for c in cmp:
            # parameters of components
            params = model.__dict__[c].parameterNames
            isvar  = []
            for p in params:
                if model.__dict__[c].__dict__[p].link == '':
                    isvar += [not model.__dict__[c].__dict__[p].frozen]
                else:
                    isvar += [False]
            # store the variable parameters for the given component
            cmp_var[c] = list(compress(params,isvar))
        return cmp_var

  	
    #################################
    #                               #
    #     (1) Plot the spectra      #
    #                               #
    #################################
        
    def first_look(self,idsp=None,
                   backgrnd=False,
                   ymin=None,ymax=None,
                   xlog=True,ylog=True,
                   rebinsig=None,rebinbnum=10,
                   savename=None):
        '''
        First look at the data (quick and simple).
        
        Keyword arguments:
        idsp              --- int or list of ints; ID of spectra to plot 
                              (in plotGroup; default is all loaded spectra)
        backgrnd          --- boolean; show background data
        ymin              --- float; the lower limit on the y-axis
        ymax              --- float; the top limit on the y-axis
        xlog              --- bool; set logscale on xaxis (default = True)
        ylog              --- bool; set logscale on yaxis (default = True)
        rebinsig          --- int; minimum sigma per bin (plotting only)
        rebinbnum         --- int; maximum number of bins to combine when
                              rebinning (plotting only)
        savename          --- str; name of output file
        
        Returns:
        None
        '''
        colors = ['k']+[plt.cm.Set1(ii) for ii in range(10)]
        if idsp is None:
            idsp = [ii+1 for ii in range(xspec.AllData.nSpectra)]
        elif type(idsp) is int:
            idsp = [idsp]
        fig,ax = plt.subplots(1,figsize=(12,8))
        for ii,idsp_ii in enumerate(idsp):
            # get data
            if backgrnd:
                bins,_,binw,_,rates,ratese = self._get_xspec_data(model=False,
                                                                  idsp=idsp_ii,
                                                                  backgrnd=True,
                                                                  rebinsig=rebinsig,
                                                                  rebinbnum=rebinbnum)
            else:
                bins,rates,binw,ratese = self._get_xspec_data(model=False,
                                                              idsp=idsp_ii,
                                                              rebinsig=rebinsig,
                                                              rebinbnum=rebinbnum)
            # plot using matplotlib
            self._make_spec_plot_main(ax,
                                      bins,rates,binw,ratese,
                                      ymin=ymin,ymax=ymax,
                                      xlog=xlog,ylog=ylog,
                                      clr=colors[ii])
        # save plot if necesarry
        if savename:
            plt.tight_layout()
            plt.savefig(savename)
        else:
            plt.show()

            
    def plot_model_and_data(self,
                            ymin=None,ymax=None,
                            subplot='ratio',plottype='folded',
                            idsp=None,idmd=None,model_name=None,
                            msize=3,colors=None,
                            addxminorticks=None,
                            setxminorticks=None,
                            rebinsig=None,rebinbnum=10,
                            extend=False,
                            savename=None):
        '''
        Create a plot of the model, data, and residuals.
        
        Keyword arguments:
        ymin           --- float; the lower limit on the y-axis
        ymax           --- float; the top limit on the y-axis
        subplot        --- string; 'res' or 'ratio', setting the content of
                           the second plot
        plottype       --- string; 'folded' (data), 'unfolded' (euf), or
                           'counts'; setting the main plot type. Default
                           is 'folded' (counts s^-1 keV^-1)
        idsp           --- int or list of ints; ID of spectra to plot 
                           (in plotGroup; default is all loaded spectra)
        idmd           --- int or list of ints; ID of model to plot (in
                           AllModels; default is the models matching the 
                           spectra defined with idsp). Note: the number of
                           models must match the number of spectra to be 
                           plotted.
        model_name     --- string or list of strings; named models to
                           include in plot. This is of particular use
                           when there are multiple named models that
                           contribute to the total model (i.e. when 
                           there are multiple sources defined in XSpec
                           for the same spectrum). The data for the 
                           models will be returned under 'mc'. Default 
                           is None; in this case the method will check
                           for additive model components.
        addxminorticks --- list; additional minor ticks for x-axis
        setxminorticks --- list; explicitly set minor ticks for x-axis
        rebinsig       --- int; minimum sigma per bin (plotting only)
        rebinbnum      --- int; maximum number of bins to combine when
                           rebinning (plotting only)
        msize          --- int; markersize
        colors         --- list of matplotlib colours to use for the plotted
                           spectra (default is None -> automatic)
        extend         --- bool; set to True to extend the plotted 
                           model to the edges of the plot using
                           a simple interpolation method
                           (defaut is False)
        savename       --- string; name of output file (default is None)
        
        Returns:
        None
        '''
        # check input
        if idsp is None:
            idsp = [ii+1 for ii in range(xspec.AllData.nSpectra)]
        elif type(idsp) is int:
            idsp = [idsp]
        if idmd is None:
            idmd = idsp
        elif type(idmd) is int:
            idmd = [idmd]
        assert len(idsp)==len(idmd), 'the number of models must match the number of spectra'
        if model_name is not None and type(model_name) is not list:
            model_name = [model_name]
        # define colors to use
        if colors is None:
            colors  = ['k']+[plt.cm.Set1(ii) for ii in range(len(idsp)-1)]
        if len(idsp)>1:
            mcolors = colors
        else:
            mcolors = ['r']
        # set up figure
        fig = plt.figure(constrained_layout=False,figsize=(15,12))
        gs = fig.add_gridspec(nrows=7, ncols=1, wspace=0, hspace=0)
        ax = fig.add_subplot(gs[0:5, :])
        ax_res = fig.add_subplot(gs[5:, :])
        for ii,idsp_ii in enumerate(idsp):
            # get data from XSPEC plot
            xdata = self._get_xspec_data(idsp=idsp_ii,idmd=idmd[ii],
                                         model_name=model_name,
                                         plottype=plottype,
                                         rebinsig=rebinsig,rebinbnum=rebinbnum)
            bins,rates,binw,ratese,mplot,res,ratio,mplot_cmp = xdata
            # specify data to be used in subplot
            if subplot=='res': 
                sp_data = res
                sp_datae = ratese
            elif subplot=='ratio':
                sp_data = ratio
                sp_datae = np.ones(len(sp_data))
            else: raise ValueError
            # main plot
            self._make_spec_plot_main(ax,
                                      bins,rates,binw,ratese,
                                      mplot=mplot,mplot_cmp=mplot_cmp,
                                      model_name=model_name,
                                      ymin=ymin,ymax=ymax,
                                      xlog=True,ylog=True,
                                      plottype=plottype,msize=msize,
                                      clr=colors[ii],mclr=mcolors[ii],
                                      addxminorticks=addxminorticks,
                                      setxminorticks=setxminorticks,
                                      xlabel=False,
                                      extend=extend)
            # residuals plot
            self._make_spec_plot_residuals(ax_res,
                                           bins,sp_data,binw,sp_datae,
                                           xlog=True,ylog=False,
                                           clr=colors[ii],
                                           subplot=subplot,msize=msize,
                                           addxminorticks=addxminorticks,
                                           setxminorticks=setxminorticks)
        # save plot if necesarry
        if savename:
            plt.tight_layout()
            plt.savefig(savename)
        else:
            plt.show()

    def _make_spec_plot_basic(self,ax,
                              x,y,xerr,yerr,
                              ymin=None,ymax=None,
                              xlog=True,ylog=True,
                              msize=2,clr='k',
                              addxminorticks=None,
                              setxminorticks=None):
        '''
        Create a basic plot of the spectral data,
        including formatting of the axes.
        '''
        # plot data
        ax.errorbar(x,y,xerr=xerr,yerr=yerr,ls='',
                    c=clr,markersize=msize,marker='s')
        # format axes
        ax.grid()
        if xlog:
            ax.set_xscale('log')
        if ylog:
            ax.set_yscale('log')
        # x-range
        ax.set_xlim((np.amin(x)-xerr[0]/2,np.amax(x)+xerr[-1]/2))
        # y-range
        if not ymin:
            ymin = np.amin(y)*2
            if ylog and ymin<0:
                ymin = 1e-2
        if not ymax:
            ymax = np.amax(y)*2
        ax.set_ylim((ymin,ymax))
        # set and format tick labels
        if addxminorticks is not None:
            minticks = list(ax.get_xticks(minor=True)) + list(addxminorticks)
            minticks.sort()
            xmin,xmax = ax.get_xlim()
            minticks = [m for m in minticks if m > xmin and m < xmax]
            ax.set_xticks(minticks,minor=True)
        elif setxminorticks is not None:
            ax.set_xticks(setxminorticks,minor=True)
        plt.setp(ax.get_xticklabels(minor=True), fontsize=13)#, fontweight='bold')
        plt.setp(ax.get_xticklabels(), fontsize=12, fontweight='bold')
        plt.setp(ax.get_yticklabels(), fontsize=12, fontweight='bold')
        ax.tick_params(axis='y', which='minor',
                       direction='out', length=4, width=1.5)

    def _make_spec_plot_main(self,ax,
                             x,y,xerr,yerr,
                             mplot=None,mplot_cmp=None,
                             model_name=None,
                             ymin=None,ymax=None,
                             xlog=True,ylog=True,
                             plottype='folded',
                             msize=2,
                             clr='k',mclr='r',
                             xlabel=True,
                             addxminorticks=None,
                             setxminorticks=None,
                             extend=False):
        '''
        Create spectral plot based on XSPEC data, including model data,
        if available.
        '''
        # generate basic plot
        self._make_spec_plot_basic(ax,x,y,xerr,yerr,
                                   ymin=ymin,ymax=ymax,
                                   xlog=xlog,ylog=ylog,
                                   msize=msize,
                                   clr=clr,
                                   addxminorticks=addxminorticks,
                                   setxminorticks=setxminorticks)
        # plot model
        if mplot is not None:
            if extend:
                x,mplot = self._extrapolate_model_log(x,xerr,mplot)
            e = [v-err for v,err in zip(x,xerr)] + [x[-1]+xerr[-1]]
            ax.stairs(mplot,edges=e,color=mclr,lw=2,label='total')
        # plot model components
        if mplot_cmp is not None:
            if clr==mclr:
                cmpclr = [mclr]*len(mplot_cmp)
            else:
                cmpclr= [plt.cm.Set1(ii+1) for ii in range(len(mplot_cmp))]
            for ii,(cmp,col) in enumerate(zip(mplot_cmp,cmpclr)):
                if extend:
                    x,mplot = self._extrapolate_model_log(bins,binw,cmp)
                if model_name is not None:
                    e = [v-err for v,err in zip(x,xerr)] + [x[-1]+xerr[-1]]
                    ax.stairs(cmp,edges=e,color=col,lw=1.5,ls='-',label=model_name[ii])
                else:
                    ax.plot(x,cmp,c=col,lw=3,ls=':')
        # set axes labels
        if xlabel:
            ax.set_xlabel('Energy (keV)',fontweight='bold',fontsize=20)
        if plottype == 'folded':
            yl = r'Counts s$^{-1}$ keV$^{-1}$'
        elif plottype == 'counts':
            yl = r'Counts keV$^{-1}$'
        elif plottype == 'unfolded':
            yl = 'keV\n'+r'[Photons cm$^{-2}$ s$^{-1}$ keV$^{-1}$]'
        if model_name is not None:
            ax.legend(loc='best',fontsize=15)
        ax.set_ylabel(yl,fontweight='bold',fontsize=20)
        
    def _make_spec_plot_residuals(self,ax,
                                  x,y,xerr,yerr,
                                  xlog=True,ylog=False,
                                  subplot='res',
                                  msize=2,clr='k',
                                  addxminorticks=None,
                                  setxminorticks=None,
                                  zeroline=True):
        '''
        Create spectral plot of the residuals (used in a 
        subplot of the plot_model_and_data() method).
        '''
        # define y-limits
        ymin = np.amin(y) - yerr[np.argmin(y)]
        ymax = np.amax(y) + yerr[np.argmax(y)]
        # generate basic plot
        self._make_spec_plot_basic(ax,x,y,xerr,yerr,
                                   ymin=ymin,ymax=ymax,
                                   xlog=xlog,ylog=ylog,
                                   msize=msize,clr=clr,
                                   addxminorticks=addxminorticks,
                                   setxminorticks=setxminorticks)
        # mark zero
        if zeroline:
            xlim = ax.get_xlim()
            ax.hlines(0,xlim[0],xlim[1],colors='green')
        # set x-label
        ax.set_xlabel('Energy (keV)',fontweight='bold',fontsize=20)
        # set y-label
        if subplot == 'res':
            yl = 'Residuals'
        else:
            yl = 'Residuals\n'+r'($\sigma$-Norm.)'#alised)'
        ax.set_ylabel(yl,fontweight='bold',fontsize=20)
        # set and format ticks
        ax.tick_params(axis='x', which='minor',
                       direction='out', length=5, width=2)
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        ax.xaxis.set_minor_formatter(FormatStrFormatter('%.2f'))


    #####################################
    #                                   #
    # (2) Print XSPEC results to screen #
    #                                   #
    #####################################
        
        
    def print_model_results(self,model_name=['']):
        '''
        Find the model results (incl. the error) and 
        print to screen. This will be done for all active
        models. The format of the output is as follows
        
        parameter_index  model_component  component_parameter  value  estimated_sigma  unit
        
        keyword argument:
        model_name   list of strings; named models. Default is to assume an unnamed model
        
        Returns:
        None
        '''
        nMod = xspec.AllData.nGroups
        for ii in range(nMod):
            for mname in model_name:
                try:
                    mod = xspec.AllModels(ii+1,mname)
                except:
                    print('Could not load model, perhaps named models should be used?')
                    return
                print(f'\nComponents of model {mname} for data group {ii+1}:')
                for cmp in mod.componentNames:
                    stid = mod.startParIndex-1
                    pars = mod.__dict__[cmp].parameterNames
                    for par in pars:
                        ind = mod.__dict__[cmp].__dict__[par]._Parameter__index + stid
                        val = mod.__dict__[cmp].__dict__[par].values[0]
                        sig = mod.__dict__[cmp].__dict__[par].sigma
                        unit = mod.__dict__[cmp].__dict__[par].unit
                        print ('{}{}{}{:.5e} +/- {:.5e} {}'.format(
                                    str(ind).ljust(4),
                                    cmp.ljust(18),
                                    par.ljust(14),
                                    val,
                                    sig,
                                    unit.rjust(6))
                              )
            print('---')
            method = xspec.Fit.statMethod
            stat = xspec.Fit.statistic
            print('Fit statistic: {}'.format(method))
            print('Test statistic: {:5.2f}'.format(stat))
            if method == 'chi':
                dof = xspec.Fit.dof
                print('Reduced chi-squared: {:5.2f}/{} = {:.3}'
                          .format(stat,dof,stat/dof))

    def print_errors(self,chisq,model_name=['']):
        '''
        Print the errors to screen, using the Xspec 
        error routine. The output has the following format:
        
        parameter_index  model_component  component_parameter  value lower_error  upper_error
        
        positional argument:
        chisq      --- float; chi-squared level at which to calculate the errors. This is
                       the argument passed to XSpec's 'error' function
        model_name --- list of strings; named models. Default is to assume an unnamed model
                    
        Returns:
        None
        '''
        # temporarily switch off the printing to CL by XSpec
        xchat = xspec.Xset.chatter, xspec.Xset.logChatter
        xspec.Xset.chatter    = 0
        xspec.Xset.logChatter = 0
        # calculate errors
        nMod = xspec.AllData.nGroups
        for ii in range(nMod):
            for mname in model_name:
                try:
                    mod = xspec.AllModels(ii+1,mname)
                except:
                    print('Could not load model, perhaps named models should be used?')
                    return
                print(f'\nComponents of model {mname} for data group {ii+1}:')
                try:
                    for cmp in mod.componentNames:
                        stid = mod.startParIndex-1
                        pars = mod.__dict__[cmp].parameterNames
                        for par in pars:
                            pind = mod.__dict__[cmp].__dict__[par]._Parameter__index + stid
                            val = mod.__dict__[cmp].__dict__[par].values[0]
                            xspec.Fit.error('{} {}'.format(chisq,pind))
                            ev = list(mod.__dict__[cmp].__dict__[par].error)
                            if ev[0]!=0:
                                ev[0] = val-ev[0]
                                ev[1] = ev[1]-val
                            print('{} {} {} {:.3e} (-){:.3e} (+){:.3e}'.format(
                                            str(pind).ljust(3),
                                            cmp.ljust(10),
                                            par.ljust(10),
                                            val,
                                            ev[0],
                                            ev[1])
                                 )
                except(Exception):
                        print('Unable to calculate errors, perhaps chisq is too high?\n')
                        xspec.Xset.chatter, xspec.Xset.logChatter = xchat
        # set XSpec's outbut levels back to their original values
        xspec.Xset.chatter, xspec.Xset.logChatter = xchat


    #####################################
    #                                   #
    #  (3) Plot XSPEC chi^2 countours   #
    #                                   #
    #####################################

    def plot_chisq_contours(self,levels=[2.3,4.61,9.21],
                            savename=None):
        '''
        Create a plot of the reduced chi-squared over the
        parameter space set in a steppar run.
        
        Keyword arguments:
        levels    --- list of floats; Delta-chisq levels to include in the
                      plot as contours (default is [2.3,4.61,9.21])
        savename  --- string; filename to store results (default is None)
         
        Returns:
        None
        '''
        chisq = xspec.Fit.statistic
        xspec.Plot('contour')
        x, y = np.meshgrid(xspec.Plot.x(), xspec.Plot.y())
        z = xspec.Plot.z()
        fig, ax = plt.subplots(1,figsize=(10,6))
        z_min, z_max = np.array(z).min(), np.array(z).max()
        c = ax.pcolormesh(x, y, z, cmap='RdBu', 
                          vmin=z_min, vmax=z_max,shading='auto')
        fig.colorbar(c, ax=ax)
        labl = xspec.Plot.labels()
        ax.set_xlabel(labl[0],fontsize=16,fontweight='bold')
        ax.set_ylabel(labl[1],fontsize=16,fontweight='bold')
        ax.set_title(labl[2],fontsize=16,fontweight='bold')
        con = [l+chisq for l in levels]
        if np.amin(z) < con[0]:
            ax.contour(x, y, z, levels=con)
        if savename:
            plt.savefig(savename)
        else:
            plt.show()
            
    def calc_error_from_1Dchisq(self,par,level=1,
                                savename=None):
        '''
        Create plot and calculate relevant uncertainties
        based on 1D chi-squared contour
        
        Positional arguments:
        par       --- the model parameter in question
        
        Keyword arguments:
        level     --- float; Delta-chisq level used to calculate the uncertainties
        savename  --- string; filename to store results (default is None)
        
        Returns:
        None
        '''
        xspec.Plot('contour')
        x, y = xspec.Plot.x(), xspec.Plot.y()
        chisq = xspec.Fit.statistic
        val = par.values[0]
        # Plot
        fig, ax = plt.subplots(1,figsize=(10,6))
        ax.plot(x,y,color='k')
        ax.hlines(chisq+level,np.amin(x),np.amax(y),colors='r',
                  label=r'$\Delta\chi^2$='+f'{level}')
        ax.vlines(val,chisq,np.amax(y),color='k',ls=':',
                  label=f'best fit: {par.name}={val:.3f}')
        # Plot details
        labl = xspec.Plot.labels()
        ax.set_xlabel(labl[0],fontsize=16,fontweight='bold')
        ax.set_ylabel(labl[1],fontsize=16,fontweight='bold')
        ax.set_title(labl[2],fontsize=16,fontweight='bold')
        ax.set_xlim((np.amin(x),np.amax(x)))
        ax.set_ylim((np.amin(y),np.amax(y)))
        ax.legend(loc='best',fontsize=18,framealpha=1)
        # Calculate and present the error
        err_low = val - x[:int(len(y)/2)]\
                         [np.argmin(np.abs(np.array(y[:int(len(y)/2)])-chisq-level))]
        err_high = x[int(len(y)/2):]\
                    [np.argmin(np.abs(np.array(y[int(len(y)/2):])-chisq-level))] - val
        print('Resulting uncertainties: {:.5e} (-) {:.5e} (+) {:.5e}'.
                  format(val,err_low,err_high))
        if savename:
            plt.savefig(savename)
        else:
            plt.show()

