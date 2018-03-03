#!/usr/bin/env python

# This function takes in a list of seeds that competed
# in a round within a region, listed from top to bottom
# in the official bracket format. It also takes a list
# of results, where a 1 (0) indicates the top (bottom) 
# team won. It outputs a list of the seeds in the next
# round, i.e., the winners of the given round.
def applyRoundResults(seeds, results):
	nGames = len(results)
	return [seeds[2*i] * results[i] + seeds[2*i+1] * (1 - results[i]) for i in range(nGames)]

# This function scores a bracket vector according to the 
# ESPN Bracket Challenge scoring system. The isPickFavorite
# flag indicates whether the bracket being scored is from the
# Pick Favorite model, in which case we assume that it correctly
# guesses the Final Four and National Championship outcomes.
def scoreBracket(bracketVector, actualResultsVector, isPickFavorite = False):
	# Round score subtotals, with only indices 1-6 used
	# as actual subtotals. The 0th element is the overall total.
	roundScores = [0, 0, 0, 0, 0, 0, 0]

	regionWinners = []
	actualRegionWinners = []

	# Compute Rounds 1-4 scores
	for region in range(4):
		start = 15 * region
		end = start + 8
		regionVector = bracketVector[start:end]
		regionResultsVector = actualResultsVector[start:end]

		seeds = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]
		actualSeeds = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]

		for r in range(1, 5):
			seeds = applyRoundResults(seeds, regionVector)
			actualSeeds = applyRoundResults(actualSeeds, regionResultsVector)

			matches = [i for i, j in zip(seeds, actualSeeds) if i == j]
			roundScores[r] += 10 * (2 ** (r-1)) * len(matches)

			start = end
			end += int(len(seeds) / 2)
			regionVector = bracketVector[start:end]
			regionResultsVector = actualResultsVector[start:end]

		regionWinners.append(seeds[0])
		actualRegionWinners.append(actualSeeds[0])

	# Compute Rounds 5-6 scores
	finalFourVector = bracketVector[-3:]
	actualFinalFourVector = actualResultsVector[-3:]

	if isPickFavorite:
		finalFourVector = actualFinalFourVector

	isCorrectFirstSemifinal = (finalFourVector[0] == actualFinalFourVector[0]) and (finalFourVector[0] == 1 and (regionWinners[0] == actualRegionWinners[0])) or (finalFourVector[0] == 0 and (regionWinners[1] == actualRegionWinners[1]))
	if isCorrectFirstSemifinal:
		print 'Is correct first semi'
		roundScores[5] += 160

	isCorrectSecondSemifinal = (finalFourVector[1] == actualFinalFourVector[1]) and (finalFourVector[1] == 1 and (regionWinners[2] == actualRegionWinners[2])) or (finalFourVector[1] == 0 and (regionWinners[3] == actualRegionWinners[3]))

	if isCorrectSecondSemifinal:
		print 'Is correct second semi'
		roundScores[5] += 160

	isCorrectChampion = (finalFourVector[2] == actualFinalFourVector[2]) and (finalFourVector[2] == 1 and isCorrectFirstSemifinal) or (finalFourVector[2] == 0 and isCorrectSecondSemifinal)
	if isCorrectChampion:
		print 'Is correct champion'
		roundScores[6] += 320

	roundScores[0] = sum(roundScores)
	return roundScores