__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


import json
import numpy as np
from itertools import combinations


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
    },
    'P_S1': {
        'bits': [0, 8, 12]
    },
    'P_S2': {
        'bits': [7, 11, 13]
    },
    'P_S3': {
        'bits': [5, 10, 13]
    },
    'P_S4': {
        'bits': [3, 9, 12]
    },
    'P_S5': {
        'bits': [2, 9, 12]
    },
    'P_S6': {
        'bits': [4, 10, 13]
    },
    'P_S7': {
        'bits': [6, 11, 13]
    },
    'P_S8': {
        'bits': [1, 8, 12]
    },
    'P_R2_1': {
        'bits': [8, 12, 14]
    },
    'P_R2_2': {
        'bits': [9, 12, 14]
    },
    'P_R2_3': {
        'bits': [10, 13, 14]
    },
    'P_R2_4': {
        'bits': [11, 13, 14]
    }
}

all_names = [
    'R1_R2_1', 'R1_R2_2', 'R1_R2_3', 'R1_R2_4',
    'S16_E8_1', 'S16_E8_2',
    'E8_F4',
    'P_S1', 'P_S2', 'P_S3', 'P_S4', 'P_S5', 'P_S6', 'P_S7', 'P_S8',
    'P_R2_1', 'P_R2_2', 'P_R2_3', 'P_R2_4'
]

triplet_names = [
    'R1_R2_1', 'R1_R2_2', 'R1_R2_3', 'R1_R2_4',
    'S16_E8_1', 'S16_E8_2',
    'E8_F4'
]

result = {
    'models': []
}

counter = 0

for i in range(len(all_names)):
    for comb in combinations(all_names, i + 1):
        bits = [all_triplets[x]['bits'] for x in comb]
        has_overlap = len(comb) * 3 > len(set(np.concatenate(bits)))
        if has_overlap:
            counter += 1
            continue
        print(counter)

        triplets_list = []
        paths_list = []

        for name in comb:
            if name in triplet_names:
                triplets_list.append(name)
            else:
                paths_list.append(name)

        if len(paths_list) == 0:
            counter += 1
            continue

        result['models'].append({
            'modelDesc': 'bitwise + triplets {}'.format(','.join(comb)),
            # 'modelName': 'modelTripletFixedOrder{}'.format(counter),
            'modelName': 'modelPath{}'.format(counter),
            'gen': 'bitwise_path_generator',
            'paths': paths_list,
            'triplets': triplets_list
        })
        counter += 1

with open('Ensemble/models/3bit_path_models.json', 'w') as f:
    json.dump(result, f, indent=4, sort_keys=True)
