#!/usr/bin/env python
import time
import json
import numpy as np
import os.path
import sys

from scoringUtils import getActualBracketVector
from scoringUtils import scoreFFFBracket, scoreBracket
from utils.runtimeSummary import RuntimeSummary


def load_ref_brackets(fmt='TTT'):
    with open("allBrackets{}.json".format(fmt)) as f:
        data = json.load(f)
        vectors = {
            int(bracket['bracket']['year']):
                np.array(list(bracket['bracket']['fullvector']), dtype=int)
            for bracket in data['brackets']}
    return vectors

probs = {}
all_triplets = {
    'E8_F4': {
        'bits': [12, 13, 14]
    },
    'S16_E8_1': {
        'bits': [8, 9, 12]
    },
    'S16_E8_2': {
        'bits': [10, 11, 13]
    },
    'R1_R2_1': {
        'bits': [0, 1, 8]
    },
    'R1_R2_2': {
        'bits': [2, 3, 9]
    },
    'R1_R2_3': {
        'bits': [4, 5, 10]
    },
    'R1_R2_4': {
        'bits': [6, 7, 11]
    }
}

def fill_triplet_probs():
    global all_triplets
    names = list(all_triplets.keys())
    for year in range(2013, 2019):
        vectors = np.vstack([v for y, v in all_brackets.items() if y < year])
        vectors = vectors[:, :60].reshape(-1, 15)
        for name in names:
            triplet = all_triplets[name]['bits']
            triplets, counts = np.unique(vectors[:, triplet], axis=0, return_counts=True)
            cdf = [1. * counts[:i].sum() / counts.sum()
                   for i in range(len(counts) + 1)]
            all_triplets[name][year] = {
                'p': cdf,
                'triplets': triplets
            }


def getP(model, year, bit_id):
    base_p = probs[year][bit_id]
    if model.get('perturbation'):
        if model.get('perturbationType') == 'fixed':
            p = base_p + np.random.uniform(-model['perturbation'], model['perturbation'])
        else:
            p = np.random.uniform((1 - model['perturbation']) * base_p, (1 + model['perturbation']) * base_p)
    else:
        p = base_p
    return np.clip(p, 0., 1.)


def generateBracket(model, year):
    if model.get('endModel') is None:
        n = np.random.rand(63)
        p = [getP(model, year, i) for i in range(63)]
        bracket = (n < p).astype(int)
        for region in range(4):
            for t in model.get('triplets', []):
                n = np.random.rand()
                for i in range(8):
                    if n > all_triplets[t][year]['p'][i] and n < all_triplets[t][year]['p'][i+1]:
                        bracket[15 * region + np.array(all_triplets[t]['bits'])]= all_triplets[t][year]['triplets'][i]
                        break
        return bracket
    else:
        raise Exception('Not implemented yet')


def performExperiments(numTrials, year, batchNumber, model):
    summarizer = RuntimeSummary(model)
    correctVector = getActualBracketVector(year)

    scores = [None] * numTrials
    scoreMethod = scoreFFFBracket if model.get('format') == 'FFF' else scoreBracket

    for n in range(numTrials):
        newBracketVector = generateBracket(model, year)
        summarizer.analyze_bracket(newBracketVector)
        newBracketScore = scoreMethod(newBracketVector, correctVector)
        scores[n] = newBracketScore[0]

    bracketListDict = {'year': year, 'actualBracket': ''.join(str(bit) for bit in correctVector), 'scores': scores}

    if numTrials < 1000:
        folderName = 'Experiments/{0}Trials'.format(numTrials)
    else:
        folderName = 'Experiments/{0}kTrials'.format(int(numTrials / 1000))
    batchFolderName = '{0}/Batch{1:02d}'.format(folderName, batchNumber)

    outputFilename = '{2}/generatedScores_{0}_{1}.json'.format(model['modelName'], year, batchFolderName)
    summaryFilename = '{2}/vectorStats_{0}_{1}.json'.format(model['modelName'], year, batchFolderName)
    with open(outputFilename, 'w') as outputFile:
        outputFile.write(json.dumps(bracketListDict))
    summarizer.to_json(summaryFilename)


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

if len(sys.argv) == 5:
    modelIndex = int(sys.argv[4])
else:
    modelIndex = -1

for modelId, modelDict in enumerate(modelsList):
    if modelIndex != -1 and modelIndex != modelId:
        continue
    modelName = modelDict['modelName']

    all_brackets = load_ref_brackets(modelDict.get('format', 'TTT'))
    # calculate bitwise MLE probs
    for year in range(2013, 2019):
        vectors = np.vstack([v for y, v in all_brackets.items() if y < year])
        probs[year] = np.mean(vectors, axis=0)

    fill_triplet_probs()

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

