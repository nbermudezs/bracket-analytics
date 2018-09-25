#!/usr/bin/env python
import csv
import os.path
import sys

######################################################################
# Author: 	Ian Ludden
# Date: 	05 Mar 2018
# Modified: 10 Apr 2018
#
# This script prepares multiple batches of treatments for
# multiple comparisons with the best (MCB) analysis.
######################################################################

numTrials = int(sys.argv[1])
metricName = sys.argv[2]
minBatchNum = int(sys.argv[3])
maxBatchNum = int(sys.argv[4])

if len(sys.argv) > 5:
	summaries_root = sys.argv[5]
else:
	summaries_root = 'Summaries'

if numTrials < 1000:
	trialsString = '{0}'.format(numTrials)
else:
	trialsString = '{0}k'.format(int(numTrials / 1000))

for year in range(2013, 2019):
	print '{0} Tournament:'.format(year)

	print 'Batch,'

	for batchNum in range(minBatchNum, maxBatchNum + 1):
		batchFilename = '{0}/exp_{1}_batch_{2:02d}.csv'.format(
			summaries_root, trialsString, batchNum)

		with open(batchFilename, 'rb') as csvfile:
			reader = csv.reader(csvfile)

			isCorrectYear = False
			for row in reader:
				if len(row) == 0:
					continue
				if str(year) in row[0]:
					isCorrectYear = True
				if isCorrectYear and (metricName in row[0]):
					sys.stdout.write('{0}, '.format(batchNum))
					sys.stdout.write(', , '.join(row[1:]))
					print ''
					break

	print ''
