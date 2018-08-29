#!/usr/bin/env python
from scoringUtils import getActualBracketVector
from scoringUtils import applyRoundResults
import json
import sys
import pprint

# Author: Ian Ludden
# Date:   03 Apr 2018
# 
# This script finds the seed distribution for each of
# the Final Four positions, using NCAA Men's Division I
# Basketball Tournament data from 1985 through the given year. 

cutoffYear = int(sys.argv[1])

# The four positions are indexed 0 through 3. 
# Each possible position-seed pairing has a unique
# identifier: [position index]_[2-digit seed number].
# For example, if the bottom position had an 8 seed,
# that would be represented as "3_08".
idStrings = []
freqCounts = []
for posIndex in range(4):
	for seedNum in range(1, 17):
		idStrings.append('{0}_{1:02d}'.format(posIndex, seedNum))
		freqCounts.append(0)

freqs = dict(zip(idStrings, freqCounts))

for year in range(1985, cutoffYear + 1):
	bracketVector = getActualBracketVector(year)

	ffSeeds = []

	# Compute Final Four seeds
	for region in range(4):
		start = 15 * region
		end = start + 8
		regionVector = bracketVector[start:end]

		seeds = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]

		for r in range(1, 5):
			seeds = applyRoundResults(seeds, regionVector)
			start = end
			end += int(len(seeds) / 2)
			regionVector = bracketVector[start:end]

		ffSeeds += seeds

	for posIndex in range(4):
		seedNum = ffSeeds[posIndex]
		freqs['{0}_{1:02d}'.format(posIndex, seedNum)] += 1

seedNums = range(1, 17)
pooledFreqCounts = [0 for i in range(16)]
pooledFreqs = dict(zip(seedNums, pooledFreqCounts))

for seedNum in range(1, 17):
	for posIndex in range(4):
		pooledFreqs[seedNum] += freqs['{0}_{1:02d}'.format(posIndex, seedNum)]

# pprint.pprint(freqs)
pprint.pprint(pooledFreqs)
