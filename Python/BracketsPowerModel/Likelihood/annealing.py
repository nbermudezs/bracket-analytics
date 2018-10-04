#!/usr/bin/env python3

__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


import json
import numpy as np
import os
import pandas as pd
import sys
import time
from collections import defaultdict
from triplets.priors.PriorDistributions import read_data
import matplotlib.pyplot as plt


FMT = 'TTT'
BASE = 'Likelihood/OtherAlpha'
PLOT_TITLE_TEMPLATE = '{}: Dist. of # of matches using P_MLE until {}'
PLOT_FILEPATH_TEMPLATE = BASE + '/Plots/count_dist-p_mle-leq-{}-{}.png'
CSV_FILEPATH_TEMPLATE = BASE + '/Distributions/{}-p_mle-leq-{}-{}.csv'
LOG_TEMPLATE = BASE + '/Logs/energy-and-p_over_time-{}-{}.1.txt'
LOG_BESTS_TEMPLATE = BASE + '/Logs/best_over_time-{}-{}.1.txt'

if not os.path.exists(BASE):
    os.makedirs(BASE)
    os.makedirs(BASE + '/Plots')
    os.makedirs(BASE + '/Logs')
    os.makedirs(BASE + '/Distributions')


std_functions = {
    'std_fn_1': lambda t, T: 0.3 * np.exp((t - T) / T)
}


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


def store_plot_and_csv(df, year, name, optimized_years):
    df['sum'] = df.sum(axis=1)
    total = df.sum(axis=0)
    total.name = 'sum'
    df = df.append(total)
    df.to_csv(CSV_FILEPATH_TEMPLATE.format('count_dist', year, name))

    p_df = df / df.loc['sum']
    p_df['sum'] = np.prod(p_df[optimized_years], axis=1)
    p_df.to_csv(CSV_FILEPATH_TEMPLATE.format('all_p_count_dist', year, name))

    df[list(range(year, 2019))].drop('sum').plot.bar()
    plt.title(PLOT_TITLE_TEMPLATE.format(name, year))
    plt.savefig(PLOT_FILEPATH_TEMPLATE.format(year, name))
    plt.close()


def experiment(P, add_noise, trials, model, current_temp=0, initial_temp=0):
    horizon = 33 - model.get('alpha')
    # print('Using data until year {}'.format(year))
    if add_noise:
        if model.get('annealed_bit') is not None:
            idx = model['annealed_bit']
        else:
            idx = np.random.choice(indices)
        zeros = np.zeros_like(P)
        if type(model['std']) == str:
            scale = std_functions[model['std']](current_temp, initial_temp)
        else:
            scale = model['std']
        if model.get('noise') == 'normal':
            zeros[idx] = np.random.normal(scale=scale)
        elif model.get('noise') == 'uniform':
            zeros[idx] = np.random.uniform(model.get('noise_low'), model.get('noise_high'))
        perturbed_P = np.clip(P + zeros, a_min=0, a_max=1)
    else:
        perturbed_P = P
    B = g(perturbed_P, trials)

    distributions = []
    series = []
    for ref_year in range(model.get('likelihood_start_year'), 2019):
        dist = estimate_score_distribution(brackets[ref_year], B, indices, trials)

        df = pd.DataFrame.from_dict(dist, orient='index').rename({0: 'count'}, axis='columns')
        # df.plot.bar()
        distributions.append((df['count'] / df['count'].sum()).values)
        series.append(pd.Series(df['count'], name=ref_year))

    mle = maximum_likelihood(distributions)[-horizon:]
    return perturbed_P, -np.log(sum(mle)), pd.concat(series, axis=1)


def print_setup(bit_P, score_P, old_score_P=None):
    print('{Pr(bit i = 1): 0<= i <= 7} = ', bit_P[indices].tolist())
    print('-log(Pr(Matches >= 29)) = {}'.format(score_P))
    if old_score_P is not None:
        print('Energy difference: {}'.format(np.exp(-old_score_P) - np.exp(-score_P)))
    print('=' * 150)


single_bit_P = [
    1.0,
    0.5928450489751618,
    0.6950938557087003,
    0.9189491423484074,
    0.7747201971300952,
    1,
    0.688728061242975,
    1
]


