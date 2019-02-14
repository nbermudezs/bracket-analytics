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
    'R1_R2_4': [6, 7, 11]
}


class RuntimeSummary:
    def __init__(self, model):
        self.model = model
        self.stats = {
            'count': 0,
            'bit_count': np.zeros(63),
            'triplets': {
                'E8_F4': defaultdict(int),
                'S16_E8_1': defaultdict(int),
                'S16_E8_2': defaultdict(int),
                'R1_R2_1': defaultdict(int),
                'R1_R2_2': defaultdict(int),
                'R1_R2_3': defaultdict(int),
                'R1_R2_4': defaultdict(int)
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

    def to_json(self, filepath):
        with open(filepath, 'w') as f:
            stats = self.stats
            stats['bit_count'] = self.stats['bit_count'].tolist()
            json.dump(stats, f)
