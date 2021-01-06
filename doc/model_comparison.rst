
Model comparison
----------------------

*examples/xspec/model_compare.py* shows an example of model selection. Keep in mind what model prior you would like to use.

* Case 1: Multiple models, want to find one best one to use from there on:
	* follow *examples/model_compare.py*, and pick the model with the highest evidence
* Case 2: Simpler and more complex models, want to find out which complexity is justified:
	* follow *examples/model_compare.py*, and keep the models above a certain threshold
* Case 3: Multiple models which could be correct, only interested in a parameter
	* Marginalize over the models: Use the posterior samples from each model, and weigh them by the 
	  relative probability of the models (weight = exp(lnZ))

Example output::

	jbuchner@ds42 $ python model_compare.py absorbed/ line/ simplest/

	Model comparison
	****************

	model simplest : log10(Z) = -1632.7  XXX ruled out
	model absorbed : log10(Z) =    -7.5  XXX ruled out
	model line     : log10(Z) =     0.0    <-- GOOD

	The last, most likely model was used as normalization.
	Uniform model priors are assumed, with a cut of log10(30) to rule out models.
	
	jbuchner@ds42 $ 

Here, the probability of the second-best model, "absorbed", is :math:`10^7.5` times
less likely than the model "line". As this exceeds our threshold (by a lot!)
we can claim the detection of an iron line!

Monte Carlo simulated spectra are recommended to derive a 
Bayes factor threshold for a preferred false selection rate.
You can find an example in the `Appendix of Buchner+14 <https://ui.adsabs.harvard.edu/abs/2014A%26A...564A.125B/abstract>`_
and in `the ultranest tutorial <https://johannesbuchner.github.io/UltraNest/example-sine-modelcomparison.html>`_.
