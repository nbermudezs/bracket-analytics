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

reference_truth = {
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
#     7/8, 0.5, 7/8, 6/8, 3/8, 1., 6/8, 1.


n_games = 3

p = [
    0.9926470588235294, 0.5, 0.6544117647058824, 0.7941176470588235, 0.625, 0.8455882352941176, 0.6176470588235294, 0.9411764705882353,
    0.9926470588235294, 0.5, 0.6544117647058824, 0.7941176470588235, 0.625, 0.8455882352941176, 0.6176470588235294, 0.9411764705882353,
    0.9926470588235294, 0.5, 0.6544117647058824, 0.7941176470588235, 0.625, 0.8455882352941176, 0.6176470588235294, 0.9411764705882353,
    0.9926470588235294, 0.5, 0.6544117647058824, 0.7941176470588235, 0.625, 0.8455882352941176, 0.6176470588235294, 0.9411764705882353
]


def _full_form_objective_function_32(year, break_region=False, truth=None):
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


def _full_form_objective_function_31(year, break_region=False, truth=None):
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


def _full_form_objective_function(year, alpha, break_region, truth):
    return objective_fns[str(alpha)](year, break_region, truth)


def full_form_objective_fn(alpha=31, break_region=False, truth=None):
    year_objs = [_full_form_objective_function(year, alpha, break_region, truth) for year in truth.keys()]
    return '*'.join(year_objs)


def get_subs(symbols, probs):
    return [
        (symbols['p_{}'.format(i)], probs[i])
        for i in range(n_games)
    ]


def mle_probs(truth):
    data = [np.array(bits).reshape(4, -1) for _, bits in truth.items()]
    data = np.vstack(data)
    return data.mean(axis=0)


def select_columns(data, cols):
    new_data = {}
    for year, bits in data.items():
        new_data[year] = np.array(data[year]).reshape(4, -1)[:, cols].reshape(-1).tolist()
    return new_data


def test_newtons_method():
    # https://jmahaffy.sdsu.edu/courses/f00/math122/lectures/newtons_method/newtonmethodeg.html
    symbols = {'x': sp.Symbol('x')}
    obj = parse_expr('4 + 8*(x**2) - x**4', symbols)
    H = hessian(obj, list(symbols.values()))
    grad = [sp.diff(obj, p_i) for p_i in symbols.values()]
    omega = 1.1

    def get_subs():
        return [(symbols['x'], omega)]

    gamma = 0.5

    while True:
        H_eval = np.array([d2f.subs(get_subs()) for d2f in H],
                          dtype=float).reshape(len(symbols.items()), len(symbols.items()))
        grad_eval = np.array(
            [f_prime.subs(get_subs()) for f_prime in grad], dtype=float)
        omega_next = omega - gamma * np.linalg.inv(H_eval).dot(grad_eval)
        if np.linalg.norm(omega - omega_next) < 1e-20:
            break
        print('omega ', omega_next)
        omega = omega_next
    import pdb; pdb.set_trace()


if __name__ == '__main__':
    print('Usage: python toy.py <gamma> <output_dir>')
    import json
    import os
    import sys
    from itertools import permutations

    gamma = float(sys.argv[1])
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = 'Likelihood/analytical/logs'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for config in permutations(range(8), n_games):
        out = open('{}/out.{}-{}.txt'.format(output_dir, '_'.join([str(x) for x in config]), gamma), 'w')
        gt_data = select_columns(reference_truth, config)
        input_data = json.dumps(gt_data)
        # import pdb; pdb.set_trace()
        out.write(input_data)
        out.write('\n')

        # omega = np.random.rand(n_games)
        omega = mle_probs(gt_data)
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
        objective_31 = parse_expr(full_form_objective_fn(break_region=True, truth=gt_data),
                                  local_dict=symbols)
        print('Objective: ', objective_31)
        print('MLE probs: ', mle_probs(gt_data))
        print('P(M_y >= {} | MLE) = {}'.format(n_games - 1, objective_31.subs(get_subs(symbols, mle_probs(gt_data)))))
        # import pdb; pdb.set_trace()
        H = hessian(objective_31, list(symbols.values()))
        grad = [sp.diff(objective_31, p_i) for p_i in symbols.values()]
        # print(H[0])

        iter_count = 0
        max_iters = 10000
        history = []
        probs = [0]
        clipped_counter = 0
        clipped_dim_counter = 0
        while True:
            history.append(omega)
            H_eval = np.array([d2f.subs(get_subs(symbols, omega)) for d2f in H], dtype=float).reshape(n_games, n_games)
            grad_eval = np.array([f_prime.subs(get_subs(symbols, omega)) for f_prime in grad], dtype=float)
            try:
                raw_omega = omega + gamma * np.linalg.inv(H_eval).dot(grad_eval)
            except np.linalg.LinAlgError:
                raw_omega = omega + gamma * np.linalg.pinv(H_eval).dot(grad_eval)
            omega_next = np.clip(raw_omega, 0., 1.)

            # print('Gradient: ', grad_eval)
            out.write('Gradient: ' + str(grad_eval))
            out.write('\n')

            p = objective_31.subs(get_subs(symbols, omega))
            print('P(M_y >= {}) = {}. '.format(n_games - 1, p), 'New omega:', omega.tolist(), ' - L2 diff: ', np.linalg.norm(omega - omega_next))
            out.write('P(M_y >= {}) = {}. '.format(n_games - 1, p))
            out.write('New omega: [')
            out.write(', '.join(omega.astype(str).tolist()))
            out.write('] - L2 diff: ')
            out.write(str(np.linalg.norm(omega - omega_next)))
            out.write('\n')

            probs.append(p)

            if iter_count > max_iters:
                break
            if np.linalg.norm(omega_next - omega) < 1e-15:
                break
            omega = omega_next
            iter_count += 1
            clipped_counter += 1 if np.any((raw_omega < 0) | (raw_omega > 1.)) else 0
            clipped_dim_counter += np.count_nonzero((raw_omega < 0) | (raw_omega > 1.))

        print('# iterations', iter_count)
        print('# of times omega was truncated', clipped_counter)
        print('# of times p_i was truncated', clipped_dim_counter)
        out.write('# iterations {}\n'.format(iter_count))
        out.write('# of times omega was truncated {}\n'.format(clipped_counter))
        out.write('# of times p_i was truncated {}\n'.format(clipped_dim_counter))

        print('Max P(.) = ', np.max(probs))
        out.write('Max P(.) = ' + str(np.max(probs)))
        out.write('\n')

        print('Final Omega: ', get_subs(symbols, omega))
        out.write('Final Omega: ' + str(get_subs(symbols, omega)))
        out.write('\n')

        print('MLE probs: ', get_subs(symbols, mle_probs(gt_data)))
        out.write('MLE probs:   ' + str(get_subs(symbols, mle_probs(gt_data))))
        out.write('\n')

        print('P(M_y >= {} | MLE) = {}'.format(n_games - 1, objective_31.subs(get_subs(symbols, mle_probs(gt_data)))))
        out.write('P(M_y >= {} | MLE) = {}'.format(n_games - 1, objective_31.subs(get_subs(symbols, mle_probs(gt_data)))))
        out.write('\n')

        # import pdb; pdb.set_trace()
