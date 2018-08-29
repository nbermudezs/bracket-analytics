#!/usr/bin/env python

from scoringUtils import scoreBracket

# Test 2015 scoring
actualBracket =   "111111111101111111110011010101111101110001000111100111110101000"

# pickFavoriteString = '111111111000101111111111000101111111111000101111111111000101111'

# Pick Favorite (with correct last three bits)
pfBracket = '111111111000101111111111000101111111111000101111111111000101000'
#111111111000101
#111111111000101
#111111111000101
#111111111000101
#000

actualVector = [int(actualBracket[i]) for i in range(63)]
testVector = [int(pfBracket[i]) for i in range(63)]

pfScores = scoreBracket(testVector, actualVector)
print pfScores


# Pick Favorite (with bits 11 and 14 of third region (East) flipped)
modifiedBracket = "111111111000101111111111000101111111111001100111111111000101000"
#111111111000101
#111111111000101
#111111111001100
#111111111000101
#000

testVector = [int(modifiedBracket[i]) for i in range(63)]

modScores = scoreBracket(testVector, actualVector)
print modScores


# Pick Favorite (with bits 11, 12, and 14 of third region (East) flipped)
modifiedBracket = '111111111000101111111111000101111111111001000111111111000101000'
#111111111000101
#111111111000101
#111111111001000
#111111111000101
#000

testVector = [int(modifiedBracket[i]) for i in range(63)]

modScores = scoreBracket(testVector, actualVector)
print modScores


# Pick Favorite (with bits 8, 11, 12, and 14 of third region (East) flipped)
modifiedBracket = '111111111000101111111111000101111111110001000111111111000101000'
#111111111000101
#111111111000101
#111111110001000
#111111111000101
#000

testVector = [int(modifiedBracket[i]) for i in range(63)]

modScores = scoreBracket(testVector, actualVector)
print modScores