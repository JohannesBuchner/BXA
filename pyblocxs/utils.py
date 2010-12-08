#!/usr/bin/env python


from sherpa.astro.ui import *
import numpy as np


def quantile(sorted_array, f):
    """Return the quantile element from sorted_array, where f is [0,1] using linear interpolation.

    Based on the description of the GSL routine
    gsl_stats_quantile_from_sorted_data - e.g.
    http://www.gnu.org/software/gsl/manual/html_node/Median-and-Percentiles.html
    but all errors are my own.

    sorted_array is assumed to be 1D and sorted.
    """
    sorted_array = np.asarray(sorted_array)

    if len(sorted_array.shape) != 1:
        raise RuntimeError, "Error: input array is not 1D"
    n = sorted_array.size

    q = (n-1) * f
    i = np.int(np.floor(q))
    delta = q - i

    return (1.0-delta) * sorted_array[i] + delta * sorted_array[i+1]


def _set_par_vals(parnames, parvals):
	"Sets the paramaters to the given values"

	for (parname,parval) in zip(parnames,parvals):
		set_par(parname, parval)

def dictionary_to_array(d,parnames):
	npars = parnames.size
	niter = d[parnames[1]].size
	out = np.zeros(( niter, npars) )
	for (i,name) in zip( range(npars), parnames):
		out[:,i] = d[name]
	return out

def variance(x):
	""" assumes np.array """
	rows = x.shape[0]
	cols = x.shape[1]
	out = np.zeros((cols,cols))
	for i in range(cols):
		mean_i = np.mean(x[:,i])
		for j in range(cols):
			mean_j = np.mean(x[:,j])
			out[i,j] = ( sum( x[:,i]*x[:,j] ) - rows*mean_i*mean_j )/(rows-1.0)
	return(out)

def projection_ci(id=None):
	if id == None:
		idval = get_default_id()
	else:
		idval = id

	projection(id=idval)
	mode =	np.array( get_proj_results().parvals )
	low = np.array( get_proj_results().parmins )
	hi = np.array( get_proj_results().parmaxes )
	npars = len(hi)
	out = np.zeros((npars,3))
	out[:,0] = mode + low
	out[:,1] = mode
	out[:,2] = mode + hi
	if verbose:
		print 'projection ci'
		hfmt = '%-12s %12s %12s %12s \n'
		s = hfmt % ('Param', 'Best-Fit', 'Lower Bound', 'Upper Bound')
		s += hfmt % ('-'*5, '-'*8, '-'*11, '-'*11)
		for name, val, lower, upper in zip(parnames, out[:,0],
			out[:,1], out[:,2]):
			s += '%-12s %12g ' % (name, val)
			s += '%12g ' % lower
			s += '%12g \n' % upper
		print s
	return out

def analyze_draws(draws,parnames, sigma=1, dict=False, verbose=True, means=False):
	parnames = np.array(parnames)
	npars = parnames.size
	if dict==False:
		d=np.copy(draws)
		draws={}
		draws["iteration"] = np.array(range( d.shape[0]))
		draws["parnames"] = parnames
		for i,par in zip(range(npars),parnames):
			draws[par] = d[:, i+1]
	out = np.zeros( (npars,3) )
	idx = draws["iteration"] > 0
	if sigma==1:
		sigfrac = 0.682689
		percent="68%"
	if sigma==2:
		sigfrac = .95
		percent="95%"
	for i in range(npars):
		parname = parnames[i]
		if parname not in draws["parnames"]:
			raise RuntimeError, "Unknown parameter '%s'" % parname
		x = np.sort(draws[parname][idx])
		out[i,0] = quantile(x, 0.5)
		if means:
			out[i,0] = np.mean(x)
		out[i,1] = quantile(x, (1-sigfrac)/2.0)
		out[i,2] = quantile(x, (1+sigfrac)/2.0)
	if verbose:
		print 'credible '+percent+' interval'
		hfmt = '%-12s %12s %12s %12s \n'
		s = hfmt % ('Param', 'Median', 'Lower Bound', 'Upper Bound')
		if means:
			s = hfmt % ('Param', 'Mean', 'Lower Bound', 'Upper Bound')
		s += hfmt % ('-'*5, '-'*6, '-'*11, '-'*11)
		for name, val, lower, upper in zip(parnames, out[:,0],
			out[:,1], out[:,2]):
				s += '%-12s %12g ' % (name, val)
				s += '%12g ' % lower
				s += '%12g \n' % upper
		print s
	result={}
	for i in range(npars):
		result[parnames[i]]=out[i,]
	return result
	
