__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_palette('dark')
plt.style.use('seaborn-white')

tmpl = 'Score_v_Size/data/analysis-score-v-size_score_{}.csv'
sizes = sorted([1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000,
                10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000,
                100000, 200000, 300000, 400000, 500000, 600000, 700000, 800000, 900000,
                1000000
                ])


def read_file(path):
    with open(path) as f:
        content = {}
        year = None
        lines = f.readlines()
        for line in lines:
            if 'Tournament' in line:
                year = int(line.split(' ')[0])
                content[year] = []
            elif 'Batch' in line:
                continue
            elif line == '\n':
                continue
            else:
                score = int(line.split(', ')[1])
                content[year].append(score)

        return {y: np.mean(l) for y, l in content.items() if len(l) > 0}


def preprocess_data():
    series = []
    for size in sizes:
        filepath = tmpl.format(size)
        series.append(pd.Series(read_file(filepath), name=size))
    df = pd.concat(series, axis=1)
    df.T.plot(figsize=(14, 7))
    df.to_csv('Score_v_Size/summary.csv')
    # plt.show()
    plt.savefig('Score_v_Size/summary-lt-10k.png')


if __name__ == '__main__':
    read_file('Score_v_Size/data/analysis-score-v-size_score_10000.csv')
    preprocess_data()