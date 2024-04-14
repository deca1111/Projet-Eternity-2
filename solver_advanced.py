from solver_local_search import getInitialSolutionAndScore
from eternity_puzzle import EternityPuzzle
from colorama import Fore, Style
from largeNeighborhoodSearch import largeNeighborhoodSearch, restartLNS
from utils import countChange, logResults, saveBestSolution
import time
from adaptiveLargeNeighborhoodSearch import ALNS, restartALNS

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

    bestSol, bestScore = solveALNS(eternity_puzzle, maxTime_)

    return bestSol, bestScore


def solveLNS(eternity_puzzle: EternityPuzzle, maxTime_=None):
    maxTime = 5 * 60 if maxTime_ is None else maxTime_
    prctDestruct = 0.1
    maxWithoutAcceptOrImprove = 10000
    debug = True
    log = True
    if log:
        date = datetime.now()
        logs = {"Date": date.strftime("%d/%m/%Y, %H:%M:%S"),
                "Algorithm": "restartLNS",
                "maxTime": maxTime,
                "prctDestruct": prctDestruct,
                "maxWithoutAcceptOrImprove": maxWithoutAcceptOrImprove,
                "debug": debug}

    startTime = time.time()

    bestSol, bestScore = restartLNS(eternity_puzzle, destructOnlyConflict, repairHeuristicAllRotation,
                                    acceptAll, maxWithoutAcceptOrImprove=maxWithoutAcceptOrImprove,
                                    prctDestruct=prctDestruct, maxTime=maxTime, debug=debug, logs=logs)

    if log:
        logs["bestScore"] = bestScore
        logs["Temps pris"] = round(time.time() - startTime, 2)
        logResults(eternity_puzzle, "advanced", logs)

    saveBestSolution(eternity_puzzle, "advanced", bestSol, bestScore, logs)

    return bestSol, bestScore


def solveALNS(eternity_puzzle: EternityPuzzle, maxTime_=None):

    # Initialisation des hyperparamètres
    maxTime = 45 * 60 if maxTime_ is None else maxTime_
    prctDestruct = 0.1
    maxWithoutAcceptOrImprove = 25000
    debug = True
    log = True
    if log:
        date = datetime.now()
        logs = {"Date": date.strftime("%d/%m/%Y, %H:%M:%S"),
                "Algorithm": "restartALNS",
                "maxTime": maxTime,
                "prctDestruct": prctDestruct,
                "maxWithoutAcceptOrImprove": maxWithoutAcceptOrImprove,
                "debug": debug}

    # Choix des fonctions de destruction, de reconstruction et d'acceptation
    listDestructFct = [destructRandom, destructProbaMostConflict, destructOnlyConflict, destructAllConflict]
    listReconstructFct = [repairHeuristicAllRotation, repairRandom]
    listAcceptFct = [acceptSameOrBetter]

    if log:
        logs["listDestructFct"] = [f.__name__ for f in listDestructFct]
        logs["listReconstructFct"] = [f.__name__ for f in listReconstructFct]
        logs["listAcceptFct"] = [f.__name__ for f in listAcceptFct]

    # Poids attribués aux fonctions choisies en fonction de différents scénarios:
    # updateWeights[0] : si la nouvelle solution est la meilleure actuellement trouvée
    # updateWeights[1] : si la nouvelle solution est meilleure que la précédente
    # updateWeights[2] : si la nouvelle solution est acceptée
    # updateWeights[3] : si la nouvelle solution est rejetée
    updateWeights = [1000, 200, 25, 1]

    if log:
        logs["updateWeights"] = updateWeights

    # Paramètre de sensibilité pour la mise à jour des poids, entre 0 et 1,
    # Si = 1 on ne change pas les poids
    # Si = 0 on ne garde que le nouveau poids
    lambda_ = 0.9

    if log:
        logs["lambda"] = lambda_

    # Lancement de l'ALNS avec restart
    startTime = time.time()
    bestSol, bestScore = restartALNS(eternity_puzzle, listDestructFct, listReconstructFct, listAcceptFct,
                                     updateWeights=updateWeights, lambda_=lambda_,
                                     maxWithoutAcceptOrImprove=maxWithoutAcceptOrImprove, prctDestruct=prctDestruct,
                                     maxTime=maxTime, debug=debug, logs=logs)

    if log:
        logs["bestScore"] = bestScore
        logs["Temps pris"] = round(time.time() - startTime, 2)
        logResults(eternity_puzzle, "advanced", logs)

    saveBestSolution(eternity_puzzle, "advanced", bestSol, bestScore, logs)

    return bestSol, bestScore
