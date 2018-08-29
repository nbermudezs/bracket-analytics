#!/usr/bin/env python
import json
import os.path
import random
import sys
from math import log
from bracketClassDefinitions import Bracket
from bracketClassDefinitions import Region
from bracketClassDefinitions import buildBracketFromJson
from scoringUtils import applyRoundResults
from scoringUtils import scoreBracket

# Author:
#     Ian Ludden
#
# Date created:
#     16 Feb 2018
#
# Last modified:
#     24 Feb 2018
#
# In this version, the same alpha value is 
# used for all games in a given round (except for R1) 
# and the alpha values are generated uniformly
# at random from small ranges based on weighted averages
# from past tournaments. 
#
# For Round 1, the alpha value computed from past outcomes
# for each particular matchup is used. 

# This function generates a 63-element list of 0s and 1s
# to represent game outcomes in a bracket. The alphaVals
# list specifies what alpha value to use for each round.
# For round i, alphaVals[i] is used. 
# (The 0-th index is unused.)
def generateBracket(alphaVals, year, isFixedFirstRoundAlphas, K):
	bracket = []
	regionWinners = []

	random.seed()

	# Loop through all regional rounds
	for region in range(4):
		seeds = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]
		for roundNum in range(1, 5):
			numGames = int(len(seeds) / 2)
			newSeeds = []
			for gameNum in range(numGames):
				s1 = seeds[2 * gameNum]
				s2 = seeds[2 * gameNum + 1]
				alpha = getAlpha(s1, s2, roundNum, alphaVals, year, isFixedFirstRoundAlphas, K)
				s1a = (s1 * 1.0) ** alpha
				s2a = (s2 * 1.0) ** alpha
				p = s2a / (s1a + s2a)
				if random.random() <= p:
					bracket.append(1)
					newSeeds.append(s1)
				else:
					bracket.append(0)
					newSeeds.append(s2)
			seeds = newSeeds
		regionWinners.append(seeds[0])

	# Round 5:
	semiFinalists = []
	for gameNum in range(2):
		s1 = regionWinners[2 * gameNum]
		s2 = regionWinners[2 * gameNum + 1]
		alpha = alphaVals[5]
		s1a = (s1 * 1.0) ** alpha
		s2a = (s2 * 1.0) ** alpha
		p = s2a / (s1a + s2a)
		if random.random() <= p:
			bracket.append(1)
			semiFinalists.append(s1)
		else:
			bracket.append(0)
			semiFinalists.append(s2)

	# Round 6:
	s1 = semiFinalists[0]
	s2 = semiFinalists[1]
	alpha = alphaVals[6]
	s1a = (s1 * 1.0) ** alpha
	s2a = (s2 * 1.0) ** alpha
	p = s2a / (s1a + s2a)
	if random.random() <= p:
		bracket.append(1)
	else:
		bracket.append(0)

	return bracket


# This function returns the alpha value to use for 
# predicting the outcome of a game in the given round
# between the given seeds s1, s2. For this version, it
# is only used for Round 1, because the other rounds
# use a fixed alpha value.
# 
# Note that K indicates the range (avg +/- K/2) from
# which the alpha value will be sampled (if 
# isFixedFirstRoundAlphas is false). 
def getAlpha(s1, s2, roundNum, alphaVals, year, isFixedFirstRoundAlphas, K):
	# Round 1 alpha values from 2013 through 2017, 
	# rounded to two decimal places
	alpha116 = [2, 2, 2, 2, 2]
	alpha215 = [1.43, 1.36, 1.38, 1.40, 1.34]
	alpha314 = [1.16, 1.14, 1.13, 1.07, 1.06]
	alpha413 = [1.10, 1.10, 1.13, 1.17, 1.16]
	alpha512 = [0.76, 0.69, 0.62, 0.68, 0.66]
	alpha611 = [1.10, 1.12, 1.08, 1.04, 0.95]
	alpha710 = [1.12, 1.18, 1.23, 1.29, 1.25]
	alpha89 = [-0.61, -0.59, -0.28, 0.27, 0]

	if roundNum == 1:
		centerVal = 0
		if s1 == 1:
			centerVal = alpha116[year - 2013]
		elif s1 == 2:
			centerVal = alpha215[year - 2013]
		elif s1 == 3:
			centerVal = alpha314[year - 2013]
		elif s1 == 4:
			centerVal = alpha413[year - 2013]
		elif s1 == 5:
			centerVal = alpha512[year - 2013]
		elif s1 == 6:
			centerVal = alpha611[year - 2013]
		elif s1 == 7:
			centerVal = alpha710[year - 2013]
		elif s1 == 8:
			centerVal = alpha89[year - 2013]
		else:
			centerVal = 0 # This should never happen, since all cases are covered

		if isFixedFirstRoundAlphas:
			return centerVal

		offset = random.random() * K - (K / 2)
		return centerVal + offset

	# Use the given fixed alpha value for Rounds 2-6
	return alphaVals[roundNum]


