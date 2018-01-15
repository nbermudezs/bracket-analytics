#!/usr/bin/env python
import json
import os.path
import sys
from math import sqrt

from bracketClassDefinitions import Bracket
from bracketClassDefinitions import Region
from bracketClassDefinitions import buildBracketFromJson
from bracketUtils import writeBracket

# This script runs a chi-squared goodness of fit test for the
# distribution of brackets across the eight final four patterns.

numBrackets = 33
expFreq = numBrackets * 1.0 / 8

patterns = ['000', '001', '010', '011', '100', '101', '110', '111']
patternFreqs = []
chiSquare = 0
for pattern in patterns:
	patternFilename = 'Brackets/TTT/allBracketsTTT{0}.json'.format(pattern)
	with open(patternFilename, 'r') as patternFile:
		jsonData = patternFile.read().replace('\n', '')
	jsonToPython = json.loads(jsonData)
	patternBrackets = jsonToPython['brackets']
	numPatternBrackets = len(patternBrackets)
	patternFreqs.append(numPatternBrackets)
	chiSquare += (numPatternBrackets - expFreq) ** 2 / expFreq
print patternFreqs
print 'X^2: {0}'.format(chiSquare)
