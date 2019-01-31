#!/usr/bin/env python
import time
import json
import numpy as np
import os.path
import random
import sys
from math import log, ceil, floor

from samplingUtils import getTruncGeom
from samplingUtils import getE8SeedBottom, getE8SeedTop
from samplingUtils import getF4SeedSplit, getF4SeedTogether
from samplingUtils import getChampion, getRunnerUp

from scoringUtils import applyRoundResults
from scoringUtils import getActualBracketVector
from scoringUtils import scoreBracket
from triplets.Constant import DEFAULT_FORMAT

import triplets.generators.AllTripletsRev as AllTripletsRev
import triplets.generators.IID_AllTriplets as IID_AllTriplets
import triplets.generators.IID_2TripletsPerRegion as IID_2TripletsPerRegion
import triplets.generators.IID_2TripletsPerRegion_F4Triplet as IID_2TripletsPerRegion_F4Triplet
import triplets.generators.E8With5TripletsPerRegion as E8With5TripletsPerRegion
import triplets.generators.E8With2TripletsPerRegion as E8With2TripletsPerRegion

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

uniform_eta_5 = {
    'model10': [ # 25_1985
        1.0,
        0.577924,
        0.738162,
        1.,
        0.750773,
        1.0,
        0.789084,
        1.0
    ],
    'model11': [ # 26_1985
        1.,
        0.492703,
        0.865210,
        1.,
        0.792790,
        1.,
        0.735384,
        1.
    ],
    'model12': [ # 27_1985
        1.,
        0.515851,
        0.767134,
        1.,
        0.659071,
        1.,
        0.624253,
        1.
    ],
    'model13': [ # 28_1985
        1.,
        0.503742,
        0.744503,
        0.985903,
        0.589451,
        0.983175,
        0.629174,
        1.
    ],
    'model1': [ # 29_1985
        1.,
        0.549093,
        0.750055,
        0.934562,
        0.667669,
        0.979045,
        0.654386,
        1.
    ],
    'model14': [ # 30_1985
        1.,
        0.702520,
        0.607727,
        0.955776,
        0.527676,
        0.914587,
        0.731135,
        1.
    ],
    'model15': [ # 31_1985
        0.979950,
        0.522624,
        0.608672,
        0.954450,
        0.815560,
        0.859511,
        0.544364,
        0.986404
    ],
    'model21': [ # 28_2002
        1,
        0.571343,
        0.717079,
        0.951833,
        0.608841,
        1.,
        0.719049,
        1.
    ],
    'model20': [ # 29_2002
        1.0,
        0.642990,
        0.715042,
        0.785525,
        0.673557,
        1.,
        0.829395,
        1.
    ],
    'model23': [ # 30_2002
        1.0,
        0.5160255517843886,
        0.7835308548717009,
        0.8281494585145786,
        0.5682714030506578,
        0.8851682475462623,
        0.5408879753527419,
        0.969572984028147
    ],
    '30_2002': [
        0.999171,
        0.642037,
        0.364341,
        0.932316,
        0.380420,
        1.,
        0.727067,
        1.
    ],
    '31_1985': [
        0.979950,
        0.522624,
        0.608672,
        0.954450,
        0.815560,
        0.859511,
        0.544364,
        0.986404
    ],
    '30_1985': [
        0,0,0,0,0,0,0,0        
    ]
}

uniform_eta_10 = {
    '25_1985': [ # 25_1985
        1.0,
        0.595991,
        0.759279,
        1.,
        0.885420,
        0.973687,
        0.741745,
        1.0
    ],
    '26_1985': [ # 26_1985
        1.,
        0.477338,
        0.766769,
        1.,
        0.711925,
        1.,
        0.721954,
        1.
    ],
    '27_1985': [ # 27_1985
        1.,
        0.507764,
        0.768398,
        1.,
        0.725525,
        1.,
        0.624253,
        1.
    ],
    '28_1985': [ # 28_1985
        1.,
        0.477274,
        0.750879,
        0.968292,
        0.724144,
        1.,
        0.659825,
        1.
    ],
    '29_1985': [ # 29_1985
        1.,
        0.546215,
        0.733021,
        0.976692,
        0.760416,
        1.,
        0.753702,
        1.
    ],
    '30_1985': [ # 30_1985
        1.,
        0.562306,
        0.577391,
        0.855698,
        0.610075,
        1.,
        0.657067,
        1.
    ],
    '31_1985': [ # 31_1985
        1.,
        0.401421,
        0.606490,
        0.627246,
        0.782481,
        0.893240,
        0.502449,
        1.
    ],
    '28_2002': [ # 28_2002
        1.,
        0.588995,
        0.659077,
        0.996761,
        0.659077,
        1.,
        0.656639,
        1.
    ],
    '29_2002': [ # 29_2002
        1.,
        0.685912,
        0.631746,
        0.966294,
        0.508074,
        1.,
        0.661963,
        1.
    ],
    '30_2002': [ # 30_2002
        0.999475,
        0.589207,
        0.921580,
        0.963287,
        0.590622,
        1.,
        0.566511,
        1.
    ]
}

