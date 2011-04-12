#!/usr/bin/env python

from sherpa.all import *
import numpy as np
from sherpa.utils import lgam, sao_fcmp
from sherpa.stats import Cash
import logging

info = logging.getLogger(__name__).info
_log = logging.getLogger("sherpa")
_level = _log.level
_tol = numpy.finfo(numpy.float).eps


__all__=['LimitError', 'MetropolisMH', 'MH', 'Sampler',
         'Walk', 'dmvt', 'ARFSimMetropolisMH', 'PCA1DAdd',
         'SIM1DAdd']

class LimitError(Exception):
    pass

def dmvt(x, mu, sigma, dof, log=True, norm=False):

    if np.min( np.linalg.eigvalsh(sigma))<=0 :
        raise RuntimeError("Error: sigma is not positive definite")
    if np.max( np.abs(sigma-sigma.T))>=1e-9 :
        raise RuntimeError("Error: sigma is not symmetric")

    p = mu.size

    # log density unnormalized
    val = (-0.5*np.log(np.linalg.det(sigma)) - (dof+p)/2.0*
            np.log( dof + np.dot( x-mu, np.dot(
                    np.linalg.inv(sigma), x-mu ) ) ) )

    # log density normalized
    if norm:
        val += (lgam((dof+p)/2.) - lgam(dof/2.) - (p/2.) *
                np.log(np.pi) + (dof/2.) * np.log(dof))

    # density
    if not log:
        val = np.exp(val)

    return val


class Walk(NoNewAttributesAfterInit):

    def __init__(self, sampler=None):
        self._sampler = sampler


    def set_sampler(self, sampler):
        self._sampler = sampler


    def __call__(self, niter, **kwargs):

        if self._sampler is None:
            raise AttributeError("sampler object has not been set, "+
                                 "please use set_sampler()")

        pars, stat = self._sampler.init(**kwargs)

        # setup proposal variables
        npars = len(pars)
        niter = int(niter)
        nelem = niter+1

        proposals = np.zeros((nelem,npars), dtype=np.float)
        proposals[0] = pars.copy()

        stats = np.zeros(nelem, dtype=np.float)
        stats[0] = stat

        acceptflag = np.zeros(nelem, dtype=np.bool)

        # Iterations
        # - no burn in at present
        # - the 0th element of the params array is the input value
        # - we loop until all parameters are within the allowable
        #   range; should there be some check to ensure we are not
        #   rejecting a huge number of proposals, which would indicate
        #   that the limits need increasing or very low s/n data?
        #
        try:
            for ii in xrange(niter):

                jump = ii+1

                current_params = proposals[ii]
                current_stat   = stats[ii]

                # Assume proposal is rejected by default
                proposals[jump] = current_params
                stats[jump]  = current_stat
                #acceptflag[jump] = False

                # Draw a proposal
                proposed_params = self._sampler.draw(current_params)
                proposed_params = np.asarray(proposed_params)
                try:
                    proposed_stat = self._sampler.calc_stat(proposed_params)
                except LimitError:
                    # automatically reject the proposal if outside hard limits
                    self._sampler.reject()
                    continue

                # Accept this proposal?
                if self._sampler.accept(current_params, current_stat,
                                         proposed_params, proposed_stat):

                    proposals[jump] = proposed_params
                    stats[jump] = proposed_stat
                    acceptflag[jump] = True

                else:

                    self._sampler.reject()
        finally:
            self._sampler.tear_down()

        params = proposals.transpose()
        return (stats, acceptflag, params)



class Sampler(NoNewAttributesAfterInit):

    def __init__(self):
        self._opts = get_keyword_defaults(self.init)

    def init(self):
        raise NotImplementedError

    def draw(self, current, **kwargs):
        raise NotImplementedError
        
    def accept(self, current, current_stat, proposal, proposal_stat, **kwargs):
        raise NotImplementedError
    
    def reject(self):
        raise NotImplementedError

    def calc_stat(self, proposed_params):
        raise NotImplementedError

    def tear_down(self):
        raise NotImplementedError


