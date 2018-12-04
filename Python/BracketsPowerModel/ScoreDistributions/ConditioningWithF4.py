#!/usr/bin/env python
import time
import json
import numpy as np
import pandas as pd
import os.path
import random
import sys
from math import log, ceil, floor

from collections import defaultdict
from ScoreDistributions.conditioningWithF4SamplingUtils import getAllE8Seeds
from ScoreDistributions.conditioningWithF4SamplingUtils import getF4SeedSplit, getF4SeedTogether, getAllF4Seeds
from ScoreDistributions.conditioningWithF4SamplingUtils import getChampionInfo, getRunnerUpInfo

from scoringUtils import getActualBracketVector
from scoringUtils import scoreBracket


######################################################################
# Author:
#     Ian Ludden
#
# Date created:
#     15 Apr 2018
#
# Last modified:
#     16 Apr 2018
#
# This general version handles all parameters previously implemented
# separately in runExperimentsFixedAlpha.py,
# runExperimentsSampleF4.py, and runExperimentsSampleE8.py.
#
# Specifically, this version supports:
# - "Forward" Power Model
# - "Reverse" Power Model (generate champ and runner-up, then forward)
# - "Reverse" Power Model with F4 (also generate other two F4 seeds)
# - F4 Model 1, where F4 seeds are generated using "Model 1,"
#   then power model is applied to games before and after
# - F4 Model 2, where F4 seeds are generated using "Model 2,"
#   then power model is applied to games before and after
# - E8 Model, where E8 seeds are generated,
#   then power model is applied to games before and after
#
# Also, the Round 1 alpha values are optionally grouped as:
# (1, 16) alone
# (2, 15) alone
# (3, 14), (4, 13)
# (5, 12), (6, 11), (7, 10)
# (8, 9) alone and fixed at 0.5 probability (alpha = 0)
#
# By default, all weighted alpha values are computed using the
# standard weighting (multiply each alpha by [# matchups]).
#
# If "isSeedWeighted" is set to "True", then the seed-weighted
# average alpha values are used.
#
# This version no longer requires models to specify the alpha value
# parameters for each round. Round 1 is always matchup-specific
# (with optional grouping), and Rounds 2-6 always use a
# weighted average.
######################################################################

# the None at the beginning is to deal with the fact that seeds are 1-indexed
annealing_probs_normal = {
    '25_1985': [  # 25_1985
        None,
        1.,
        1.,
        1.,
        1.,
        0.814192,
        0.789125,
        0.756526,
        0.415157
    ],
    '26_1985': [  # 26_1985
        None,
        1.,
        1.,
        1.,
        1.,
        0.799078,
        0.791546,
        0.697350,
        0.441784
    ],
    '27_1985': [  # 27_1985
        None,
        1.,
        1.,
        1.,
        1.,
        0.722126,
        0.762280,
        0.689283,
        0.527814
    ],
    '28_1985': [  # 28_1985
        None,
        1.,
        1.,
        0.989434,
        0.971340,
        0.755157,
        0.682175,
        0.611461,
        0.503551
    ],
    '29_1985': [  # 29_1985
        None,
        1.,
        0.995290,
        0.825406,
        0.949107,
        0.654723,
        0.534530,
        0.709000,
        0.562951
    ],
    '30_1985': [  # 30_1985
        None,
        1.,
        1.,
        0.995477,
        0.963320,
        0.613353,
        0.642372,
        0.715826,
        0.350238
    ],
    '31_1985': [  # 31_1985
        None,
        0.992647,
        1.000000,
        0.845588,
        0.794118,
        0.757265,
        0.614272,
        0.605541,
        0.500000
    ],
    '28_2002': [  # 28_2002
        None,
        1.,
        0.995914,
        1.,
        0.827174,
        0.644819,
        0.623167,
        0.511112,
        0.641224
    ],
    '29_2002': [  # 29_2002
        None,
        1.,
        1.,
        0.952321,
        0.884696,
        0.651188,
        0.629961,
        0.772527,
        0.664883
    ],
    '30_2002': [  # 30_2002
        None,
        1.,
        1.,
        1.,
        0.783221,
        0.747075,
        0.660914,
        0.801631,
        0.419372
    ]
}