def covariance_ci(covariance, fits, parnames, sigma=1, verbose=True):
	npars = fits.size
	out = np.zeros( (npars, 3) )
	out[:,0] = fits
	out[:,1] = fits - sigma*np.sqrt( np.diagonal(covariance) )
	out[:,2] = fits + sigma*np.sqrt( np.diagonal(covariance) )
	if sigma==1:
		percent = '68%'
	if sigma==2:
		percent = '95%'
	if verbose:
		print 'covariance '+percent+' ci'
		hfmt = '%-12s %12s %12s %12s \n'
		s = hfmt % ('Param', 'Best-Fit', 'Lower Bound', 'Upper Bound')
		s += hfmt % ('-'*5, '-'*8, '-'*11, '-'*11)
		for name, val, lower, upper in zip(parnames, out[:,0],
			out[:,1], out[:,2]):
			s += '%-12s %12g ' % (name, val)
			s += '%12g ' % lower
			s += '%12g \n' % upper
		print s
	result={}
	for i in range(npars):
		result[parnames[i]]=out[i,[1,2]]
	return result

def print_fits(parnames, mles, medians):
	print 'Parameter Estimates'
	hfmt = '%-12s %12s %12s \n'
	s = hfmt % ('Param','Estimator', 'Estimate')
	s += hfmt % ('-'*5, '-'*9, '-'*8)
	estimator = ['Sherpa', 'MCMC']
	for i in range(parnames.size):
		s += '%-17s %6s %12g \n' % (parnames[i], estimator[0], mles[i])
		s += '%-17s %6s %12g \n' % (' ', estimator[1], medians[i])
	print s

def print_all_cis(sigma, cis, parnames, sim, calc_proj=False, log=False, inv=False ):
	""" assumes dictionaries of confidence intervals stored 
		covar_cis
		mh_ints
		proj_cis
		"""
	for sig in sigma:
		if sig==1:
			percent = '68%'
		if sig==2:
			percent = '95%'
		print percent+' CIs'
		methods=np.array(['Covariance','MCMC'])
		if calc_proj==True:
			methods=np.array(['Covariance','MCMC','Projection'])
		hfmt = '%-17s %12s %12s %12s \n'
		s = hfmt % ('Param', 'Method', 'Lower Bound', 'Upper Bound')
		s += hfmt % ('-'*5, '-'*6, '-'*11, '-'*11)
		for i, name in enumerate(parnames):
			s += '%-17s %12s ' % (name, methods[0])
			s += '%12g ' % cis[0][name]['sigma='+str(sig)][sim,0]
			s += '%12g \n' % cis[0][name]['sigma='+str(sig)][sim,1]
			s += '%-17s %12s ' % (' ', methods[1])
			s += '%12g ' % cis[1][name]['sigma='+str(sig)][sim,0]
			s += '%12g \n' % cis[1][name]['sigma='+str(sig)][sim,1]
			if calc_proj==True:
				s += '%-17s %12s ' % (' ', methods[2])
				s += '%12g ' % cis[2][name]['sigma='+str(sig)][sim,0]
				s += '%12g \n' % cis[2][name]['sigma='+str(sig)][sim,1]
		print s

#if log[i]:
#s += '%-17s %12s ' % (' ', 'Delta')
#s += '%12g ' % delta_cis[name]['sigma='+str(sig)][sim,0]
#s += '%12g \n' % delta_cis[name]['sigma='+str(sig)][sim,1]
		
