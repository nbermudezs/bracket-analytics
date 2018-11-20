#!/usr/bin/env python3

__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


from copy import deepcopy
from itertools import combinations
from sympy.parsing.sympy_parser import parse_expr
from sympy.matrices import hessian
import numpy as np
import sympy as sp


truth = {
    2016: [
        1, 0, 1, 0, 0, 1, 1, 1,
        1, 1, 0, 1, 0, 1, 0, 1,
        1, 0, 1, 1, 1, 0, 1, 1,
        1, 0, 0, 1, 0, 1, 0, 0
    ],
    2017: [
        1, 1, 1, 1, 0, 1, 1, 1,
        1, 1, 1, 1, 0, 1, 1, 1,
        1, 0, 1, 1, 0, 1, 1, 1,
        1, 1, 0, 1, 1, 1, 0, 1
    ],
    2018: [
        0, 0, 1, 0, 0, 1, 1, 1,
        1, 0, 1, 1, 1, 1, 1, 1,
        1, 0, 1, 0, 1, 1, 0, 1,
        1, 1, 1, 1, 0, 1, 1, 1
    ]
}

reference_truth = deepcopy(truth)
#     7/8, 0.5, 7/8, 6/8, 3/8, 1., 6/8, 1.


n_games = 3

p = [
    0.9926470588235294, 0.5, 0.6544117647058824, 0.7941176470588235, 0.625, 0.8455882352941176, 0.6176470588235294, 0.9411764705882353,
    0.9926470588235294, 0.5, 0.6544117647058824, 0.7941176470588235, 0.625, 0.8455882352941176, 0.6176470588235294, 0.9411764705882353,
    0.9926470588235294, 0.5, 0.6544117647058824, 0.7941176470588235, 0.625, 0.8455882352941176, 0.6176470588235294, 0.9411764705882353,
    0.9926470588235294, 0.5, 0.6544117647058824, 0.7941176470588235, 0.625, 0.8455882352941176, 0.6176470588235294, 0.9411764705882353
]

omega = np.array([
    0.9926470588235294,
    0.5,
    0.6544117647058824,
    0.7941176470588235,
    0.625,
    0.8455882352941176,
    0.6176470588235294,
    0.9411764705882353
])


