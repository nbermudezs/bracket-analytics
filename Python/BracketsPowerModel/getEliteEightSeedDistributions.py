#!/usr/bin/env python
from scoringUtils import getActualBracketVector
from scoringUtils import applyRoundResults
import json
import sys
import pprint

# Author: Ian Ludden
# Date:   02 Apr 2018
# 
# This script finds the seed distribution for each of
# the Elite Eight positions, using NCAA Men's Division I
# Basketball Tournament data from 1985 through the given year. 

# print 'Year,Champ Seed,Champ Region,FF_c Seed,FF_c Region,Runner-up Seed,Runner-up Region,FF_r Seed,FF_r Region'

cutoffYear = int(sys.argv[1])

# The eight positions are indexed 0 through 7. 
# Each possible position-seed pairing has a unique
# identifier: [position index]_[2-digit seed number].
# For example, if the bottom position had an 8 seed,
# that would be represented as "7_08".
idStrings = []
freqCounts = []
for posIndex in range(8):
	for seedNum in range(1, 17):
		idStrings.append('{0}_{1:02d}'.format(posIndex, seedNum))
		freqCounts.append(0)

freqs = dict(zip(idStrings, freqCounts))

for year in range(1985, cutoffYear + 1):
	bracketVector = getActualBracketVector(year)

	e8Seeds = []

	# Compute Elite Eight seeds
	for region in range(4):
		start = 15 * region
		end = start + 8
		regionVector = bracketVector[start:end]

		seeds = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]

		for r in range(1, 4):
			seeds = applyRoundResults(seeds, regionVector)
			start = end
			end += int(len(seeds) / 2)
			regionVector = bracketVector[start:end]

		e8Seeds += seeds

	for posIndex in range(8):
		seedNum = e8Seeds[posIndex]
		freqs['{0}_{1:02d}'.format(posIndex, seedNum)] += 1

seedNums = range(1, 17)
pooledFreqCounts = [0 for i in range(16)]
pooledFreqs = dict(zip(seedNums, pooledFreqCounts))

for seedNum in range(1, 17):
	for posIndex in range(8):
		pooledFreqs[seedNum] += freqs['{0}_{1:02d}'.format(posIndex, seedNum)]

# pprint.pprint(freqs)
topSeeds = [1, 4, 5, 8, 9, 12, 13, 16]
bottomSeeds = [2, 3, 6, 7, 10, 11, 14, 15]

for seedNum in topSeeds:
	print '{0},{1}'.format(seedNum, pooledFreqs[seedNum])

print ''

for seedNum in bottomSeeds:
	print '{0},{1}'.format(seedNum, pooledFreqs[seedNum])