def proj_ci( id=None,sigma=1, verbose=True):
	if id == None:
		idval = get_default_id()
	else:
		idval = id
	get_proj().sigma = sigma
	proj(id=idval)
	parnames = np.array(get_proj_results().parnames)
	npars = parnames.size
	fits = np.array(get_proj_results().parvals)
	lower = np.array(get_proj_results().parmins)
	upper = np.array(get_proj_results().parmaxes)
	out = np.zeros( (npars, 3) )
	out[:,0] = fits
	out[:,1] = fits + lower
	out[:,2] = fits + upper
	if sigma==1:
		percent = '68%'
	if sigma==2:
		percent = '95%'
	if verbose:
		print 'projection '+percent+' ci'
		hfmt = '%-12s %12s %12s %12s \n'
		s = hfmt % ('Param', 'Best-Fit', 'Lower Bound', 'Upper Bound')
		s += hfmt % ('-'*5, '-'*8, '-'*11, '-'*11)
		for name, val, lower, upper in zip(parnames, out[:,0],
			out[:,1], out[:,2]):
			s += '%-12s %12g ' % (name, val)
			s += '%12g ' % lower
			s += '%12g \n' % upper
		print s
	result={}
	for i in range(npars):
		result[parnames[i]]=out[i,[1,2]]
	return result

def print_coverage( parnames, coverage, sigma, calc_proj=False):
	print 'Coverage Probability'
	methods=np.array(['Covariance','MCMC'])
	if calc_proj==True:
		methods=np.array(['Covariance','MCMC','Projection'])
	s = '%-17s %12s' % ('Param', 'Method')
	for i in sigma:
		if i==1:
			percent = '68%'
		if i==2:
			percent = '95%'
		s+= ' %12s' % percent
		
	s += '\n'
	s +=  '%-17s %12s' % ('-'*5, '-'*6)
	for i in sigma:
		s += ' %12s' % ('-'*11)
		
	s+= '\n'
	for par in parnames:
			s += '%-17s %12s ' % (par, methods[0])
			for sig in range(sigma.size):
				s += '%12g ' % np.round( coverage[par][sig,0],3)
			s += '\n'
			s += '%-17s %12s ' % (' ', methods[1])
			for sig in range(sigma.size):
				s += '%12g ' % np.round( coverage[par][sig,1],3)
			s += '\n'
			if calc_proj==True:
				s += '%-17s %12s ' % (' ', methods[2])
				for sig in range(sigma.size):
					s += '%12g ' % np.round( coverage[par][sig,2],3)
				s += '\n'
	print s

def print_width( parnames, width, sigma, calc_proj=False):
	print 'Mean Width'
	methods=np.array(['Covariance','MCMC'])
	if calc_proj==True:
		methods=np.array(['Covariance','MCMC','Projection'])
	s = '%-17s %12s' % ('Param', 'Method')
	for i in sigma:
		if i==1:
			percent = '68%'
		if i==2:
			percent = '95%'
		s+= ' %12s' % percent
		
	s += '\n'
	s +=  '%-17s %12s' % ('-'*5, '-'*6)
	for i in sigma:
		s += ' %12s' % ('-'*11)
		
	s+= '\n'
	for par in parnames:
			s += '%-17s %12s ' % (par, methods[0])
			for sig in range(sigma.size):
				s += '%12g ' % width[par][sig,0]
			s += '\n'
			s += '%-17s %12s ' % (' ', methods[1])
			for sig in range(sigma.size):
				s += '%12g ' % width[par][sig,1]
			s += '\n'
			if calc_proj==True:
				s += '%-17s %12s ' % (' ', methods[2])
				for sig in range(sigma.size):
					s += '%12g ' % width[par][sig,2]
				s += '\n'
	print s


def delta_ci( mu, covar, sigma=1, log=False, inv=False):
	if log:
		CI = np.exp( log(mu)+ np.array([-1,1])*sigma*np.sqrt(covar)/mu)
	if inv:
		CI = 1.0/( 1.0/mu + np.array([1,-1])*sigma*np.sqrt( covar)/ np.power(mu,2))
	return CI
		
	

def print_key( key, colnames ):
	hfmt = '%-17s %-12s %-12s \n'
	s = hfmt % ('Param', colnames[0], colnames[1])
	s += hfmt % ('-'*5, '-'*6, '-'*4)
	for par in key.keys():
		s += '%-17s %-12g %-12g \n' % (par, key[par][0], key[par][1])
	print s