BT_probs = {}
def load_BT_probs():
    global BT_probs
    for year in range(2013, 2019):
        year_dist = defaultdict(float)
        data = pd.read_csv('bradleyTerry/probs-{}.csv'.format(year), usecols=['player1', 'player2', 'prob1wins']).values
        for i in range(data.shape[0]):
            s1, s2, p = data[i, :]
            s1 = int(s1[1:])
            s2 = int(s2[1:])
            year_dist[(s1, s2)] = p
            year_dist[(s2, s1)] = 1. - p
        BT_probs[year] = year_dist

annealing_probs_normal = {k: np.array(omega)
                          for k, omega in annealing_probs_normal.items()}


# Returns the estimated probability that s1 beats s2
def getP(s1, s2, model, year, roundNum):
    if model.get('annealing_model') is not None and roundNum == 1:
        return annealing_probs_normal[model.get('annealing_model')][min(s1, s2)]
    if model.get('bradleyTerry'):
        if s1 == s2:
            return 0.5
        return BT_probs[year][(s1, s2)]
    alpha = getAlpha(s1, s2, model, year, roundNum)
    s1a = (s1 * 1.0) ** alpha
    s2a = (s2 * 1.0) ** alpha
    return s2a / (s1a + s2a)


# This function generates a 63-element list of 0s and 1s
# to represent game outcomes in a bracket. The model specifies
# which alpha value(s) to use for each round.
def generateBracket(model, year):
    model['F4_correct_counter'] = model['conditions'].get('F4_correct')
    bracket = []

    random.seed()

    endModel = 'None'
    if 'endModel' in model:
        endModel = model['endModel']

    e8Seeds = []
    if endModel == 'E8':
        e8Seeds = getAllE8Seeds(year, model)
    else:
        e8Seeds = [-1, -1, -1, -1, -1, -1, -1, -1]

    f4Seeds = []
    if endModel == 'F4_1':
        f4Seeds = getAllF4Seeds(year, getF4SeedTogether, model, NC_info=None, RU_info=None)
    elif endModel == 'F4_2':
        f4Seeds = getAllF4Seeds(year, getF4SeedSplit, model, NC_info=None, RU_info=None)
    else:
        f4Seeds = [-1, -1, -1, -1]

    ncgSeeds = [-1, -1]
    if 'Rev' in endModel:
        champion, champRegion = getChampionInfo(year, model)
        runnerUp, ruRegion = getRunnerUpInfo(year, model, (champion, champRegion))
        champHalf = champRegion / 2
        f4Seeds = getAllF4Seeds(year, getF4SeedTogether, model,
                                RU_info=(runnerUp, ruRegion),
                                NC_info=(champion, champRegion))
        # print('NC', champion, champRegion)
        # print('RU', runnerUp, ruRegion)
        ruRegion = ruRegion % 2

        if champHalf == 0:
            ncgSeeds = [champion, runnerUp]
        else:
            ncgSeeds = [runnerUp, champion]

        ffrRegion = 1 - ruRegion

        if champRegion < 2:
            ruRegion += 2
            ffrRegion += 2
            ffcRegion = 1 - champRegion
        else:
            ffcRegion = 5 - champRegion

    if endModel == 'Rev_4':
        f4Seeds[ffcRegion] = getF4SeedTogether(year)
        f4Seeds[ffrRegion] = getF4SeedTogether(year)

    # Loop through regional rounds R64, R32, and S16
    for region in range(4):
        seeds = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]
        for roundNum in range(1, 5):
            numGames = int(len(seeds) / 2)
            newSeeds = []
            for gameNum in range(numGames):
                s1 = seeds[2 * gameNum]
                s2 = seeds[2 * gameNum + 1]

                # Force any fixed F4/E8 seeds to make it through
                s1Wins = (s1 == f4Seeds[region]) or ((roundNum < 4) and (
                        (s1 == e8Seeds[2 * region]) or (
                        s1 == e8Seeds[2 * region + 1])))
                s2Wins = (s2 == f4Seeds[region]) or ((roundNum < 4) and (
                        (s2 == e8Seeds[2 * region]) or (
                        s2 == e8Seeds[2 * region + 1])))

                if s1Wins:
                    p = 1
                elif s2Wins:
                    p = 0
                else:
                    p = getP(s1, s2, model, year, roundNum)

                if random.random() <= p:
                    bracket.append(1)
                    newSeeds.append(s1)
                else:
                    bracket.append(0)
                    newSeeds.append(s2)
            seeds = newSeeds
        f4Seeds[region] = seeds[0]

    # Round 5:
    for gameNum in range(2):
        s1 = f4Seeds[2 * gameNum]
        s2 = f4Seeds[2 * gameNum + 1]

        if 'Rev' in endModel:
            if (2 * gameNum == champRegion) or (2 * gameNum == ruRegion):
                p = 1
            elif (2 * gameNum + 1 == champRegion) or (
                    2 * gameNum + 1 == ruRegion):
                p = 0
            else:
                p = getP(s1, s2, model, year, 5)
        else:
            p = getP(s1, s2, model, year, 5)

        if random.random() <= p:
            bracket.append(1)
            ncgSeeds[gameNum] = s1
        else:
            bracket.append(0)
            ncgSeeds[gameNum] = s2

    # Round 6:
    s1 = ncgSeeds[0]
    s2 = ncgSeeds[1]

    if 'Rev' in endModel:
        if champHalf == 0:
            p = 1 if not model['conditions'].get('RU_wins', False) else 0
        else:
            p = 0 if not model['conditions'].get('RU_wins', False) else 1
    else:
        p = getP(s1, s2, model, year, 6)

    if random.random() <= p:
        bracket.append(1)
    else:
        bracket.append(0)
    # print(f4Seeds)

    # if year == 2016:
    #     truth = [1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1]
    #     scores = scoreBracket(bracket, truth)
    #     if scores[-1] != 320:
    #         import pdb; pdb.set_trace()

    return bracket


