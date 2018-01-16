#!/usr/bin/env python

# DEPRECATED: This function converts a region's vector from up/down representation
# to favorite/underdog representation.
# def convertUpToFavorite(vectorString):
# 	debug = False
# 	vector = [int(vectorString[i]) for i in range(0, len(vectorString))]
# 	firstRoundResults = vector[0:8]

# 	favoritesUnderdogsVector = firstRoundResults

# 	round1Up = [1, 8, 5, 4, 6, 3, 7, 2]
# 	round1Down = [16, 9, 12, 13, 11, 14, 10, 15]
# 	oppositeFirstRoundResults = [1 - firstRoundResults[i] for i in range(0, 8)]
# 	secondRoundTeams = []
# 	for i in range(0, 8):
# 		if firstRoundResults[i] == 1:
# 			secondRoundTeams.append(round1Up[i])
# 		else:
# 			secondRoundTeams.append(round1Down[i])

# 	if debug:
# 		print secondRoundTeams

# 	thirdRoundTeams = []
# 	for i in range(0, 4):
# 		upTeam = secondRoundTeams[2 * i]
# 		downTeam = secondRoundTeams[2 * i + 1]

# 		if debug:
# 			print '{0} vs. {1}'.format(upTeam, downTeam)

# 		gameResult = vector[8 + i]

# 		if debug:
# 			print 'Result: {0}\n'.format(gameResult)

# 		if gameResult == 1:
# 			thirdRoundTeams.append(upTeam)
# 		else:
# 			thirdRoundTeams.append(downTeam)
# 		if upTeam > downTeam:
# 			favoritesUnderdogsVector.append(1 - gameResult)
# 		else:
# 			favoritesUnderdogsVector.append(gameResult)

# 	if debug:
# 		print thirdRoundTeams

# 	upTeam1 = thirdRoundTeams[0]
# 	downTeam1 = thirdRoundTeams[1]
# 	upTeam2 = thirdRoundTeams[2]
# 	downTeam2 = thirdRoundTeams[3]

# 	semiResult1 = vector[12]
# 	if semiResult1 == 1:
# 		regionalUpTeam = upTeam1
# 	else:
# 		regionalUpTeam = downTeam1

# 	if upTeam1 > downTeam1:
# 		favoritesUnderdogsVector.append(1 - semiResult1)
# 	else:
# 		favoritesUnderdogsVector.append(semiResult1)

# 	semiResult2 = vector[13]
# 	if semiResult2 == 1:
# 		regionalDownTeam = upTeam2
# 	else:
# 		regionalDownTeam = downTeam2

# 	if upTeam2 > downTeam2:
# 		favoritesUnderdogsVector.append(1 - semiResult2)
# 	else:
# 		favoritesUnderdogsVector.append(semiResult2)

# 	if debug:
# 		print '{0} vs. {1}'.format(regionalUpTeam, regionalDownTeam)

# 	finalResult = vector[14]
# 	if regionalUpTeam > regionalDownTeam:
# 		favoritesUnderdogsVector.append(1 - finalResult)
# 	else:
# 		favoritesUnderdogsVector.append(finalResult)

# 	return ''.join(str(favoritesUnderdogsVector[i]) for i in range(0, len(favoritesUnderdogsVector)))


