"""
Compare analysed models using the stats.json files (which contain the evidence,
but also marginal summaries)
"""
import json
import sys
from math import log, log10

prefixes = sys.argv[1:]

models = dict([(f, json.load(open(f + "stats.json"))['global evidence']) for f in prefixes])

best = max(models, key=models.__getitem__)
Zbest = models[best]
limit = 30 # for example, Jeffreys scale for the Bayes factor

print
print 'Model comparison'
print '****************'
print
for m in sorted(models, key=models.__getitem__):
	Zrel = (models[m] - Zbest) # / log(10)
	print 'model %-10s: log10(Z) = %7.1f %s' % (m, Zrel, 
		' XXX ruled out' if Zrel < -log(limit) else '   <-- GOOD' )