uniform_eta_20 = {
    '25_1985': [ # 25_1985
        1.,
        0.415157,
        0.814192,
        1.,
        0.789125,
        1.,
        0.756526,
        1.
    ],
    '26_1985': [ # 26_1985
        1.,
        0.441784,
        0.799078,
        1.,
        0.791546,
        1.,
        0.697350,
        1.
    ],
    '27_1985': [ # 27_1985
        1.,
        0.527814,
        0.722126,
        1.,
        0.762280,
        1.,
        0.689283,
        1.
    ],
    '28_1985': [ # 28_1985
        1.,
        0.503551,
        0.755157,
        0.971340,
        0.682175,
        0.989434,
        0.611461,
        1.
    ],
    '29_1985': [ # 29_1985
        1.,
        0.562951,
        0.654723,
        0.949107,
        0.534530,
        0.825406,
        0.709000,
        0.995290
    ],
    '30_1985': [ # 30_1985
        1.,
        0.3502384133386571,
        0.6133525242201664,
        0.9633198561262579,
        0.6423723569935303,
        0.9954766492459859,
        0.715826397189987,
        1.
    ],
    '31_1985': [ # 31_1985
        0.992647,
        0.500000,
        0.757265,
        0.794118,
        0.614272,
        0.845588,
        0.605541,
        1.
    ],
    '28_2002': [ # 28_2002
        1.,
        0.641224,
        0.644819,
        0.827174,
        0.623167,
        1.,
        0.511112,
        0.995914,
    ],
    '29_2002': [ # 29_2002
        1.,
        0.664883,
        0.651188,
        0.884696,
        0.629961,
        0.952321,
        0.772527,
        1.
    ],
    '30_2002': [ # 30_2002
        1.,
        0.41937166219285094,
        0.7470747930028194,
        0.783221067033738,
        0.6609135273067605,
        1.,
        0.8016305717092117,
        1.
    ]
}

perturbed_ps = {
    'model10': [
        1.0,
        0.4229103348680731,
        0.8686253918935398,
        1.0,
        0.8123704992250859,
        1.0,
        0.7077991428824237,
        1.0,
    ],
    'model11': [
        1.0,
        0.426407803982116,
        0.8185896601561352,
        1.0,
        0.7023989582786588,
        1.0,
        0.6732989797077819,
        1.0,
    ],
    'model12': [
        1.0,
        0.40952672906312887,
        0.7854648378949232,
        1.0,
        0.7606474009097475,
        1.0,
        0.6539118110780404,
        1.0,
    ],
    'model13': [
        1.0,
        0.47544408691902595,
        0.7559601878920554,
        0.9487586660088168,
        0.7109945653089622,
        1.0,
        0.6877373278227099,
        1.0,
    ],
    'model14': [
        1.0,
        0.6897381544845143,
        0.6574444680210119,
        0.9879908588573346,
        0.6011024159891302,
        0.9211618267386112,
        0.8727621098790732,
        1.0,
    ],
    'model15': [
        0.9926470588235294,
        0.5,
        0.6544117647058824,
        0.7941176470588235,
        0.625,
        0.8455882352941176,
        0.5069725126093771,
        0.9411764705882353,
    ],
    'model20': [
        1.0,
        0.7294731173878907,
        0.6258223531539129,
        0.9164091224773702,
        0.5715239568648995,
        1.0,
        0.7069538395226441,
        1.0,
    ],
    'model21': [
        1.0,
        0.6810812994722260,
        0.6782287991306060,
        1.0,
        0.6065824706992460,
        0.9954042914277010,
        0.6102388677298300,
        1.0
    ],
    'model22': [
        1.0,
        0.7074624431810751,
        0.7470166821001302,
        1.0,
        0.5968548284479815,
        0.9691087987086129,
        0.8588856269144272,
        1.0
    ],
    'model30': [
        1.0,
        0.0,
        0.15639768832340517,
        1.0,
        1.0,
        0.823616960019198,
        0.5363817471415633,
        1.0,
    ]
}