class MH(Sampler):
    """ The Metropolis Hastings Sampler """ 

    def __init__(self, fit, sigma, mu, dof):
        self._df = dof
        self._fit = fit
        self._mu = numpy.array(mu)
        self._sigma = numpy.array(sigma)
        self._thawedparmins = numpy.array(fit.model.thawedparhardmins)
        self._thawedparmaxes = numpy.array(fit.model.thawedparhardmaxes)
        self._oldthawedpars = numpy.array(fit.model.thawedpars)

        # add backwards compatibility with < CIAO 4.2
        if hasattr(fit.model, 'startup'):
            fit.model.startup()
        
        if not isinstance(fit.stat, Cash):
            raise RuntimeError("Fit statistic must be cash, not %s" %
                               fit.stat.name)
        Sampler.__init__(self)


    def _calc_fit_stat(self):
        return -0.5*self._fit.calc_stat()


    def init(self, log=False, inv=False, defaultprior=True, priorshape=False,
             priors=(), originalscale=True, verbose=False,
             scale=1, sigma_m=False):

        if self._sigma is None or self._mu is None:
            raise AttributeError('sigma or mu is None, initialization failed')

        self.prior = np.ones(self._mu.size)
        self.defaultprior = defaultprior
	self.priorshape = np.array(priorshape)
	self.originalscale = np.array(originalscale)
        self.currently_metropolis = False
        self.scale = scale
        self.prior_funcs = priors
        
        if verbose:
            info(str(self.prior_funcs))

	# if not default prior, prior calculated at each iteration
	if not defaultprior:
            if self.priorshape.size != self._mu.size:
                raise RuntimeError(
                    "If not using default prior, must specify a " +
                    "function for the prior on each parameter")
            if self.originalscale.size != self._mu.size:
                raise RuntimeError(
                    "If not using default prior, must specify the " +
                    "scale on which the prior is defined for each parameter")

        self.jacobian = np.zeros(self._mu.size, dtype=bool)
	# jacobian needed if transforming parameter but prior for parameter
        # on original scale
	if not defaultprior:
            # if log transformed but prior on original scale, jacobian
            # for those parameters is needed
            if np.sum( log*self.originalscale ) > 0:
                self.jacobian[ log*self.originalscale ] = True
            if np.sum( inv*self.originalscale ) > 0:
                self.jacobian[ inv*self.originalscale ] = True

	self.log = np.array(log)
	if self.log.size == 1:
            self.log = np.tile(self.log, self._mu.size)

        self.inv = np.array(inv)
	if self.inv.size == 1:
            self.inv = np.tile(self.inv, self._mu.size)

        if np.sum(log*inv) > 0:
            raise RuntimeError(
                "Cannot specify both log and inv transformation for the same " +
                "parameter")
	if verbose:
            info("Running Metropolis-Hastings")

        current = self._mu.copy()
        stat = self._calc_fit_stat()

        # include prior
        stat = self.update(stat, self._mu)

        self.initial_stat = stat


	# using delta method to create proposal distribution on log scale for
        # selected parameters
	if np.sum(self.log) > 0:
		logcovar = self._sigma.copy()
		logcovar[:,self.log]= logcovar[:,self.log]/self._mu[self.log]
		logcovar[self.log]= (logcovar[self.log].T/self._mu[self.log]).T
		self._sigma = np.copy(logcovar)
		self._mu[self.log]=np.log(self._mu[self.log])
		current[self.log]=np.log( current[self.log])

	# using delta method to create proposal distribution on inverse scale
        # for selected parameters
	if np.sum(self.inv) > 0:
		invcovar = self._sigma.copy()
		invcovar[:,self.inv] = invcovar[:,self.inv]/(
                                       -1.0*np.power(self._mu[self.inv],2))
		invcovar[self.inv] = (invcovar[self.inv].T/(
                                      -1.0*np.power(self._mu[self.inv],2))).T
		self._sigma = np.copy(invcovar)
		self._mu[self.inv]=1.0/(self._mu[self.inv])
		current[self.inv]=1.0/( current[self.inv])

	self.rejections=0

        self.sigma_m = sigma_m
	if np.mean(sigma_m) == False:
            self.sigma_m = self._sigma.copy()

        return (current, stat)


    def update(self, stat, mu, init=True):
        """ include prior """
	if not self.defaultprior:
            x = mu.copy()
            if np.sum(self.originalscale) < mu.size:
                for j in xrange(mu.size):
                    if self.log[j]*(1-self.originalscale[j])>0:
                        x[j] = np.log(x[j])
                    if self.inv[j]*(1-self.originalscale[j])>0:
                        x[j] = 1.0 / x[j]

            for ii, func in enumerate(self.prior_funcs):
                if self.priorshape[ii]:
                    self.prior[ii] = func(x[ii])

        # If no prior then
        # 0.0 == np.sum(np.log(np.ones(mu.size)))
        stat += np.sum(np.log(self.prior))

	if np.sum(self.log*self.jacobian) > 0:
            stat += np.sum( np.log( mu[self.log*self.jacobian] ) )
	if np.sum(self.inv*self.jacobian) > 0:
            stat_temp = np.sum(2.0*np.log(np.abs(mu[self.inv*self.jacobian])))
            if init:
		stat += stat_temp
            else:
                stat -= stat_temp
        return stat


    def draw(self, current):
        """Create a new set of parameter values using the t distribution.

        Given the best-guess (mu) and current (current) set of
        parameters, along with the covariance matrix (sigma),
        return a new set of parameters.
        """
        zero_vec = np.zeros_like(self._mu)
        q = np.random.chisquare(self._df, 1)[0]

        proposal = self.mh(self._mu, zero_vec, q)

        return proposal


    def mh(self, mu, zero_vec, q):
	""" MH jumping rule """
        proposal = mu + np.random.multivariate_normal(zero_vec,
                              self._sigma)/ np.sqrt(q/self._df)

        if np.sum(self.log)>0:
            proposal[self.log]=np.exp(proposal[self.log])
        if np.sum(self.inv)>0:
            proposal[self.inv]=1.0/proposal[self.inv]

        return proposal


    def dmvt(self, x, log=True, norm=False):
        return dmvt(x, self._mu, self._sigma, self._df, log, norm)


    def accept_mh(self, current, current_stat, proposal, proposal_stat):
        alpha = np.exp(proposal_stat + self.dmvt(current) -
                       current_stat - self.dmvt(proposal))

        return alpha


    def accept(self, current, current_stat, proposal, proposal_stat, **kwargs):
        """
        Should the proposal be accepted (using the Cash statistic and the
        t distribution)?
        """
        alpha = self.accept_mh(current, current_stat,
                               proposal, proposal_stat)

        u = np.random.uniform(0,1,1)
        return u <= alpha


    def reject(self):
        ### added for test
        self.rejections += 1


    def calc_stat(self, proposed_params):

        # automatic rejection outside hard limits
        mins  = sao_fcmp(proposed_params, self._thawedparmins, _tol)
        maxes = sao_fcmp(self._thawedparmaxes, proposed_params, _tol)
        if -1 in mins or -1 in maxes:
            #print'hard limit exception'
            raise LimitError('Sherpa parameter hard limit exception')

        try:
            # ignore warning from Sherpa about hard limits
            _log.setLevel(50)

            # soft limits are ignored, hard limits rejected.
            # proposed values beyond hard limit default to limit.
            self._fit.model.thawedpars = proposed_params
            _log.setLevel(_level)

            # Calculate statistic on proposal
            proposed_stat = self._calc_fit_stat()

        except:
            # set the model back to original state on exception
            self._fit.model.thawedpars = self._oldthawedpars
            raise

        #putting parameters back on log scale
        if np.sum(self.log)>0:
            proposed_params[self.log] = np.log( proposed_params[self.log] )
        #putting parameters back on inverse scale
        if np.sum(self.inv)>0:
            proposed_params[self.inv] = 1.0/proposed_params[self.inv]

        # include prior
        proposed_stat = self.update(proposed_stat, proposed_params, False)

        return proposed_stat


    def tear_down(self):
        # set the model back to original state
        self._fit.model.thawedpars = self._oldthawedpars
        
        # add backwards compatibility with < CIAO 4.2
        if hasattr(self._fit.model, 'teardown'):
            self._fit.model.teardown()



