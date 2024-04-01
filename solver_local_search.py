import copy

from algoHeuristic import solverHeuristique1DeepEdgeFirstV2
from algoLocalSearch import solverLSNaive, solverLocalSearchGlobal, getVoisinageOnlyConflictV1, getVoisinageOnlyConflictV2
from eternity_puzzle import EternityPuzzle
from heuristiques import heuristicNbConflictPieceV3
from utils import selectWithNbConflict, printGridIndexes


def solve_local_search(eternity_puzzle: EternityPuzzle):
    """
    Local search solution of the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """

    printGridIndexes(eternity_puzzle)


    solution, nbConflict = solverHeuristique1DeepEdgeFirstV2(eternity_puzzle, heuristicNbConflictPieceV3)

    voisinage = getVoisinageOnlyConflictV2(eternity_puzzle, solution)

    print(len(voisinage))

    # solution, nbConflict = solverLSNaive(eternity_puzzle, 15)
    # solution, nbConflict = solverLocalSearchGlobal(eternity_puzzle, getVoisinageOnlyConflictV1, selectWithNbConflict, eternity_puzzle.get_total_n_conflict, 30)
    return solution, nbConflict