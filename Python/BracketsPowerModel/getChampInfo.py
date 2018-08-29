#!/usr/bin/env python
from bracketInfoUtils import getLoser, getWinner
from scoringUtils import getActualBracketVector
import json

# Author: Ian Ludden
# Date:   15 Mar 2018
# 
# This script finds the seed and region indices of the 
# champion, runner-up, and semi-final losers for each 
# NCAA Men's Basketball Tournament bracket from 1985
# through 2017. 

print 'Year,Champ Seed,Champ Region,FF_c Seed,FF_c Region,Runner-up Seed,Runner-up Region,FF_r Seed,FF_r Region'

for year in range(1985, 2017 + 1):
	bracketVector = getActualBracketVector(year)
	champInfo = getWinner(bracketVector)
	ruInfo = getLoser(bracketVector)

	print '{8},{0},{1},{2},{3},{4},{5},{6},{7}'.format(champInfo[0], champInfo[1], champInfo[2], champInfo[3], ruInfo[0], ruInfo[1], ruInfo[2], ruInfo[3], year)
