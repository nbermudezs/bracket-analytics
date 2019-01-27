__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from Ensemble.calculateAlpha import compute_all_alphas
from math import ceil


sns.set_palette('dark')
plt.style.use("seaborn-white")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 150


def load_ref_brackets():
    with open("allBracketsTTT.json") as f:
        data = json.load(f)
        vectors = {
            int(bracket['bracket']['year']):
                np.array(list(bracket['bracket']['fullvector']), dtype=int)
            for bracket in data['brackets']}
    return vectors


def split_array(array, split_size):
    index = len(array)
    result = []
    while index > 0:
        result.append(array[max(index - split_size, 0):index])
        index -= split_size
    return result


def save_and_clear_plt(path):
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


class Analyzer:
    @staticmethod
    def slide_exclusive_window(brackets, window_size, start=1985, end=2019):
        cuts = split_array(brackets, window_size)
        labels = split_array(np.arange(start, end), window_size)
        labels = list(reversed(['{}-{}'.format(r[0], r[-1]) for r in labels]))
        return list(reversed([compute_all_alphas(cut) for cut in cuts])), labels

    @staticmethod
    def slide_rolling_window(brackets, window_size, start=1985, end=2019):
        result = []
        labels = []

        years = list(range(start, end))
        for i in range(window_size, len(brackets) + 1):
            data = brackets[i - window_size:i]
            result.append(compute_all_alphas(data))
            labels.append('{}-{}'.format(years[i - window_size], years[i - 1]))

        return result, labels

    @staticmethod
    def slide_incremental_window(brackets, window_size, start=1985, end=2019):
        cuts = split_array(brackets, window_size)
        result = []
        labels = []
        for i in range(len(cuts)):
            history = np.concatenate(cuts[:(i+1)])
            result.append(compute_all_alphas(history))
            if window_size > 1:
                labels.append('{}-{}'.format(start, start + len(history)))
            else:
                labels.append(str(start + len(history)))
        return result, labels

    @staticmethod
    def visualize(alphas_set, labels, window_size, start=1985, end=2019, prefix='', rotation='horizontal'):
        pairs = [(1, 16), (8, 9), (5, 12), (4, 13), (6, 11), (3, 14), (7, 10),
                 (2, 15)]
        for s1, s2 in pairs:
            y = [alphas[1][s1][s2] for alphas in alphas_set]
            fig, ax = plt.subplots(figsize=(9, 5))
            ax.plot(labels, y, color='black')
            ax.set_xticklabels(labels, fontsize=8, rotation=rotation)
            ax.set_title(
                r'$\hat\alpha_{{{}, ({}, {})}}$-value comparison over'.format(1, s1, s2)
                + '\n {} years window size'.format(window_size))
            ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
            # plt.show()
            save_and_clear_plt('Ensemble/plots/{}-R1_{}-{}_w{}.png'.format(prefix, s1, s2, window_size))

        series = []
        for round in range(2, 7):
            y = [alphas[round] for alphas in alphas_set]
            series.append(y)
            fig, ax = plt.subplots(figsize=(9, 5))
            ax.plot(labels, y, color='black')
            ax.set_xticklabels(labels, fontsize=8, rotation=rotation)
            ax.set_title(r'$\hat\alpha_{}$-value comparison over'.format(round)
                         + '\n {} years window size'.format(window_size))
            ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
            # plt.show()
            save_and_clear_plt('Ensemble/plots/{}-R{}_w{}.png'.format(prefix, round, window_size))

        df = pd.DataFrame(np.array(series).T, index=labels,
                          columns=['Round 2', 'Round 3', 'Round 4', 'Round 5',
                                   'Round 6'])
        df.plot.bar(figsize=(9, 5))
        plt.title(r'$\hat\alpha$-value comparison over'
                  + '\n {} years window size'.format(window_size))
        plt.legend(fancybox=True)
        # plt.show()
        save_and_clear_plt('Ensemble/plots/{}-R2to6_w{}.png'.format(prefix, window_size))

    @staticmethod
    def visualize_line(alphas_set, labels, window_size, start=1985, end=2019, prefix=''):
        pairs = [(1, 16), (8, 9), (5, 12), (4, 13), (6, 11), (3, 14), (7, 10),
                 (2, 15)]
        for s1, s2 in pairs:
            y = [alphas[1][s1][s2] for alphas in alphas_set]
            ticks = min(10, len(y) - 1)
            fig, ax = plt.subplots(figsize=(9, 5))
            ax.plot(labels, y, color='black')
            ax.set_xticklabels(labels, fontsize=8)
            ax.xaxis.set_major_locator(plt.MaxNLocator(ticks))
            ax.set_title(
                r'$\hat\alpha_{{{}, ({}, {})}}$-value comparison over'.format(1, s1, s2)
                + '\n {} years window size'.format(window_size))
            ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
            # plt.show()
            save_and_clear_plt('Ensemble/plots/{}-R1_{}-{}_w{}.png'.format(prefix, s1, s2, window_size))

        series = []
        for round in range(2, 7):
            y = [alphas[round] for alphas in alphas_set]
            ticks = min(10, len(y) - 1)
            series.append(y)
            fig, ax = plt.subplots(figsize=(9, 5))
            ax.plot(labels, y, color='black')
            ax.set_xticklabels(labels, fontsize=8)
            ax.xaxis.set_major_locator(plt.MaxNLocator(ticks))
            ax.set_title(r'$\hat\alpha_{}$-value comparison over'.format(round)
                         + '\n {} years window size'.format(window_size))
            ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
            # plt.show()
            save_and_clear_plt('Ensemble/plots/{}-R{}_w{}.png'.format(prefix, round, window_size))

        df = pd.DataFrame(np.array(series).T, index=labels,
                          columns=['Round 2', 'Round 3', 'Round 4', 'Round 5',
                                   'Round 6'])
        df.plot(rot=0, figsize=(9, 5))
        plt.title(r'$\hat\alpha$-value comparison over'
                  + '\n {} years window size'.format(window_size))
        plt.legend(fancybox=True)
        # plt.show()
        save_and_clear_plt('Ensemble/plots/{}-R2to6_w{}.png'.format(prefix, window_size))


if __name__ == '__main__':
    brackets = [b for y, b in load_ref_brackets().items()]

    for window_size in [4, 5, 7, 10, 15]:
        alphas_set, labels = Analyzer.slide_exclusive_window(brackets, window_size)
        Analyzer.visualize(alphas_set, labels, window_size, prefix='exclusive')

    for window_size in [4, 5, 7, 10, 15]:
        alphas_set, labels = Analyzer.slide_rolling_window(brackets, window_size)
        Analyzer.visualize(alphas_set, labels, window_size, prefix='rolling', rotation='vertical')

    for window_size in [1, 4, 5, 7, 10, 15]:
        alphas_set, labels = Analyzer.slide_incremental_window(brackets, window_size)
        Analyzer.visualize(alphas_set, labels, window_size, prefix='incremental', rotation='vertical')