def _full_form_objective_function_32(year, break_region=False):
    all_factors = []
    if break_region:
        ctrl = 4
    else:
        ctrl = 1
    for k in range(ctrl):
        factors = []
        for i in range(32 // ctrl):
            j = i % 8
            if j >= n_games:
                continue
            if truth[year][n_games * k + i] == 0:
                factors.append('(1-p_{})'.format(j))
            else:
                factors.append('p_{}'.format(j))
        all_factors.append('*'.join(factors))
    return '*'.join(all_factors)


def _full_form_objective_function_31(year, break_region=False):
    all_summands = []
    if break_region:
        ctrl = 4
    else:
        ctrl = 1

    for k in range(ctrl):
        # 31
        summands = []
        for flip in range(32 // ctrl):
            if flip >= n_games:
                break
            factors = []
            for i in range(32 // ctrl):
                j = i % 8
                if j >= n_games:
                    continue
                if i == flip:
                    if truth[year][n_games * k + i] == 1:
                        factors.append('(1-p_{})'.format(j))
                    else:
                        factors.append('p_{}'.format(j))
                else:
                    if truth[year][n_games * k + i] == 0:
                        factors.append('(1-p_{})'.format(j))
                    else:
                        factors.append('p_{}'.format(j))
            summands.append('*'.join(factors))
        # import pdb; pdb.set_trace()

        # 32
        factors = []
        for i in range(32 // ctrl):
            j = i % 8
            if j >= n_games:
                continue
            if truth[year][n_games * k + i] == 0:
                factors.append('(1-p_{})'.format(j))
            else:
                factors.append('p_{}'.format(j))
        print('k={}. '.format(k), '((' + '+'.join(summands) + ')' + '+' + '*'.join(factors) + ')')
        all_summands.append('((' + '+'.join(summands) + ')' + '+' + '*'.join(factors) + ')')
    return '(' + '*'.join(all_summands) + ')'


objective_fns = {
    '32': _full_form_objective_function_32,
    '31': _full_form_objective_function_31
}


def _full_form_objective_function(year, alpha, break_region):
    return objective_fns[str(alpha)](year, break_region)


def full_form_objective_fn(alpha=31, break_region=False):
    year_objs = [_full_form_objective_function(year, alpha, break_region) for year in truth.keys()]
    return '*'.join(year_objs)


def get_subs(symbols, probs=omega):
    return [
        (symbols['p_{}'.format(i)], probs[i])
        for i in range(n_games)
    ]


def mle_probs():
    data = [np.array(bits).reshape(4, -1) for _, bits in truth.items()]
    data = np.vstack(data)
    return data.mean(axis=0)


def select_columns(data, cols):
    new_data = {}
    for year, bits in data.items():
        new_data[year] = np.array(data[year]).reshape(4, -1)[:, cols].reshape(-1).tolist()
    return new_data


if __name__ == '__main__':
    print('Usage: python toy.py <gamma>')
    import json
    import sys
    from itertools import permutations

    gamma = float(sys.argv[1])

    for config in permutations(range(8), n_games):
        out = open('Likelihood/analytical/logs/out.{}-{}.txt'.format('_'.join([str(x) for x in config]), gamma), 'w')
        truth = select_columns(reference_truth, config)
        input_data = json.dumps(truth, indent=4)
        # import pdb; pdb.set_trace()
        out.write(input_data)
        out.write('\n')

        omega = np.random.rand(8)
        # print('Objective: ', full_form_objective_fn(break_region=True))
        omega_symbols = {
            'p_0': sp.Symbol('p_0'),
            'p_1': sp.Symbol('p_1'),
            'p_2': sp.Symbol('p_2'),
            'p_3': sp.Symbol('p_3'),
            'p_4': sp.Symbol('p_4'),
            'p_5': sp.Symbol('p_5'),
            'p_6': sp.Symbol('p_6'),
            'p_7': sp.Symbol('p_7'),
        }

        symbols = {k: v
                   for k, v in omega_symbols.items()
                   if int(k.split('_')[1]) < n_games}
        objective_31 = parse_expr(full_form_objective_fn(break_region=True),
                                  local_dict=symbols)
        print('Objective: ', objective_31)
        # import pdb; pdb.set_trace()
        H = hessian(objective_31, list(symbols.values()))
        grad = [sp.diff(objective_31, p_i) for p_i in symbols.values()]
        # print(H[0])

        iter_count = 0
        max_iters = 10000
        history = []
        omega = omega[:n_games]
        probs = []
        while True:
            history.append(omega)
            H_eval = np.array([d2f.subs(get_subs(symbols)) for d2f in H], dtype=float).reshape(n_games, n_games)
            grad_eval = np.array([f_prime.subs(get_subs(symbols)) for f_prime in grad], dtype=float)
            omega_next = np.clip(omega + gamma * np.linalg.inv(H_eval).dot(grad_eval), 0., 1.)

            print('Gradient: ', grad_eval)
            out.write('Gradient: ' + str(grad_eval))
            out.write('\n')

            print('New omega:', omega.tolist(), ' - L2 diff: ', np.linalg.norm(omega - omega_next))
            out.write('New omega: [')
            out.write(', '.join(omega.astype(str).tolist()))
            out.write('] - L2 diff: ')
            out.write(str(np.linalg.norm(omega - omega_next)))
            out.write('\n')

            p = objective_31.subs(get_subs(symbols))
            print('P(M_y >= {}) = {}'.format(n_games - 1, p))
            out.write('P(M_y >= {}) = {}'.format(n_games - 1, p))
            out.write('\n')

            probs.append(p)

            if iter_count > max_iters:
                break
            if np.linalg.norm(omega - omega_next) < 1e-20:
                break
            omega = omega_next
            iter_count += 1

        print('Max P(.) = ', np.max(probs))
        out.write('Max P(.) = ' + str(np.max(probs)))
        out.write('\n')

        print('Final Omega: ', get_subs(symbols))
        out.write('Final Omega: ' + str(get_subs(symbols)))
        out.write('\n')

        print('MLE probs: ', get_subs(symbols, mle_probs()))
        out.write('MLE probs:   ' + str(get_subs(symbols, mle_probs())))
        out.write('\n')

        print('P(M_y >= {} | MLE) = {}'.format(n_games - 1, objective_31.subs(get_subs(symbols, mle_probs()))))
        out.write('P(M_y >= {} | MLE) = {}'.format(n_games - 1, objective_31.subs(get_subs(symbols, mle_probs()))))
        out.write('\n')

        # import pdb; pdb.set_trace()
