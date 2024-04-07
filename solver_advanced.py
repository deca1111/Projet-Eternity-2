from solver_local_search import getInitialSolutionAndScore
from eternity_puzzle import EternityPuzzle
from colorama import Fore, Style


def solve_advanced(eternity_puzzle: EternityPuzzle):
    """
    Your solver for the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """

    bestSol, bestScore = getInitialSolutionAndScore(eternity_puzzle)

    return bestSol, bestScore
