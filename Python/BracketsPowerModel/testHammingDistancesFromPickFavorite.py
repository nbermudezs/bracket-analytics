#!/usr/bin/env python
import json
from bracketClassDefinitions import Bracket
from bracketClassDefinitions import Region
from bracketClassDefinitions import buildBracketFromJson

with open('allBracketsTTT.json', 'r') as inputFile:
	jsonData = inputFile.read().replace('\n', '')

dataPyDict = json.loads(jsonData)
bracketList = dataPyDict['brackets']

# First 60 bits of Pick Favorite bracket string
pfBracketString = '111111111000101111111111000101111111111000101111111111000101'
#111111111000101
#111111111000101
#111111111000101
#111111111000101

# 2015:
#111111111101111
#111110011010101
#111101110001000
#111100111110101

pfVector = [int(pfBracketString[i]) for i in range(len(pfBracketString))]

for bracketDict in bracketList:
	bracket = buildBracketFromJson(bracketDict['bracket'])
	actualFirst60 = bracket.fullVector[0:60]
	actualVector = [int(actualFirst60[i]) for i in range(len(actualFirst60))]
	hammingDist = sum(ch1 != ch2 for ch1, ch2 in zip(pfVector, actualVector))
	print '{0}: {1}'.format(bracket.year, hammingDist)
	# print '{0:<20s}{1}'.format('Actual: ', actualFirst60)
	# print '{0:<20s}{1}'.format('Pick Fav.: ', pfBracketString)
	# print ''
