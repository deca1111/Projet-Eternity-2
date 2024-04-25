# Auteurs
# Armel Ngounou Tchawe - 2238017
# Léo Valette - 2307835


from solver_local_search import getInitialSolutionAndScore
from eternity_puzzle import EternityPuzzle
from colorama import Fore, Style
from largeNeighborhoodSearch import largeNeighborhoodSearch, restartLNS, restartBestLNS, restartBestAndRandom_LNS
from utils import countChange, logResults, saveBestSolution
import time
from adaptiveLargeNeighborhoodSearch import ALNS, restartALNS, restartBestALNS, restartBestAndRandom_ALNS

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

    maxTime = 60 * 60 if maxTime_ is None else maxTime_  # Temps maximum d'exécution

    debug = False  # Affichage des informations pendant l'exécution
    log = False  # Sauvegarde des logs
    saveBestSol = False  # Sauvegarde de la meilleure solution dans un dossier a part

    bestSol, bestScore = solveLNS(eternity_puzzle, maxTime_=maxTime, debug=debug, log=log, saveBestSol=saveBestSol)

    return bestSol, bestScore


def solveLNS(eternity_puzzle: EternityPuzzle, maxTime_=None, debug=False, log=False, saveBestSol=False):

    # Initialisation des hyperparamètres
    maxTime = 60 * 60 if maxTime_ is None else maxTime_  # Temps maximum d'exécution
    prctDestruct = 0.10
    maxWithoutAcceptOrImprove = 10000
    prctWorstAccept = 0.1
    ratioBest = 0.5

    if log:
        date = datetime.now()
        logs = {"Date": date.strftime("%d/%m/%Y, %H:%M:%S"),
                "Algorithm": "",
                "maxTime": maxTime,
                "prctDestruct": prctDestruct,
                "maxWithoutAcceptOrImprove": maxWithoutAcceptOrImprove,
                "debug": debug,
                "tag": "run",
                "NbIter": 0}
    else:
        logs = {}

    startTime = time.time()

    if prctWorstAccept is not None:
        def acceptPrctWorst_(oldCost, newCost):
            return acceptPrctWorst(oldCost, newCost, prct=prctWorstAccept)

    # bestSol, bestScore = restartLNS(eternity_puzzle, destructFct=destructOnlyConflict,
    #                                 reconstructFct=repairHeuristicPieceBest, acceptFct=acceptAll,
    #                                 maxWithoutAcceptOrImprove=maxWithoutAcceptOrImprove,
    #                                 prctDestruct=prctDestruct, maxTime=maxTime, debug=debug, logs=logs)

    bestSol, bestScore = restartBestAndRandom_LNS(eternity_puzzle, destructFctRandom=destructOnlyConflict,
                                                  reconstructFctRandom=repairHeuristicEmplacementBest,
                                                  acceptFctRandom=acceptAll,
                                                  maxWithoutAcceptOrImprove=maxWithoutAcceptOrImprove,
                                                  prctDestruct=prctDestruct, maxTime=maxTime, ratioBest=ratioBest,
                                                  debug=debug, logs=logs)

    if log:
        if logs["AcceptFct"] == acceptPrctWorst_.__name__:
            logs["prctWorstAccept"] = prctWorstAccept
        if logs["Algorithm"] == "restartBestAndRandom_LNS":
            logs["ratioBest"] = ratioBest
        logs["bestScore"] = bestScore
        logs["Temps pris"] = round(time.time() - startTime, 2)
        logResults(eternity_puzzle, "advanced", logs)

    if saveBestSol:
        saveBestSolution(eternity_puzzle, "advanced", bestSol, bestScore, logs)

    return bestSol, bestScore


