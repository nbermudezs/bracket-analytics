#!/usr/bin/env python
import time
import json
import numpy as np
import os.path
import sys

from scoringUtils import getActualBracketVector
from scoringUtils import scoreBracket


def load_ref_brackets():
    with open("allBracketsTTT.json") as f:
        data = json.load(f)
        vectors = {
            int(bracket['bracket']['year']):
                np.array(list(bracket['bracket']['fullvector']), dtype=int)
            for bracket in data['brackets']}
    return vectors

all_brackets = load_ref_brackets()
probs = {}
for year in range(2013, 2019):
    vectors = np.vstack([v for y, v in all_brackets.items() if y < year])
    probs[year] = np.mean(vectors, axis=0)


def getP(model, year, bit_id):
    return 0.5


def generateBracket(model, year):
    n = np.random.rand(63)
    p = [getP(model, year, i) for i in range(63)]
    return (n < p).astype(int).tolist()


def performExperiments(numTrials, year, batchNumber, model):
    correctVector = getActualBracketVector(year)

    scores = [None] * numTrials

    for n in range(numTrials):
        newBracketVector = generateBracket(model, year)
        newBracketScore = scoreBracket(newBracketVector, correctVector)
        scores[n] = newBracketScore[0]

    bracketListDict = {'year': year, 'actualBracket': ''.join(str(bit) for bit in correctVector), 'scores': scores}

    if numTrials < 1000:
        folderName = 'Experiments/{0}Trials'.format(numTrials)
    else:
        folderName = 'Experiments/{0}kTrials'.format(int(numTrials / 1000))
    batchFolderName = '{0}/Batch{1:02d}'.format(folderName, batchNumber)

    outputFilename = '{2}/generatedScores_{0}_{1}.json'.format(model['modelName'], year, batchFolderName)
    with open(outputFilename, 'w') as outputFile:
        outputFile.write(json.dumps(bracketListDict))


######################################################################
# This script runs experiments with the given models,
# number of trials, and number of batches for 2013 through 2018.
######################################################################

# Load models
if len(sys.argv) > 3:
    modelFilename = sys.argv[3]
else:
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

    for year in range(2013, 2019):
        print '\t {0}: {1}'.format(year, time.strftime("%Y-%m-%d %H:%M"))
        for batchNumber in range(numBatches):
            print '\t\t {0}: {1}'.format(batchNumber, time.strftime("%Y-%m-%d %H:%M"))
            if numTrials < 1000:
                folderName = 'Experiments/{0}Trials'.format(numTrials)
            else:
                folderName = 'Experiments/{0}kTrials'.format(int(numTrials / 1000))

            if not os.path.exists(folderName):
                os.makedirs(folderName)

            batchFolderName = '{0}/Batch{1:02d}'.format(folderName, batchNumber)
            if not os.path.exists(batchFolderName):
                os.makedirs(batchFolderName)

            performExperiments(numTrials, year, batchNumber, modelDict)

