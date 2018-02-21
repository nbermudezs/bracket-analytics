#!/usr/bin/env python
import json
import os.path
import sys
from math import sqrt

from Utils.bracketClassDefinitions import Bracket
from Utils.bracketClassDefinitions import Region
from Utils.bracketClassDefinitions import buildBracketFromJson
from Utils.bracketUtils import writeBracket

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
print 'Final Four with Nat\'l Championship:'
print patterns
print patternFreqs
print 'X^2: {0}\n\n'.format(chiSquare)

# GOF Test: final four games vs. uniform
ffPatterns = ['00', '01', '10', '11']
ffPatternFreqs = [0 for i in range(len(ffPatterns))]

filename = 'Brackets/TTT/allBracketsTTT.json'
with open(filename, 'r') as file:
	jsonData = file.read().replace('\n', '')

bracketsDict = json.loads(jsonData)
brackets = bracketsDict['brackets']
for bracket in brackets:
	ff = bracket['bracket']['finalfour']
	index = int(ff[1]) * 2 + int(ff[0])
	ffPatternFreqs[index] = ffPatternFreqs[index] + 1

expFreq = numBrackets * 1.0 / len(ffPatterns)
ffChiSquare = 0

for i in range(len(ffPatterns)):
	ffChiSquare += (ffPatternFreqs[i] - expFreq) ** 2 / expFreq

print 'Final Four Only:'
print ffPatterns
print ffPatternFreqs
print 'X^2: {0}\n\n'.format(ffChiSquare)

# GOF Test: Sum of last three bits vs. binomial distr.
actualFreqs = []
actualFreqs.append(patternFreqs[0])
actualFreqs.append(patternFreqs[1] + patternFreqs[2] + patternFreqs[4])
actualFreqs.append(patternFreqs[3] + patternFreqs[5] + patternFreqs[6])
actualFreqs.append(patternFreqs[7])

binomDist = [1, 3, 3, 1]
expectedFreqs = [binomDist[i] / 8.0 * 33 for i in range(4)]

sumChiSquare = 0
for i in range(4):
	sumChiSquare += (actualFreqs[i] - expectedFreqs[i]) ** 2 / expectedFreqs[i]

print 'Sum of Last Three Bits vs. Binomial(n = 3, p = 0.5):'
print '          {:<5d} {:<5d} {:<5d} {:<5d}'.format(0, 1, 2, 3)
print 'Expected: {:<5.2f} {:<5.2f} {:<5.2f} {:<5.2f}'.format(expectedFreqs[0], expectedFreqs[1], expectedFreqs[2], expectedFreqs[3])
print 'Actual:   {:<5d} {:<5d} {:<5d} {:<5d}'.format(actualFreqs[0], actualFreqs[1], actualFreqs[2], actualFreqs[3])
print 'X^2: {0}'.format(sumChiSquare)
print '\n'




# GOF Test: First 16 years



# GOF Test: Most recent 16 years