class MetropolisMH(MH):
    """ The Metropolis Metropolis-Hastings Sampler """ 

    def init(self, log=False, inv=False, defaultprior=True, priorshape=False,
             priors=(), originalscale=True, verbose=False,
             scale=1, sigma_m=False, p_M=.5):

        if verbose:
            info("Running Metropolis and Metropolis-Hastings")

        self.p_M = p_M
        self.accept_func = None
        return MH.init(self, log, inv, defaultprior, priorshape, priors,
                       originalscale, verbose, scale, sigma_m)


    def draw(self, current):
        """Create a new set of parameter values using the t distribution.

        Given the best-guess (mu) and current (current) set of
        parameters, along with the covariance matrix (sigma),
        return a new set of parameters.
        """
        zero_vec = np.zeros_like(self._mu)
        q = np.random.chisquare(self._df, 1)[0]

        u = np.random.uniform(0,1,1)
        proposal = None
        if u <= self.p_M:
            proposal = self.metropolis(current, zero_vec, q)
            self.accept_func = self.accept_metropolis
        else:
            proposal = self.mh(self._mu, zero_vec, q)
            self.accept_func = self.accept_mh

        return proposal


    def metropolis(self, mu, zero_vec, q):
        """ Metropolis Jumping Rule """
        proposal = mu + np.random.multivariate_normal(zero_vec,
                        self.sigma_m*self.scale)/ np.sqrt(q/self._df)

        if np.sum(self.log)>0:
            proposal[self.log]=np.exp(proposal[self.log])
        if np.sum(self.inv)>0:
            proposal[self.inv]=1.0/proposal[self.inv]

        return proposal


    def accept_metropolis(self, current, current_stat, proposal, proposal_stat):
        alpha = np.exp( proposal_stat - current_stat)
        return alpha


    def accept(self, current, current_stat, proposal, proposal_stat, **kwargs):
        """
        Should the proposal be accepted (using the Cash statistic and the
        t distribution)?
        """
        alpha = self.accept_func(current, current_stat, proposal, proposal_stat)
        u = np.random.uniform(0,1,1)
        return u <= alpha


