#!/usr/bin/env python
import sys
from Utils.bracketUtils import testPairwiseIndependence

# This script tests every pair of bit positions for 
# independence. 

outputFilename = str(sys.argv[1])

with open(outputFilename, 'w') as outputFile:
	for i in range(4):
		offset = i * 15
		for pos1 in range(1, 15):
			for pos2 in range(pos1 + 1, 15):
				testPairwiseIndependence(pos1 + offset, pos2 + offset, outputFile)
			for pos2 in range(60, 63):
				testPairwiseIndependence(pos1 + offset, pos2, outputFile)