# This function converts a region's vector from the default format (all top/bottom)
# to the given format.
# Example Format: TFT means use "Top/Bottom" for the 2nd round and Elite Eight,
#                 but "Favorite/Underdog" for the Sweet Sixteen).  
def convertRegionVector(vectorString, bracketFormat):
	isSecondRoundTopBottom = 'T' == bracketFormat[0]
	isSweetSixteenTopBottom = 'T' == bracketFormat[1]
	isEliteEightTopBottom = 'T' == bracketFormat[2]

	debug = False
	vector = [int(vectorString[i]) for i in range(0, len(vectorString))]
	firstRoundResults = vector[0:8]

	newVector = firstRoundResults

	round1Top = [1, 8, 5, 4, 6, 3, 7, 2]
	round1Bottom = [16, 9, 12, 13, 11, 14, 10, 15]
	secondRoundTeams = []
	for i in range(0, len(firstRoundResults)):
		if firstRoundResults[i] == 1:
			secondRoundTeams.append(round1Top[i])
		else:
			secondRoundTeams.append(round1Bottom[i])

	if debug:
		print secondRoundTeams

	thirdRoundTeams = []
	for i in range(0, 4):
		topTeam = secondRoundTeams[2 * i]
		bottomTeam = secondRoundTeams[2 * i + 1]

		if debug:
			print '{0} vs. {1}'.format(topTeam, bottomTeam)

		gameResult = vector[8 + i]

		if debug:
			print 'Result: {0}\n'.format(gameResult)

		if gameResult == 1:
			thirdRoundTeams.append(topTeam)
		else:
			thirdRoundTeams.append(bottomTeam)
		
		isTopFavorite = topTeam < bottomTeam

		if isSecondRoundTopBottom or isTopFavorite:
			newVector.append(gameResult)
		else:
			newVector.append(1 - gameResult)

	if debug:
		print thirdRoundTeams

	topTeam1 = thirdRoundTeams[0]
	bottomTeam1 = thirdRoundTeams[1]
	topTeam2 = thirdRoundTeams[2]
	bottomTeam2 = thirdRoundTeams[3]

	semiResult1 = vector[12]
	if semiResult1 == 1:
		regionalTopTeam = topTeam1
	else:
		regionalTopTeam = bottomTeam1

	isTopFavorite1 = topTeam1 < bottomTeam1

	if isSweetSixteenTopBottom or isTopFavorite1:
		newVector.append(semiResult1)
	else:
		newVector.append(1 - semiResult1)

	semiResult2 = vector[13]
	if semiResult2 == 1:
		regionalBottomTeam = topTeam2
	else:
		regionalBottomTeam = bottomTeam2

	isTopFavorite2 = topTeam2 < bottomTeam2

	if isSweetSixteenTopBottom or isTopFavorite2:
		newVector.append(semiResult2)
	else:
		newVector.append(1 - semiResult2)

	if debug:
		print '{0} vs. {1}'.format(regionalTopTeam, regionalBottomTeam)

	finalResult = vector[14]

	isTopFavoriteFinal = regionalTopTeam < regionalBottomTeam

	if isEliteEightTopBottom or isTopFavoriteFinal:
		newVector.append(finalResult)
	else:
		newVector.append(1 - finalResult)

	return ''.join(str(newVector[i]) for i in range(0, len(newVector)))


# This function writes the JSON representation of the given bracket to
# the given file. It does not close the file.
def writeBracket(file, bracket):
	fileContent = """\
{
	"bracket": {
		"year": "%s",
		"regions": [
			{"name": "%s", "vector": "%s"},
			{"name": "%s", "vector": "%s"},
			{"name": "%s", "vector": "%s"},
			{"name": "%s", "vector": "%s"}
		],
		"finalfour": "%s",
		"fullvector": "%s"
	}
}
""" % (str(bracket.year), bracket.regions[0].name, bracket.regions[0].vector, bracket.regions[1].name, bracket.regions[1].vector, bracket.regions[2].name, bracket.regions[2].vector, bracket.regions[3].name, bracket.regions[3].vector, bracket.finalFour, bracket.fullVector)
	file.write(fileContent)


