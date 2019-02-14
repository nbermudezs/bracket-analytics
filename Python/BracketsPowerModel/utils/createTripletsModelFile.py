__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


import json
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
    }
}

triplet_names = list(all_triplets.keys())


result = {
    'models': []
}

counter = 0

for i in range(len(triplet_names)):
    for comb in combinations(triplet_names, i + 1):
        result['models'].append({
            'modelDesc': 'bitwise + triplets {}'.format(','.join(comb)),
            'modelName': 'model{}'.format(counter),
            'gen': 'bitwise_triplet_generator',
            'triplets': list(comb)
        })
        counter += 1

with open('Ensemble/models/all_triplet_comb_models.json', 'w') as f:
    json.dump(result, f, indent=4)
