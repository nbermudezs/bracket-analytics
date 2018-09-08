__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"

import numpy as np
import random
import sys; sys.path.append("..")
import tensorflow as tf

from triplets.Constant import UNPOOLED, POOLED, regions
from triplets.priors.PriorDistributions import read_data
from time import time

triplets = [
    np.array([0, 1, 8]),
    np.array([2, 3, 9]),
    np.array([4, 5, 10]),
    np.array([6, 7, 11]),
    np.array([12, 13, 14])
]

cdf_cache = {}


def build_cdf(data, bits, idx):
    if idx not in cdf_cache:
        group = data[bits].groupby(bits.tolist()).size().reset_index(name='count')

        def agg(row):
            row['count'] = group.iloc[0:row.name + 1]['count'].sum()
            return row
        group = group.apply(agg, axis=1)
        try:
            group['count'] = group['count'] / (1. * group['count'].values[-1])
        except IndexError:
            import pdb; pdb.set_trace()
        cdf_cache[idx] = group.values.astype(float)
    return cdf_cache[idx]


def getP(s1, s2, matchPosition, roundNum):
    # import pdb; pdb.set_trace()
    return 0

def getTriplet(s1, s2, s1Wins, s2Wins, matchPosition, roundNum):
    triplet = [0, 0, 0]
    if s1Wins:
        triplet[0] = 1
    if s2Wins:
        triplet[1] = 1

def generate(fmt, data, unpooled, pool_type, e8Seeds):
    regions_a = regions if pool_type == UNPOOLED else [0, 0, 0, 0]

    vector = -np.ones(63, dtype=int)

    # fill in all bits fixed by f4Seeds
    offsets = [None, 0, 8, 12, 14]
    dummy = -1
    for region in range(4):
        regionOffset = region * 15
        seeds = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]
        for roundNum in range(1, 5):
            roundOffset = offsets[roundNum]
            numGames = int(len(seeds) / 2)
            newSeeds = []
            for gameNum in range(numGames):
                s1 = seeds[2 * gameNum]
                s2 = seeds[2 * gameNum + 1]
                matchPosition = regionOffset + roundOffset + gameNum

                if vector[matchPosition] != -1:
                    continue

                # Force any fixed F4 seeds to make it through
                s1Wins = ((roundNum < 4) and ((s1 == e8Seeds[2*region]) or (s1 == e8Seeds[2*region + 1])))
                s2Wins = ((roundNum < 4) and ((s2 == e8Seeds[2*region]) or (s2 == e8Seeds[2*region + 1])))

                if s1Wins:
                    vector[matchPosition] = 1 if fmt == 'TTT' else (1 if s1 < s2 else 0)
                    newSeeds.append(s1)
                elif s2Wins:
                    vector[matchPosition] = 0 if fmt == 'TTT' else (1 if s2 < s1 else 0)
                    newSeeds.append(s2)
                else:
                    newSeeds.append(dummy)
                    dummy -= 1
            seeds = newSeeds

    for region_id, region in enumerate(regions_a):
        for idx, triplet in enumerate(triplets):
            bits = triplet + region * 15
            vector_bits = triplet + region_id * 15

            if np.all(vector[vector_bits] == -1):
                cdf = build_cdf(data, bits, idx + region * 5)

                # not fixed bits on the triplet
                rn = np.random.rand()
                row = np.nonzero(cdf[:, 3] - rn > 0)[0][0]
                values = cdf[row][:3]
                vector[vector_bits] = values
            else:
                key = hash(tuple(bits.tolist() + vector[vector_bits].tolist()))
                tmp_data = data
                others, vector_others = [], []
                for bit, vector_bit in zip(bits, vector_bits):
                    if vector[vector_bit] != -1:
                        if key not in cdf_cache:
                            tmp_data = tmp_data[tmp_data[bit] == vector[vector_bit]]
                    else:
                        others.append(bit)
                        vector_others.append(vector_bit)
                if tmp_data.size == 0:
                    tmp_data = data
                if len(others) == 0:
                    # all bits are already filled (possible with Rev_4)
                    continue

                cdf = build_cdf(tmp_data, np.array(others), key)
                rn = np.random.rand()
                row = np.nonzero(cdf[:, -1] - rn > 0)[0][0]
                values = cdf[row][:-1]
                vector[vector_others] = values
                # either use conditional p or independent

    # import pdb; pdb.set_trace()
    triplet = np.array([60, 61, 62])
    cdf = build_cdf(unpooled, triplet, 21)
    rn = np.random.rand()
    row = np.nonzero(cdf[:, 3] - rn > 0)[0][0]
    values = cdf[row][:3]
    for i, bit_id in enumerate(triplet):
        vector[bit_id] = values[i]
    assert np.count_nonzero(vector == -1) == 0
    return vector


unpooled, pooled = None, None
data = None
last_state = (None, None, None) # fmt, year, is_pooled

def generateSingleBracket(fmt, max_year, e8Seeds, is_pooled=False):
    global unpooled
    global pooled
    global data
    global last_state

    pool_type = POOLED if is_pooled else UNPOOLED
    new_state = (fmt, max_year, is_pooled)
    if data is None or new_state != last_state:
        cdf_cache.clear()
        unpooled, pooled = read_data(fmt, max_year)
        if is_pooled:
            data = pooled.astype(int)
        else:
            data = unpooled.astype(int)
        last_state = new_state

    return generate(fmt, data, unpooled, pool_type, e8Seeds).tolist()
