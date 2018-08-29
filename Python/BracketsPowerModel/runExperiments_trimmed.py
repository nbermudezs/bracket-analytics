#!/usr/bin/env python
import time
import json
import os.path
import random
import sys
from math import log, ceil, floor

from samplingUtils import getTruncGeom
from samplingUtils import getE8SeedBottom, getE8SeedTop
from samplingUtils import getF4SeedSplit, getF4SeedTogether
from samplingUtils import getChampion, getRunnerUp

from scoringUtils import applyRoundResults
from scoringUtils import getActualBracketVector
from scoringUtils import scoreBracket

######################################################################
# Author:
#     Ian Ludden
#
# Date created:
#     15 Apr 2018
#
# Last modified:
#     15 Apr 2018
#
# This general version handles all parameters previously implemented 
# separately in runExperimentsFixedAlpha.py, 
# runExperimentsSampleF4.py, and runExperimentsSampleE8.py. 
# 
# Specifically, this version supports:
# - "Forward" Power Model
# - "Reverse" Power Model (generate champ and runner-up, then forward)
# - "Reverse" Power Model with F4 (also generate other two F4 seeds)
# - F4 Model 1, where F4 seeds are generated using "Model 1," 
#   then power model is applied to games before and after
# - F4 Model 2, where F4 seeds are generated using "Model 2," 
#   then power model is applied to games before and after
# - E8 Model, where E8 seeds are generated,  
#   then power model is applied to games before and after
# 
# Also, the Round 1 alpha values are optionally grouped as:
# (1, 16) alone
# (2, 15) alone
# (3, 14), (4, 13) 
# (5, 12), (6, 11), (7, 10)
# (8, 9) alone and fixed at 0.5 probability (alpha = 0)
# 
# All weighted alpha values are computed using the standard 
# weighting (multiply each alpha by [# matchups]).
#
# This version no longer requires models to specify the alpha value
# parameters for each round. Round 1 is always matchup-specific 
# (with optional grouping), and Rounds 2-6 always use a 
# weighted average. 
######################################################################

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
	f4Seeds = [-1, -1, -1, -1]
	ncgSeeds = [-1, -1]

	genE8Seeds = []

	for region in range(4):
		seeds = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]
		for roundNum in range(1, 4):
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
			genE8Seeds.append(seed)

	e8Seeds = genE8Seeds

	# Round 4:
	for gameNum in range(4):
		s1 = e8Seeds[2 * gameNum]
		s2 = e8Seeds[2 * gameNum + 1]
		p = getP(s1, s2, model, year, 4)

		if random.random() <= p:
			bracket.append(1)
			f4Seeds[gameNum] = s1
		else:
			bracket.append(0)
			f4Seeds[gameNum] = s2

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
# between the given seeds s1, s2. 
def getAlpha(s1, s2, model, year, roundNum):
	# Round 1 grouped alpha values for predicting 2013-2019,
	# where the first index is the better seed and the 
	# second index is [year - 2013]. The grouping is:
	# 1, 2, 3-4, 5-7, 8
	# r1GroupedAlphas = [
	# 	[],
	# 	[2,2,2,2,2,2,1.7692038993],
	# 	[1.4252197727,1.3625656943,1.3804523797,1.3977167918,1.3440101948,1.3602838429,1.3760407791],
	# 	[1.1327439019,1.1199577274,1.1293433883,1.1189438356,1.1083639629,1.1365944197,1.1245771481],
	# 	[1.1327439019,1.1199577274,1.1293433883,1.1189438356,1.1083639629,1.1365944197,1.1245771481],
	# 	[0.992260877,0.996405404,0.9802794213,1.0053287528,0.9535901796,0.947768435,0.9722115628],
	# 	[0.992260877,0.996405404,0.9802794213,1.0053287528,0.9535901796,0.947768435,0.9722115628],
	# 	[0.992260877,0.996405404,0.9802794213,1.0053287528,0.9535901796,0.947768435,0.9722115628],
	# 	[0,0,0,0,0,0,0]]
	r1GroupedAlphas = [
		[],
		[2,2,2,2,2,2,1.77],
		[1.43,1.36,1.38,1.40,1.34,1.36,1.38],
		[1.13,1.12,1.13,1.12,1.11,1.14,1.12],
		[1.13,1.12,1.13,1.12,1.11,1.14,1.12],
		[0.99,1.00,0.98,1.01,0.95,0.95,0.97],
		[0.99,1.00,0.98,1.01,0.95,0.95,0.97],
		[0.99,1.00,0.98,1.01,0.95,0.95,0.97],
		[-0.61,-0.59,-0.28,0.27,0,0.26,0]]

	# Round 1 separated alpha values for predicting 2013-2019,
	# where the first index is the better seed and the 
	# second index is [year - 2013]. 
	# r1SeparateAlphas = [
	# 	[],
	# 	[2,2,2,2,2,2,1.7692038993],
	# 	[1.4252197727,1.3625656943,1.3804523797,1.3977167918,1.3440101948,1.3602838429,1.3760407791],
	# 	[1.1631440406,1.1437646,1.1260389104,1.0702482606,1.0570363456,1.0808615169,1.1038431398],
	# 	[1.1023437632,1.0961508547,1.1326478663,1.1676394106,1.1596915802,1.1923273226,1.1453111565],
	# 	[0.7612823908,0.6898202312,0.6242869483,0.6828764698,0.6603066747,0.6767844807,0.7293107575],
	# 	[1.0995538121,1.1222629842,1.0820607889,1.0447312883,0.9537101213,0.86947563,0.8427577133],
	# 	[1.1159464279,1.1771329966,1.2344905268,1.2883785003,1.2467537426,1.2970451943,1.3445662175],
	# 	[0,0,0,0,0,0,0]]
	r1SeparateAlphas = [
		[],
		[2,2,2,2,2,2,1.77],
		[1.43,1.36,1.38,1.40,1.34,1.36,1.38],
		[1.16,1.14,1.13,1.07,1.06,1.08,1.10],
		[1.10,1.10,1.13,1.17,1.16,1.19,1.15],
		[0.76,0.69,0.62,0.68,0.66,0.68,0.73],
		[1.10,1.12,1.08,1.04,0.95,0.87,0.84],
		[1.12,1.18,1.23,1.29,1.24,1.30,1.34],
		[-0.61,-0.59,-0.28,0.27,0,0.26,0]]

	# Rounds 2-6 weighted average alpha values for predicting
	# 2013-2019, where the first index is [roundNum - 2] and 
	# the second index is [year - 2013].
	# r2to6Alphas = [
	# 	[1.0960226368,1.0255184405,1.0280047853,1.0169015383,1.0085075325,1.0517190671,1.0349243918],
	# 	[0.9074472394,0.8963083681,0.8581664326,0.8815834483,0.9021714769,0.9088993287,0.8644826467],
	# 	[0.3579691718,0.2302351327,0.1909716145,0.2167374254,0.136706458,0.1188463061,0.1504395788],
	# 	[0.6673769231,0.6983681575,0.5784406838,0.6093441472,0.6389325696,0.674510496,0.7010202861],
	# 	[1.4133971593,1.4171625002,1.441447396,1.441447396,1.1671880002,1.1671880002,1.199219231]]
	r2to6Alphas = [
		[1.10,1.03,1.03,1.02,1.01,1.05,1.03],
		[0.91,0.90,0.86,0.88,0.90,0.91,0.86],
		[0.36,0.23,0.19,0.22,0.14,0.12,0.15],
		[0.67,0.70,0.58,0.61,0.64,0.67,0.70],
		[1.41,1.42,1.44,1.44,1.17,1.17,1.20]]

	isR1Grouped = 'False'
	if 'isR1Grouped' in model:
		isR1Grouped = 'True' in model['isR1Grouped']

	alpha = 0

	if (isR1Grouped) and (roundNum == 1):
		alpha = r1GroupedAlphas[s1][year - 2013]
	elif roundNum == 1:
		alpha = r1SeparateAlphas[s1][year - 2013]
	else:
		alpha = r2to6Alphas[roundNum - 2][year - 2013]

	# if 'r1ScalingPercent' in model:
	# 	r1ScalingPercent = float(model['r1ScalingPercent'])
	# 	alpha = alpha * (100.0 + r1ScalingPercent) / 100.0
	# 	if alpha > 2:
	# 		alpha = 2

	# print '{0} vs. {1}, alpha = {2:5.2f}'.format(s1, s2, alpha)

	return alpha


# Unused: if we want to measure this later, we can. 
# 
# # This function computes how many picks a bracket
# # got correct given the bracket's score vector.
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


######################################################################
# This script runs experiments with the given models, 
# number of trials, and number of batches for 2013 through 2018. 
######################################################################

# Load models
modelFilename = 'models.json'
with open(modelFilename, 'r') as modelFile:
	modelsDataJson = modelFile.read().replace('\n', '')

modelsDict = json.loads(modelsDataJson)
modelsList = modelsDict['models']

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

