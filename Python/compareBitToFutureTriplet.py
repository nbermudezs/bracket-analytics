#!/usr/bin/env python
import json
import os.path
import sys

from Utils.bracketClassDefinitions import Bracket
from Utils.bracketClassDefinitions import Region
from Utils.bracketClassDefinitions import buildBracketFromJson
from Utils.bracketUtils import writeBracket
from pprint import pprint


# Build contingency tables for each R32 game versus 
# the following triplet, i.e., the two S16 games and the E8
# game for that region. 


def getS16E8Positions(r32Pos):
	region = r32Pos / 15
	if region == 0:
		return [12, 13, 14]

	if region == 1:
		return [27, 28, 29]

	if region == 2:
		return [42, 43, 44]

	# if region == 3:
	return [57, 58, 59]



def getPathPositions(r64Pos):
	region = r64Pos / 15
	offset = 15 * region
	pos = r64Pos - offset

	if pos < 2:
		path = [8, 12, 14]
	elif pos < 4:
		path = [9, 12, 14]
	elif pos < 6:
		path = [10, 13, 14]
	else:
		path = [11, 13, 14]

	return [path[i] + offset for i in range(len(path))]



def getR32S16Positions(r64Pos):
	region = r64Pos / 15
	offset = 15 * region
	pos = r64Pos - offset

	if pos < 4:
		triplet = [8, 9, 12]
	else:
		triplet = [10, 11, 13]

	return [triplet[i] + offset for i in range(len(triplet))]



def printTable(pos, triplet, freqs):
	print ',{0}\\{1}-{2}-{3},111,110,101,100,011,010,001,000,'.format(pos, triplet[0], triplet[1], triplet[2])
	print ',1,{0},{1},{2},{3},{4},{5},{6},{7}'.format(freqs['1_111'], freqs['1_110'], freqs['1_101'], freqs['1_100'], freqs['1_011'], freqs['1_010'], freqs['1_001'], freqs['1_000'])
	print ',0,{0},{1},{2},{3},{4},{5},{6},{7}'.format(freqs['0_111'], freqs['0_110'], freqs['0_101'], freqs['0_100'], freqs['0_011'], freqs['0_010'], freqs['0_001'], freqs['0_000'])
	print '\n'

bracketFormat = str(sys.argv[1]) # For now, just 'TTT' or 'FFF'

inputFilename = 'Brackets/{0}/allBrackets{0}.json'.format(bracketFormat)

with open(inputFilename, 'r') as inputFile:
	jsonData = inputFile.read().replace('\n', '')

jsonToPython = json.loads(jsonData)
bracketList = jsonToPython['brackets']

numBrackets = len(bracketList)

patterns3 = ['000', '001', '010', '011', '100', '101', '110', '111']
patterns1 = ['0', '1']

# Build patterns such as '1_010' as keys for tallying results
patterns = []
for i in patterns1:
	for j in patterns3:
		patterns.append('{0}_{1}'.format(i, j))

zeroList = [0 for i in patterns]

for pos in range(63):
	region = pos / 15
	offset = 15 * region
	posMod15 = pos - offset

	# Only looking at R64 and R32 positions
	if region >= 4 or posMod15 >= 12:
		continue

	print 'Position:,{0}'.format(pos)

	if posMod15 > 7:
		freqs_1 = dict(zip(patterns, zeroList)) # R32 vs. S16E8 triplet
		triplet_1 = getS16E8Positions(pos)

		for i in range(numBrackets):
			bracket = buildBracketFromJson(bracketList[i]['bracket'])
			bracketString = bracket.fullVector
			string_1 = '{0}{1}{2}'.format(bracketString[triplet_1[0]], bracketString[triplet_1[1]], bracketString[triplet_1[2]])
			
			string_1 = '{0}_{1}'.format(str(bracketString[pos]), string_1)

			freqs_1[string_1] += 1

		print 'R32 vs. S16/E8 Triplet:'
		printTable(pos, triplet_1, freqs_1)
		
		continue

	freqs_2 = dict(zip(patterns, zeroList)) # R64 vs. R32->S16->E8 path
	freqs_3 = dict(zip(patterns, zeroList)) # R64 vs. R32S16 triplet

	triplet_2 = getPathPositions(pos)
	triplet_3 = getR32S16Positions(pos)

	for i in range(numBrackets):
		bracket = buildBracketFromJson(bracketList[i]['bracket'])
		bracketString = bracket.fullVector

		string_2 = '{0}{1}{2}'.format(bracketString[triplet_2[0]], bracketString[triplet_2[1]], bracketString[triplet_2[2]])
		string_3 = '{0}{1}{2}'.format(bracketString[triplet_3[0]], bracketString[triplet_3[1]], bracketString[triplet_3[2]])

		string_2 = '{0}_{1}'.format(str(bracketString[pos]), string_2)
		string_3 = '{0}_{1}'.format(str(bracketString[pos]), string_3)

		freqs_2[string_2] += 1
		freqs_3[string_3] += 1

	print 'R64 vs. R32/S16/E8 Path:'
	printTable(pos, triplet_2, freqs_2)

	print 'R64 vs. R32/S16 Triplet:'
	printTable(pos, triplet_3, freqs_3)

