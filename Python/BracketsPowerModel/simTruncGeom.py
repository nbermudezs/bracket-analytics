#!/usr/bin/env python
import random
from math import log, ceil

# Test of truncated geometric r.v. simulation.

# Returns a sample of a truncated geometric r.v.
# with parameter p and probabilities that add to sumOfProbs.
def getTruncGeom(p, sumOfProbs):
	u = random.random() * sumOfProbs
	return int(ceil(log(1 - u) / log(1 - p)))

# Truncated geometric parameters for predicting 2013-2018 seasons.
# See ReverseModel/ChampionRunnerUpSeedDistributions.ods for 
# how these values were computed.
pChamp = [0.5090909091, 0.5178571429, 0.4761904762, 0.484375, 0.4848484848, 0.4925373134]
champSum = [0.9966270601, 0.997079845, 0.9943325575, 0.9950034329, 0.9950400208, 0.9956022259]

pRU = [0.3835616438, 0.3766233766, 0.3529411765, 0.3604651163, 0.367816092, 0.375]
ruSum = [0.9791494637, 0.9771963641, 0.9692708809, 0.9720157349, 0.9744878244, 0.9767169356]

for year in range(2013, 2019):
	print 'Year {0}:'.format(year)
	nTrials = 100000

	champFreqs = [0 for i in range(17)]
	for trialNum in range(nTrials):
		sampleVal = getTruncGeom(pChamp[year - 2013], champSum[year - 2013])
		champFreqs[sampleVal] += 1

	print 'Champion Distribution:'
	for i in range(1, len(champFreqs)):
		print '{0:02d} - {1:<7.3f}'.format(i, champFreqs[i] * 1.0 / nTrials)

	print '\n'

	ruFreqs = [0 for i in range(17)]
	for trialNum in range(nTrials):
		sampleVal = getTruncGeom(pRU[year - 2013], ruSum[year - 2013])
		ruFreqs[sampleVal] += 1

	print 'Runner-up Distribution:'
	for i in range(1, len(ruFreqs)):
		print '{0:02d} - {1:<7.3f}'.format(i, ruFreqs[i] * 1.0 / nTrials)

	print '\n'