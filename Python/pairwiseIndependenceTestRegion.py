#!/usr/bin/env python
import json
import os.path
import sys
from math import sqrt

from Utils.bracketClassDefinitions import Bracket
from Utils.bracketClassDefinitions import Region
from Utils.bracketClassDefinitions import buildBracketFromJson
from Utils.bracketUtils import writeBracket

# This script runs a chi-squared test of independence for the
# two given bit positions in every region.

formats = ['TTT', 'TTF', 'TFT', 'TFF', 'FTT', 'FTF', 'FFT', 'FFF']

patterns = ['00', '01', '10', '11']

pos1 = int(sys.argv[1])
pos2 = int(sys.argv[2])

for formatType in formats:
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
		for region in range(4):
			offset = region * 15
			pos1Result = int(bracket.fullVector[pos1 + offset])
			pos2Result = int(bracket.fullVector[pos2 + offset])
			index = pos1Result * 2 + pos2Result
			patternFreqs[index] = patternFreqs[index] + 1

	rowSums = [patternFreqs[0] + patternFreqs[1], patternFreqs[2] + patternFreqs[3]]
	colSums = [patternFreqs[0] + patternFreqs[2], patternFreqs[1] + patternFreqs[3]]

	print '{0}: Game {1} (left) vs. Game {2} (top)'.format(formatType, pos1, pos2)
	# print '      |  0  |  1  || Total'
	# print '--------------------------'
	# print '   0  | {:<3} | {:<3} || {:<3}'.format(patternFreqs[0], patternFreqs[1], rowSums[0])
	# print '--------------------------'
	# print '   1  | {:<3} | {:<3} || {:<3}'.format(patternFreqs[2], patternFreqs[3], rowSums[1])
	# print '--------------------------'
	# print '--------------------------'
	# print 'Total | {:<3} | {:<3} || {:<3}\n'.format(colSums[0], colSums[1], numBrackets * 4)

	chiSquare = 0
	nObservations = numBrackets * 4
	for r in range(len(rowSums)):
		for c in range(len(colSums)):
			expFreq = rowSums[r] * colSums[c] * 1.0 / nObservations
			obsFreq = patternFreqs[2 * r + c] * 1.0
			chiSquare += (obsFreq - expFreq) ** 2 / expFreq

	print 'c^2: {:<6.4f}\n\n'.format(chiSquare)