def analysis(draws=1000):
	""" Assume fit already performed """
	covariance()
	covar = get_covar_results().extra_output
	p = get_parameter_info()
	covar_ci = covariance_ci(covar,p['parvals'])
	proj = proj_ci()
	d = get_draws(params=p, verbose=False, niter=draws)
	parnames = p['parnames']
	npars = parnames.size
	x = dictionary_to_array(d,parnames)
	sample_covar = variance(x)
	sample_means = np.dot( np.zeros(draws+1)+1, x )/ (draws+1.0)
	sample_covar_ci = covariance_ci(sample_covar, sample_means)
	sample_int = analyze_draws(d, parnames)
	acceptance_rate = np.mean(d['accept'])
	out={
		"covar": covar, "covar_ci": covar_ci, "sample_covar": sample_covar,
		"sample_covar_ci": sample_covar_ci, "proj_ci": proj, "sample_int":sample_int,
		"acceptance_rate": acceptance_rate}
	return out

def grid2by2( parnames, min1, max1, min2, max2, dim ):
	""" calc posterior density over grid
		assumes that the cash is being used"""
	par1 = min1 + (max1 - min1) * np.array( range( 0,dim )) / (dim-1.0)
	par2 = min2 + (max2 - min2) * np.array( range( 0,dim )) / (dim-1.0)
	post = np.zeros((dim,dim))
	parvals = np.zeros((dim*dim,2))
	parvals[:,0] = np.repeat( par1, dim )
	parvals[:,1] = np.tile( par2, dim )
	for i in range(0,dim):
		set_par(parnames[0], par1[i])
		for j in range(0,dim):
			set_par(parnames[1], par2[j])
			post[i,j] = -.5*calc_stat(1)
	result = { "post": post, "parvals": parvals}
	return result

def eval_prior( x, f, *args):
	""" args should be tuple with the necessary arguments for f in the right order
		
		"""
	out = f( x, *args)
	return out
	
#def flat(x, log=False, inv=False):
	"""flat on original scale means not flat on transformed scale
		x assumed to be on original scale"""
#	if (log==False and inv==False):
#		prior = 1
#	if (np.sum(log)>0 and inv==True):
#		raise RuntimeError, "Not yet implemented!"
#	if np.sum(log)>0:
#		prior = x
#	if inv:
#		prior =  np.power(x,2.0) 
#	return prior

def flat(x):
	return 1

def inverse(x):
	prior = 1.0/x
	return prior

def inverse2(x):
	prior = 1.0/np.power(x,2)
	return prior


