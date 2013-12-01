
Model discovery
---------------------

Is the model the right one? Is there more in the data? These questions can not
be answered in a statistical way, **but** what we can do is 

1. generate ideas on what models could fit better
2. test those models for significance with model selection

For the first point, **Quantile-Quantile plots** provide a unbinned, less noisy alternative to 
residual plots.

In these plots, for each energy the number of counts observed with lower energy
are plotted on one axis, while the predicted are on the other axis.
If model and data agree perfectly, this would be a straight line. 
Deviances are indications of possible mis-fits.

A Gaussian line in the data, but absent in the model, would be present as an 
S-shaped offset (shaped like the cumulative distribution of the Gaussian).