# This function counts how many wins each seed number had in 
# each round of the given bracket. 
# It returns a list of 16 lists of 6 values, indicating 
# the number of 1-seed wins in the first round, second round, 
# sweet 16, etc. for each seed number.
# Note that the bracket must use top/bottom representation.
def countWinsPerRound(bracket):
	numSeeds = 16
	numRounds = 6
	winCounts = [[0 for i in range(numSeeds)] for i in range(numRounds)]

	round1Top = [1, 8, 5, 4, 6, 3, 7, 2]
	round1Bottom = [16, 9, 12, 13, 11, 14, 10, 15]

	finalFourTeams = []

	for region in bracket.regions:
		vector = [int(region.vector[i]) for i in range(numSeeds - 1)]

		secondRoundTeams = [vector[i] * round1Top[i] + (1 - vector[i]) * round1Bottom[i] for i in range(8)]
		for team in secondRoundTeams:
			winCounts[0][team - 1] = winCounts[0][team - 1] + 1

		sweetSixteenTeams = [vector[8 + i] * secondRoundTeams[2 * i] + (1 - vector[8 + i]) * secondRoundTeams[2 * i + 1] for i in range(4)]
		for team in sweetSixteenTeams:
			winCounts[1][team - 1] = winCounts[1][team - 1] + 1

		eliteEightTeams = [vector[12 + i] * sweetSixteenTeams[2 * i] + (1 - vector[12 + i]) * sweetSixteenTeams[2 * i + 1] for i in range(2)]
		for team in eliteEightTeams:
			winCounts[2][team - 1] = winCounts[2][team - 1] + 1

		finalFourTeam = eliteEightTeams[1 - vector[14]]
		winCounts[3][finalFourTeam - 1] = winCounts[3][finalFourTeam - 1] + 1
		finalFourTeams.append(finalFourTeam)

	finalFourVector = [int(bracket.finalFour[i]) for i in range(3)]
	finalTeamLeft = finalFourTeams[1 - finalFourVector[0]]
	finalTeamRight = finalFourTeams[3 - finalFourVector[1]]
	winCounts[4][finalTeamLeft - 1] = winCounts[4][finalTeamLeft - 1] + 1
	winCounts[4][finalTeamRight - 1] = winCounts[4][finalTeamRight - 1] + 1

	champTeam = finalTeamLeft * finalFourVector[2] + finalTeamRight * (1 - finalFourVector[2])
	winCounts[5][champTeam - 1] = winCounts[5][champTeam - 1] + 1
	return winCounts


# This function runs a chi-squared test of independence for the
# two given bit positions in every representation.

def testPairwiseIndependenceAllFormats(pos1, pos2, outputFile):
	import json
	from bracketClassDefinitions import Bracket
	from bracketClassDefinitions import Region
	from bracketClassDefinitions import buildBracketFromJson

	DEBUG = True
	formats = ['TTT', 'TTF', 'TFT', 'TFF', 'FTT', 'FTF', 'FFT', 'FFF']
	patterns = ['00', '01', '10', '11']

	for formatType in formats:
		patternFreqs = [0 for i in range(4)]
		filename = 'Brackets/{0}/allBrackets{0}.json'.format(formatType)
		with open(filename, 'r') as inputFile:
			jsonData = inputFile.read().replace('\n', '')
		jsonToPython = json.loads(jsonData)
		bracketList = jsonToPython['brackets']
		numBrackets = len(bracketList)

		for i in range(numBrackets):
			bracketDict = bracketList[i]['bracket']
			bracket = buildBracketFromJson(bracketDict)
			pos1Result = int(bracket.fullVector[pos1])
			pos2Result = int(bracket.fullVector[pos2])
			index = pos1Result * 2 + pos2Result
			patternFreqs[index] = patternFreqs[index] + 1

		rowSums = [patternFreqs[0] + patternFreqs[1], patternFreqs[2] + patternFreqs[3]]
		colSums = [patternFreqs[0] + patternFreqs[2], patternFreqs[1] + patternFreqs[3]]

		# The chi-square critical value for 1 degree of freedom and alpha = 0.05
		# is 3.841. (Source: http://www.itl.nist.gov/div898/handbook/eda/section3/eda3674.htm)
		# We print the result only if it is deemed significant.

		chiSquare = 0
		nObservations = numBrackets
		for r in range(len(rowSums)):
			for c in range(len(colSums)):
				expFreq = rowSums[r] * colSums[c] * 1.0 / nObservations

				if expFreq > 0:
					obsFreq = patternFreqs[2 * r + c] * 1.0
					chiSquare += (obsFreq - expFreq) ** 2 / expFreq
				else:
					print '{0}: Game {1} (left) vs. Game {2} (top)'.format(formatType, pos1, pos2)
					print 'Cannot perform chi-square test of independence: expected frequency is 0.'
					return

		header = '{0}: Game {1} (left) vs. Game {2} (top)'.format(formatType, pos1, pos2)
		chiSquareLine = 'c^2: {:<6.4f}\n\n'.format(chiSquare)

		if chiSquare >= 3.841:
			outputFile.write(header)
			outputFile.write('\n')
			outputFile.write(chiSquareLine)

		if DEBUG:
			print header
			print '      |  0  |  1  || Total'
			print '--------------------------'
			print '   0  | {:<3} | {:<3} || {:<3}'.format(patternFreqs[0], patternFreqs[1], rowSums[0])
			print '--------------------------'
			print '   1  | {:<3} | {:<3} || {:<3}'.format(patternFreqs[2], patternFreqs[3], rowSums[1])
			print '--------------------------'
			print '--------------------------'
			print 'Total | {:<3} | {:<3} || {:<3}\n'.format(colSums[0], colSums[1], numBrackets * 4)
			print chiSquareLine


