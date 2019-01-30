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

sns.set_palette('dark')
plt.style.use('seaborn-white')

num_trials = int(sys.argv[1])
num_batches = int(sys.argv[2])
models_path = sys.argv[3]
summary_path = sys.argv[4]


if not os.path.exists('{}/dist'.format(summary_path)):
    os.makedirs('{}/dist'.format(summary_path))

if not os.path.exists('{}/stats'.format(summary_path)):
    os.makedirs('{}/stats'.format(summary_path))


for year in range(2013, 2019):
    with open(models_path) as f:
        models = json.load(f)
    for batchNumber in range(num_batches):
        if num_trials < 1000:
            folderName = 'Experiments/{0}Trials'.format(num_trials)
        else:
            folderName = 'Experiments/{0}kTrials'.format(int(num_trials / 1000))
        batchFolderName = '{0}/Batch{1:02d}'.format(folderName, batchNumber)
        for model in models['models']:
            name = model['modelName']
            scores_path = '{2}/generatedScores_{0}_{1}.json'.format(name, year, batchFolderName)

            with open(scores_path) as f:
                data = json.load(f)
            scores = data['scores']

            stats = dict()
            stats['mean'] = np.mean(scores)
            stats['s'] = np.std(scores, ddof=1)
            stats['percentiles'] = np.percentile(scores, q=np.arange(0, 100, step=5)).tolist()
            stats['max'] = np.max(scores)
            stats['min'] = np.min(scores)
            stats['median'] = np.median(scores)

            with open('{}/stats/{}_batch{}.json'.format(summary_path, name, batchNumber), 'w') as f:
                json.dump(stats, f)

            _, counts = np.unique(scores, return_counts=True)
            y_max = np.max(counts)
            bins = (np.max(scores) - np.min(scores)) / 10

            sns.distplot(scores, kde=False, bins=bins)
            plt.title('Score distribution for {} - {}'.format(name, year))
            plt.xlabel('Score')
            plt.ylabel('Count')
            plt.axvline(stats['mean'], linestyle='dotted', color='black')
            plt.text(stats['mean'] + 5, y_max, 'mean')

            plt.axvline(stats['percentiles'][-2], linestyle='dotted', color='red')
            plt.text(stats['percentiles'][-2] + 5, y_max, '90%', color='red')

            # plt.show()
            # exit(0)
            plt.savefig('{0}/dist/dist_{1}_batch{2}.png'.format(summary_path, name, batchNumber), dpi=150)
            plt.cla()
            plt.clf()

            sns.distplot(scores, kde=True, bins=bins,
                         hist_kws=dict(cumulative=True))
            plt.title('Score CDF for {} - {}'.format(name, year))
            plt.xlabel('P')
            plt.ylabel('Count')
            plt.savefig('{0}/dist/cdf_{1}_batch{2}.png'.format(summary_path, name, batchNumber), dpi=150)
            plt.cla()
            plt.clf()
