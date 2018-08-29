#!/usr/bin/env python
from scoringUtils import applyRoundResults

# This function returns the seed number and region index (0, 1, 2, or 3)
# of the national champion for the given bracket. 
# It also returns the seed number and region index of the 
# team they beat in the Final Four. 
def getWinner(bracketVector):
	championInfo = []
	regionWinners = []

	# Compute Rounds 1-4 scores
	for region in range(4):
		start = 15 * region
		end = start + 8
		regionVector = bracketVector[start:end]

		seeds = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]

		for r in range(1, 5):
			seeds = applyRoundResults(seeds, regionVector)

			start = end
			end += int(len(seeds) / 2)
			regionVector = bracketVector[start:end]

		regionWinners.append(seeds[0])

	# Compute Rounds 5-6 scores
	finalFourVector = bracketVector[-3:]

	championshipGameSeeds = applyRoundResults(regionWinners, finalFourVector[0:2])

	championRegion = 0
	if finalFourVector[2] == 1:
		championRegion = 1 - finalFourVector[0]
		ffLoserRegion = finalFourVector[0]
	else:
		championRegion = 3 - finalFourVector[1]
		ffLoserRegion = 2 + finalFourVector[1]

	championInfo.append(championshipGameSeeds[1 - finalFourVector[2]])
	championInfo.append(championRegion)
	championInfo.append(regionWinners[ffLoserRegion])
	championInfo.append(ffLoserRegion)
	return championInfo

# This function returns the seed number and region index (0, 1, 2, or 3)
# of the national runner-up for the given bracket. 
# It also returns the seed number and region index of the 
# team they beat in the Final Four. 
def getLoser(bracketVector):
	runnerUpInfo = []
	regionWinners = []

	# Compute Rounds 1-4 scores
	for region in range(4):
		start = 15 * region
		end = start + 8
		regionVector = bracketVector[start:end]

		seeds = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]

		for r in range(1, 5):
			seeds = applyRoundResults(seeds, regionVector)

			start = end
			end += int(len(seeds) / 2)
			regionVector = bracketVector[start:end]

		regionWinners.append(seeds[0])

	# Compute Rounds 5-6 scores
	finalFourVector = bracketVector[-3:]

	runnerUpRegion = 0
	if finalFourVector[2] == 1:
		runnerUpRegion = 3 - finalFourVector[1]
		ffLoserRegion = 2 + finalFourVector[1]
	else:
		runnerUpRegion = 1 - finalFourVector[0]
		ffLoserRegion = finalFourVector[0]

	runnerUpInfo.append(regionWinners[runnerUpRegion])
	runnerUpInfo.append(runnerUpRegion)
	runnerUpInfo.append(regionWinners[ffLoserRegion])
	runnerUpInfo.append(ffLoserRegion)
	return runnerUpInfo