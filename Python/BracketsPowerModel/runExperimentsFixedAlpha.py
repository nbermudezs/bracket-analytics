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
#     23 Mar 2018
#
# In this version, the alpha values are determined by the given
# JSON description of the model. 

# Returns the estimated probability that s1 beats s2
def getP(s1, s2, model, year, roundNum):
	alpha = getAlpha(s1, s2, model, year, roundNum)

	# if roundNum <= 3:
	# 	print '{0:02d} vs. {1:02d} - {2:5.2f}'.format(s1, s2, alpha)

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

	# print '\n{0}, {1}:'.format(model['modelName'], year)

	# If Reverse Model, need to pick winner and/or runner-up first
	champSeed = 0
	champRegion = -2
	ruSeed = 0
	ruRegion = -2
	ffrRegion = -2
	ffcRegion = -2

	if "True" in model['isReverseModel']:
		# print 'Using reverse model.'
		# Truncated geometric parameters for predicting 2013-2018 seasons.
		# See ReverseModel/ChampionRunnerUpSeedDistributions.ods for 
		# how these values were computed.
		pChamp = [0.5090909091, 0.5178571429, 0.4761904762, 0.484375, 0.4848484848, 0.4925373134]
		champSum = [0.9966270601, 0.997079845, 0.9943325575, 0.9950034329, 0.9950400208, 0.9956022259]

		pRU = [0.3835616438, 0.3766233766, 0.3529411765, 0.3604651163, 0.367816092, 0.375]
		ruSum = [0.9791494637, 0.9771963641, 0.9692708809, 0.9720157349, 0.9744878244, 0.9767169356]

		pC = pChamp[year - 2013]
		cSum = champSum[year - 2013]
		pR = pRU[year - 2013]
		rSum = ruSum[year - 2013]

		champSeed = getTruncGeom(pC, cSum)
		ruSeed = getTruncGeom(pR, rSum)

		champRegion = int(floor(random.random() * 4))
		ruRegion = int(floor(random.random() * 2))

		ffrRegion = 1 - ruRegion

		if champRegion < 2:
			ruRegion += 2
			ffrRegion += 2
			ffcRegion = 1 - champRegion
		else:
			ffcRegion = 5 - champRegion

		# print 'Champion:  {0:02d} from Region {1}'.format(champSeed, champRegion)
		# print 'Runner-up: {0:02d} from Region {1}'.format(ruSeed, ruRegion)

	if ('isFFReverseModel' in model) and ("True" in model['isFFReverseModel']):
		# FFc indicates the Final Four team which lost to the champion, and 
		# FFr indicates the Final Four team which lost to the runner-up.

		# Truncated geometric parameters for predicting 2013-2018 seasons.
		# See ReverseModel/ChampionRunnerUpSeedDistributions.ods for 
		# how these values were computed.
		pFFc = [0.4, 0.365, 0.373, 0.354, 0.357, 0.356]
		ffcSum = [0.955, 0.961, 0.964, 0.959, 0.961, 0.961]
		pFFr = [0.35, 0.345, 0.349, 0.356, 0.330, 0.317]
		ffrSum = [0.991, 0.991, 0.991, 0.992, 0.988, 0.985]

		# The truncated geometric fit is bad for FFc with the 11-seeds included,
		# so we first pick whether to use the model. We choose not to with 
		# probability equal to the proportion of 11-seeds historically. 
		pDoNotUseTruncGeomFFC = [0.071, 0.069, 0.067, 0.065, 0.063, 0.061]
		if random.random() <= pDoNotUseTruncGeomFFC[year-2013]:
			ffcSeed = 11
		else:
			ffcSeed = getTruncGeom(pFFc[year-2013], ffcSum[year-2013])

		# The truncated geometric fit is acceptable for all years for FFr, so
		# we always use the trunc geom model. 
		ffrSeed = getTruncGeom(pFFr[year-2013], ffrSum[year-2013])
	else:
		ffcSeed = -1
		ffrSeed = -1


	random.seed()
	# print '\nYear: {1}, Model name: {0}'.format(model['modelName'], year)
	# print 'Champion, FFc, Runner-up, FFr seeds/regions:'
	# print '{0} - {1}\n{2} - {3}\n{4} - {5}\n{6} - {7}\n'.format(champSeed, champRegion, ffcSeed, ffcRegion, ruSeed, ruRegion, ffrSeed, ffrRegion)

	# Loop through all regional rounds
	for region in range(4):
		# print '=== Region {0} ==='.format(region)
		seeds = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]
		for roundNum in range(1, 5):
			# print '--- Round {0} ---'.format(roundNum)
			numGames = int(len(seeds) / 2)
			newSeeds = []
			for gameNum in range(numGames):
				s1 = seeds[2 * gameNum]
				s2 = seeds[2 * gameNum + 1]

				# If reverse model is used, these conditions are relevant
				if region == champRegion:
					if s1 == champSeed:
						print 'SPECIAL CASE: '.format('Force champ (s1) to win.')
						p = 1
					elif s2 == champSeed:
						print 'SPECIAL CASE: '.format('Force champ (s2) to win.')
						p = 0
					else:
						p = getP(s1, s2, model, year, roundNum)
				elif region == ruRegion:
					if s1 == ruSeed:
						print 'SPECIAL CASE: '.format('Force ru (s1) to win.')
						p = 1
					elif s2 == ruSeed:
						print 'SPECIAL CASE: '.format('Force ru (s2) to win.')
						p = 0
					else:
						p = getP(s1, s2, model, year, roundNum)
				elif region == ffcRegion:
					if s1 == ffcSeed:
						print 'SPECIAL CASE: '.format('Force ffc (s1) to win.')
						p = 1
					elif s2 == ffcSeed:
						print 'SPECIAL CASE: '.format('Force ffc (s2) to win.')
						p = 0
					else:
						p = getP(s1, s2, model, year, roundNum)
				elif region == ffrRegion:
					if s1 == ffrSeed:
						print 'SPECIAL CASE: '.format('Force ffr (s1) to win.')
						p = 1
					elif s2 == ffrSeed:
						print 'SPECIAL CASE: '.format('Force ffr (s2) to win.')
						p = 0
					else:
						p = getP(s1, s2, model, year, roundNum)
				else:
					p = getP(s1, s2, model, year, roundNum)

				# if roundNum == 1:
				# 	print '{0:5.2f}'.format(p)

				# print '{0:02d} vs. {1:02d}: p = {2:5.3f}'.format(s1, s2, p)
				if random.random() <= p:
					bracket.append(1)
					newSeeds.append(s1)
				else:
					bracket.append(0)
					newSeeds.append(s2)
			seeds = newSeeds
		regionWinners.append(seeds[0])

	# print '{0:<10s}{1}'.format('Gen. F4:', regionWinners)

	# Round 5:
	semiFinalists = []
	for gameNum in range(2):
		s1 = regionWinners[2 * gameNum]
		s2 = regionWinners[2 * gameNum + 1]

		if gameNum == (champRegion / 2):
			if s1 == champSeed:
				print 'SPECIAL CASE: '.format('Force champ (s1) to win F4.')
				p = 1
			elif s2 == champSeed:
				print 'SPECIAL CASE: '.format('Force champ (s2) to win F4.')
				p = 0
			else:
				p = getP(s1, s2, model, year, 5)
		elif gameNum == (ruRegion / 2):
			if s1 == ruSeed:
				print 'SPECIAL CASE: '.format('Force ru (s1) to win F4.')
				p = 1
			elif s2 == ruSeed:
				print 'SPECIAL CASE: '.format('Force ru (s2) to win F4.')
				p = 0
			else:
				p = getP(s1, s2, model, year, 5)
		else:
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

	if champRegion <= -1:
		p = getP(s1, s2, model, year, 6)
	elif champRegion < 2:
		print 'SPECIAL CASE: '.format('Force champ (s1) to win NCG.')
		p = 1
	else:
		print 'SPECIAL CASE: '.format('Force champ (s2) to win NCG.')
		p = 0 # champRegion is 2 or 3

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

	# if 'r1ScalingPercent' in model:
	# 	r1ScalingPercent = float(model['r1ScalingPercent'])
	# 	alpha = alpha * (100.0 + r1ScalingPercent) / 100.0
	# 	if alpha > 2:
	# 		alpha = 2

	# print '{0} vs. {1}, alpha = {2:5.2f}'.format(s1, s2, alpha)

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

