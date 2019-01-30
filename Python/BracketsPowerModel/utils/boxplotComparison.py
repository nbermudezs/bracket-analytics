__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"

import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-white')
sns.set_palette('dark')

summary = [
    {
        'modelName': 'F4_A',
        'ref': 'ludden',
        'refType': 'models'
    },
    {
        'modelName': 'E8',
        'ref': 'ludden',
        'refType': 'models'
    },
    {
        'modelName': 'bradley-terry_models',
        'ref': 'bradley-terry',
        'refType': 'ensemble',
        'label': 'Bradley-Terry'
    }
]

if __name__ == '__main__':
    import sys

    num_trials = int(sys.argv[1])
    num_batches = int(sys.argv[2])
    prefix = sys.argv[3]

    for year in range(2013, 2019):
        for batch_num in range(num_batches):
            bxp = []
            for setup in summary:
                path = 'Summary_{}_{}/stats/{}/{}_batch{}.json'.format(
                    setup['ref'],
                    setup['refType'],
                    year,
                    setup['modelName'],
                    batch_num)
                with open(path) as f:
                    data = json.load(f)['bxp']
                    data['label'] = setup.get('label', setup['modelName'])
                    bxp.append(data)
            ax = plt.subplot()
            ax.bxp(bxp, whiskerprops=dict(linestyle='--'))
            plt.savefig(prefix + '_batch{}_{}'.format(batch_num, year))