#!/usr/bin/env python
import json
import os.path
import sys

from Utils.bracketClassDefinitions import Bracket
from Utils.bracketClassDefinitions import Region
from Utils.bracketClassDefinitions import buildBracketFromJson
from Utils.bracketUtils import countWinsPerRound


# This script measures how far each seed advances in the tournament. 
# It should reproduce the results at 
# http://bracketodds.cs.illinois.edu/seedadv.html
# The input file should be allBracketsTTT.json.

inputFilename = str(sys.argv[1])

with open(inputFilename, 'r') as inputFile:
	jsonData = inputFile.read().replace('\n', '')

jsonToPython = json.loads(jsonData)
bracketList = jsonToPython['brackets']

numBrackets = len(bracketList)

numSeeds = 16
numRounds = 6
winCounts = [[0 for i in range(numSeeds)] for i in range(numRounds)]

for i in range(numBrackets):
	bracketDict = bracketList[i]['bracket']
	bracket = buildBracketFromJson(bracketDict)
	bracketWinCounts = countWinsPerRound(bracket)
	for j in range(numRounds):
		for k in range(numSeeds):
			winCounts[j][k] = winCounts[j][k] + bracketWinCounts[j][k]

print 'Seed | R64 | R32 | S16 | E8  | F4  | NF '
print '----------------------------------------'
for i in range(numSeeds):
	print '{:<4} | {:<3} | {:<3} | {:<3} | {:<3} | {:<3} | {:<3}'.format(i + 1, winCounts[0][i], winCounts[1][i], winCounts[2][i], winCounts[3][i], winCounts[4][i], winCounts[5][i])
print '----------------------------------------\n'

print 'Seed | Expected Number of Wins'
print '------------------------------'
for i in range(numSeeds):
	freqWinCount = [0 for numWins in range(numRounds + 1)]
	freqWinCount[0] = numBrackets * 4 - winCounts[0][i]
	for j in range(1, numRounds):
		freqWinCount[j] = winCounts[j - 1][i] - winCounts[j][i]
	freqWinCount[-1] = winCounts[-1][i]

	total = sum(freqWinCount)
	if total == 0:
		expNumWins = 0
	else:
		expNumWins = sum([freqWinCount[j] * j for j in range(len(freqWinCount))]) * 1.0 / total
	print '{:<4} | {:<10.2f}'.format(i + 1, expNumWins)
print '------------------------------'