from solver_local_search import getInitialSolutionAndScore
from eternity_puzzle import EternityPuzzle
from colorama import Fore, Style
from largeNeighborhoodSearch import largeNeighborhoodSearch, restartLNS
from utils import countChange, logResults, saveBestSolution
import time

import os
from destructFct import *
from repairFct import *
from acceptFct import *


def solve_advanced(eternity_puzzle: EternityPuzzle, maxTime_=None):
    """
    Your solver for the problem
    :param eternity_puzzle: object describing the input
    :param maxTime_: maximum time in seconds
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """

    if maxTime_ is None:
        maxTime = 15 * 60
    else:
        maxTime = maxTime_

    prctDestruct = 0.15
    maxWithoutAccept = 10000
    debug = True
    log = True
    logs = {"Algorithm": "restartLNS",
            "maxTime": maxTime,
            "prctDestruct": prctDestruct,
            "maxWithoutAccept": maxWithoutAccept,
            "debug": debug}

    startTime = time.time()

    bestSol, bestScore = restartLNS(eternity_puzzle, destructProbaMostConflict, repairHeuristicAllRotation,
                                    acceptOnlyBetter,
                                    maxWithoutAccept=maxWithoutAccept, prctDestruct=prctDestruct,
                                    maxTime=maxTime, debug=debug)

    if log:
        logs["bestScore"] = bestScore
        logs["Temps écoulé"] = round(time.time() - startTime, 2)
        logResults(eternity_puzzle, "advanced", logs)

    saveBestSolution(eternity_puzzle, "advanced", bestSol, bestScore)

    return bestSol, bestScore

