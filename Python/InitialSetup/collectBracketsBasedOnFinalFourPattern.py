#!/usr/bin/env python
import json
import os.path
import sys

from bracketClassDefinitions import Bracket
from bracketClassDefinitions import Region
from bracketClassDefinitions import buildBracketFromJson
from bracketUtils import writeBracket

inputFilename = str(sys.argv[1])
pattern = str(sys.argv[2])

inputFilenameNoExtension = inputFilename[0:inputFilename.find('.')]

outputFilename = '{0}{1}.json'.format(inputFilenameNoExtension, pattern)

outputFile = open(outputFilename, 'w')

outputFile.write('{')
outputFile.write('"brackets": [')

with open(inputFilename, 'r') as inputFile:
	jsonData = inputFile.read().replace('\n', '')

jsonToPython = json.loads(jsonData)
bracketList = jsonToPython['brackets']

numBrackets = len(bracketList)

found = False

for i in range(0, numBrackets):
	bracketDict = bracketList[i]['bracket']
	bracket = buildBracketFromJson(bracketDict)

	if bracket.finalFour == pattern:
		if found:
			outputFile.write(',')
		else:
			found = True
		writeBracket(outputFile, bracket)

outputFile.write(']')
outputFile.write('}')

outputFile.close()
