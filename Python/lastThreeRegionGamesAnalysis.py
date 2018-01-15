#!/usr/bin/env python
import json
import os.path
import sys
from math import sqrt

from bracketClassDefinitions import Bracket
from bracketClassDefinitions import Region
from bracketClassDefinitions import buildBracketFromJson
from bracketUtils import writeBracket

# This script runs a chi-squared test of independence for the
# 13th/14th bits and the 15th bit.

formats = ['TTT', 'TTF', 'TFT', 'TFF', 'FTT', 'FTF', 'FFT', 'FFF']

patterns = ['000', '001', '010', '011', '100', '101', '110', '111']

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
		for region in range(4):
			offset = region * 15
			lastThreeGames = bracket.fullVector[12 + offset:15 + offset]
			patternFreqs[lastThreeGames] = patternFreqs[lastThreeGames] + 1

	rowSums = [patternFreqs['000'] + patternFreqs['001'], patternFreqs['010'] + patternFreqs['011'], patternFreqs['100'] + patternFreqs['101'], patternFreqs['110'] + patternFreqs['111']]
	colSums = [patternFreqs['000'] + patternFreqs['010'] + patternFreqs['100'] + patternFreqs['110'], patternFreqs['001'] + patternFreqs['011'] + patternFreqs['101'] + patternFreqs['111']]

	print '{0}:'.format(formatType)
	print '      |  0  |  1  || Total'
	print '--------------------------'
	print '   00 | {:<3} | {:<3} || {:<3}'.format(patternFreqs['000'], patternFreqs['001'], rowSums[0])
	print '--------------------------'
	print '   01 | {:<3} | {:<3} || {:<3}'.format(patternFreqs['010'], patternFreqs['011'], rowSums[1])
	print '--------------------------'
	print '   10 | {:<3} | {:<3} || {:<3}'.format(patternFreqs['100'], patternFreqs['101'], rowSums[2])
	print '--------------------------'
	print '   11 | {:<3} | {:<3} || {:<3}'.format(patternFreqs['110'], patternFreqs['111'], rowSums[3])
	print '--------------------------'
	print '--------------------------'
	print 'Total | {:<3} | {:<3} || {:<3}\n'.format(colSums[0], colSums[1], numBrackets * 4)

	chiSquare = 0
	nObservations = numBrackets * 4
	for r in range(len(rowSums)):
		for c in range(len(colSums)):
			expFreq = rowSums[r] * colSums[c] * 1.0 / nObservations
			obsFreq = patternFreqs[patterns[2 * r + c]] * 1.0
			chiSquare += (obsFreq - expFreq) ** 2 / expFreq

	print 'c^2: {:<6.4f}\n\n'.format(chiSquare)