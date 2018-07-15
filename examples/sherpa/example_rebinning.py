from __future__ import print_function
import numpy
import bxa.sherpa as bxa
from bxa.sherpa.rebinnedmodel import RebinnedModel
from sherpa.models.parameter import Parameter

load_pha('interval0pc.pi')

slowmodel = xspowerlaw.p1 * xswabs.a1
ebins  = [0.001] + numpy.logspace(-1, 2, 1000).tolist()
#ebins = (numpy.linspace(0, 40, 80) + 0.001).tolist() + [100]
ebins = numpy.array(ebins)

lognH = Parameter(modelname='mymodel', name='nH', val=20, min=20, max=26,
         hard_min=20, hard_max=26)
a1.nH = 10**(lognH - 22)
p1.PhoIndex.min = 1
p1.PhoIndex.val = 2
p1.PhoIndex.max = 3
parameters = [
	(lognH, 81),
	(p1.PhoIndex, 41),
]

fastmodel = RebinnedModel(slowmodel=slowmodel, ebins=ebins, parameters=parameters, filename = 'testmodel.npz', modelname='fastmodel')

set_model(fastmodel)
print('plotting ...')
ignore(None, 0.5)
ignore(4, None)
set_xlog()
set_ylog()
plot_source()
#group_counts(20)
plot_fit()
fit()
plot_fit()

