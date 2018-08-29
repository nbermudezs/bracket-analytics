#!/usr/bin/env python
import time
import json
import os.path
import random
import sys
from math import log, ceil, floor
from samplingUtils import getTruncGeom
from scoringUtils import applyRoundResults
from scoringUtils import getActualBracketVector
from scoringUtils import scoreBracket

# Author:
#     Ian Ludden
#
# Date created:
#     16 Feb 2018
#
# Last modified:
#     15 Apr 2018
#
# In this version, the alpha values are determined by the given
# JSON description of the model. 

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

	random.seed()

	e8Seeds = [-1, -1, -1, -1, -1, -1, -1, -1]
	f4Seeds = []
	ncgSeeds = [-1, -1]

	genE8Seeds = []

	for region in range(4):
		seeds = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]
		for roundNum in range(1, 5):
			numGames = int(len(seeds) / 2)
			newSeeds = []
			for gameNum in range(numGames):
				s1 = seeds[2 * gameNum]
				s2 = seeds[2 * gameNum + 1]
				p = getP(s1, s2, model, year, roundNum)

				if random.random() <= p:
					bracket.append(1)
					newSeeds.append(s1)
				else:
					bracket.append(0)
					newSeeds.append(s2)
			seeds = newSeeds
		for seed in seeds:
			f4Seeds.append(seed)

	# e8Seeds = genE8Seeds

	# # Round 4:
	# for gameNum in range(4):
	# 	s1 = e8Seeds[2 * gameNum]
	# 	s2 = e8Seeds[2 * gameNum + 1]
	# 	p = getP(s1, s2, model, year, 4)

	# 	if random.random() <= p:
	# 		bracket.append(1)
	# 		f4Seeds[gameNum] = s1
	# 	else:
	# 		bracket.append(0)
	# 		f4Seeds[gameNum] = s2

	# Round 5:
	for gameNum in range(2):
		s1 = f4Seeds[2 * gameNum]
		s2 = f4Seeds[2 * gameNum + 1]
		p = getP(s1, s2, model, year, 5)

		if random.random() <= p:
			bracket.append(1)
			ncgSeeds[gameNum] = s1
		else:
			bracket.append(0)
			ncgSeeds[gameNum] = s2

	# Round 6:
	s1 = ncgSeeds[0]
	s2 = ncgSeeds[1]

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

	# r1SeparateAlphas = [
	# 	[],
	# 	[2,2,2,2,2,2,1.77],
	# 	[1.43,1.36,1.38,1.40,1.34,1.36,1.38],
	# 	[1.16,1.14,1.13,1.07,1.06,1.08,1.10],
	# 	[1.10,1.10,1.13,1.17,1.16,1.19,1.15],
	# 	[0.76,0.69,0.62,0.68,0.66,0.68,0.73],
	# 	[1.10,1.12,1.08,1.04,0.95,0.87,0.84],
	# 	[1.12,1.18,1.23,1.29,1.24,1.30,1.34],
	# 	[-0.61,-0.59,-0.28,0.27,0,0.26,0]]


	# r2to6Alphas = [
	# 	[1.10,1.03,1.03,1.02,1.01,1.05,1.03],
	# 	[0.91,0.90,0.86,0.88,0.90,0.91,0.86],
	# 	[0.36,0.23,0.19,0.22,0.14,0.12,0.15],
	# 	[0.67,0.70,0.58,0.61,0.64,0.67,0.70],
	# 	[1.41,1.42,1.44,1.44,1.17,1.17,1.20]]

	# roundName = 'round{0}'.format(roundNum)
	# roundInfo = model[roundName]

	# isWeightedAverage = "True" in roundInfo['isWeightedAverage']
	# isMatchupSpecific = "True" in roundInfo['isMatchupSpecific']

	# if isMatchupSpecific:
	# 	if roundNum > 1:
	# 		sys.exit("Sorry, matchup-specific alpha values for Rounds 2-6 are not implemented.")

	# 	betterSeed = min(s1, s2)
	# 	alpha = round1MatchupAlphaAvgsByYear[betterSeed][year - 2013]
	# elif isWeightedAverage:
	# 	if roundNum == 1:
	# 		sys.exit("Nah, there's no way we're using the weighted average for Round 1.")
	# 	alpha = alphaAvgsByYear[year - 2013][roundNum]
	# else:
	# 	alpha = roundInfo['fixedAlpha']

	if roundNum == 1:
		alpha = round1MatchupAlphaAvgsByYear[s1][year - 2013]
	else:
		alpha = alphaAvgsByYear[year - 2013][roundNum]

	# if 'r1ScalingPercent' in model:
	# 	r1ScalingPercent = float(model['r1ScalingPercent'])
	# 	alpha = alpha * (100.0 + r1ScalingPercent) / 100.0
	# 	if alpha > 2:
	# 		alpha = 2

	# print '{0} vs. {1}, alpha = {2:5.2f}'.format(s1, s2, alpha)

	return alpha


# This function computes how many picks a bracket
# got correct given the bracket's score vector.
# def calcCorrectPicks(scoreVector):
# 	numCorrectPicks = 0
# 	for roundNum in range(1, 7):
# 		numCorrectPicks += scoreVector[roundNum] / (10 * (2 ** (roundNum - 1)))
# 	return numCorrectPicks


# This function generates and scores brackets
# for the given year using the given model.
# It prints the results in JSON format.
def performExperiments(numTrials, year, batchNumber, model):
	correctVector = getActualBracketVector(year)

	brackets = []
	for n in range(numTrials):
		newBracketVector = generateBracket(model, year)
		newBracketScore = scoreBracket(newBracketVector, correctVector)

		newBracketString = ''.join(str(bit) for bit in newBracketVector)

		brackets.append({'bracketVector': newBracketString, 'score': newBracketScore})

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
modelFilename = 'models_TEST.json'
with open(modelFilename, 'r') as modelFile:
	modelsDataJson = modelFile.read().replace('\n', '')

modelsDict = json.loads(modelsDataJson)
modelsList = modelsDict['models']


# This script runs experiments with the given models, number of trials,
# and number of batches for the 2013 through 2018 tournaments. 
numTrials = int(sys.argv[1])
numBatches = int(sys.argv[2])

for modelDict in modelsList:
	modelName = modelDict['modelName']

	print '{0:<8s}: {1}'.format(modelName, time.strftime("%Y-%m-%d %H:%M"))

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

