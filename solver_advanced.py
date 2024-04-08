from solver_local_search import getInitialSolutionAndScore
from eternity_puzzle import EternityPuzzle
from colorama import Fore, Style
from largeNeighborhoodSearch import largeNeighborhoodSearch
from utils import countChange, logResults
import time

import os
from destructFct import *
from repairFct import *
from acceptFct import *


def solve_advanced(eternity_puzzle: EternityPuzzle):
    """
    Your solver for the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """

    maxTime = 5 * 60
    prctDestruct = 0.15
    maxWithoutAccept = 10000
    debug = True
    log = True
    logs = {"maxTime": maxTime,
            "prctDestruct": prctDestruct,
            "maxWithoutAccept": maxWithoutAccept,
            "debug": debug}

    rootTest = "testDestroyRepair"

    startTime = time.time()

    initialSolution, initialScore = getInitialSolutionAndScore(eternity_puzzle)

    # eternity_puzzle.display_solution(initialSolution, os.path.join(rootTest, "initial_solution.png"))
    #
    # destoyedSol, _, _ = destructProbaMostConflict(eternity_puzzle, initialSolution, prctDestruct=prctDestruct)
    #
    # eternity_puzzle.display_solution(destoyedSol, os.path.join(rootTest, "destructed_solution.png"))
    #
    # bestSol = initialSolution
    # bestScore = initialScore

    bestSol, bestScore = largeNeighborhoodSearch(eternity_puzzle, initialSolution,
                                                 destructProbaMostConflict, repairHeuristicAllRotation, acceptOnlyBetter,
                                                 prctDestruct=prctDestruct, maxWithoutAccept=maxWithoutAccept,
                                                 remainingTime=maxTime - (time.time() - startTime), debug=debug)

    if log:
        logs["bestScore"] = bestScore
        logs["Temps écoulé"] = round(time.time() - startTime, 2)
        logResults(eternity_puzzle, "advanced", logs)
    return bestSol, bestScore

