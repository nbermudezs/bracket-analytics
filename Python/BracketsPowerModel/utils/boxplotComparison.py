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
from utils.summaries import summaries

plt.style.use('seaborn-white')
sns.set_palette('dark')

if __name__ == '__main__':
    import os
    import sys

    num_trials = int(sys.argv[1])
    num_batches = int(sys.argv[2])
    models_path = sys.argv[3]
    summaries_root = sys.argv[4]
    prefix = summaries_root + '/boxplots/'

    if not os.path.exists(prefix):
        os.makedirs(prefix)

    prefix = prefix + 'plot'

    key = models_path.split('/')[-1].replace('_models.json', '')

    for year in range(2013, 2019):
        for batch_num in range(num_batches):
            bxp = []
            for setup in summaries[key]:
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
            plt.savefig(prefix + '{1}_batch{0}.png'.format(batch_num, year))
            plt.cla()
            plt.clf()