# This function computes how many picks a bracket
# got correct given the bracket's score vector.
def calcCorrectPicks(scoreVector):
	numCorrectPicks = 0
	for roundNum in range(1, 7):
		numCorrectPicks += scoreVector[roundNum] / (10 * (2 ** (roundNum - 1)))
	return numCorrectPicks
	

# This function generates and scores brackets
# for the given year using the given fixed alpha values for each round.
# It prints the results in JSON format. 
def performFixedAlphaExperiments(numTrials, year, isFixedFirstRoundAlphas, isFixedK, rangeK, batchNumber):
	inputFilename = 'allBracketsTTT.json'
	with open(inputFilename, 'r') as inputFile:
		dataJson = inputFile.read().replace('\n', '')

	dataPyDict = json.loads(dataJson)
	bracketList = dataPyDict['brackets']

	bracket = None

	for bracketDict in bracketList:
		bracket = buildBracketFromJson(bracketDict['bracket'])
		if bracket.year == year:
			break

	correctVector = [int(bracket.fullVector[i]) for i in range(len(bracket.fullVector))]

	# 0-th index is unused for easy indexing
	alphaAvg = [0, 1.2, 1.0, 1.0, 0.3, 1.3, 1.8]

	# Weighted average alpha values per round per year, rounded to two dec. places
	if year == 2013:
		alphaAvg = [0, 1.01, 1.10, 0.91, 0.36, 1.00, 1.54]
	elif year == 2014:
		alphaAvg = [0, 1.00, 1.03, 0.90, 0.23, 1.03, 1.54]
	elif year == 2015:
		alphaAvg = [0, 1.04, 1.03, 0.86, 0.19, 0.93, 1.55]
	elif year == 2016:
		alphaAvg = [0, 1.12, 1.02, 0.88, 0.22, 0.97, 1.57]
	elif year == 2017:
		alphaAvg = [0, 1.05, 1.01, 0.90, 0.14, 1.00, 1.35]
	else:
		alphaAvg = [0, 1.2, 1.0, 1.0, 0.3, 1.3, 1.8] # should not reach this; old guesses for alpha values

	brackets = []

	for n in range(numTrials):
		# Sample to get new alpha values for each trial
		if isFixedK:
			alphaSwing = [rangeK for i in range(7)]
		else:
			alphaSwing = []
			for i in range(7):
				swingVal = random.random() * rangeK
				alphaSwing.append(swingVal)

		alphaVals = [0]
		for roundNum in range(1, 7):
			roundAlpha = alphaAvg[roundNum]
			roundAlpha += (2 * random.random() - 1) * alphaSwing[roundNum]
			alphaVals.append(roundAlpha)

		newBracketVector = generateBracket(alphaVals, year, isFixedFirstRoundAlphas, alphaSwing[1]) # We pass in the K that will be used for R1, if needed
		newBracketScore = scoreBracket(newBracketVector, correctVector)
		numCorrectPicks = calcCorrectPicks(newBracketScore)

		newBracketString = ''.join(str(outcome) for outcome in newBracketVector)
		brackets.append({'bracketVector': newBracketString, 'score': newBracketScore, 'correctPicks': numCorrectPicks, 'alphaVals': ['{0:5.2f}'.format(alphaVals[j]) for j in range(1, 7)]})

	bracketListDict = {'year': year, 'actualBracket': bracket.fullVector, 'brackets': brackets}

	outputFilename = 'Experiments/OneMillionTrials/Batch{5:02d}/generatedBrackets_{0}_{1}_{2}_{3}_{4:.2f}.json'.format(numTrials, year, isFixedFirstRoundAlphas, isFixedK, rangeK, batchNumber)
	with open(outputFilename, 'w') as outputFile:
		outputFile.write(json.dumps(bracketListDict))


# This script runs randomly-generated-alpha-value experiments 
# for the 2013 through 2017 tournaments. 
isFixedFirstRoundAlphas = int(sys.argv[2]) == 1
isFixedK = int(sys.argv[3]) == 1
rangeK = float(sys.argv[4])
batchNumber = int(sys.argv[5])

numTrials = int(sys.argv[1])
for year in range(2013, 2018):
	performFixedAlphaExperiments(numTrials, year, isFixedFirstRoundAlphas, isFixedK, rangeK, batchNumber)

