#!/usr/bin/env python3

__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


import json
import numpy as np
import pandas as pd
import sys
from collections import defaultdict
from triplets.priors.PriorDistributions import read_data
import matplotlib.pyplot as plt


FMT = 'TTT'
PLOT_TITLE_TEMPLATE = '{}: Dist. of # of matches using P_MLE until {}'
PLOT_FILEPATH_TEMPLATE = 'Likelihood/FixedPerturbation/Plots/count_dist-p_mle-leq-{}-{}.png'
CSV_FILEPATH_TEMPLATE = 'Likelihood/FixedPerturbation/Distributions/{}-p_mle-leq-{}-{}.csv'
LOG_TEMPLATE = 'Likelihood/FixedPerturbation/Logs/energy-and-p_over_time-{}-{}.1.txt'
LOG_BESTS_TEMPLATE = 'Likelihood/FixedPerturbation/Logs/best_over_time-{}-{}.1.txt'


with open('allBrackets{}.json'.format(FMT)) as f:
    brackets = {
        int(x['bracket']['year']): np.array(list(x['bracket']['fullvector']), dtype=int)
        for x in json.load(f)['brackets']}


def h(round_num):
    if round_num == 1:
        return np.array(list(range(0, 8)))
    elif round_num == 2:
        return np.array(list(range(8, 12)))
    elif round_num == 3:
        return np.array([12, 13])
    elif round_num == 4:
        return np.array([14])
    else:
        return np.array([])


def g(P, trials):
    batch = []
    for trial in range(trials):
        for region in range(4):
            bracket = (np.random.rand(*P.shape) < P)
            batch.append(bracket)
    return batch


def estimate_score_distribution(ref, B, indices, trials):
    distribution = defaultdict(lambda: 1)
    _ = [distribution[score] for score in range(0, len(indices) * 4 + 1)]

    for trial in range(trials):
        trial_score = 0
        for region in range(4):
            bracket = B[4 * trial + region]
            trial_score += np.count_nonzero(bracket[indices] == ref[indices + region * 15])
        distribution[trial_score] += 1
    return distribution


def maximum_likelihood(evidence):
    return np.prod(evidence, axis=0)


indices = h(round_num=1)

np.random.seed(1991)
SAVE_PLOTS = False


def store_plot_and_csv(df, year, name):
    df['sum'] = df.sum(axis=1)
    total = df.sum(axis=0)
    total.name = 'sum'
    df = df.append(total)
    df.to_csv(CSV_FILEPATH_TEMPLATE.format('count_dist', year, name))

    p_df = df / df.loc['sum']
    p_df['sum'] = np.prod(p_df[list(range(1985, 2019))], axis=1)
    p_df.to_csv(CSV_FILEPATH_TEMPLATE.format('all_p_count_dist', year, name))

    df[list(range(year, 2019))].drop('sum').plot.bar()
    plt.title(PLOT_TITLE_TEMPLATE.format(name, year))
    plt.savefig(PLOT_FILEPATH_TEMPLATE.format(year, name))
    plt.close()


def experiment(P, trials):
    B = g(P, trials)

    distributions = []
    series = []
    for ref_year in range(1985, 2019):
        dist = estimate_score_distribution(brackets[ref_year], B, indices, trials)

        df = pd.DataFrame.from_dict(dist, orient='index').rename({0: 'count'}, axis='columns')
        # df.plot.bar()
        distributions.append((df['count'] / df['count'].sum()).values)
        series.append(pd.Series(df['count'], name=ref_year))

    mle = maximum_likelihood(distributions)[-4:]
    return P, -np.log(sum(mle)), pd.concat(series, axis=1)


def print_setup(bit_P, score_P, old_score_P=None):
    print('{Pr(bit i = 1): 0<= i <= 7} = ', bit_P[indices].tolist())
    print('-log(Pr(Matches >= 29)) = {}'.format(score_P))
    if old_score_P is not None:
        print('Energy difference: {}'.format(np.exp(-old_score_P) - np.exp(-score_P)))
    print('=' * 150)


def run_experiments(start_year, stop_year):
    perturbation = np.array([0.1, -0.1])
    for year in np.arange(start=start_year, stop=stop_year + 1, step=1):
        unpooled, pooled = read_data('TTT', year)
        pooled = pooled.astype(int).values
        P = np.mean(pooled, axis=0)

        print('=' * 50 + 'Baseline for data before {}'.format(year) + '=' * 50)
        prev_P, prev_pr, count_df = experiment(P, trials=100000)
        store_plot_and_csv(count_df, year - 1, 'Baseline')
        print_setup(prev_P, prev_pr)

        for i in range(0, 256):
            selector = np.array(list('{0:08b}'.format(i)), dtype=int)
            perturbed_P = P.copy()
            perturbed_P[indices] = np.clip(P[indices] + perturbation[selector], a_min=0., a_max=1.)
            new_P, new_pr, count_df = experiment(perturbed_P, trials=100000)
            store_plot_and_csv(count_df, year - 1, 'perturbed-{}'.format(i))
            print_setup(new_P, new_pr, prev_pr)


if __name__ == '__main__':
    start_year = int(sys.argv[1])
    stop_year = int(sys.argv[2])
    run_experiments(start_year, stop_year)
