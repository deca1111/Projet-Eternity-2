# Auteurs
# Armel Ngounou Tchawe - 2238017
# Léo Valette - 2307835


from algoHeuristic import (solverHeuristique1Deep, solverHeuristique1DeepRestart, solverHeuristique1DeepEdgeFirst,
                           solverHeuristique1DeepEdgeFirstV2)
from heuristiques import heuristicNbConflictPieceV1, heuristicNbConflictPieceV2, heuristicNbConflictPieceV3

from utils import saveBestSolution


def solve_heuristic(eternity_puzzle):
    """
    Heuristic solution of the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """
    saveBestSol = False

    solution, nbConflict = solverHeuristique1DeepEdgeFirstV2(eternity_puzzle, heuristicNbConflictPieceV3)

    if saveBestSol:
        saveBestSolution(eternity_puzzle, "heuristic", solution, nbConflict)

    return solution, nbConflict

