#!/usr/bin/env python
import csv
import json
import os.path
import random
import sys
from math import log
from bracketClassDefinitions import Bracket
from bracketClassDefinitions import Region
from bracketClassDefinitions import SimpleBracket
from bracketClassDefinitions import buildBracketFromJson
import numpy as np

# 
# Author: 	Ian Ludden
# Date: 	13 Mar 2018
# Modified: 13 Mar 2018
# 

# "Static" lists
regions = ['W', 'X', 'Y', 'Z']
r2g1 = [1, 16, 8, 9]
r2g2 = [5, 12, 4, 13]
r2g3 = [6, 11, 3, 14]
r2g4 = [7, 10, 2, 15]

r3g1 = r2g1 + r2g2
r3g2 = r2g3 + r2g4

# Returns the estimated probability that s1 beats s2
def getP(s1, s2, model, year, roundNum):
	alpha = getAlpha(s1, s2, model, year, roundNum)
	s1a = (s1 * 1.0) ** alpha
	s2a = (s2 * 1.0) ** alpha
	return s2a / (s1a + s2a)

# This function returns the alpha value to use for 
# predicting the outcome of a game in the given round
# between the given seeds s1, s2. For this version, it
# is only used for Round 1, because the other rounds
# use a fixed alpha value.
# 
# Note that K indicates the range (avg +/- K/2) from
# which the alpha value will be sampled (if 
# isFixedFirstRoundAlphas is false). 
def getAlpha(s1, s2, model, year, roundNum):
	# Round 1 alpha values from 2013 through 2018, 
	# rounded to two decimal places (2 is the default value).
	# First dimension is better seed number (1 at index 1),
	# second dimension is year (2013 at index 0)
	round1MatchupAlphaAvgsByYear = [
		[],
		[2, 2, 2, 2, 2, 2],
		[1.43, 1.36, 1.38, 1.40, 1.34, 1.36],
		[1.16, 1.14, 1.13, 1.07, 1.06, 1.08],
		[1.10, 1.10, 1.13, 1.17, 1.16, 1.19],
		[0.76, 0.69, 0.62, 0.68, 0.66, 0.68],
		[1.10, 1.12, 1.08, 1.04, 0.95, 0.87],
		[1.12, 1.18, 1.23, 1.29, 1.25, 1.30],
		[-0.61, -0.59, -0.28, 0.27, 0, 0.26]]

	# Round 1-6 weighted avg. alpha values from 
	# 2013 through 2017. 
	# First dimension is year (2013 at index 0), 
	# second dimension is round number (R1 at index 1)
	alphaAvgsByYear = [
		[0, 1.01, 1.10, 0.91, 0.36, 0.67, 1.41],
		[0, 1.00, 1.03, 0.90, 0.23, 0.70, 1.42],
		[0, 1.04, 1.03, 0.86, 0.19, 0.58, 1.44],
		[0, 1.12, 1.02, 0.88, 0.22, 0.61, 1.44],
		[0, 1.05, 1.01, 0.90, 0.14, 0.64, 1.17],
		[0, 1.09, 1.05, 0.91, 0.12, 0.67, 1.17]]

	roundName = 'round{0}'.format(roundNum)
	roundInfo = model[roundName]

	isWeightedAverage = "True" in roundInfo['isWeightedAverage']
	isMatchupSpecific = "True" in roundInfo['isMatchupSpecific']

	if isMatchupSpecific:
		if roundNum > 1:
			sys.exit("Sorry, matchup-specific alpha values for Rounds 2-6 are not implemented.")

		betterSeed = min(s1, s2)
		return round1MatchupAlphaAvgsByYear[betterSeed][year - 2013]

	if isWeightedAverage:
		return alphaAvgsByYear[year - 2013][roundNum]

	return roundInfo['fixedAlpha']

# This function computes the round in which the two given
# teams may meet.
def getRound(s1, s2):
	s1Num = int(s1[1:3])
	s1Region = regions.index(s1[0])
	s2Num = int(s2[1:3])
	s2Region = regions.index(s2[0])

	if s1Region == s2Region:
		if s1Num == 17 - s2Num:
			return 1
		elif (s1Num in r2g1 and s2Num in r2g1) or (s1Num in r2g2 and s2Num in r2g2) or (s1Num in r2g3 and s2Num in r2g3) or (s1Num in r2g4 and s2Num in r2g4):
			return 2
		elif (s1Num in r3g1 and s2Num in r3g1) or (s1Num in r3g2 and s2Num in r3g2):
			return 3
		else:
			return 4
	elif (s1Region < 2 and s2Region < 2) or (s1Region >= 2 and s2Region >= 2):
		return 5
	else:
		return 6

# This script generates probability predictions for the 
# winner of every possible matchup in the tournament. 
# The results will be submitted to the Kaggle competition.

teamsFilename = 'Kaggle2018/Workspace/NCAATourneySeeds.csv'
year = 2018

# Load models
modelFilename = 'models.json'
with open(modelFilename, 'r') as modelFile:
	modelsDataJson = modelFile.read().replace('\n', '')

modelsDict = json.loads(modelsDataJson)
modelsList = modelsDict['models']

# Only using model5, the Reverse Model 
# with R1 matchup-specific, others wt. avg.
model = modelsList[0]

with open(teamsFilename, 'r') as teamsFile:
	reader = csv.reader(teamsFile)

	teamSeeds = []
	teamIDs = []

	for row in reader:
		if len(row) == 0:
			continue
		teamSeeds.append(row[1])
		teamIDs.append(int(row[2]))

print 'ID,Pred'
for i in range(len(teamSeeds)):
	s1 = teamSeeds[i]
	s1Num = int(s1[1:3])
	id1 = teamIDs[i]

	for j in range(i + 1, len(teamSeeds)):
		s2 = teamSeeds[j]
		s2Num = int(s2[1:3])

		roundNum = getRound(s1, s2)
		# print '{0:<5} vs. {1:<5} in Round {2}'.format(s1, s2, roundNum)
		# Get probability that s1 beats s2 in Round 'roundNum'
		p = getP(s1Num, s2Num, model, year, roundNum)

		# Let's just assume the 1-seeds win, because everyone else will
		if s1Num == 1 and s2Num == 16:
			p = 1
		if s1Num == 16 and s2Num == 1:
			p = 0

		id2 = teamIDs[j]

		# Scale up probability favorite wins by 20%
		if p < 1 and p > 0:
			if s1Num < s2Num:
				p = min(p * 1.2, 0.99)
			if s2Num < s1Num:
				p = p / 1.2

		# Print predicted probability that team with lower id beats
		# team with higher id
		if id1 > id2:
			print '{0}_{1}_{2},{3:.4f}'.format(year, id2, id1, 1-p)
		else:
			print '{0}_{1}_{2},{3:.4f}'.format(year, id1, id2, p)

