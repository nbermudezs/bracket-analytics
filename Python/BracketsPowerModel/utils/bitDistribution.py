__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import sys


plt.style.use('seaborn-white')
sns.set_palette('dark')


fmt = sys.argv[1]
out = sys.argv[2]

FIRST_ROUND_SELECTOR = [0, 7, 5, 3, 2, 4, 6, 1]
LEGENDS = ['1 vs 16', '2 vs 15', '3 vs 14', '4 vs 13', '5 vs 12', '6 vs 11', '7 vs 10', '8 vs 9']

with open('allBrackets{}.json'.format(fmt)) as f:
    brackets = json.load(f)['brackets']

for year in range(2013, 2020):
    vectors = [list(bracket['bracket']['fullvector'])
               for bracket in brackets
               if int(bracket['bracket']['year']) < year]
    vectors = np.array(vectors, dtype=int)
    probs = np.mean(vectors, axis=0)

    plt.figure(figsize=(14, 6))
    plt.bar(range(63), probs, color='black')
    plt.title('P(bit = 1)')
    plt.xlabel('Bit')
    plt.ylabel('Probability')
    plt.savefig(out + '/fractions_63bit_{}'.format(year), dpi=150)
    plt.cla()
    plt.clf()


    # + fixed perturbation
    l, u = np.zeros(63), np.zeros(63)
    for i in range(63):
        l[i] = probs[i] if probs[i] < 0.1 else 0.1
        u[i] = 1 - probs[i] if probs[i] > 0.9 else 0.1
    plt.figure(figsize=(14, 6))
    plt.bar(range(63), probs, yerr=[l, u], ecolor='grey', color='black')
    plt.title('P(bit = 1)')
    plt.xlabel('Bit')
    plt.ylabel('Probability')
    plt.savefig(out + '/fractions_63bit_fixed10_{}'.format(year), dpi=150)
    plt.cla()
    plt.clf()

    l = probs * 0.1
    u = np.clip(probs * 1.1, 0, 1.) - probs
    plt.figure(figsize=(14, 6))
    plt.bar(range(63), probs, yerr=[l, u], ecolor='grey', color='black')
    plt.title('P(bit = 1)')
    plt.xlabel('Bit')
    plt.ylabel('Probability')
    plt.savefig(out + '/fractions_63bit_percent10_{}'.format(year), dpi=150)
    plt.cla()
    plt.clf()

    probs = probs[:60].reshape(-1, 15)
    plt.bar(range(15), np.mean(probs, axis=0),
            yerr=np.std(probs, axis=0, ddof=1),
            ecolor='grey', color='black')
    plt.title('P(bit = 1)')
    plt.xlabel('Bit')
    plt.ylabel('Probability')
    plt.savefig(out + '/fractions_region_{}'.format(year), dpi=150)
    plt.cla()
    plt.clf()

    probs = probs[:, FIRST_ROUND_SELECTOR]
    plt.bar(LEGENDS, np.mean(probs, axis=0),
            yerr=np.std(probs, axis=0, ddof=1),
            ecolor='grey', color='black')
    plt.title('P(bit = 1)')
    plt.savefig(out + '/fractions_R1_{}'.format(year), dpi=150)
    plt.cla()
    plt.clf()