def run_annealing(model, start_year, stop_year):
    optimized_years = list(range(model.get('likelihood_start_year'), 2019))
    # pr = Pr(M_i >= 29)
    for year in np.arange(start=start_year, stop=stop_year + 1, step=1):
        unpooled, pooled = read_data(model['format'], year)
        pooled = pooled.astype(int).values
        P = np.mean(pooled, axis=0)

        # P = np.array([1.0, 0.5928450489751618, 0.6950938557087003, 0.9189491423484074, 0.721206790987267, 1.0, 0.7345229047483148, 1.0, 0.0, 1.0, 1.0, 1.0, 0.8031569810310453, 0.9244015862122775, 1.0])

        print('=' * 50 + 'Baseline for data before {}'.format(year) + '=' * 50)
        prev_P, prev_pr, count_df = experiment(P, add_noise=False, trials=100000, model=model)
        store_plot_and_csv(count_df, year - 1, 'Baseline', optimized_years=optimized_years)
        # this is used to set a single bit to the optimal value we found so far
        # P[0] = 1.0
        # P[1] = 0.4231184017779921
        # P[2] = 0.752286265633227
        # P[3] = 0.9491817654669973
        # P[4] = 0.721206790987267
        # P[5] = 1.0
        # P[6] = 0.7345229047483148
        # P[7] = 1.0

        # prev_P = np.array([ 1.        ,  0.49166667,  0.63333333,  0.79166667,  0.65833333,
        #     0.85      ,  0.60833333,  0.94166667,  0.86666667,  0.49166667,
        #     0.475     ,  0.35      ,  0.76666667,  0.40833333,  0.60833333])
        # prev_pr = 258.53736133404186
        print_setup(prev_P, prev_pr)

        pr_0 = prev_pr
        best_pr = prev_pr

        T_0 = model.get('initial_temp', 6.)
        t = T_0

        print('Logs: ' + LOG_TEMPLATE.format(model['name'], year))
        print('Best P Logs: ' + LOG_BESTS_TEMPLATE.format(model['name'], year))
        f = open(LOG_TEMPLATE.format(model['name'], year), 'w')
        best_log = open(LOG_BESTS_TEMPLATE.format(model['name'], year), 'w')
        counter = 0
        while t >= 0:
            print('=' * 50 + 'Temperature: {}'.format(t) + '=' * 50)

            favorable_count = 0
            for trial_at_fixed_temperature in range(10000):
                print('t={:05d}'.format(trial_at_fixed_temperature), end='\r')
                new_P, new_pr, count_df = experiment(prev_P, add_noise=True, trials=10000, model=model, current_temp=t, initial_temp=T_0)

                accept_p = 1 if new_pr < prev_pr else min(1., np.exp(-(new_pr - prev_pr) / t))
                if np.random.rand() < accept_p:
                    f.write('{},{}: {}\n'.format(counter, new_pr,
                                                 ','.join(new_P.astype(str))))
                    prev_P = new_P
                    prev_pr = new_pr
                    favorable_count += 1

                    print('t={0:05d} - ACCEPTED. Energy: {1}'.format(trial_at_fixed_temperature, new_pr))
                    if new_pr < best_pr:
                        print_setup(new_P, new_pr, pr_0)
                        best_pr = new_pr
                        store_plot_and_csv(count_df, year - 1, model['name'], optimized_years=optimized_years)
                        best_log.write('{},{}: {}\n'.format(counter, new_pr, ','.join(new_P.astype(str))))
                    if favorable_count == 50:
                        break
                counter += 1
            f.flush()
            if model['cooling'] == 'linear':
                t -= model['cooling_delta']


if __name__ == '__main__':
    model_filepath = sys.argv[1]
    start_year = int(sys.argv[2])
    stop_year = int(sys.argv[3])
    if len(sys.argv) == 5:
        selected_model = sys.argv[4]
    else:
        selected_model = None

    with open(model_filepath, 'r') as f:
        models = json.load(f)['models']

    for model in models:
        if selected_model is not None and selected_model != model['name']:
            continue
        run_annealing(model, start_year, stop_year)
