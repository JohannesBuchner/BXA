from __future__ import print_function
try:
	import bxa.sherpa as bxa
	bxa.default_logging()
	print('loading background fitting module...')
	from bxa.sherpa.background.pca import auto_background
	from bxa.sherpa.rebinnedmodel import RebinnedModel
	from sherpa.models.parameter import Parameter

	# load data: 
	
	# this is for SWIFT XRT, GRB data
	datafile = os.environ.get('INPUTFILE', 'interval0pc.pi')
	if datafile == 'interval0pc.pi':
		# for swift we should load pc and wt spectra
		id = 2
		load_pha(id, 'interval0pc.pi')
		if get_rmf(id).energ_lo[0] == 0: get_rmf(id).energ_lo[0] = 0.001
		if get_arf(id).energ_lo[0] == 0: get_arf(id).energ_lo[0] = 0.001

		id2 = None
		otherids = ()
		if os.path.exists('interval0wt.pi') and False:
			id2 = 3
			load_pha(id2, 'interval0wt.pi')
			if get_rmf(id2).energ_lo[0] == 0: get_rmf(id2).energ_lo[0] = 0.001
			if get_arf(id2).energ_lo[0] == 0: get_arf(id2).energ_lo[0] = 0.001
			otherids = (id2,)
			if not (get_bkg(id2).counts.sum() > 100):
				delete_data(id2)
				id2 = None
				otherids = ()
		ignore(None, 0.7)
		ignore(7, None)
	else:
		# generic case
		id = 2
		load_pha(id, datafile)
		if get_rmf(id).energ_lo[0] == 0: get_rmf(id).energ_lo[0] = 0.001
		if get_arf(id).energ_lo[0] == 0: get_arf(id).energ_lo[0] = 0.001

		id2 = None
		otherids = ()
		ignore(None, 0.5)
		ignore(7, None)
	
	# set reasonable defaults
	
	set_stat('cstat')
	set_xsabund('wilm')
	set_xsxsect('vern')

	# next we set up a source model.
	#    with automatic milky way absorption
	galabso = bxa.auto_galactic_absorption(id)
	
	################
	# simplistic model
	object_type = os.environ.get('object_type', 'AGN')
	
	if object_type == 'simplistic':
		model = xszpowerlw.src * xszwabs.abso * galabso
		model2 = model
		srclevel = Parameter('src', 'level', numpy.log10(src.norm.val), -8, 2, -8, 2)
		srcnh = Parameter('src', 'nh', numpy.log10(abso.nH.val)+22, 19, 24, 19, 24)
		galnh = Parameter('gal', 'nh', numpy.log10(galabso.nH.val)+22, 19, 24, 19, 24)
		src.PhoIndex.min = 1
		src.PhoIndex.max = 3
		src.PhoIndex.val = 2
		src.norm.min = 1e-10
		src.norm.max = 100
		src.norm.val = 1e-5
		src.redshift.min = 0
		src.redshift.max = 10
		abso.redshift = src.redshift
		abso.nH.min = 1e19 / 1e22
		abso.nH.max = 1e24 / 1e22
		src.norm = 10**srclevel
		abso.nH = 10**(srcnh - 22)

		priors = []
		parameters = [srclevel, src.PhoIndex, srcnh, src.redshift]
		priors += [bxa.create_uniform_prior_for(srclevel)]
		priors += [bxa.create_gaussian_prior_for(src.PhoIndex, 1.95, 0.15)]
		priors += [bxa.create_uniform_prior_for(srcnh)]
		priors += [bxa.create_uniform_prior_for(src.redshift)]
	
	################
	# GRB & AGN model
	if object_type in ['GRB', 'AGN']:
		# use Murray Brightman's sphere model for GRB
		load_table_model("sphere", os.environ.get('MODELDIR', '/opt/models') + '/sphere0708.fits')
		load_table_model("sphere2", os.environ.get('MODELDIR', '/opt/models') + '/sphere0708.fits')
		srclevel = Parameter('src', 'level', 0, -8, 3, -8, 3)
		srclevel2 = Parameter('src2', 'level', 0, -8, 3, -8, 3)
		print('combining components')
		model = sphere * galabso
		model2 = sphere2 * galabso
		print('linking parameters')
		sphere.norm = 10**srclevel
		sphere2.norm = 10**srclevel2
		srcnh = Parameter('src', 'nH', 22, 20, 26, 20, 26)
		sphere.nH = 10**(srcnh - 22)
		sphere2.nH = 10**(srcnh - 22)
		print('setting redshift limits')
		redshift = Parameter('src', 'z', 0, 0, 10, 0, 10)
		sphere.redshift.max = 10
		sphere2.redshift.max = 10
		sphere.redshift = redshift
		sphere2.redshift = redshift
		
		print('creating priors')
		priors = []
		parameters = [srclevel, sphere.phoindex, srcnh, redshift]
		priors += [bxa.create_uniform_prior_for(srclevel)]
		priors += [bxa.create_gaussian_prior_for(sphere.phoindex, 1.95, 0.15)]
		priors += [bxa.create_uniform_prior_for(srcnh)]
		priors += [bxa.create_uniform_prior_for(redshift)]
		
		if id2:
			print('creating priors for second data model')
			parameters += [srclevel2, sphere2.phoindex]
			priors += [bxa.create_uniform_prior_for(srclevel2)]
			priors += [bxa.create_gaussian_prior_for(sphere2.phoindex, 1.95, 0.15)]
		
		if object_type == 'AGN':
			# add soft scattering pl for AGN
			model = model + xszpowerlw.softscat
			model2 = model2 + xszpowerlw.softscat2
			softscatnorm = Parameter('src', 'softscatnorm', -2, -7, -1, -10, 0)
			softscat.norm = sphere.norm * 10**softscatnorm
			softscat.PhoIndex = sphere.phoindex
			softscat.redshift = redshift
			softscat2.PhoIndex = sphere2.phoindex
			softscat2.norm = sphere2.norm * 10**softscatnorm
			softscat2.redshift = redshift
			
			parameters.append(softscatnorm)
			priors += [bxa.create_uniform_prior_for(softscatnorm)]
	
	assert len(priors) == len(parameters), 'priors: %d parameters: %d' % (len(priors), len(parameters))
	
	################
	# set model
	
	#    find background automatically using PCA method
	set_model(id, model)
	convmodel = get_model(id)
	bkg_model = auto_background(id)
	set_full_model(id, convmodel + bkg_model*get_bkg_scale(id))

	parameters.append(bkg_model.pars[0])
	priors += [bxa.create_uniform_prior_for(bkg_model.pars[0])]
	
	if id2:
		set_model(id2, model2)
		convmodel2 = get_model(id2)
		bkg_model2 = auto_background(id2)
		set_full_model(id2, convmodel2 + bkg_model2*get_bkg_scale(id2))
	
		parameters.append(bkg_model2.pars[0])
		priors += [bxa.create_uniform_prior_for(bkg_model2.pars[0])]
	
	show_model(id)
	#################
	# BXA run
	priorfunction = bxa.create_prior_function(priors = priors)
	print('running BXA ...')
	prefix = os.environ.get('OUTPREFIX', '') + 'xz_%s_' % object_type
	bxa.nested_run(id, otherids=otherids, prior=priorfunction, parameters = parameters, 
		resume = True, verbose=True, 
		outputfiles_basename = prefix,
		importance_nested_sampling = False)

	m = get_bkg_fit_plot(id)
	numpy.savetxt(prefix + 'bkg.txt', numpy.transpose([m.dataplot.x, m.dataplot.y, m.modelplot.x, m.modelplot.y]))

	m = get_fit_plot(id)
	numpy.savetxt(prefix + 'xz_src.txt', numpy.transpose([m.dataplot.x, m.dataplot.y, m.modelplot.x, m.modelplot.y]))

	if id2:
		m = get_fit_plot(id2)
		numpy.savetxt(prefix + 'xz_src2.txt', numpy.transpose([m.dataplot.x, m.dataplot.y, m.modelplot.x, m.modelplot.y]))

	exit()


except Exception as e:
	print('ERROR:', e)
	exit()