class PCA1DAdd(object):

    def __init__(self, hdus):

        hdu = hdus[1]
        #self.specresp = hdu.data.field('SPECRESP')
        self.bias     = hdu.data.field('BIAS')

        hdu = hdus[2]
        self.component = hdu.data.field('COMPONENT')
        self.fvariance = hdu.data.field('FVARIANCE')
        self.eigenval  = hdu.data.field('EIGENVAL')
        self.eigenvec  = hdu.data.field('EIGENVEC')


    def get_specresp(self, specresp):
        new_arf = specresp + self.bias
        N = len(self.component)
        rr = numpy.random.rand(N, 1)
        tmp = self.eigenvec * self.eigenval[:,numpy.newaxis] * rr
        return new_arf + tmp.sum(axis=0)



class SIM1DAdd(object):

    def __init__(self, hdus):

        hdu = hdus[1]
        #self.specresp = hdu.data.field('SPECRESP')
        self.bias     = hdu.data.field('BIAS')

        hdu = hdus[2]
        self.component = hdu.data.field('COMPONENT')
        self.simcomp = hdu.data.field('SIMCOMP')

    def get_specresp(self, specresp):
        new_arf = specresp + self.bias
        N = len(self.component)
        rr = numpy.random.randint(0,N)
        return new_arf + self.simcomp[rr]


