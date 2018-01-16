#!/usr/bin/env python
import sys
from Utils.bracketUtils import testPairwiseIndependence

# This script tests every pair of bit positions in the region 
# for independence, pooling across all four regions.

outputFilename = str(sys.argv[1])

# Test all possible pairs in region
total = 0
nBits = 15
formats = ['TTT', 'TTF', 'TFT', 'TFF', 'FTT', 'FTF', 'FFT', 'FFF']

with open(outputFilename, 'w') as outputFile:
	for formatType in formats:
		count = 0
		for i in range(nBits):
			for j in range(i + 1, nBits):
				count += testPairwiseIndependence(i, j, formatType, outputFile, True)
		total += count
		print '{0}: count = {1}'.format(formatType, count)

print 'Total = {0}'.format(total)

