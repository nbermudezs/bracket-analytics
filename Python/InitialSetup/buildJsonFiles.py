#!/usr/bin/env python
import sys
import os.path

startYear = int(sys.argv[1])
endYear = int(sys.argv[2])

for year in range(startYear, endYear + 1):
	print(year)
	filename = str(year) + 'bracket.txt'
	newFilename = str(year) + '.json'

	regionNames = ['', '', '', '']
	regionVectors = ['', '', '', '']
	finalFour = ''
	fullVector = ''

	if not os.path.isfile(filename):
		continue

	with open(filename, 'r') as bracketTextFile:
		counter = 1
		for line in bracketTextFile:
			line = line.rstrip('\n')
			if counter < 13:
				if counter % 3 == 2:
					regionNames[counter / 3] = line.rstrip(':')
				if counter % 3 == 0:
					regionVectors[counter / 3 - 1] = line
			if counter == 15:
				finalFour = line
			if counter == 18:
				fullVector = line
			counter += 1
	bracketTextFile.close()

	if not fullVector == ''.join(regionVectors) + finalFour:
		print('------------------------------------------')
		print 'ERROR: Vectors do not match for year %s.' % (str(year))
		print('------------------------------------------')
		continue

	bracketJsonFile = open(newFilename, 'w')
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
""" % (str(year), regionNames[0], regionVectors[0], regionNames[1], regionVectors[1], regionNames[2], regionVectors[2], regionNames[3], regionVectors[3], finalFour, fullVector)
	bracketJsonFile.write(fileContent)
	bracketJsonFile.close()