class ARFSimMetropolisMH(MetropolisMH):

    def __init__(self, fit, sigma, mu, dof):
        MetropolisMH.__init__(self, fit, sigma, mu, dof)
        self._arfsrc = {}
        self._arfbkg = {}
        if hasattr(fit.model, 'teardown'):
            fit.model.teardown()
        if hasattr(fit.data, 'datasets'):
            for ii, data in enumerate(fit.data.datasets):
                if not hasattr(data, 'response_ids'):
                    raise TypeError("dataset does not contain an ARF, dataset must be PHA")
                self._arfsrc[ii] = {}
                self._arfbkg[ii] = {}
                for resp_id in data.response_ids:
                    arf, rmf = data.get_response(resp_id)
                    arf.notice(); rmf.notice();
                    self._arfsrc[ii][resp_id] = numpy.array(arf.specresp)
                for bkg_id in data.background_ids:
                    bkg = data.get_background(bkg_id)
                    self._arfbkg[ii][bkg_id] = {}
                    for bkg_resp_id in bkg.response_ids:
                        barf, brmf = bkg.get_response(bkg_resp_id)
                        barf.notice(); brmf.notice();
                        self._arfbkg[ii][bkg_id][bkg_resp_id] = numpy.array(barf.specresp)
        else:
            data = fit.data
            if not hasattr(data, 'response_ids'):
                raise TypeError("dataset does not contain an ARF, dataset must be PHA")
            self._arfsrc[1] = {}
            self._arfbkg[1] = {}
            for resp_id in data.response_ids:
                arf, rmf = data.get_response(resp_id)
                arf.notice(); rmf.notice();
                self._arfsrc[1][resp_id] = numpy.array(arf.specresp)
            for bkg_id in data.background_ids:
                bkg = data.get_background(bkg_id)
                self._arfbkg[1][bkg_id] = {}
                for bkg_resp_id in bkg.response_ids:
                    barf, brmf = bkg.get_response(bkg_resp_id)
                    barf.notice(); brmf.notice();
                    self._arfbkg[1][bkg_id][bkg_resp_id] = numpy.array(barf.specresp)


    def init(self, log=False, inv=False, defaultprior=True, priorshape=False,
             priors=(), originalscale=True, verbose=False,
             scale=1, sigma_m=False, arf=None):
        self.arf = arf
        return MetropolisMH.init(self, log, inv, defaultprior, priorshape,
                                 priors, originalscale, verbose, scale,
                                 sigma_m)

    def draw(self, current):
        fit = self._fit
        if hasattr(fit.data, 'datasets'):
            for ii, data in enumerate(fit.data.datasets):
                if not hasattr(data, 'response_ids'):
                    raise TypeError("dataset does not contain an ARF, dataset must be PHA")
                for resp_id in data.response_ids:
                    arf, rmf = data.get_response(resp_id)
                    arf.notice(); rmf.notice();
                    arf.specresp = self.arf.get_specresp(self._arfsrc[ii][resp_id])
                    data.set_response(arf, rmf, resp_id)
                for bkg_id in data.background_ids:
                    bkg = data.get_background(bkg_id)
                    for bkg_resp_id in bkg.response_ids:
                        barf, brmf = bkg.get_response(bkg_resp_id)
                        barf.notice(); brmf.notice();
                        barf.specresp = self.arf.get_specresp(self._arfbkg[ii][bkg_id][bkg_resp_id])
                        bkg.set_response(barf, brmf, bkg_resp_id)
        else:
            data = fit.data
            if not hasattr(data, 'response_ids'):
                raise TypeError("dataset does not contain an ARF, dataset must be PHA")
            for resp_id in data.response_ids:
                arf, rmf = data.get_response(resp_id)
                arf.notice(); rmf.notice();
                arf.specresp = self.arf.get_specresp(self._arfsrc[1][resp_id])
                data.set_response(arf, rmf, resp_id)
            for bkg_id in data.background_ids:
                bkg = data.get_background(bkg_id)
                for bkg_resp_id in bkg.response_ids:
                    barf, brmf = bkg.get_response(bkg_resp_id)
                    barf.notice(); brmf.notice();
                    barf.specresp = self.arf.get_specresp(self._arfbkg[1][bkg_id][bkg_resp_id])
                    bkg.set_response(barf, brmf, bkg_resp_id)
        return MetropolisMH.draw(self, current)


    def tear_down(self):
        MetropolisMH.tear_down(self)
        fit = self._fit
        if hasattr(fit.data, 'datasets'):
            for ii, data in enumerate(fit.data.datasets):
                if not hasattr(data, 'response_ids'):
                    raise TypeError("dataset does not contain an ARF, dataset must be PHA")
                for resp_id in data.response_ids:
                    arf, rmf = data.get_response(resp_id)
                    arf.notice(); rmf.notice();
                    arf.specresp = self._arfsrc[ii][resp_id]
                    data.set_response(arf, rmf, resp_id)
                for bkg_id in data.background_ids:
                    bkg = data.get_background(bkg_id)
                    for bkg_resp_id in bkg.response_ids:
                        barf, brmf = bkg.get_response(bkg_resp_id)
                        barf.notice(); brmf.notice();
                        barf.specresp = self._arfbkg[ii][bkg_id][bkg_resp_id]
                        bkg.set_response(barf, brmf, bkg_resp_id)
        else:
            data = fit.data
            if not hasattr(data, 'response_ids'):
                raise TypeError("dataset does not contain an ARF, dataset must be PHA")
            for resp_id in data.response_ids:
                arf, rmf = data.get_response(resp_id)
                arf.notice(); rmf.notice();
                arf.specresp = self._arfsrc[1][resp_id]
                data.set_response(arf, rmf, resp_id)
            for bkg_id in data.background_ids:
                bkg = data.get_background(bkg_id)
                for bkg_resp_id in bkg.response_ids:
                    barf, brmf = bkg.get_response(bkg_resp_id)
                    barf.notice(); brmf.notice();
                    barf.specresp = self._arfbkg[1][bkg_id][bkg_resp_id]
                    bkg.set_response(barf, brmf, bkg_resp_id)