# This function runs a chi-squared test of independence for the
# two given bit positions in the given representation. It returns
# 1 if the test indicates significant dependence, and 0 otherwise.
#
# If isPooled = True, then the positions are treated as positions
# within the region and are pooled across all four regions.
# In this case, pos1 and pos2 should be between 0 and 14, inclusive. 

def testPairwiseIndependence(pos1, pos2, formatType, outputFile, isPooled=False):
	import json
	from bracketClassDefinitions import Bracket
	from bracketClassDefinitions import Region
	from bracketClassDefinitions import buildBracketFromJson

	DEBUG = False
	patterns = ['00', '01', '10', '11']
	patternFreqs = [0 for i in range(4)]
	filename = 'Brackets/{0}/allBrackets{0}.json'.format(formatType)
	with open(filename, 'r') as inputFile:
		jsonData = inputFile.read().replace('\n', '')
	jsonToPython = json.loads(jsonData)
	bracketList = jsonToPython['brackets']
	numBrackets = len(bracketList)

	for i in range(numBrackets):
		bracketDict = bracketList[i]['bracket']
		bracket = buildBracketFromJson(bracketDict)

		nRegions = 1
		if isPooled:
			nRegions = 4

		for region in range(nRegions):
			offset = region * 15
			pos1Result = int(bracket.fullVector[pos1 + offset])
			pos2Result = int(bracket.fullVector[pos2 + offset])
			index = pos1Result * 2 + pos2Result
			patternFreqs[index] = patternFreqs[index] + 1

	rowSums = [patternFreqs[0] + patternFreqs[1], patternFreqs[2] + patternFreqs[3]]
	colSums = [patternFreqs[0] + patternFreqs[2], patternFreqs[1] + patternFreqs[3]]

	# The chi-square critical value for 1 degree of freedom and alpha = 0.05
	# is 3.841. (Source: http://www.itl.nist.gov/div898/handbook/eda/section3/eda3674.htm)
	# We print the result only if it is deemed significant.

	isSignificant = 0
	chiSquare = 0
	nObservations = numBrackets * nRegions

	for r in range(len(rowSums)):
		for c in range(len(colSums)):
			expFreq = rowSums[r] * colSums[c] * 1.0 / nObservations

			if expFreq > 0:
				obsFreq = patternFreqs[2 * r + c] * 1.0
				chiSquare += (obsFreq - expFreq) ** 2 / expFreq
			else:
				if DEBUG:
					print '{0}: Game {1} (left) vs. Game {2} (top)'.format(formatType, pos1, pos2)
					print 'Cannot perform chi-square test of independence: expected frequency is 0.'
				return isSignificant

	header = '{0}: Bits {1} and {2}'.format(formatType, pos1, pos2)
	chiSquareLine = 'c^2 = {:<6.4f}\n\n'.format(chiSquare)

	if chiSquare >= 3.841:
		# outputFile.write('{0}: {1}'.format(header, chiSquareLine))
		outputFile.write('{0:02d} {1:02d} --- {2:>7.4f}\n'.format(pos1, pos2, chiSquare))
		isSignificant = 1

	if DEBUG:
		print header
		print '      |  0  |  1  || Total'
		print '--------------------------'
		print '   0  | {:<3} | {:<3} || {:<3}'.format(patternFreqs[0], patternFreqs[1], rowSums[0])
		print '--------------------------'
		print '   1  | {:<3} | {:<3} || {:<3}'.format(patternFreqs[2], patternFreqs[3], rowSums[1])
		print '--------------------------'
		print '--------------------------'
		print 'Total | {:<3} | {:<3} || {:<3}\n'.format(colSums[0], colSums[1], numBrackets * 4)
		print chiSquareLine

	return isSignificant


