#!/usr/bin/env python
import json
import os.path
import sys
from math import sqrt

from Utils.bracketClassDefinitions import Bracket
from Utils.bracketClassDefinitions import Region
from Utils.bracketClassDefinitions import buildBracketFromJson
from Utils.bracketUtils import writeBracket

# This function runs a chi-squared test of independence for the
# first two game positions given (as a two-bit number) 
# vs. the third game position.

def testTwoToOneIndependence(pos1, pos2, pos3, isPooled=False):
	formats = ['TTT', 'TTF', 'TFT', 'TFF', 'FTT', 'FTF', 'FFT', 'FFF']
	patterns = ['000', '001', '010', '011', '100', '101', '110', '111']

	numRegions = 4
	if not isPooled:
		numRegions = 1

	print 'formatType, pos1, pos2, pos3, chiSquared, n111, n110, n101, n100, n011, n010, n001, n000'

	for formatType in formats:
		patternFreqs = dict(zip(patterns, [0 for i in range(8)]))
		filename = 'Brackets/{0}/allBrackets{0}.json'.format(formatType)
		with open(filename, 'r') as inputFile:
			jsonData = inputFile.read().replace('\n', '')
		jsonToPython = json.loads(jsonData)
		bracketList = jsonToPython['brackets']
		numBrackets = len(bracketList)

		for i in range(numBrackets):
			bracketDict = bracketList[i]['bracket']
			bracket = buildBracketFromJson(bracketDict)
			for region in range(numRegions):
				offset = region * 15
				threeGames = ''
				if pos1 + offset >= len(bracket.fullVector):
					print 'Houston, we have a problem. pos1 + offset = {0}'.format(pos1 + offset)
				threeGames += bracket.fullVector[pos1 + offset]
				threeGames += bracket.fullVector[pos2 + offset]
				threeGames += bracket.fullVector[pos3 + offset]
				patternFreqs[threeGames] = patternFreqs[threeGames] + 1

		n000 = patternFreqs['000']
		n001 = patternFreqs['001']
		n010 = patternFreqs['010']
		n011 = patternFreqs['011']
		n100 = patternFreqs['100']
		n101 = patternFreqs['101']
		n110 = patternFreqs['110']
		n111 = patternFreqs['111']

		nxx1 = n001 + n011 + n101 + n111
		nxx0 = n000 + n010 + n100 + n110

		n11x = n111 + n110
		n10x = n101 + n100
		n01x = n011 + n010 
		n00x = n001 + n000

		nObservations = numBrackets * numRegions

		rowSums = [patternFreqs['000'] + patternFreqs['001'], patternFreqs['010'] + patternFreqs['011'], patternFreqs['100'] + patternFreqs['101'], patternFreqs['110'] + patternFreqs['111']]
		colSums = [patternFreqs['000'] + patternFreqs['010'] + patternFreqs['100'] + patternFreqs['110'], patternFreqs['001'] + patternFreqs['011'] + patternFreqs['101'] + patternFreqs['111']]
		
		chiSquare = 0
		for r in range(len(rowSums)):
			for c in range(len(colSums)):
				expFreq = rowSums[r] * colSums[c] * 1.0 / nObservations
				if expFreq == 0: # This hack dodges division by zero
					expFreq = 0.00000001
				obsFreq = patternFreqs[patterns[2 * r + c]] * 1.0
				chiSquare += (obsFreq - expFreq) ** 2 / expFreq

		summaryString = '{12},{0:02d},{1:02d},{2:02d},{3:.3f},{4},{5},{6},{7},{8},{9},{10},{11}'.format(pos1, pos2, pos3, chiSquare, n111, n110, n101, n100, n011, n010, n001, n000, formatType)

		# if chiSquare >= 7.815: # critical value for 3 degrees of freedom, alpha = 0.05
		print summaryString


# This script tests all reasonable two-to-one matchings, i.e., 
# for every game in R2-R6, it tests the games feeding into it.
# The final four games are not tested. 

# Pooled version:
# pos3Options = [8, 9, 10, 11, 12, 13, 14]
# isPooled = True
# for pos3 in pos3Options:
# 	if pos3 < 12:
# 		pos1 = pos3 - 8 + (pos3 - 8)
# 		pos2 = pos1 + 1
# 	elif pos3 < 14:
# 		pos1 = ((pos3 - 12) % 2) * 2 + 8
# 	else: 
# 		pos1 = 12

# 	pos2 = pos1 + 1

# 	testTwoToOneIndependence(pos1, pos2, pos3, isPooled)


# Unpooled version:
pos3Options = [8, 9, 10, 11, 12, 13, 14]
isPooled = False

for regionIndex in range(4):
	for pos3_u in pos3Options:
		if pos3_u < 12:
			pos1 = pos3_u - 8 + (pos3_u - 8)
		elif pos3_u < 14:
			pos1 = ((pos3_u - 12) % 2) * 2 + 8
		else: 
			pos1 = 12

		pos2 = pos1 + 1

		offset = regionIndex * 15
		pos3 = pos3_u + offset
		pos1 += offset
		pos2 += offset

		testTwoToOneIndependence(pos1, pos2, pos3, isPooled)
