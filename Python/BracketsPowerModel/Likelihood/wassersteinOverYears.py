#!/usr/bin/env python3

__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance
from Likelihood.annealing import CSV_FILEPATH_TEMPLATE


to_compare = [
    'optimal-ensembled'
]


for model in to_compare:
    model_distances = []
    for year_i in range(2009, 2019):
        for year_j in range(year_i + 1, 2019):
            distance = 0
            ref_df = pd.read_csv(CSV_FILEPATH_TEMPLATE.format('count_dist', year_i, to_compare[0]))
            df = pd.read_csv(CSV_FILEPATH_TEMPLATE.format('count_dist', year_j, model))
            columns = df.columns[1:-1]

            for col in columns:
                distance += wasserstein_distance(ref_df[col].values, df[col].values)
            model_distances.append(distance)
            print('Work to transform {}-{} into {}-{}: {}'.format(model, year_i, model, year_j, distance))

    print('Model average work: {}'.format(np.mean(model_distances)))