# This function performs a chi-square goodness-of-fit (GOF)
# test of the three given positions against a uniform distribution.
# If isPooled == True, then the four regions are pooled together.

def testGofToUniform(pos1, pos2, pos3, isPooled, outputFile):
	import json
	from bracketClassDefinitions import Bracket
	from bracketClassDefinitions import Region
	from bracketClassDefinitions import buildBracketFromJson

	DEBUG = True
	formats = ['TTT', 'TTF', 'TFT', 'TFF', 'FTT', 'FTF', 'FFT', 'FFF']
	patterns = ['000', '001', '010', '011', '100', '101', '110', '111']
	if pos3 == -1:
		patterns = ['00', '01', '10', '11']

	for formatType in formats:
		patternFreqs = [0 for i in range(len(patterns))]
		filename = 'Brackets/{0}/allBrackets{0}.json'.format(formatType)
		with open(filename, 'r') as inputFile:
			jsonData = inputFile.read().replace('\n', '')
		jsonToPython = json.loads(jsonData)
		bracketList = jsonToPython['brackets']
		numBrackets = len(bracketList)

		for i in range(numBrackets):
			bracketDict = bracketList[i]['bracket']
			bracket = buildBracketFromJson(bracketDict)

			numRegions = 1
			if isPooled:
				numRegions = 4
			for region in range(numRegions):
				offset = region * 15
				pos1Result = int(bracket.fullVector[pos1 + offset])
				pos2Result = int(bracket.fullVector[pos2 + offset])
				if pos3 == -1:
					pos3Result = 0
				else:
					pos3Result = int(bracket.fullVector[pos3 + offset])
				nPatterns = len(patterns)
				index = pos1Result * nPatterns / 2 + pos2Result * nPatterns / 4 + pos3Result
				patternFreqs[index] = patternFreqs[index] + 1

		numBrackets = 33 * numRegions
		expFreq = numBrackets * 1.0 / nPatterns

		chiSquare = 0
		for i in range(nPatterns):
			chiSquare += (patternFreqs[i] - expFreq) ** 2 / expFreq
		
		chiSquareLine = 'chi-square value = {0}'.format(chiSquare)

		print formatType
		print patterns
		print patternFreqs
		print chiSquareLine
		print ''

		if not outputFile is None:
			header = '{3}: GOF Test vs. Uniform For Positions {0}, {1}, and {2}:\n'.format(pos1, pos2, pos3, formatType)
			if pos3 == -1:
				header = '{0}: GOF Test vs. Uniform For Positions {1} and {2}:\n'.format(formatType, pos1, pos2)
			
			outputFile.write(header)
			outputFile.write(patterns)
			outputFile.write('\n')
			outputFile.write(patternFreqs)
			outputFile.write('\n{0}\n\n'.format(chiSquareLine))
