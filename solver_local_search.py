from algoLocalSearch import solverLSNaiveRandomStart


def solve_local_search(eternity_puzzle):
    """
    Local search solution of the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """

    solution, nbConflict = solverLSNaiveRandomStart(eternity_puzzle, 120)
    return solution, nbConflict