newone = {}
for key in uniform_eta_5.keys():
    sorted_p = np.array(uniform_eta_5[key])[[0, 7, 5, 3, 2, 4, 6, 1]]
    newone[key] = [None] + sorted_p.tolist()
uniform_eta_5 = newone

# Returns the estimated probability that s1 beats s2
def getP(s1, s2, model, year, roundNum):
    if model.get('annealing_model') is not None and roundNum == 1:
        return uniform_eta_5[model.get('annealing_model')][min(s1, s2)]
    alpha = getAlpha(s1, s2, model, year, roundNum)
    s1a = (s1 * 1.0) ** alpha
    s2a = (s2 * 1.0) ** alpha
    return s2a / (s1a + s2a)


# This function generates a 63-element list of 0s and 1s
# to represent game outcomes in a bracket. The model specifies
# which alpha value(s) to use for each round.
def generateBracket(model, year):
    pooled = model.get('pooled', False)
    generator = model.get('generator', None)
    fmt = model.get('format', 'TTT')
    override_f4 = model.get('overrideF4', DEFAULT_FORMAT)

    if generator == 'IID_AllTriplets':
        return IID_AllTriplets.generateSingleBracket(year, is_pooled=pooled, model=model)
    elif generator == 'IID_2TripletsPerRegion':
        return IID_2TripletsPerRegion.generateSingleBracket(year, is_pooled=pooled, model=model)
    elif generator == 'IID_2TripletsPerRegion_F4Triplet':
        return IID_2TripletsPerRegion_F4Triplet.generateSingleBracket(year, is_pooled=pooled, model=model)

    bracket = []

    # random.seed()

    endModel = 'None'
    if 'endModel' in model:
        endModel = model['endModel']

    e8Seeds = []
    if endModel == 'E8':
        for i in range(4):
            e8Seeds.append(getE8SeedTop(year))
            e8Seeds.append(getE8SeedBottom(year))
    else:
        e8Seeds = [-1, -1, -1, -1, -1, -1, -1, -1]

    f4Seeds = []
    if endModel == 'F4_1':
        for i in range(4):
            f4Seeds.append(getF4SeedTogether(year))
    elif endModel == 'F4_2':
        for i in range(4):
            f4Seeds.append(getF4SeedSplit(year))
    else:
        f4Seeds = [-1, -1, -1, -1]

    ncgSeeds = [-1, -1]
    if 'Rev' in endModel:
        champion = getChampion(year)
        runnerUp = getRunnerUp(year)
        champRegion = int(floor(random.random() * 4))
        champHalf = champRegion / 2
        ruRegion = int(floor(random.random() * 2))

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

        f4Seeds[champRegion] = champion
        f4Seeds[ruRegion] = runnerUp
    else:
        champRegion = -1
        ruRegion = -1

    if endModel == 'Rev_4':
        f4Seeds[ffcRegion] = getF4SeedTogether(year)
        f4Seeds[ffrRegion] = getF4SeedTogether(year)

    if not generator:
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
                    s1Wins = (s1 == f4Seeds[region]) or ((roundNum < 4) and ((s1 == e8Seeds[2*region]) or (s1 == e8Seeds[2*region + 1])))
                    s2Wins = (s2 == f4Seeds[region]) or ((roundNum < 4) and ((s2 == e8Seeds[2*region]) or (s2 == e8Seeds[2*region + 1])))

                    if s1Wins:
                        p = 1
                    elif s2Wins:
                        p = 0
                    else:
                        p = getP(s1, s2, model, year, roundNum)

                    if random.random() <= p:
                        bracket.append(1 if fmt == 'TTT' else (1 if s1 < s2 else 0))
                        newSeeds.append(s1)
                    else:
                        bracket.append(0 if fmt == 'TTT' else (1 if s2 < s1 else 0))
                        newSeeds.append(s2)
                seeds = newSeeds
            f4Seeds[region] = seeds[0]
        bracket = bracket + [-1, -1, -1]
    elif generator == 'AllTripletsRev':
        bracket = AllTripletsRev.generateSingleBracket(
            year,
            f4Seeds,
            champRegion,
            ruRegion,
            is_pooled=pooled,
            model=model)
        if override_f4:
            return bracket
    elif generator == 'E8With2TripletsPerRegion' and endModel == 'E8':
        bracket, f4Seeds = E8With2TripletsPerRegion.generateSingleBracket(
            year,
            e8Seeds,
            is_pooled=pooled,
            model=model)
        if override_f4:
            return bracket
    elif generator == 'E8With5TripletsPerRegion' and endModel == 'E8':
        bracket, f4Seeds = E8With5TripletsPerRegion.generateSingleBracket(
            year,
            e8Seeds,
            is_pooled=pooled,
            model=model)
        if override_f4:
            return bracket

    # Round 5:
    for gameNum in range(2):
        s1 = f4Seeds[2 * gameNum]
        s2 = f4Seeds[2 * gameNum + 1]

        if 'Rev' in endModel:
            if (2 * gameNum == champRegion) or (2 * gameNum == ruRegion):
                p = 1
            elif (2 * gameNum + 1 == champRegion) or (2 * gameNum + 1 == ruRegion):
                p = 0
            else:
                p = getP(s1, s2, model, year, 5)
        else:
            p = getP(s1, s2, model, year, 5)

        if random.random() <= p:
            bracket[60 + gameNum] = 1
            ncgSeeds[gameNum] = s1
        else:
            bracket[60 + gameNum] = 0
            ncgSeeds[gameNum] = s2

    # Round 6:
    s1 = ncgSeeds[0]
    s2 = ncgSeeds[1]

    if 'Rev' in endModel:
        if champHalf == 0:
            p = 1
        else:
            p = 0
    else:
        p = getP(s1, s2, model, year, 6)

    if random.random() <= p:
        bracket[-1] = 1
    else:
        bracket[-1] = 0

    # assert len(bracket) == 63
    # assert np.count_nonzero(np.array(bracket) == -1) == 0
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
        [2,2,2,2,2,2,1.7692038993],
        [1.4252197727,1.3625656943,1.3804523797,1.3977167918,1.3440101948,1.3602838429,1.3760407791],
        [1.1327439019,1.1199577274,1.1293433883,1.1189438356,1.1083639629,1.1365944197,1.1245771481],
        [1.1327439019,1.1199577274,1.1293433883,1.1189438356,1.1083639629,1.1365944197,1.1245771481],
        [0.992260877,0.996405404,0.9802794213,1.0053287528,0.9535901796,0.947768435,0.9722115628],
        [0.992260877,0.996405404,0.9802794213,1.0053287528,0.9535901796,0.947768435,0.9722115628],
        [0.992260877,0.996405404,0.9802794213,1.0053287528,0.9535901796,0.947768435,0.9722115628],
        [0,0,0,0,0,0,0]]

    r1GroupedAlphasSeedWeighted = [
        [],
        [2,2,2,2,2,2,1.7692038993],
        [1.4252197727,1.3625656943,1.3804523797,1.3977167918,1.3440101948,1.3602838429,1.3760407791],
        [1.1239462408,1.1116452654,1.120961419,1.1095749793,1.0990011131,1.1266664795,1.1160620929],
        [1.1239462408,1.1116452654,1.120961419,1.1095749793,1.0990011131,1.1266664795,1.1160620929],
        [0.9481178098,0.9341775923,0.9014353156,0.928223297,0.8792796956,0.8692346352,0.8944760731],
        [0.9481178098,0.9341775923,0.9014353156,0.928223297,0.8792796956,0.8692346352,0.8944760731],
        [0.9481178098,0.9341775923,0.9014353156,0.928223297,0.8792796956,0.8692346352,0.8944760731],
        [0,0,0,0,0,0,0]]

    # Round 1 separated alpha values for predicting 2013-2019,
    # where the first index is the better seed and the
    # second index is [year - 2013].
    r1SeparateAlphas = [
        [],
        [2,2,2,2,2,2,1.7692038993],
        [1.4252197727,1.3625656943,1.3804523797,1.3977167918,1.3440101948,1.3602838429,1.3760407791],
        [1.1631440406,1.1437646,1.1260389104,1.0702482606,1.0570363456,1.0808615169,1.1038431398],
        [1.1023437632,1.0961508547,1.1326478663,1.1676394106,1.1596915802,1.1923273226,1.1453111565],
        [0.7612823908,0.6898202312,0.6242869483,0.6828764698,0.6603066747,0.6767844807,0.7293107575],
        [1.0995538121,1.1222629842,1.0820607889,1.0447312883,0.9537101213,0.86947563,0.8427577133],
        [1.1159464279,1.1771329966,1.2344905268,1.2883785003,1.2467537426,1.2970451943,1.3445662175],
        [0,0,0,0,0,0,0]]

    # Rounds 2-6 weighted average alpha values for predicting
    # 2013-2019, where the first index is [roundNum - 2] and
    # the second index is [year - 2013].
    r2to6Alphas = [
        [1.0960226368,1.0255184405,1.0280047853,1.0169015383,1.0085075325,1.0517190671,1.0349243918],
        [0.9074472394,0.8963083681,0.8581664326,0.8815834483,0.9021714769,0.9088993287,0.8644826467],
        [0.3579691718,0.2302351327,0.1909716145,0.2167374254,0.136706458,0.1188463061,0.1504395788],
        [0.6673769231,0.6983681575,0.5784406838,0.6093441472,0.6389325696,0.674510496,0.7010202861],
        [1.4133971593,1.4171625002,1.441447396,1.441447396,1.1671880002,1.1671880002,1.199219231]]

    r2to6AlphasSeedWeighted = [
        [0.7300894976,0.7256867311,0.7262248008,0.7307164601,0.7402819935,0.7447518994,0.7411460851],
        [0.7154059556,0.7241293547,0.7009183735,0.7114893029,0.7391687766,0.7355894309,0.7143276345],
        [0.5619089765,0.5264272183,0.4945600154,0.4919846802,0.4697685742,0.4595952558,0.4593748076],
        [0.8217277548,0.8254069985,0.6989678614,0.7047260475,0.7106414922,0.7227985752,0.7466939569],
        [0.711033407,0.7322638446,0.8439593326,0.8439593326,0.813649393,0.813649393,0.8276050547]]

    isR1Grouped = 'False'
    if 'isR1Grouped' in model:
        isR1Grouped = 'True' in model['isR1Grouped']

    isSeedWeighted = ('isSeedWeighted' in model) and ('True' in model['isSeedWeighted'])

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

    scores = []
    for n in range(numTrials):
        newBracketVector = generateBracket(model, year)
        newBracketScore = scoreBracket(newBracketVector, correctVector)
        # numCorrectPicks = calcCorrectPicks(newBracketScore)

        newBracketString = ''.join(str(bit) for bit in newBracketVector)
        scores.append(newBracketScore[0])

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
modelFilename = sys.argv[3]
with open(modelFilename, 'r') as modelFile:
    modelsDataJson = modelFile.read().replace('\n', '')

modelsDict = json.loads(modelsDataJson)
modelsList = modelsDict['models']

numTrials = int(sys.argv[1])
numBatches = int(sys.argv[2])
if len(sys.argv) == 5:
    years = [int(sys.argv[4])]
else:
    years = range(2013, 2019)

# import cProfile, pstats
# from io import StringIO
# pr = cProfile.Profile()
# pr.enable()

for modelDict in modelsList:
    modelName = modelDict['modelName']

    print '{0:<8s}: {1}'.format(modelName, time.strftime("%Y-%m-%d %H:%M"))

    for batchNumber in range(numBatches):
        if numTrials < 1000:
            folderName = 'Experiments/{0}Trials'.format(numTrials)
        else:
            folderName = 'Experiments/{0}kTrials'.format(int(numTrials / 1000))

        if not os.path.exists(folderName):
            os.makedirs(folderName)

        batchFolderName = '{0}/Batch{1:02d}'.format(folderName, batchNumber)
        if not os.path.exists(batchFolderName):
            os.makedirs(batchFolderName)

        for year in years:
            performExperiments(numTrials, year, batchNumber, modelDict)

#
# pr.disable()
# s = StringIO()
# ps = pstats.Stats(pr).sort_stats('cumulative')
# ps.print_stats()