def solveALNS(eternity_puzzle: EternityPuzzle, maxTime_=None, debug=False, log=False, saveBestSol=False):

    # Initialisation des hyperparamètres
    maxTime = 15 * 60 if maxTime_ is None else maxTime_
    prctDestruct = 0.1
    maxWithoutAcceptOrImprove = 10000
    prctWorstAccept = 0.1

    if log:
        date = datetime.now()
        logs = {"Date": date.strftime("%d/%m/%Y, %H:%M:%S"),
                "Algorithm": "",
                "maxTime": maxTime,
                "prctDestruct": prctDestruct,
                "maxWithoutAcceptOrImprove": maxWithoutAcceptOrImprove,
                "debug": debug}
        if prctWorstAccept is not None:
            logs["prctWorstAccept"] = prctWorstAccept
    else:
        logs = {}

    def acceptPrctWorst_(oldCost, newCost):
        return acceptPrctWorst(oldCost, newCost, prct=prctWorstAccept)

    # Choix des fonctions de destruction, de reconstruction et d'acceptation
    listDestructFct = [destructRandom, destructProbaMostConflict, destructOnlyConflict, destructAllConflict]
    listReconstructFct = [repairHeuristicEmplacementBest]
    listAcceptFct = [acceptOnlyBetter, acceptSameOrBetter]

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
    bestSol, bestScore = restartBestALNS(eternity_puzzle, listDestructFct, listReconstructFct, listAcceptFct,
                                         updateWeights=updateWeights, lambda_=lambda_,
                                         maxWithoutAcceptOrImprove=maxWithoutAcceptOrImprove, prctDestruct=prctDestruct,
                                         maxTime=maxTime, debug=debug, logs=logs)

    if log:
        logs["bestScore"] = bestScore
        logs["Temps pris"] = round(time.time() - startTime, 2)
        logResults(eternity_puzzle, "advanced", logs)

    if saveBestSol:
        saveBestSolution(eternity_puzzle, "advanced", bestSol, bestScore, logs)

    return bestSol, bestScore


def solverALNS_splitRestart(eternity_puzzle: EternityPuzzle, maxTime_=None, debug=False, log=False, saveBestSol=False):

    # Initialisation des hyperparamètres
    maxTime = 15 * 60 if maxTime_ is None else maxTime_
    prctDestruct = 0.1
    maxWithoutAcceptOrImprove = 10000
    prctWorstAccept = 0.25
    ratioBest = 2

    if log:
        date = datetime.now()
        logs = {"Date": date.strftime("%d/%m/%Y, %H:%M:%S"),
                "Algorithm": "",
                "maxTime": maxTime,
                "prctDestruct": prctDestruct,
                "maxWithoutAcceptOrImprove": maxWithoutAcceptOrImprove,
                "debug": debug}
        if prctWorstAccept is not None:
            logs["prctWorstAccept"] = prctWorstAccept
    else:
        logs = {}

    def acceptPrctWorst_(oldCost, newCost):
        return acceptPrctWorst(oldCost, newCost, prct=prctWorstAccept)

    # Choix des fonctions de destruction, de reconstruction et d'acceptation
    listDestructFctRandomRestart = [destructRandom, destructProbaMostConflict, destructOnlyConflict,
                                    destructAllConflict]
    listReconstructFctRandomRestart = [repairHeuristicEmplacementBest, repairHeuristicPieceBest]
    listAcceptFctRandomRestart = [acceptOnlyBetter, acceptSameOrBetter, acceptPrctWorst]

    listDestructFctBestRestart = listDestructFctRandomRestart
    listReconstructFctBestRestart = listReconstructFctRandomRestart
    listAcceptFctBestRestart = listAcceptFctRandomRestart

    if log:
        logs["listDestructFctRandomRestart"] = [f.__name__ for f in listDestructFctRandomRestart]
        logs["listReconstructFctRandomRestart"] = [f.__name__ for f in listReconstructFctRandomRestart]
        logs["listAcceptFctRandomRestart"] = [f.__name__ for f in listAcceptFctRandomRestart]

        logs["listDestructFctBestRestart"] = [f.__name__ for f in listDestructFctBestRestart]
        logs["listReconstructFctBestRestart"] = [f.__name__ for f in listReconstructFctBestRestart]
        logs["listAcceptFctBestRestart"] = [f.__name__ for f in listAcceptFctBestRestart]

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

    # Lancement de l'ALNS avec restart best and random
    startTime = time.time()

    bestSol, bestScore = restartBestAndRandom_ALNS(eternity_puzzle,
                                                   listDestructFctRandomRestart,
                                                   listReconstructFctRandomRestart,
                                                   listAcceptFctRandomRestart,
                                                   listDestructFctBest=listDestructFctBestRestart,
                                                   listReconstructFctBest=listReconstructFctBestRestart,
                                                   listAcceptFctBest=listAcceptFctBestRestart,
                                                   updateWeights=updateWeights, lambda_=lambda_,
                                                   ratioBest=ratioBest,
                                                   maxWithoutAcceptOrImprove=maxWithoutAcceptOrImprove,
                                                   prctDestruct=prctDestruct, maxTime=maxTime, debug=debug, logs=logs)

    if log:
        logs["bestScore"] = bestScore
        logs["Temps pris"] = round(time.time() - startTime, 2)
        logResults(eternity_puzzle, "advanced", logs)

    if saveBestSol:
        saveBestSolution(eternity_puzzle, "advanced", bestSol, bestScore, logs)

    return bestSol, bestScore
