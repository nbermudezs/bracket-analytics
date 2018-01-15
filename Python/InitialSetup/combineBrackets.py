#!/usr/bin/env python
import json
import os.path
import sys

# from bracketClassDefinitions import Bracket
# from bracketClassDefinitions import Region
# from bracketClassDefinitions import buildBracket

startYear = int(sys.argv[1])
endYear = int(sys.argv[2])

outputFilename = 'allbrackets.json'
outputFile = open(outputFilename, 'w')

outputFile.write('{')
outputFile.write('"brackets": [')

for year in range(startYear, endYear + 1):
	filename = str(year) + '.json'

	if not os.path.isfile(filename):
		continue

	with open(filename, 'r') as bracketJsonFile:
		for line in bracketJsonFile:
			outputFile.write(line)

	if year != endYear:
		outputFile.write(',')

outputFile.write(']')
outputFile.write('}')

outputFile.close()
