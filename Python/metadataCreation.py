#!/usr/bin/env python
import json
import os.path
import sys

from bracketClassDefinitions import Bracket
from bracketClassDefinitions import Region
from bracketClassDefinitions import buildBracketFromJson
from bracketUtils import convertRegionVector
from bracketUtils import writeBracket

inputFilename = str(sys.argv[1])

inputFilenameNoExtension = inputFilename[0:inputFilename.find('.')]

outputFilename = '{0}_metadata.json'.format(inputFilenameNoExtension)

outputFile = open(outputFilename, 'w')

outputFile.write('{')

with open(inputFilename, 'r') as inputFile:
	jsonData = inputFile.read().replace('\n', '')

jsonToPython = json.loads(jsonData)
bracketList = jsonToPython['brackets']

numBrackets = len(bracketList)

fullVectorSum = [0 for i in range(63)]

for i in range(numBrackets):
	bracketDict = bracketList[i]['bracket']
	bracket = buildBracketFromJson(bracketDict)
	
	for j in range(63):
		if bracket.fullVector[j] == '1':
			fullVectorSum[j] += 1

outputFile.write('"sumOfBrackets": ')
outputFile.write(json.dumps(fullVectorSum))
outputFile.write('}')

outputFile.close()
