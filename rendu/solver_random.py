# Auteurs
# Armel Ngounou Tchawe - 2238017
# Léo Valette - 2307835

import numpy as np
import copy
from datetime import datetime


from utils import saveBestSolution


def solve_random(eternity_puzzle):
    """
    Random solution of the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """

    saveBestSol = False  # Sauvegarde de la meilleure solution

    solution = []
    remaining_piece = copy.deepcopy(eternity_puzzle.piece_list)

    for i in range(eternity_puzzle.n_piece):
        range_remaining = np.arange(len(remaining_piece))
        piece_idx = np.random.choice(range_remaining)

        piece = remaining_piece[piece_idx]

        permutation_idx = np.random.choice(np.arange(4))

        piece_permuted = eternity_puzzle.generate_rotation(piece)[permutation_idx]

        solution.append(piece_permuted)

        remaining_piece.remove(piece)

    score = eternity_puzzle.get_total_n_conflict(solution)

    date = datetime.now()
    logs = {
        "Algorithm": "Random",
        "Date": date.strftime("%d/%m/%Y, %H:%M:%S"),
        "Score": score,
        }

    if saveBestSol:
        saveBestSolution(eternity_puzzle, "random", solution, score, logDict=logs)

    return solution, score


def solve_best_random(eternity_puzzle, n_trial=1000):
    """
    Random solution of the problem (best of n_trial random solution generated)
    :param eternity_puzzle: object describing the input
    :param n_trial: number of random solution generated
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution, the solution is the best among the n_trial generated ones
    """
    saveBestSol = False

    best_solution = None
    bestScore = float("inf")

    for i in range(n_trial):

        cur_sol, cur_n_conflict = solve_random(eternity_puzzle)

        if cur_n_conflict < bestScore:
            bestScore = cur_n_conflict
            best_solution = cur_sol

    assert best_solution != None

    date = datetime.now()
    logs = {
        "Algorithm": "Random",
        "Date": date.strftime("%d/%m/%Y, %H:%M:%S"),
        "Nb trial": n_trial,
        }

    if saveBestSol:
        saveBestSolution(eternity_puzzle, "random", best_solution, bestScore, logDict=logs)

    return best_solution, bestScore
