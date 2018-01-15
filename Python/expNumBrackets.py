#!/usr/bin/env python
import json
import os.path
import sys
from math import sqrt

from Utils.bracketClassDefinitions import Bracket
from Utils.bracketClassDefinitions import Region
from Utils.bracketClassDefinitions import buildBracketFromJson

# This script computes the expected number of brackets that must
# be generated to get a perfect bracket.

print '\n\nExpected # of Brackets to Generate for One Perfect Bracket'
print '----------------------------------------------------------'

formats = ['TTT', 'TTF', 'TFT', 'TFF', 'FTT', 'FTF', 'FFT', 'FFF']
numBrackets = 33

for formatType in formats:
	filename = 'Brackets/{0}/allBrackets{0}_metadata.json'.format(formatType)
	with open(filename, 'r') as inputFile:
		jsonData = inputFile.read().replace('\n', '')
	jsonToPython = json.loads(jsonData)
	sumVector = jsonToPython['sumOfBrackets']
	nBits = len(sumVector)

	total = 1.0

	for i in range(nBits):
		count = sumVector[i]
		p = count * 1.0 / numBrackets
		maxVal = -1
		if p != 1 and p != 0:
			maxVal = max(1 / p, 1 / (1-p))
			total *= maxVal
		# print '{0}: count = {1}, p = {2:5.2f}, max(1/p, 1/(1-p)) = {3:5.2f}'.format(i, count, p, maxVal)
		

	print '{0}: {1:5.2E} brackets\n'.format(formatType, total)

