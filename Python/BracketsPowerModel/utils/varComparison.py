__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"

import json
import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

plt.style.use('seaborn-white')
sns.set_palette('dark')

summary = [
    {
        'modelName': 'power',
        'ref': 'ludden',
        'refType': 'models'
    },
    {
        'modelName': 'F4_A',
        'ref': 'ludden',
        'refType': 'models'
    },
    {
        'modelName': 'F4_B',
        'ref': 'ludden',
        'refType': 'models'
    },
    {
        'modelName': 'NCG',
        'ref': 'ludden',
        'refType': 'models'
    },
    {
        'modelName': 'E8',
        'ref': 'ludden',
        'refType': 'models'
    },
    {
        'modelName': 'ludden_models',
        'ref': 'ludden',
        'refType': 'ensemble',
        'label': 'Ludden et. al'
    }
]


def batch_variance(num_trials, num_batches, prefix):
    for year in range(2013, 2019):
        for batch_num in range(num_batches):
            variances = []
            labels = []
            for setup in summary:
                path = 'Experiments/{0}Trials/Batch{1:02d}/generatedScores_{2}_{3}.json'.format(
                    num_trials if num_trials < 1000 else str(int(num_trials / 1000)) + 'k',
                    batch_num,
                    setup['modelName'],
                    year
                )
                with open(path) as f:
                    scores = json.load(f)['scores']
                    var = np.var(scores)
                    variances.append(var)
                    labels.append(setup.get('label', setup['modelName']))
            sns.barplot(labels, variances, order=labels, color='black')
            plt.savefig(prefix + '{1}_score_variance_batch{0}.png'.format(batch_num, year))
            plt.cla()
            plt.clf()


def max_score_variance(num_trials, num_batches, prefix):
    for year in range(2013, 2019):
        variances = []
        labels = []
        for setup in summary:
            max_scores = []
            for batch_num in range(num_batches):
                path = 'Experiments/{0}Trials/Batch{1:02d}/generatedScores_{2}_{3}.json'.format(
                    num_trials if num_trials < 1000 else str(int(num_trials / 1000)) + 'k',
                    batch_num,
                    setup['modelName'],
                    year
                )
                with open(path) as f:
                    scores = json.load(f)['scores']
                    max_scores.append(np.max(scores))
            variances.append(np.var(max_scores))
            labels.append(setup.get('label', setup['modelName']))
        sns.barplot(labels, variances, order=labels, color='black')
        plt.savefig(prefix + 'max_score_variance_{}.png'.format(year))
        plt.cla()
        plt.clf()


if __name__ == '__main__':
    import os
    import sys

    num_trials = int(sys.argv[1])
    num_batches = int(sys.argv[2])
    models_path = sys.argv[3]
    summaries_root = sys.argv[4]
    prefix = summaries_root + '/variance/'

    if not os.path.exists(prefix):
        os.makedirs(prefix)

    batch_variance(num_trials, num_batches, prefix)
    max_score_variance(num_trials, num_batches, prefix)
