#!/usr/bin/env python
from Utils.scoringUtils import scoreBracket

actual2012String = '110101001001111101111101001001111111111010100110001011010100101'
testString = '100111111000111111101111010001101111011100100101111111010101110'

actual2012Bracket = [int(actual2012String[i]) for i in range(len(actual2012String))]
testBracket = [int(testString[i]) for i in range(len(testString))]

scores = scoreBracket(testBracket, actual2012Bracket)

print scores


# Actual 2012:
# 11010100 1001 11 1
# 10111110 1001 00 1
# 11111111 1010 10 0
# 11000101 1010 10 0
# 10 1

# Test 2012:
# 10011111 1000 11 1
# 11110111 1010 00 1
# 10111101 1100 10 0
# 10111111 1010 10 1
# 11 0