# This function returns the alpha value to use for
# predicting the outcome of a game in the given round
# between the given seeds s1, s2.
def getAlpha(s1, s2, model, year, roundNum):
    # Round 1 grouped alpha values for predicting 2013-2019,
    # where the first index is the better seed and the
    # second index is [year - 2013]. The grouping is:
    # 1, 2, 3-4, 5-7, 8
    r1GroupedAlphas = [
        [],
        [2, 2, 2, 2, 2, 2, 1.7692038993],
        [1.4252197727, 1.3625656943, 1.3804523797, 1.3977167918, 1.3440101948,
         1.3602838429, 1.3760407791],
        [1.1327439019, 1.1199577274, 1.1293433883, 1.1189438356, 1.1083639629,
         1.1365944197, 1.1245771481],
        [1.1327439019, 1.1199577274, 1.1293433883, 1.1189438356, 1.1083639629,
         1.1365944197, 1.1245771481],
        [0.992260877, 0.996405404, 0.9802794213, 1.0053287528, 0.9535901796,
         0.947768435, 0.9722115628],
        [0.992260877, 0.996405404, 0.9802794213, 1.0053287528, 0.9535901796,
         0.947768435, 0.9722115628],
        [0.992260877, 0.996405404, 0.9802794213, 1.0053287528, 0.9535901796,
         0.947768435, 0.9722115628],
        [0, 0, 0, 0, 0, 0, 0]]

    r1GroupedAlphasSeedWeighted = [
        [],
        [2, 2, 2, 2, 2, 2, 1.7692038993],
        [1.4252197727, 1.3625656943, 1.3804523797, 1.3977167918, 1.3440101948,
         1.3602838429, 1.3760407791],
        [1.1239462408, 1.1116452654, 1.120961419, 1.1095749793, 1.0990011131,
         1.1266664795, 1.1160620929],
        [1.1239462408, 1.1116452654, 1.120961419, 1.1095749793, 1.0990011131,
         1.1266664795, 1.1160620929],
        [0.9481178098, 0.9341775923, 0.9014353156, 0.928223297, 0.8792796956,
         0.8692346352, 0.8944760731],
        [0.9481178098, 0.9341775923, 0.9014353156, 0.928223297, 0.8792796956,
         0.8692346352, 0.8944760731],
        [0.9481178098, 0.9341775923, 0.9014353156, 0.928223297, 0.8792796956,
         0.8692346352, 0.8944760731],
        [0, 0, 0, 0, 0, 0, 0]]

    # Round 1 separated alpha values for predicting 2013-2019,
    # where the first index is the better seed and the
    # second index is [year - 2013].
    r1SeparateAlphas = [
        [],
        [2, 2, 2, 2, 2, 2, 1.7692038993],
        [1.4252197727, 1.3625656943, 1.3804523797, 1.3977167918, 1.3440101948,
         1.3602838429, 1.3760407791],
        [1.1631440406, 1.1437646, 1.1260389104, 1.0702482606, 1.0570363456,
         1.0808615169, 1.1038431398],
        [1.1023437632, 1.0961508547, 1.1326478663, 1.1676394106, 1.1596915802,
         1.1923273226, 1.1453111565],
        [0.7612823908, 0.6898202312, 0.6242869483, 0.6828764698, 0.6603066747,
         0.6767844807, 0.7293107575],
        [1.0995538121, 1.1222629842, 1.0820607889, 1.0447312883, 0.9537101213,
         0.86947563, 0.8427577133],
        [1.1159464279, 1.1771329966, 1.2344905268, 1.2883785003, 1.2467537426,
         1.2970451943, 1.3445662175],
        [0, 0, 0, 0, 0, 0, 0]]

    # Rounds 2-6 weighted average alpha values for predicting
    # 2013-2019, where the first index is [roundNum - 2] and
    # the second index is [year - 2013].
    r2to6Alphas = [
        [1.0960226368, 1.0255184405, 1.0280047853, 1.0169015383, 1.0085075325,
         1.0517190671, 1.0349243918],
        [0.9074472394, 0.8963083681, 0.8581664326, 0.8815834483, 0.9021714769,
         0.9088993287, 0.8644826467],
        [0.3579691718, 0.2302351327, 0.1909716145, 0.2167374254, 0.136706458,
         0.1188463061, 0.1504395788],
        [0.6673769231, 0.6983681575, 0.5784406838, 0.6093441472, 0.6389325696,
         0.674510496, 0.7010202861],
        [1.4133971593, 1.4171625002, 1.441447396, 1.441447396, 1.1671880002,
         1.1671880002, 1.199219231]]

    r2to6AlphasSeedWeighted = [
        [0.7300894976, 0.7256867311, 0.7262248008, 0.7307164601, 0.7402819935,
         0.7447518994, 0.7411460851],
        [0.7154059556, 0.7241293547, 0.7009183735, 0.7114893029, 0.7391687766,
         0.7355894309, 0.7143276345],
        [0.5619089765, 0.5264272183, 0.4945600154, 0.4919846802, 0.4697685742,
         0.4595952558, 0.4593748076],
        [0.8217277548, 0.8254069985, 0.6989678614, 0.7047260475, 0.7106414922,
         0.7227985752, 0.7466939569],
        [0.711033407, 0.7322638446, 0.8439593326, 0.8439593326, 0.813649393,
         0.813649393, 0.8276050547]]

    isR1Grouped = 'False'
    if 'isR1Grouped' in model:
        isR1Grouped = 'True' in model['isR1Grouped']

    isSeedWeighted = ('isSeedWeighted' in model) and (
            'True' in model['isSeedWeighted'])

    alpha = 0

    if (isR1Grouped) and (roundNum == 1):
        if isSeedWeighted:
            alpha = r1GroupedAlphasSeedWeighted[s1][year - 2013]
        else:
            alpha = r1GroupedAlphas[s1][year - 2013]
    elif roundNum == 1:
        alpha = r1SeparateAlphas[s1][year - 2013]
    else:
        if isSeedWeighted:
            alpha = r2to6AlphasSeedWeighted[roundNum - 2][year - 2013]
        else:
            alpha = r2to6Alphas[roundNum - 2][year - 2013]

    return alpha


