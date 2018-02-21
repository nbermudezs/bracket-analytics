#!/usr/bin/env python
import json
from math import sqrt
from Utils.bracketClassDefinitions import Bracket
from Utils.bracketClassDefinitions import Region
from Utils.bracketClassDefinitions import buildBracketFromJson

# This function runs a chi-squared test of independence for the
# two given bit positions in the given representation. It returns
# 1 if the test indicates significant dependence, and 0 otherwise.
#
# If isPooled = True, then the positions are treated as positions
# within the region and are pooled across all four regions.
# In this case, pos1 and pos2 should be between 0 and 14, inclusive. 
# 
# Note that this is a modified version of the testPairwiseIndependence
# function in Utils/bracketUtils.py. 

def testPairwiseIndependence(pos1, pos2, formatType, isPooled=False):
	patterns = ['00', '01', '10', '11']
	patternFreqs = [0 for i in range(4)]

	filename = 'Brackets/{0}/allBrackets{0}.json'.format(formatType)

	with open(filename, 'r') as inputFile:
		jsonData = inputFile.read().replace('\n', '')

	jsonToPython = json.loads(jsonData)
	bracketList = jsonToPython['brackets']
	numBrackets = len(bracketList)

	for i in range(numBrackets):
		bracketDict = bracketList[i]['bracket']
		bracket = buildBracketFromJson(bracketDict)

		nRegions = 1
		if isPooled:
			nRegions = 4

		for region in range(nRegions):
			offset = region * 15
			pos1Result = int(bracket.fullVector[pos1 + offset])
			pos2Result = int(bracket.fullVector[pos2 + offset])
			index = pos1Result * 2 + pos2Result
			patternFreqs[index] = patternFreqs[index] + 1

	nObservations = numBrackets * nRegions

	n11 = patternFreqs[3]
	n10 = patternFreqs[2]
	n01 = patternFreqs[1]
	n00 = patternFreqs[0]

	n1x = n11 + n10
	n0x = n01 + n00
	nx1 = n11 + n01
	nx0 = n10 + n00

	phiNum = n11 * n00 - n10 * n01
	phiDen = sqrt(n1x * n0x * nx1 * nx0)
	if phiDen > 0:
		phi = phiNum / phiDen
	else:
		phi = 0
	chiSquare = phi * phi * nObservations

	summaryString = '{0:02d},{1:02d},{2},{3},{4},{5},{6:.2f},{7:.2f}'.format(pos1, pos2, n11, n10, n01, n00, phi, chiSquare)

	# The chi-square critical value for 1 degree of freedom and alpha = 0.05
	# is 3.841. (Source: http://www.itl.nist.gov/div898/handbook/eda/section3/eda3674.htm)
	# We print the result only if it is deemed significant.

	isSignificant = 0

	if chiSquare >= 3.841:
		isSignificant = 1
		print summaryString

	return isSignificant


# This script runs a chi-squared test of independence  and computes
# the phi coefficient for all pairs of bits in a region 
# (pooled across all four regions).

total = 0
nBits = 15
isPooled = True
formats = ['TTT', 'TTF', 'TFT', 'TFF', 'FTT', 'FTF', 'FFT', 'FFF']

for formatType in formats:
	print formatType
	count = 0

	for i in range(nBits):
		for j in range(i + 1, nBits):
			count += testPairwiseIndependence(i, j, formatType, isPooled)

	total += count
	print 'Subtotal,{0}'.format(count)

print 'Total,{0}'.format(total)