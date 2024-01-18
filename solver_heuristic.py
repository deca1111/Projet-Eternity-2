from algoSolveur import solverHeuristique1DeepV1, solverHeuristique1DeepV2
from heuristiques import heuristicNbConflictPieceV1, heuristicNbConflictPieceV2


def solve_heuristic(eternity_puzzle):
    """
    Heuristic solution of the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """

    solution, nbConflict = solverHeuristique1DeepV2(eternity_puzzle, heuristicNbConflictPieceV2)

    return solution, nbConflict

