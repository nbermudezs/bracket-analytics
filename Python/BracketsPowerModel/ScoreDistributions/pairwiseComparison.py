__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"

import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns
import sys
from collections import defaultdict


sns.set(style="white", color_codes=True)

num_trials = int(sys.argv[1])
num_replications = int(sys.argv[2])
models_file = sys.argv[3]
if len(sys.argv) == 5:
    year = int(sys.argv[4])
else:
    year = None
output_dir = 'ScoreDistributions/newCode/'

with open(models_file) as f:
    models = json.load(f)['models']


if num_trials < 1000:
    folderName = 'Experiments/Conditioning/{0}Trials'.format(num_trials)
else:
    folderName = 'Experiments/Conditioning/{0}kTrials'.format(int(num_trials / 1000))


# selected_models = [
#     'NC_RU_correct',
#     'NC_correct',
#     'NC_correct_noRU',
#     'NC_RU_swapped',
#     'RU_correct_noNC',
# ]
# selected_models = np.random.permutation(selected_models)

selected_models = [model['modelName'] for model in models]


cache = {}


def get_scores(model_name, year, tmp=False):
    key = (folderName, 0, model_name, year, tmp)
    if key in cache:
        return cache[key]
    with open('{0}/Batch{1:02d}/generatedBrackets_{2}_{3}.json'.format(folderName, 0, model_name, year)) as f:
        data = json.load(f)
        brackets = data['brackets']
        # print('# brackets: ', len(brackets))
        if tmp:
            scores = [bracket['score'][0] for bracket in brackets if bracket['score'][-2] == 160]
        else:
            scores = [bracket['score'][0] for bracket in brackets]
        # max_scores, counts = np.unique(scores, return_counts=True)
    cache[key] = np.array(scores), np.min(scores), np.max(scores), np.mean(scores)
    return cache[key]


def plot_it(data_a, data_b, name, legend=None):
    if len(data_a) != len(data_b):
        x = min(len(data_a), len(data_b))
        data_a = np.random.choice(data_a, x)
        data_b = np.random.choice(data_b, x)
    l = min(data_a.min(), data_b.min())
    u = max(data_a.max(), data_b.max())
    n_bins = (u - l) // 10
    marginal_kws = dict(bins=n_bins, rug=True)
    # sns.jointplot(data_a, data_b, kind="hex", color="#4CB391",
    #               marginal_kws=marginal_kws)
    # plt.savefig('{}/pairwise-{}/jointplot-{}.png'.format(output_dir, year, name))
    # plt.clf()

    _, bins, _ = plt.hist(data_a, n_bins, range=(l, u))
    plt.hist(data_b, bins=bins, alpha=0.5, range=(l, u))
    if legend:
        plt.legend(legend)
    plt.savefig('{}/pairwise-{}/hist-{}.png'.format(output_dir, year or 'avg', name))
    plt.clf()
    # plt.show()


def P_x(scores, counts, x):
    return 1. * counts[scores == x].sum() / counts.sum()


def P_y_leq_x(scores, counts, x):
    return 1. * counts[scores <= x].sum() / counts.sum()


def calculations(data_a, data_b, name_a, name_b):
    scores_a, counts_a = np.unique(data_a, return_counts=True)
    scores_b, counts_b = np.unique(data_b, return_counts=True)

    p = 0.
    for score in scores_a:
        p += P_x(scores_a, counts_a, score) * P_y_leq_x(scores_b, counts_b, score)
    # print('P(`{}` < `{}`) = {}'.format(name_b, name_a, p))
    return p

    # p = 0.
    # for score in scores_b:
    #     p += P_x(scores_b, counts_b, score) * P_leq_y(scores_a, counts_a, score)
    # print('P(`{}` < `{}`) = {}'.format(name_a, name_b, p))


