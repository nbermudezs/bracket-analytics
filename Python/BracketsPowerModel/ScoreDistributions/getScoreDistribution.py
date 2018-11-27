__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


import json
import matplotlib.pyplot as plt
import numpy as np
import os
import seaborn as sns
import sys
from collections import defaultdict


num_trials = int(sys.argv[1])
num_replications = int(sys.argv[2])
models_file = sys.argv[3]
output_dir = 'ScoreDistributions/plots/tmp'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

with open(models_file) as f:
    models = json.load(f)['models']


if num_trials < 1000:
    folderName = 'Experiments/{0}Trials'.format(num_trials)
else:
    folderName = 'Experiments/{0}kTrials'.format(int(num_trials / 1000))


BIN_SIZE = 20
for model in models:
    desc = model['modelDesc'].replace('Reverse: ', '')
    name = model['modelName']
    for year in range(2013, 2014):
        across_batch_min = 1920
        across_batch_max = 0
        dists = []
        for batch_id in range(num_replications):
            print('Batch {}/{}. Processing {} for year {}'.format(batch_id, num_replications, name, year))
            with open('{0}/Batch{1:02d}/generatedBrackets_{2}_{3}.json'.format(folderName, batch_id, name, year)) as f:
                data = json.load(f)
                brackets = data['brackets']
                print('# brackets: ', len(brackets))
                scores = [bracket['score'][0] for bracket in brackets]
                max_scores, counts = np.unique(scores, return_counts=True)
                dist_dict = defaultdict(int, {a: b for (a, b) in zip(max_scores, counts)})
                dists.append(dist_dict)
                across_batch_min = min(across_batch_min, min(scores))
                across_batch_max = max(across_batch_max, max(scores))

                n_bins = int((max(scores) - min(scores)) / BIN_SIZE)
                sns.distplot(scores, bins=n_bins, kde=False)
                plt.title('Score distribution \n Model: `{}`, Year: {}'.format(desc, year))
                plt.xlabel('ESPN Score')
                plt.ylabel('Count')
                plt.savefig('{}/{}_{}.{}.png'.format(output_dir, name, year, batch_id))
                plt.clf()

        l, u = across_batch_min, across_batch_max
        matrix = np.array([(dist[score]) for dist in dists for score in np.arange(l, u, 10)]).reshape(num_replications, -1)
        error = np.std(matrix, axis=0)
        n_bins = int((u - l) / BIN_SIZE)
        data = np.repeat(np.arange(l, u, 10), matrix.mean(axis=0).round(0).astype(int))
        sns.distplot(data, bins=n_bins, kde=False)
        plt.title('Mean Score distribution \n Model: `{}`, Year: {}'.format(desc, year))
        plt.xlabel('ESPN Score')
        plt.ylabel('Count')
        plt.savefig('{}/{}_{}.mean.png'.format(output_dir, name, year))
        plt.clf()
        # import pdb; pdb.set_trace()