def grid3by3( parnames, mins, maxes, dim, log=False, inv=False, defaultprior=True, priorshape=flat, originalscale=True, verbose=False, dataid=1):
	""" calc log posterior density over 3-d grid
		assumes that the cash is being used
		default prior is flat on the scale of the transformation
		if default prior is False, must specify priorshape and originalscale for each parameter
			"""
	
	prior=np.repeat( 1.0, parnames.size)
	priorshape = np.array(priorshape)
	originalscale = np.array(originalscale)
	# if not default prior, prior calculated at each iteration
	if defaultprior!=True:
		if priorshape.size!=parnames.size:
			raise RuntimeError, "If not using default prior, must specify a function for the prior on each parameter"
		if originalscale.size!=parnames.size:
			raise RuntimeError, "If not using default prior, must specify the scale on which the prior is defined for each parameter"
	
	jacobian = np.repeat( False, parnames.size)
	### jacobian needed if transforming parameter but prior for parameter on original scale
	if defaultprior!=True:
		### if log transformed but prior on original scale, jacobian for those parameters is needed
		if np.sum( log*originalscale ) > 0:
			jacobian[ log*originalscale ] = True
		if np.sum( inv*originalscale ) > 0:
			jacobian[ inv*originalscale ] = True
		
	dim = np.array(dim)
	if dim.size==1:
		dim = np.tile( dim, parnames.size)
		
	log = np.array(log)
	if log.size==1:
		log = np.tile( log, parnames.size)
		
	inv = np.array(inv)
	if inv.size==1:
		inv = np.tile( inv, parnames.size)
		
	for i in dim:
		if np.mod( i,2) !=0:
			raise RuntimeError, "grid must have even dimensions"

	def eval_grid(paramspace, calc_stat, dataid):

		post = np.zeros(len(paramspace), dtype=float)

		for ii, parvals in enumerate(paramspace):
			### parameters stored in paramspace on original scale
			_set_par_vals(parnames, parvals)
			if defaultprior!=True:
				x=np.copy(parvals)
				if np.sum(originalscale) < parnames.size:
					for i in range(parnames.size):
						if log[i]*(1-originalscale[i])>0:
							x[i]=np.log( x[i])
						if inv[i]*(1-originalscale[i])>0:
							x[i]=1.0/x[i]
				for par in range(0, parnames.size):
					prior[par] = eval_prior( x[par], priorshape[par])
					#print prior

			post[ii] = -.5*calc_stat(dataid) + np.sum( np.log( prior ) )
			#post[ii] = -.5*calc_stat(dataid) 
			
			# y=log(x) = g(x)
			# x= ginv(y) = exp(y)
			# jacobian is thus |x|
			if np.sum(log*jacobian)>0:					
				post[ii] += np.sum( np.log( parvals[log*jacobian] ) )
			# y = g(x) = 1/x
			# x = ginv(y) = 1/y
			# jacobian is thus |-1/y^2|=x^2
			if np.sum(inv*jacobian)>0:
				post[ii] += np.sum( 2.0*np.log( np.abs(parvals[inv*jacobian]) ) )
			if verbose:
				if np.mod(ii,1000)==0:
					print ii

		return post

	# worker function run in each process, adds pid and it's section of
	# post to the queue.
	def worker(pid, q, paramspace, calc_stat, dataid):

		q.put( (pid, eval_grid(paramspace, calc_stat, dataid) ) )


	naxes=3

	# create indices of 3 x dim permutation
	idx = np.zeros((dim[0]*dim[1]*dim[2],3))
	idx[:,0] = np.repeat( range(dim[0]), dim[1]*dim[2] )
	idx[:,1] = np.tile( np.repeat( range(dim[1]), dim[2]), dim[0])
	idx[:,2] = np.tile( range(dim[2]), dim[0]*dim[1] )
	idx = np.array( idx, int)

	paramspace = []
	spaces = []
	for ii, par in enumerate(parnames):
		space = mins[ii] + (maxes[ii] - mins[ii]) * np.arange(0,dim[ii]) / (dim[ii]-1.0)
		if np.sum(log)>0:
			if log[ii]==True:
				# create equally spaced on log scale, but store on original scale
				space = np.log(mins[ii]) + (np.log(maxes[ii]) - np.log(mins[ii])) * np.arange(0,dim[ii]) / (dim[ii]-1.0)
				space = np.exp(space)
		if np.sum(inv)>0:
			if inv[ii]==True:
				# create equally spaced on inverse scale
				space = 1.0/mins[ii] + (1.0/maxes[ii] - 1.0/mins[ii]) * np.arange(0,dim[ii]) / (dim[ii]-1.0)
				space=np.sort(space)
				#store on original scale
				space = 1.0/space

		# create permutation of parameter values in order of parameter
		# number.  Indexing the current space will correctly mirror the
		# parameter values in the permutation.	This allows for using a
		# single for loop in updating the model parameters in one shot.
		#	space = [ 0.5, 0.6 ]
		#	idx	  = [ 0, 0, 0, 1, 1, 1 ]
		#	space[idx] = [ 0.5, 0.5, 0.5, 0.6, 0.6, 0.6]
		paramspace.append(space[idx[::,ii]])
		spaces.append(space)

	# rotate the space so it becomes an array of permuted parameter vectors.
	paramspace = np.asarray(paramspace, dtype=float).T

	multi=False
	ncpus=1
	try:
		import multiprocessing
		multi=True
		ncpus = multiprocessing.cpu_count()
		if verbose:
			print ("Multiprocessing found: %i cores available" % ncpus)
	except:
		if verbose:
			print ("Multiprocessing could not be found, proceeding on 1 core")
		pass

	if multi and ncpus > 1:

		#q = multiprocessing.Queue()
		manager = multiprocessing.Manager()
		q = manager.Queue()

		# partition the parameter space according to num cpus
		start = 0
		nelem = len(paramspace)
		chunk = int(nelem / ncpus)
		resid = int(nelem % ncpus)
		stop  = chunk

		# process ids keep the pieces in order for post array
		pid = 0

		tasks = []
		# less the last CPU, partition the paramspace for each process
		for ii in xrange(ncpus-1):
			paramspace[start:stop]
			tasks.append(multiprocessing.Process(target=worker,
								 args=(pid, q, paramspace[start:stop],
									   calc_stat, dataid)))
			start += chunk
			stop += chunk
			pid += 1


		# last CPU includes residual grid elements (mod ncpus)
		tasks.append(multiprocessing.Process(target=worker,
							 args=(pid, q, paramspace[start:stop+resid],
								   calc_stat, dataid)))

		for task in tasks:
			task.start()

		for task in tasks:
			task.join()

		# use hash table to quickly sort pieces of post by pid
		results = {}
		while not q.empty():
			id, array = q.get()
			results[id] = array
			
		post = np.asarray([results[key] for key in range(ncpus)],
						  dtype=float)

	else:

		# if multiprocessing is not found or not multi-core
		# proceed using full paramspace.
		post = eval_grid(paramspace, calc_stat, dataid)
		
	#temp1=np.copy(post[:,1])
	#temp2=np.copy(post[:,2])
	#post[:,1]=np.copy(temp2)
	#post[:,2]=np.copy(temp1)
	post = post.reshape(dim[0],dim[1],dim[2])
	post = post-np.max(post)
	margin1 = np.sum( np.sum( np.exp(post), 2), 1)
	margin2 = np.sum( np.sum( np.exp(post), 2), 0)
	margin3 = np.sum( np.sum( np.exp(post), 1), 0)
	joint12 = np.sum( np.exp(post), 2)
	joint13 = np.sum( np.exp(post), 1)
	joint23 = np.sum( np.exp(post), 0)
	result = { "post": post,
				   parnames[0]: np.column_stack( (spaces[0],margin1)),
				   parnames[1]: np.column_stack( (spaces[1],margin2)),
				   parnames[2]: np.column_stack( (spaces[2],margin3)),
				   "joint"+parnames[0]+parnames[1]: joint12,
				   "joint"+parnames[0]+parnames[2]: joint13,
				   "joint"+parnames[1]+parnames[2]: joint23 }
	return result

