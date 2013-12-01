
Model comparison
----------------------
*examples/model_compare.py* shows an example of model selection. Keep in mind what model prior you would like to use.

* Case 1: Multiple models, want to find one best one to use from there on:
	* follow *examples/model_compare.py*, and pick the model with the highest evidence
* Case 2: Simpler and more complex models, want to find out which complexity is justified:
	* follow *examples/model_compare.py*, and keep the models above a certain threshold
* Case 3: Multiple models which could be correct, only interested in a parameter
	* Marginalize over the models: Use the posterior samples from each model, and weigh them by the 
	  relative probability of the models (weight = exp(lnZ))

