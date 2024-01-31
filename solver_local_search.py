from algoLocalSearch import solverLSNaive, solverLocalSearchGlobal


def solve_local_search(eternity_puzzle):
    """
    Local search solution of the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """

    solution, nbConflict = solverLSNaive(eternity_puzzle, 15)

    return solution, nbConflict
