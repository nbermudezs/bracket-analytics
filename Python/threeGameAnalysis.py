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
# first two game positions given vs. the third game position.

formats = ['TTT', 'TTF', 'TFT', 'TFF', 'FTT', 'FTF', 'FFT', 'FFF']
patterns = ['000', '001', '010', '011', '100', '101', '110', '111']

pos1 = int(sys.argv[1])
pos2 = int(sys.argv[2])
pos3 = int(sys.argv[3])
pooled = True

if len(sys.argv) > 4:
	pooled = bool(sys.argv[4])

numRegions = 4
if not pooled:
	numRegions = 1

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
			threeGames += bracket.fullVector[pos1 + offset]
			threeGames += bracket.fullVector[pos2 + offset]
			threeGames += bracket.fullVector[pos3 + offset]
			patternFreqs[threeGames] = patternFreqs[threeGames] + 1

	rowSums = [patternFreqs['000'] + patternFreqs['001'], patternFreqs['010'] + patternFreqs['011'], patternFreqs['100'] + patternFreqs['101'], patternFreqs['110'] + patternFreqs['111']]
	colSums = [patternFreqs['000'] + patternFreqs['010'] + patternFreqs['100'] + patternFreqs['110'], patternFreqs['001'] + patternFreqs['011'] + patternFreqs['101'] + patternFreqs['111']]

	print '{0}: Bits {1} and {2} vs. Bit {3}'.format(formatType, pos1, pos2, pos3)
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