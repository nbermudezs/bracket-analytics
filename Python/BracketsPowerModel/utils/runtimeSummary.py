__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


import json
import numpy as np
from collections import defaultdict


all_triplets = {
    'E8_F4': [12, 13, 14],
    'S16_E8_1': [8, 9, 12],
    'S16_E8_2': [10, 11, 13],
    'R1_R2_1': [0, 1, 8],
    'R1_R2_2': [2, 3, 9],
    'R1_R2_3': [4, 5, 10],
    'R1_R2_4': [6, 7, 11],

    'P_S1': [0, 8, 12],
    'P_S2': [7, 11, 13],
    'P_S3': [5, 10, 13],
    'P_S4': [3, 9, 12],
    'P_S5': [2, 9, 12],
    'P_S6': [4, 10, 13],
    'P_S7': [6, 11, 13],
    'P_S8': [1, 8, 12],
    'P_R2_1': [8, 12, 14],
    'P_R2_2': [9, 12, 14],
    'P_R2_3': [10, 13, 14],
    'P_R2_4': [11, 13, 14],

}


class RuntimeSummary:
    def __init__(self, model):
        self.model = model
        self.stats = {
            'count': 0,
            'bit_count': np.zeros(63),
            'triplets': {k: defaultdict(int) for k, _ in all_triplets.items()},
            'seed_dist': {
                'E8': defaultdict(int),
                'F4': defaultdict(int),
                'NCG': defaultdict(int),
                'Champ': defaultdict(int),
                'R1': defaultdict(int),
                'R2': defaultdict(int),
                'R3': defaultdict(int)
            }
        }

    def analyze_bracket(self, bracket):
        self.stats['count'] += 1
        self.stats['bit_count'] += bracket
        regions = bracket[:60].reshape(-1, 15)
        for triplet_name, bits in all_triplets.items():
            triplets, counts = np.unique(regions[:, bits], axis=0, return_counts=True)
            for t, c in zip(triplets, counts):
                self.stats['triplets'][triplet_name][''.join(t.astype(str))] += c

        f4 = []
        for region in range(4):
            round_id = 1
            seeds = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]
            bits = bracket[region * 15:region * 15 + 15]
            for i, bit in enumerate(bits[:8]):
                self.stats['seed_dist']['R1'][seeds[i * 2 + (1 - bit)]] += 1
            while len(seeds) > 1:
                new_seeds = []
                n_games = len(seeds) // 2
                for game in range(n_games):
                    if bits[game] == 1:
                        new_seeds.append(seeds[game * 2])
                    else:
                        new_seeds.append(seeds[game * 2 + 1])
                seeds = new_seeds
                if len(seeds) == 1:
                    self.stats['seed_dist']['F4'][seeds[0]] += 1
                elif len(seeds) == 2:
                    self.stats['seed_dist']['E8'][seeds[0]] += 1
                    self.stats['seed_dist']['E8'][seeds[1]] += 1
                elif len(seeds) == 4:
                    for seed in seeds:
                        self.stats['seed_dist']['R3'][seed] += 1
                elif len(seeds) == 8:
                    for seed in seeds:
                        self.stats['seed_dist']['R2'][seed] += 1

            f4.append(seeds[0])

        ncg = []
        if bracket[-3] == 1:
            self.stats['seed_dist']['NCG'][f4[0]] += 1
            ncg.append(f4[0])
        else:
            self.stats['seed_dist']['NCG'][f4[1]] += 1
            ncg.append(f4[1])

        if bracket[-2] == 1:
            self.stats['seed_dist']['NCG'][f4[2]] += 1
            ncg.append(f4[2])
        else:
            self.stats['seed_dist']['NCG'][f4[3]] += 1
            ncg.append(f4[3])
        champ = ncg[1 - bracket[-1]]

        self.stats['seed_dist']['Champ'][champ] += 1

    def to_json(self, filepath):
        with open(filepath, 'w') as f:
            stats = self.stats
            stats['bit_count'] = self.stats['bit_count'].tolist()
            json.dump(stats, f)
