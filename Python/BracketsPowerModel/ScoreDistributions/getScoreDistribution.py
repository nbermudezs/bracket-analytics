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


num_trials = int(sys.argv[1])
num_replications = int(sys.argv[2])
models_file = sys.argv[3]
output_dir = 'ScoreDistributions/plots'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

with open(models_file) as f:
    models = json.load(f)['models']


if num_trials < 1000:
    folderName = 'Experiments/{0}Trials'.format(num_trials)
else:
    folderName = 'Experiments/{0}kTrials'.format(int(num_trials / 1000))


for model in models:
    desc = model['modelDesc'].replace('Reverse: ', '')
    name = model['modelName']
    for batch_id in range(num_replications):
        for year in range(2013, 2019):
            print('Processing {} for year {}'.format(name, year))
            with open('{0}/Batch{1:02d}/generatedBrackets_{2}_{3}.json'.format(folderName, batch_id, name, year)) as f:
                data = json.load(f)
                brackets = data['brackets']
                print('# brackets: ', len(brackets))
                scores = [bracket['score'][0] for bracket in brackets]
                l, u = np.min(scores), np.max(scores)
                n_bins = (u - l) / 20
                sns.distplot(scores, bins=n_bins, kde=False)
                plt.title('Score distribution \n Model: `{}`, Year: {}'.format(desc, year))
                plt.xlabel('ESPN Score')
                plt.ylabel('Count')
                plt.savefig('ScoreDistributions/plots/{}_{}.{}.png'.format(name, year, batch_id))
                plt.clf()
