#!/usr/bin/env python
import json
import os.path
import random
import sys
from math import log, ceil, floor
from samplingUtils import getTruncGeom, getE8SeedTop, getE8SeedBottom
from scoringUtils import applyRoundResults
from scoringUtils import getActualBracketVector
from scoringUtils import scoreBracket

# Author:
#     Ian Ludden
#
# Date created:
#     10 Apr 2018
#
# Last modified:
#     10 Apr 2018
#
# In this version, the Elite Eight seeds are sampled first.
# The remaining games are then decided using the (forward) Power Model.
# 
# Also, the Round 1 alpha values are grouped as:
# (1, 16) alone
# (2, 15) alone
# (3, 14), (4, 13) 
# (5, 12), (6, 11), (7, 10)
# (8, 9) alone and fixed at 0.5 probability (alpha = 0)
# 
# Also, all weighted alpha values are now based on proportions 
# for weighted seeds (rather than weighting after computing 
# matchup-specific alpha values). 

# Returns the estimated probability that s1 beats s2
def getP(s1, s2, model, year, roundNum):
	alpha = getAlpha(s1, s2, model, year, roundNum)
	s1a = (s1 * 1.0) ** alpha
	s2a = (s2 * 1.0) ** alpha
	return s2a / (s1a + s2a)

# This function generates a 63-element list of 0s and 1s
# to represent game outcomes in a bracket. The model specifies
# which alpha value(s) to use for each round. 
def generateBracket(model, year):
	bracket = []
	regionWinners = []

	random.seed()

	isEliteEightSampleModel = "True" in model['isEliteEightSampleModel']

	e8Seeds = []
	if isEliteEightSampleModel:
		for i in range(4):
			e8Seeds.append(getE8SeedTop(year))
			e8Seeds.append(getE8SeedBottom(year))
	else:
		e8Seeds = [-1, -1, -1, -1, -1, -1, -1, -1]

	genE8seeds = []

	# Loop through regional rounds R64, R32, and S16
	for region in range(4):
		seeds = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]
		for roundNum in range(1, 4): # Don't do Elite Eight games yet
			numGames = int(len(seeds) / 2)
			newSeeds = []
			for gameNum in range(numGames):
				s1 = seeds[2 * gameNum]
				s2 = seeds[2 * gameNum + 1]

				# Force the region winner to make it through
				if (s1 == e8Seeds[2*region]) or (s1 == e8Seeds[2*region + 1]):
					p = 1
				elif (s2 == e8Seeds[2*region]) or (s2 == e8Seeds[2*region + 1]):
					p = 0
				else:
					p = getP(s1, s2, model, year, roundNum)

				if random.random() <= p:
					bracket.append(1)
					newSeeds.append(s1)
				else:
					bracket.append(0)
					newSeeds.append(s2)
			seeds = newSeeds
		for seed in seeds:
			genE8seeds.append(seed)

	e8Seeds = genE8seeds

	# Round 4:
	f4seeds = []
	for gameNum in range(4):
		s1 = e8Seeds[2 * gameNum]
		s2 = e8Seeds[2 * gameNum + 1]
		p = getP(s1, s2, model, year, 4)

		if random.random() <= p:
			bracket.append(1)
			f4seeds.append(s1)
		else:
			bracket.append(0)
			f4seeds.append(s2)

	# Round 5:
	semiFinalists = []
	for gameNum in range(2):
		s1 = f4seeds[2 * gameNum]
		s2 = f4seeds[2 * gameNum + 1]
		p = getP(s1, s2, model, year, 5)

		if random.random() <= p:
			bracket.append(1)
			semiFinalists.append(s1)
		else:
			bracket.append(0)
			semiFinalists.append(s2)

	# Round 6:
	s1 = semiFinalists[0]
	s2 = semiFinalists[1]
	p = getP(s1, s2, model, year, 6)

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
def getAlpha(s1, s2, model, year, roundNum):
	# Round 1 grouped alpha values for predicting 2013 through 2019, 
	# rounded to two decimal places (2 is the default value).
	# First dimension is better seed number (1 at index 1),
	# second dimension is year (2013 at index 0)

	# R1 alpha values, grouped as:
	# 1, 2, 3-4, 5-7, and 8
	round1MatchupAlphaAvgsByYear = [
		[],
		[2, 2, 2, 2, 2, 2, 1.77],
		[1.43, 1.36, 1.38, 1.40, 1.34, 1.36, 1.38],
		[1.12, 1.11, 1.12, 1.11, 1.10, 1.13, 1.12],
		[1.12, 1.11, 1.12, 1.11, 1.10, 1.13, 1.12],
		[0.95, 0.93, 0.90, 0.93, 0.88, 0.87, 0.89],
		[0.95, 0.93, 0.90, 0.93, 0.88, 0.87, 0.89],
		[0.95, 0.93, 0.90, 0.93, 0.88, 0.87, 0.89],
		[0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]]

	# Round 1-6 weighted avg. alpha values from 
	# 2013 through 2019, using new weighting scheme.
	# First dimension is year (2013 at index 0), 
	# second dimension is round number (R1 at index 1)
	alphaAvgsByYear = [
		[0, 0.83, 0.83, 0.83, 0.83, 0.82, 0.83, 0.82],
		[0, 0.73, 0.73, 0.73, 0.73, 0.74, 0.74, 0.74],
		[0, 0.72, 0.72, 0.70, 0.71, 0.74, 0.74, 0.71],
		[0, 0.56, 0.53, 0.49, 0.49, 0.47, 0.46, 0.46],
		[0, 0.82, 0.83, 0.70, 0.70, 0.71, 0.72, 0.75],
		[0, 0.71, 0.73, 0.84, 0.84, 0.81, 0.81, 0.83]]

	roundName = 'round{0}'.format(roundNum)
	roundInfo = model[roundName]

	isWeightedAverage = "True" in roundInfo['isWeightedAverage']
	isMatchupSpecific = "True" in roundInfo['isMatchupSpecific']

	if isMatchupSpecific:
		if roundNum > 1:
			sys.exit("Sorry, matchup-specific alpha values for Rounds 2-6 are not implemented.")

		betterSeed = min(s1, s2)
		alpha = round1MatchupAlphaAvgsByYear[betterSeed][year - 2013]
	elif isWeightedAverage:
		alpha = alphaAvgsByYear[year - 2013][roundNum]
	else:
		alpha = roundInfo['fixedAlpha']

	if 'r1ScalingPercent' in model:
		r1ScalingPercent = float(model['r1ScalingPercent'])
		alpha = alpha * (100.0 + r1ScalingPercent) / 100.0
		if alpha > 2:
			alpha = 2

	return alpha


