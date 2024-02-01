from algoLocalSearch import solverLSNaive, solverLocalSearchGlobal, getVoisinageOnlyConflict
from eternity_puzzle import EternityPuzzle
from utils import selectWithNbConflict


def solve_local_search(eternity_puzzle: EternityPuzzle):
    """
    Local search solution of the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """

    # solution, nbConflict = solverLSNaive(eternity_puzzle, 15)
    solution, nbConflict = solverLocalSearchGlobal(eternity_puzzle, getVoisinageOnlyConflict, selectWithNbConflict, eternity_puzzle.get_total_n_conflict, 600)
    return solution, nbConflict