# class MHSim(object):

#     def __init__(self, fit, sigma, mu, dof, sptype=MetropolisMH):

#         # initialize a sampling method
#         #sampler = MH(fit, sigma, mu, dof)
#         sampler = sptype(fit, sigma, mu, dof)

#         # contruct the Metropolis-Hastings instance with MH Sampler + Walk
#         self._walk = Walk(sampler)


#     def __call__(self, niter=1e3, **kwargs):
#         # run simulation
#         stats, accept, params = self._walk(niter, **kwargs)
#         return (stats, accept, params)



# class MHEstError(object):

#     @staticmethod
#     def _get_error(vals, nbins=50):

#         (y, x) = np.histogram(vals, bins=nbins, new=True)
#         xlo = x[:-1]
#         xhi = x[1:]

#         d = Data1DInt('', xlo, xhi, y)
#         m = Gauss1D('g1')
#         m.integrate=False
#         m.guess(*d.to_guess())

#         f = Fit(d, m)
#         r = f.fit()

#         return m.fwhm.val/2.3548200450309493  # F = sqrt(8*log(2))*sigma


#     def __init__(self, fit):
#         self.__model = fit.model
#         self.__mh = MHSim(fit)


#     def __call__(self, nbins=50, niter=1e3, normalize=True, **kwargs):

#         # run simulation
#         stats, accept, params = self.__mh(niter, normalize, **kwargs)

#         errs = [self._get_error(param,nbins) for param in params]

#         vals = self.__model.thawedpars
#         names = [par.fullname for par in self.__model.pars if not par.frozen]

#         s = ""
#         s += "%s %g-sigma (%2g%%) bounds:" % ("mh", 1, 68.2689)

#         hfmt = '\n   %-12s %12s %12s %12s'
#         s += hfmt % ('Param', 'Best-Fit', 'Lower Bound', 'Upper Bound')
#         s += hfmt % ('-'*5, '-'*8, '-'*11, '-'*11)

#         for name, val, err in zip(names, vals, errs):
#             s += '\n   %-12s %12g ' % (name, val)
#             s += '%12g ' % -err
#             s += '%12g'  % err

#         return s