# This function computes how many picks a bracket
# got correct given the bracket's score vector.
def calcCorrectPicks(scoreVector):
	numCorrectPicks = 0
	for roundNum in range(1, 7):
		numCorrectPicks += scoreVector[roundNum] / (10 * (2 ** (roundNum - 1)))
	return numCorrectPicks


# This function generates and scores brackets
# for the given year using the given model.
# It prints the results in JSON format.
def performExperiments(numTrials, year, batchNumber, model):
	correctVector = getActualBracketVector(year)

	brackets = []
	for n in range(numTrials):
		newBracketVector = generateBracket(model, year)
		newBracketScore = scoreBracket(newBracketVector, correctVector)
		numCorrectPicks = calcCorrectPicks(newBracketScore)

		newBracketString = ''.join(str(bit) for bit in newBracketVector)

		brackets.append({'bracketVector': newBracketString, 'score': newBracketScore, 'correctPicks': numCorrectPicks, 'model': model['modelName']})

	bracketListDict = {'year': year, 'actualBracket': ''.join(str(bit) for bit in correctVector), 'brackets': brackets}

	if numTrials < 1000:
		folderName = 'Experiments/{0}Trials'.format(numTrials)
	else:
		folderName = 'Experiments/{0}kTrials'.format(int(numTrials / 1000))
	batchFolderName = '{0}/Batch{1:02d}'.format(folderName, batchNumber)

	outputFilename = '{2}/generatedBrackets_{0}_{1}.json'.format(model['modelName'], year, batchFolderName)
	with open(outputFilename, 'w') as outputFile:
		outputFile.write(json.dumps(bracketListDict))


# Load models
modelFilename = 'models19Only.json'
with open(modelFilename, 'r') as modelFile:
	modelsDataJson = modelFile.read().replace('\n', '')

modelsDict = json.loads(modelsDataJson)
modelsList = modelsDict['models']


# This script runs experiments with the given models, number of trials,
# and number of batches for the 2013 through 2017 tournaments. 
numTrials = int(sys.argv[1])
numBatches = int(sys.argv[2])

for modelDict in modelsList:
	modelName = modelDict['modelName']

	for batchNumber in range(numBatches):
		if numTrials < 1000:
			folderName = 'Experiments/{0}Trials'.format(numTrials)
		else:
			folderName = 'Experiments/{0}kTrials'.format(int(numTrials / 1000))

		if not os.path.exists(folderName):
			os.makedirs(folderName)

		batchFolderName = '{0}/Batch{1:02d}'.format(folderName, batchNumber)
		if not os.path.exists(batchFolderName):
			os.makedirs(batchFolderName)

		for year in range(2013, 2019):
			performExperiments(numTrials, year, batchNumber, modelDict)

