from __future__ import print_function

__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os


forward_base_dir = 'ScoreDistributions/20MM/np/power'
backward_base_dir = 'ScoreDistributions/20MM/np/E8'
output_dir = 'ScoreDistributions/forwardBackwardComparison'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print('Model,Count Forward, Count Backward, Min Forward, Min Backward, Max Forward, Max Backward, Mean Forward, Mean Backward, STD Forward, STD Backward, Backward Better?')

for file in os.listdir(forward_base_dir):
    data_a = np.load(forward_base_dir + '/' + file)
    if not os.path.exists(backward_base_dir + '/' + file):
        continue
    data_b = np.load(backward_base_dir + '/' + file)

    a_min = data_a.min() if data_a.size > 0 else 1920
    b_min = data_b.min() if data_b.size > 0 else 1920

    a_max = data_a.max() if data_a.size > 0 else 0
    b_max = data_b.max() if data_b.size > 0 else 0

    _min = np.min([a_min, b_min])
    _max = np.max([a_max, b_max])

    if _min == _max or data_a.size + data_b.size == 0:
        continue

    better = b_max > a_max or (b_max == a_max and b_min > a_min)
    print(', '.join([
        file,
        str(data_a.size), str(data_b.size),
        str(a_min), str(b_min),
        str(a_max), str(b_max),
        str(data_a.mean()), str(data_b.mean()),
        str(data_a.std(ddof=1)), str(data_b.std(ddof=1)), better]))

    continue

    n_bins = (_max - _min) / 10

    if data_a.size > 1:
        sns.distplot(data_a, kde=False, bins=n_bins)
    if data_b.size > 1:
        sns.distplot(data_b, kde=False, bins=n_bins)
    name = file[:file.rfind('_')]
    year = file[file.rfind('_'):-4]
    plt.title('Score distribution for model={}, year={}'.format(name, year))
    plt.savefig(output_dir + '/dist-{}'.format(file.replace('npy', 'png')))
    plt.legend(['Forward', 'Backward'])
    plt.cla()
    plt.clf()