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
patterns = ['0000', '0001', '0010', '0011', '0100', '0101', '0110', '0111', '1000', '1001', '1010', '1011', '1100', '1101', '1110', '1111']
nPatterns = len(patterns)

for formatType in formats:
	patternFreqs = dict(zip(patterns, [0 for i in range(nPatterns)]))
	filename = 'Brackets/{0}/allBrackets{0}.json'.format(formatType)
	with open(filename, 'r') as inputFile:
		jsonData = inputFile.read().replace('\n', '')
	jsonToPython = json.loads(jsonData)
	bracketList = jsonToPython['brackets']
	numBrackets = len(bracketList)

	for i in range(numBrackets):
		bracketDict = bracketList[i]['bracket']
		bracket = buildBracketFromJson(bracketDict)
		offset = 15
		finalGames = ''
		for region in range(4):
			finalGames += bracket.fullVector[14 + region * offset]
		patternFreqs[finalGames] = patternFreqs[finalGames] + 1

	# rowSums = [patternFreqs['000'] + patternFreqs['001'], patternFreqs['010'] + patternFreqs['011'], patternFreqs['100'] + patternFreqs['101'], patternFreqs['110'] + patternFreqs['111']]
	# colSums = [patternFreqs['000'] + patternFreqs['010'] + patternFreqs['100'] + patternFreqs['110'], patternFreqs['001'] + patternFreqs['011'] + patternFreqs['101'] + patternFreqs['111']]
	# nObservations = numBrackets * numRegions

	print '{0}: Regional Finals GOF Test'.format(formatType)
	print patternFreqs

	expFreq = numBrackets / nPatterns
	chiSquare = 0

	for i in range(nPatterns):
		chiSquare += (patternFreqs[patterns[i]] - expFreq) ** 2 / expFreq

	print 'chi-square value = {0}\n\n'.format(chiSquare)

	# print '{0}: Bits {1} and {2} vs. Bit {3}'.format(formatType, pos1, pos2, pos3)
	# print '      |  0  |  1  || Total'
	# print '--------------------------'
	# print '   00 | {:<3} | {:<3} || {:<3}'.format(patternFreqs['000'], patternFreqs['001'], rowSums[0])
	# print '--------------------------'
	# print '   01 | {:<3} | {:<3} || {:<3}'.format(patternFreqs['010'], patternFreqs['011'], rowSums[1])
	# print '--------------------------'
	# print '   10 | {:<3} | {:<3} || {:<3}'.format(patternFreqs['100'], patternFreqs['101'], rowSums[2])
	# print '--------------------------'
	# print '   11 | {:<3} | {:<3} || {:<3}'.format(patternFreqs['110'], patternFreqs['111'], rowSums[3])
	# print '--------------------------'
	# print '--------------------------'
	# print 'Total | {:<3} | {:<3} || {:<3}\n'.format(colSums[0], colSums[1], nObservations)

	# chiSquare = 0
	# for r in range(len(rowSums)):
	# 	for c in range(len(colSums)):
	# 		expFreq = rowSums[r] * colSums[c] * 1.0 / nObservations
	# 		# if expFreq == 0: # This hack dodges division by zero
	# 		# 	expFreq = 0.00000001
	# 		obsFreq = patternFreqs[patterns[2 * r + c]] * 1.0
	# 		chiSquare += (obsFreq - expFreq) ** 2 / expFreq

	# print 'c^2: {:<6.4f}\n\n'.format(chiSquare)