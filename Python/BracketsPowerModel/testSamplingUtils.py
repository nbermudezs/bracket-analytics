#!/usr/bin/env python
from math import log, ceil, floor
from pprint import pprint
import random
from samplingUtils import getF4SeedTogether, getF4SeedSplit, getE8SeedTop, getE8SeedBottom

# Author:
#     Ian Ludden
#
# Date created:
#     09 Apr 2018
#
# Last modified:
#     09 Apr 2018
#
# This script tests the functions in samplingUtils.py.

nTrials = 10000

# Test 1:
# Sample many Final Four seeds (using Model1) for each year, 
# then visually compare the results to the actual distribution. 

# print '--- Final Four seeds, Model1 ---'
# for year in range(2019, 2012, -1):
# 	seeds = range(1, 17)
# 	seedCounts = [0 for i in range(len(seeds))]
# 	freqs = dict(zip(seeds, seedCounts))

# 	for trialNum in range(nTrials):
# 		seed = getF4SeedTogether(year)
# 		freqs[seed] += 1

# 	# Scale back down to the appropriate total
# 	totalCount = 4 * (year - 1985)

# 	for seed in range(1, 17):
# 		freqs[seed] = freqs[seed] * 1.0 / nTrials * totalCount

# 	print year
# 	pprint(freqs)
# 	print '\n'


# Test 2:
# Sample many Final Four seeds (using Model2) for each year, 
# then visually compare the results to the actual distribution. 

# print '--- Final Four seeds, Model2 ---'
# for year in range(2019, 2012, -1):
# 	seeds = range(1, 17)
# 	seedCounts = [0 for i in range(len(seeds))]
# 	freqs = dict(zip(seeds, seedCounts))

# 	for trialNum in range(nTrials):
# 		seed = getF4SeedSplit(year)
# 		freqs[seed] += 1

# 	# Scale back down to the appropriate total
# 	totalCount = 4 * (year - 1985)

# 	for seed in range(1, 17):
# 		freqs[seed] = freqs[seed] * 1.0 / nTrials * totalCount

# 	print year
# 	pprint(freqs)
# 	print '\n'


# Test 3:
# Sample many Elite Eight seeds (top half) for each year, 
# then visually compare the results to the actual distribution. 

print '--- Elite Eight seeds (top half) ---'
for year in range(2019, 2012, -1):
	seeds = [1, 4, 5, 8, 9, 12, 13, 16]
	seedCounts = [0 for i in range(len(seeds))]
	freqs = dict(zip(seeds, seedCounts))

	for trialNum in range(nTrials):
		seed = getE8SeedTop(year)
		freqs[seed] += 1

	# Scale back down to the appropriate total
	totalCount = 4 * (year - 1985)

	for seed in seeds:
		freqs[seed] = freqs[seed] * 1.0 / nTrials * totalCount

	print year
	pprint(freqs)
	print '\n'


# Test 4:
# Sample many Elite Eight seeds (bottom half) for each year, 
# then visually compare the results to the actual distribution. 

print '--- Elite Eight seeds (bottom half) ---'
for year in range(2019, 2012, -1):
	seeds = [2, 3, 6, 7, 10, 11, 14, 15]
	seedCounts = [0 for i in range(len(seeds))]
	freqs = dict(zip(seeds, seedCounts))

	for trialNum in range(nTrials):
		seed = getE8SeedBottom(year)
		freqs[seed] += 1

	# Scale back down to the appropriate total
	totalCount = 4 * (year - 1985)

	for seed in seeds:
		freqs[seed] = freqs[seed] * 1.0 / nTrials * totalCount

	print year
	pprint(freqs)
	print '\n'