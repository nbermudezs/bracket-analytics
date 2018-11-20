#!/usr/bin/env python3

__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


from itertools import combinations
from sympy.parsing.sympy_parser import parse_expr
from sympy.matrices import hessian
import numpy as np
import sympy as sp


truth = {
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


def optimal_p(i):
    factors = []
    for j in range(32):
        if j % 8 == i:
            continue
        if truth[j] == 1:
            factors.append((1. - p[j]) / p[j])
        else:
            factors.append(p[j]/(1. - p[j]))
    print('B=', np.sum(factors))
    return np.sum(factors)


def create_equation(i):
    terms = [['x', '(1-x)'] if truth[2018][i + 8 * r] == 1 else ['(1-x)', 'x']
             for r in range(4)]

    equation = []
    equation.append('*'.join([t[0] for t in terms]) + '*' + str(optimal_p(i)))
    for t_i in range(4):
        term = []
        for j in range(4):
            if j == t_i:
                term.append(terms[j][1])
            else:
                term.append(terms[j][0])
        equation.append('*'.join(term))
    eq = '+'.join(equation)
    print(eq)


def _full_form_objective_function_32(year):
    factors = []
    for i in range(32):
        j = i % 8
        if truth[year][i] == 0:
            factors.append('(1-p_{})'.format(j))
        else:
            factors.append('p_{}'.format(j))
    return '*'.join(factors)


def _full_form_objective_function_31(year):
    summands = []
    for flip in range(32):
        factors = []
        for i in range(32):
            j = i % 8
            if i == flip:
                if truth[year][i] == 1:
                    factors.append('(1-p_{})'.format(j))
                else:
                    factors.append('p_{}'.format(j))
            else:
                if truth[year][i] == 0:
                    factors.append('(1-p_{})'.format(j))
                else:
                    factors.append('p_{}'.format(j))
        summands.append('*'.join(factors))
    return '(' + '+'.join(summands) + ')'


def _full_form_objective_function_30(year):
    summands = []
    for flip_i in range(32):
        for flip_j in range(32):
            if flip_i == flip_j:
                continue
            factors = []
            for i in range(32):
                j = i % 8
                if i in [flip_i, flip_j]:
                    if truth[year][i] == 1:
                        factors.append('(1-p_{})'.format(j))
                    else:
                        factors.append('p_{}'.format(j))
                else:
                    if truth[year][i] == 0:
                        factors.append('(1-p_{})'.format(j))
                    else:
                        factors.append('p_{}'.format(j))
            summands.append('*'.join(factors))
    return '(' + '+'.join(summands) + ')'


objective_fns = {
    '32': _full_form_objective_function_32,
    '31': _full_form_objective_function_31,
    '30': _full_form_objective_function_30
}


def _full_form_objective_function(year, alpha):
    obj = '+'.join([
        objective_fns[str(alpha_i)](year)
        for alpha_i in range(alpha, 33)
    ])
    return obj


def full_form_objective_fn(alpha=31):
    year_objs = [_full_form_objective_function(year, alpha) for year in truth.keys()]
    return '*'.join(year_objs)


def get_subs(symbols):
    return [
        (symbols['p_{}'.format(i)], omega[i])
        for i in range(8)
    ]


if __name__ == '__main__':
    # fns = [create_equation(i) for i in range(8)]

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
    objective_31 = parse_expr(full_form_objective_fn(),
                              local_dict=omega_symbols)
    H = hessian(objective_31, list(omega_symbols.values()))
    grad = [sp.diff(objective_31, p_i) for p_i in omega_symbols.values()]
    print(H[0])

    iter_count = 0
    max_iters = 10000
    history = []
    while True:
        history.append(omega)
        H_eval = np.array([d2f.subs(get_subs(omega_symbols)) for d2f in H], dtype=float).reshape(8, 8)
        grad_eval = np.array([f_prime.subs(get_subs(omega_symbols)) for f_prime in grad], dtype=float)
        omega_next = np.clip(omega + np.linalg.inv(H_eval).dot(grad_eval), 0., 1.)
        print(omega.tolist(), ' - L2 diff: ', np.linalg.norm(omega - omega_next))
        print('P(M_y >= 31) = ', objective_31.subs(get_subs(omega_symbols)))
        omega = omega_next
        if iter_count > max_iters:
            break
        iter_count += 1
