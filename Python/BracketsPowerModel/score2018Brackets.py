#!/usr/bin/env python
import sys
import csv
from scoringUtils import getActualBracketVector
from scoringUtils import scoreBracket

bracketsFilename = sys.argv[1]

# Will only print brackets at or above this minimum score 
minScore = 0
if len(sys.argv) > 2:
	minScore = int(sys.argv[2])

actualVector = getActualBracketVector(2018)

print 'Vector,Score,R64,R32,S16,E8,F4,NCG'

with open(bracketsFilename, 'rb') as csvfile:
	reader = csv.reader(csvfile)

	for row in reader:
		if len(row) == 0:
			continue
		bracketString = str(row[0])
		bracketVector = [int(bracketString[i]) for i in range(len(bracketString))]
		bracketScore = scoreBracket(bracketVector, actualVector)

		if bracketScore[0] >= minScore:
			print '"{0}",{1},{2},{3},{4},{5},{6},{7}'.format(bracketString, bracketScore[0], bracketScore[1], bracketScore[2], bracketScore[3], bracketScore[4], bracketScore[5], bracketScore[6])
