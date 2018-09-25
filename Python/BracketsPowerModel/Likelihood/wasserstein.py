#!/usr/bin/env python3

__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


import pandas as pd
from scipy.stats import wasserstein_distance
from Likelihood.annealing import CSV_FILEPATH_TEMPLATE


to_compare = [
    'Baseline',
    'optimal',
    'optimal-ensembled', # take the values from single bit simulated annealing and put them all together.
    'optimal-bit0',
    'optimal-bit1',
    'optimal-bit2',
    'optimal-bit3',
    'optimal-bit4',
    'optimal-bit5',
    'optimal-bit6',
    'optimal-bit7'
]

for year in range(2009, 2019):
    print('=' * 18 + 'Analysis for baseline using data up to {}'.format(year) + '=' * 18)
    ref_df = pd.read_csv(CSV_FILEPATH_TEMPLATE.format('count_dist', year, to_compare[0]))
    for model in to_compare[1:]:
        distance = 0
        df = pd.read_csv(CSV_FILEPATH_TEMPLATE.format('count_dist', year, model))
        columns = df.columns[1:-1]
        for col in columns:
            distance += wasserstein_distance(ref_df[col].values, df[col].values)
        print('Work to transform {} into {}: {}'.format(to_compare[0], model, distance))
    print('=' * 79)