def write_post_3by3( parnames, folder, post):
	write_table( post["joint"+parnames[0]+parnames[1]], folder+"/"+"joint"+parnames[0]+parnames[1]+".out")
	write_table( post["joint"+parnames[0]+parnames[2]], folder+"/"+"joint"+parnames[0]+parnames[2]+".out")
	write_table( post["joint"+parnames[1]+parnames[2]], folder+"/"+"joint"+parnames[1]+parnames[2]+".out")
	write_table( post[parnames[0]], folder+"/"+parnames[0]+".out")
	write_table( post[parnames[1]], folder+"/"+parnames[1]+".out")
	write_table( post[parnames[2]], folder+"/"+parnames[2]+".out")
	


def grid3by3_old( pars, dim, log=False, dataid=1):
	""" calc log posterior density over 3-d grid
		assumes that the cash is being used
		assumes that the par mins and maxes have been set by the user
	"""

	dim = np.array(dim)
	if dim.size==1:
		dim = np.tile( dim, 3)

	def eval_grid(paramspace, get_model, calc_stat, dataid):

		post = np.zeros(len(paramspace), dtype=float)

		for ii, parvals in enumerate(paramspace):
			get_model(dataid).thawedpars = parvals
			post[ii] = -.5*calc_stat(dataid)
			if np.sum(log)>0:
				post[ii] -= np.sum( np.log( parvals[log] ) )
			print ii

		return post

	# worker function run in each process, adds pid and it's section of
	# post to the queue.
	def worker(pid, q, paramspace, get_model, calc_stat, dataid):

		q.put( (pid, eval_grid(paramspace, get_model, calc_stat, dataid) ) )


	naxes=3

	# create indices of 3 x dim permutation
	idx = np.zeros((dim[0]*dim[1]*dim[2],3))
	idx[:,0] = np.repeat( range(dim[0]), dim[1]*dim[2] )
	idx[:,1] = np.tile( np.repeat( range(dim[1]), dim[2]), dim[0])
	idx[:,2] = np.tile( range(dim[2]), dim[0]*dim[1] )
	idx = np.array( idx, int)

	paramspace = []
	spaces = []
	for ii, par in enumerate(pars):
		space = par.min + (par.max - par.min) * np.arange(0,dim[ii]) / (dim[ii]-1.0)
		if np.sum(log)>0:
			if log[ii]==True:
				space = np.log(par.min) + (np.log(par.max) - np.log(par.min)) * np.arange(0,dim[ii]) / (dim[ii]-1.0)
				space = np.exp(space)
		# create permutation of parameter values in order of parameter
		# number.  Indexing the current space will correctly mirror the
		# parameter values in the permutation.	This allows for using a
		# single for loop in updating the model parameters in one shot.
		#	space = [ 0.5, 0.6 ]
		#	idx	  = [ 0, 0, 0, 1, 1, 1 ]
		#	space[idx] = [ 0.5, 0.5, 0.5, 0.6, 0.6, 0.6]
		paramspace.append(space[idx[::,ii]])
		spaces.append(space)

	# rotate the space so it becomes an array of permuted parameter vectors.
	paramspace = np.asarray(paramspace, dtype=float).T

	multi=False
	ncpus=1
	try:
		import multiprocessing
		multi=True
		ncpus = multiprocessing.cpu_count()
		print ("Multiprocessing found: %i cores available" % ncpus)
	except:
		print ("Multiprocessing could not be found, proceeding on 1 core")
		pass

	if multi and ncpus > 1:

		#q = multiprocessing.Queue()
		manager = multiprocessing.Manager()
		q = manager.Queue()

		# partition the parameter space according to num cpus
		start = 0
		nelem = len(paramspace)
		chunk = int(nelem / ncpus)
		resid = int(nelem % ncpus)
		stop  = chunk

		# process ids keep the pieces in order for post array
		pid = 0

		tasks = []
		# less the last CPU, partition the paramspace for each process
		for ii in xrange(ncpus-1):
			paramspace[start:stop]
			tasks.append(multiprocessing.Process(target=worker,
								 args=(pid, q, paramspace[start:stop],
									   get_model, calc_stat, dataid)))
			start += chunk
			stop += chunk
			pid += 1


		# last CPU includes residual grid elements (mod ncpus)
		tasks.append(multiprocessing.Process(target=worker,
							 args=(pid, q, paramspace[start:stop+resid],
								   get_model, calc_stat, dataid)))

		for task in tasks:
			task.start()

		for task in tasks:
			task.join()

		# use hash table to quickly sort pieces of post by pid
		results = {}
		while not q.empty():
			id, array = q.get()
			results[id] = array
		post = np.asarray([results[key] for key in range(ncpus)],
						  dtype=float)

	else:

		# if multiprocessing is not found or not multi-core
		# proceed using full paramspace.
		post = eval_grid(paramspace, get_model, calc_stat, dataid)
	#temp1=np.copy(post[:,1])
	#temp2=np.copy(post[:,2])
	#post[:,1]=np.copy(temp2)
	#post[:,2]=np.copy(temp1)
	post = post.reshape(dim[0],dim[1],dim[2])

	margin1 = np.sum( np.sum( np.exp(post), 2), 1)
	margin2 = np.sum( np.sum( np.exp(post), 2), 0)
	margin3 = np.sum( np.sum( np.exp(post), 1), 0)
	joint12 = np.sum( np.exp(post), 2)
	joint13 = np.sum( np.exp(post), 1)
	joint23 = np.sum( np.exp(post), 0)
	result = { "post": post,
				   pars[0].fullname: np.column_stack( (spaces[0],margin1)),
				   pars[1].fullname: np.column_stack( (spaces[1],margin2)),
				   pars[2].fullname: np.column_stack( (spaces[2],margin3)),
				   "joint"+pars[0].fullname+pars[1].fullname: joint12,
				   "joint"+pars[0].fullname+pars[2].fullname: joint13,
				   "joint"+pars[1].fullname+pars[2].fullname: joint23 }
	return result