def clustermap(matrix):
    plt.rcParams["figure.figsize"] = (20, 20)

    cols = [x.replace('conditioning_', '') for x in selected_models]
    tmp = np.concatenate((np.array(cols)[:, np.newaxis], matrix), axis=1)
    df = pd.DataFrame(tmp, columns=['model'] + cols).set_index('model').astype(float)
    sns.set(font_scale=0.7)
    sns.set_palette('colorblind')
    sns.heatmap(df, center=0, annot=True, cmap="YlGnBu")
    # sns.clustermap(df, cmap="YlGnBu", center=0, annot=True)
    plt.xticks(rotation='horizontal', fontsize=8)
    plt.yticks(rotation='horizontal', fontsize=8)
    plt.title('Probability of score from X less than or equal to score from Y')
    plt.xlabel('Y')
    plt.ylabel('X', rotation='horizontal')
    plt.savefig(output_dir + 'comparisonHeatmap-{}.png'.format(year or 'avg'))
    # plt.savefig(output_dir + 'comparisonClustermap-{}.png'.format(year or 'avg'))
    plt.cla()
    # plt.show()


def to_dot_graph(matrix, names):
    graph_str = 'digraph hierarchy {{ \n\t{0} \n}}'
    lines = []
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[0]):
            if row == col:
                continue
            if matrix[row, col] > 0.5:
                lines.append('{} -> {} [label="{}"];'.format(names[row], names[col], matrix[row, col].round(2)))

    graph_str = graph_str.format('\n\t'.join(lines))
    with open('graph.dot', 'w') as f:
        f.write(graph_str)
    return graph_str


def to_latex(matrix, names):
    pass


def order_matrix(matrix, names):
    indicator_matrix = matrix > 0.5
    counts = np.sum(indicator_matrix, axis=0)
    sorter = np.argsort(counts)
    matrix = matrix[:, sorter]
    matrix = matrix[sorter, :]
    new_names = [names[i] for i in sorter]
    return matrix, new_names


def run_all(year, outputs=False):
    matrix = np.zeros((len(selected_models), len(selected_models)))
    entries = []
    for i in range(len(selected_models)):
        data_a, _, _, _ = get_scores(selected_models[i], year)
        for j in range(len(selected_models)):
            data_b, _, _, _ = get_scores(selected_models[j], year)
            # plot_it(data_a, data_b, name='{}-v-{}'.format(selected_models[i], selected_models[j]), legend=[selected_models[i], selected_models[j]])
            p = calculations(data_a, data_b, selected_models[i], selected_models[j])
            matrix[j, i] = p
            entries.append(['P({} <= {})'.format(selected_models[j], selected_models[i]), p])

    if outputs:
        matrix, new_names = order_matrix(matrix, selected_models)
        clustermap(matrix)
        to_dot_graph(matrix, new_names)
        to_latex(matrix, new_names)
    entries = np.array(entries)
    entries = entries[np.argsort(entries[:, -1])[::-1], :]
    print(entries)
    return matrix


if __name__ == '__main__':
    if not os.path.exists(output_dir + '/pairwise-{}'.format(year)) and year:
        os.makedirs(output_dir + '/pairwise-{}'.format(year))
    # data_a, _, _, _ = get_scores('NC_RU_correct', 2013)
    # data_b, _, _, _ = get_scores('NC_RU_swapped', 2013)
    # import pdb; pdb.set_trace()
    """
    data_a, _, _, _ = get_scores('conditioning_NC_noRU', 2013)
    data_b, _, _, _ = get_scores('conditioning_NC', 2013, tmp=True)
    import pdb; pdb.set_trace()


    plot_it(data_a, data_b,
            name='{}-v-{}'.format('Cond. NC_noRU', 'Cond. NC filter RU'),
            legend=['Cond. NC_noRU', 'Cond. NC (filter RU)'])
    # import pdb; pdb.set_trace()
    """
    if year is None:
        matrices = []
        for y in range(2013, 2019):
            matrix = run_all(y)
            matrices.append(matrix)
        avg_matrix = np.mean(matrices, axis=0)
        avg_matrix, names = order_matrix(avg_matrix, selected_models)
        clustermap(avg_matrix)
        to_dot_graph(avg_matrix, names)
    else:
        run_all(year, outputs=True)