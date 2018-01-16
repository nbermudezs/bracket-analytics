#!/usr/bin/env python
import sys
from Utils.bracketUtils import testPairwiseIndependence

# This script tests every pair of bit positions for 
# independence. 

outputFilename = str(sys.argv[1])

# Version where it's limited to direct connections in the bracket 'tree'
# total = 0
# nBits = 63
# formats = ['TTT', 'TTF', 'TFT', 'TFF', 'FTT', 'FTF', 'FFT', 'FFF']

# with open(outputFilename, 'w') as outputFile:
# 	for formatType in formats:
# 		count = 0
# 		for i in range(63):
# 			regionIndex = int(i / 15)
# 			regionStart = regionIndex * 15
# 			for j in range(i + 1, regionStart + 14):
# 				count += testPairwiseIndependence(i, j, formatType, outputFile)
# 		total += count
# 		print '{0}: count = {1}'.format(formatType, count)

# print 'Total = {0}'.format(total)


# Test all possible pairs
total = 0
nBits = 60
formats = ['TTT', 'TTF', 'TFT', 'TFF', 'FTT', 'FTF', 'FFT', 'FFF']

with open(outputFilename, 'w') as outputFile:
	for formatType in formats:
		outputFile.write(formatType)
		outputFile.write('\n')
		count = 0
		for i in range(nBits):
			for j in range(i + 1, nBits):
				count += testPairwiseIndependence(i, j, formatType, outputFile)
		total += count
		print '{0}: count = {1}'.format(formatType, count)
	outputFile.write('\n')

print 'Total = {0}'.format(total)