def grid3by3slow( parnames, mins, maxes, dim ):
	""" calc log posterior density over 3-d grid
		assumes that the cash is being used"""
	par1 = mins[0] + (maxes[0] - mins[0]) * np.array( range( 0,dim )) / (dim-1.0)
	par2 = mins[1] + (maxes[1] - mins[1]) * np.array( range( 0,dim )) / (dim-1.0)
	par3 = mins[2] + (maxes[2] - mins[2]) * np.array( range( 0,dim )) / (dim-1.0)

	post = np.zeros((dim,dim,dim))
	#parvals = np.zeros((dim*dim*dim,3))
	#parvals[:,0] = np.repeat( par1, dim*dim )
	#parvals[:,1] = np.tile( np.repeat( par2, dim), dim)
	#parvals[:,2] = np.tile( par3, dim*dim )
	for i in range(0,dim):
		set_par(parnames[0], par1[i])
		for j in range(0,dim):
			set_par(parnames[1], par2[j])
			for k in range(0,dim):
				set_par(parnames[2], par3[k])
				post[i,j,k] = -.5*calc_stat(1)
	margin1 = np.sum( np.sum( np.exp(post), 2), 1)
	margin2 = np.sum( np.sum( np.exp(post), 2), 0)
	margin3 = np.sum( np.sum( np.exp(post), 1), 0)
	joint12 = np.sum( np.exp(post), 2)
	joint13 = np.sum( np.exp(post), 1)
	joint23 = np.sum( np.exp(post), 0)
	result = { "post": post, parnames[0]: np.column_stack( (par1,margin1)),
		parnames[1]: np.column_stack( (par2,margin2)), parnames[2]: np.column_stack( (par3,margin3)),
		"joint"+parnames[0]+parnames[1]: joint12,
		"joint"+parnames[0]+parnames[2]: joint13,
		 "joint"+parnames[1]+parnames[2]: joint23 }
	return result