# Unused: if we want to measure this later, we can.
#
# # This function computes how many picks a bracket
# # got correct given the bracket's score vector.
# def calcCorrectPicks(scoreVector):
# 	numCorrectPicks = 0
# 	for roundNum in range(1, 7):
# 		numCorrectPicks += scoreVector[roundNum] / (10 * (2 ** (roundNum - 1)))
# 	return numCorrectPicks


# This function generates and scores brackets
# for the given year using the given model.
# It prints the results in JSON format.
def performExperiments(numTrials, year, batchNumber, model):
    correctVector = getActualBracketVector(year)

    brackets = []
    for n in range(numTrials):
        newBracketVector = generateBracket(model, year)
        newBracketScore = scoreBracket(newBracketVector, correctVector)

        if model['conditions'].get('F4_correct') != '*':
            f4_correct = model['conditions'].get('F4_correct')
            assert(newBracketScore[-3] == 80 * f4_correct)
            if f4_correct == 0:
                assert (newBracketScore[-1] == 0)
                assert (newBracketScore[-2] == 0)

        if model['modelName'] == 'NC_correct_noRU':
            assert(newBracketScore[-1] == 320)
            assert(newBracketScore[-2] == 160)
            assert(newBracketScore[-3] >= 80)
        elif model['modelName'] == 'NC_correct':
            try:
                assert (newBracketScore[-1] == 320)
                assert (newBracketScore[-2] >= 160)
            except:
                import pdb; pdb.set_trace()
        elif model['modelName'] == 'NC_RU_correct':
            assert (newBracketScore[-1] == 320)
            assert (newBracketScore[-2] == 320)
        elif model['modelName'] == 'NC_RU_swapped':
            assert (newBracketScore[-1] == 0)
            assert (newBracketScore[-2] == 320)
            assert (newBracketScore[0] <= 1920 - 320)
        elif model['modelName'] == 'RU_correct_noNC':
            assert (newBracketScore[-1] == 0)
            assert (newBracketScore[-2] >= 160)
        elif model['modelName'] == 'RU_correct':
            assert (newBracketScore[-2] >= 160)
        elif 'F4' in model['modelName'] and type(model['conditions'].get('F4_correct')) == int:
            count = model['conditions'].get('F4_correct')
            assert (newBracketScore[-3] == 80 * count)
        elif 'E8' in model['modelName'] and type(model['conditions'].get('E8_correct')) == int:
            count = model['conditions'].get('E8_correct')
            assert (newBracketScore[-4] == 40 * count)

        # numCorrectPicks = calcCorrectPicks(newBracketScore)

        newBracketString = ''.join(str(bit) for bit in newBracketVector)

        # brackets.append({'bracketVector': newBracketString, 'score': newBracketScore, 'correctPicks': numCorrectPicks, 'model': model['modelName']})
        brackets.append(
            {'bracketVector': newBracketString, 'score': newBracketScore})

    bracketListDict = {'year': year, 'actualBracket': ''.join(
        str(bit) for bit in correctVector), 'brackets': brackets}

    if numTrials < 1000:
        folderName = 'Experiments/Conditioning/{0}Trials'.format(numTrials)
    else:
        folderName = 'Experiments/Conditioning/{0}kTrials'.format(int(numTrials / 1000))
    batchFolderName = '{0}/Batch{1:02d}'.format(folderName, batchNumber)

    outputFilename = '{2}/generatedBrackets_{0}_{1}.json'.format(
        model['modelName'], year, batchFolderName)
    with open(outputFilename, 'w') as outputFile:
        outputFile.write(json.dumps(bracketListDict))


######################################################################
# This script runs experiments with the given models,
# number of trials, and number of batches for 2013 through 2018.
######################################################################
load_BT_probs()

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

# import cProfile, pstats
# from io import StringIO
# pr = cProfile.Profile()
# pr.enable()

for modelDict in modelsList:
    modelName = modelDict['modelName']

    print '{0:<8s}: {1}'.format(modelName, time.strftime("%Y-%m-%d %H:%M"))

    for batchNumber in range(numBatches):
        if numTrials < 1000:
            folderName = 'Experiments/Conditioning/{0}Trials'.format(numTrials)
        else:
            folderName = 'Experiments/Conditioning/{0}kTrials'.format(int(numTrials / 1000))

        if not os.path.exists(folderName):
            os.makedirs(folderName)

        batchFolderName = '{0}/Batch{1:02d}'.format(folderName, batchNumber)
        if not os.path.exists(batchFolderName):
            os.makedirs(batchFolderName)

        for year in range(2013, 2014):
            performExperiments(numTrials, year, batchNumber, modelDict)

#
# pr.disable()
# s = StringIO()
# ps = pstats.Stats(pr).sort_stats('cumulative')
# ps.print_stats()
