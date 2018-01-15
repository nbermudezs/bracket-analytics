#!/usr/bin/env python
import json
import os.path
import sys

from bracketClassDefinitions import Bracket
from bracketClassDefinitions import Region
from bracketClassDefinitions import buildBracketFromJson
from bracketUtils import convertRegionVector
from bracketUtils import writeBracket

inputFilename = 'Brackets/TTT/allBracketsTTT.json'

bracketFormat = str(sys.argv[1])

outputFilename = 'Brackets/{0}/allBrackets{0}.json'.format(bracketFormat)

outputFile = open(outputFilename, 'w')

outputFile.write('{')
outputFile.write('"brackets": [')

with open(inputFilename, 'r') as inputFile:
	jsonData = inputFile.read().replace('\n', '')

jsonToPython = json.loads(jsonData)
bracketList = jsonToPython['brackets']

numBrackets = len(bracketList)

for i in range(0, numBrackets):
	bracketDict = bracketList[i]['bracket']
	bracket = buildBracketFromJson(bracketDict)

	for region in bracket.regions:
		region.vector = convertRegionVector(region.vector, bracketFormat)

	bracket.fullVector = ''.join([bracket.regions[j].vector for j in range(0, 4)]) + bracket.finalFour

	writeBracket(outputFile, bracket)

	if i < numBrackets - 1:
		outputFile.write(',')

outputFile.write(']')
outputFile.write('}')

outputFile.close()