# 3-d array operations
# x[i,:,:] returns ith matrix, corresponds to par1[i]
# x[:,i,:] returns ith row of each matrix, corresponds to par2[i]
# x[:,:,i] returns ith column of each matrix, corresponds to par3[i]
# np.sum( x, 0 ) returns sum of i,j elements of each matrix
# np.sum( x, 1) returns sum of each column of each matrix, row i corresponds to ith matrix
# np.sum( x, 2) returns sum of each row of each matrix, row i corresponds to ith matrix
####  also corresponds to joint i,k
# np.sum( np.sum( x, 2), 1) returns sum of each matrix
# np.sum( np.sum( x, 2), 0) returns sum over matrices of the sum of each row of each matrix
# np.sum( np.sum( x, 1) , 0) returns sum over matrices of the sum of each col of each matrix
# np.repeat( x,2 ) repeats each element of x twice
# np.tile(x, 2) repeats entire x twice

def write_table(draws, outfile, thin=1):
	"Writes the draws to the file called outfile"
	fout = open(outfile, "w")
	for (i,line) in zip( range( 1, draws.shape[0]+1), draws):
		if np.mod(i,thin)==0:
			for element in line:
				fout.write("%s " % element)
			fout.write("\n")
	fout.close()

def write_vec(vec, outfile):
	fout = open(outfile, "w")
	vec = np.array(vec)
	for i in range(0,vec.size):
		fout.write("%s" % vec[i])
		fout.write("\n")
	fout.close()

#def print_covar_int():
#	print "covariance function CI's"
#	print "			  best fit	lval   hval"
#	for i in range(npars):
#		print "%s %g %g %g" % (parnames[i].ljust(10), covar_ci[i,0], covar_ci[i,1], covar_ci[i,2])



def print_sample_int():
	print "Credible Interval from draws"
	print "				 median		lval	hval"
	for i in range(npars):
		print "%s %g %g %g" % (parnames[i].ljust(10), sample_int[i,0], sample_int[i,1], sample_int[i,2])

def print_covar_CI_array(parnames, array):
	hfmt = '\n	 %-12s %12s %12s %12s'
	s = hfmt % ('Param', 'Best-Fit', 'Lower Bound', 'Upper Bound')
	s += hfmt % ('-'*5, '-'*8, '-'*11, '-'*11)
	for name, val, lower, upper in zip(parnames, array[:,0],
		array[:,1], array[:,2]):
				s += '\n   %-12s %12g ' % (name, val)
				s += '%12g ' % lower
				s += '%12g' % upper
	print s

def plot_hist(vals, nbins=50):
	erase()
	(hy,hx) = np.histogram(vals, bins=nbins, new=True)
	xlo = hx[:-1]
	xhi = hx[1:]
	add_histogram(xlo,xhi, hy)
