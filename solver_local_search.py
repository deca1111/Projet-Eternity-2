import copy
import time
from algoHeuristic import solverHeuristique1DeepEdgeFirstV2
from algoLocalSearch import getVoisinageOnlyConflictV1, getVoisinageOnlyConflictV2, simulatedAnnealing, localSearch, \
    findFirstUpgradingNeighbor
from eternity_puzzle import EternityPuzzle
from heuristiques import heuristicNbConflictPieceV3
from utils import selectWithNbConflict, printGridIndexes, saveBestSolution, logResults
import numpy as np

from colorama import Fore, Style


def solve_local_search(eternity_puzzle: EternityPuzzle):
    """
    Local search solution of the problem
    :param eternity_puzzle: object describing the input
    :return: a tuple (solution, cost) where solution is a list of the pieces (rotations applied) and
        cost is the cost of the solution
    """

    bestSol, bestScore = getInitialSolutionAndScore(eternity_puzzle)

    print(f"Initial score: {bestScore}")

    maxTime = 15 * 60
    debug = True

    startingTemp = 1
    tauxDecroissance = 0.999
    maxWithoutImprovement = 500

    startTime = time.time()
    nbIter = 1

    log_ = {}
    scores = []

    while time.time() - startTime < maxTime and bestScore > 0:
        if debug:
            print(Fore.WHITE + f"---------------- Iteration: {nbIter} - Temps "
                  f"restant: {round(maxTime - (time.time() - startTime), 2)} s -----------------")


        startingSol, _ = getInitialSolutionAndScore(eternity_puzzle)

        remainingTime = maxTime - (time.time() - startTime)
        # Recherche à partir de la solution initiale

        # Simulated Annealing
        # currentSol, currentScore = simulatedAnnealing(eternity_puzzle, startingSol, startingTemp,
        #                                               tauxDecroissance, maxWithoutImprovement=maxWithoutImprovement,
        #                                               remainingTime=remainingTime, debug=debug)

        # Local Search, premier voisin améliorant
        currentSol, currentScore = localSearch(eternity_puzzle, startingSol, getVoisinageOnlyConflictV2,
                                               findFirstUpgradingNeighbor, eternity_puzzle.get_total_n_conflict,
                                               remainingTime=remainingTime, debug=True, logs=log_)

        scores.append(currentScore)

        # Mise à jour de la meilleure solution
        if currentScore < bestScore:
            bestSol = currentSol
            bestScore = currentScore
            if debug:
                print(Fore.GREEN + f"New best score: {bestScore} - Temps "
                      f"restant: {round(maxTime - (time.time() - startTime), 2)} s")
        else:
            if debug:
                print(Fore.RED + f"No improvement: {currentScore} - Temps "
                      f"restant: {round(maxTime - (time.time() - startTime), 2)} s")

        nbIter += 1

    print(Style.RESET_ALL)

    logs = {"Date": time.strftime("%d/%m/%Y, %H:%M:%S"),
            "Algorithm": "LocalSearch",
            "voisinageFct": log_["voisinageFct"] if "voisinageFct" in log_ else "getVoisinageOnlyConflictV2",
            "selectFct": log_["selectFct"] if "selectFct" in log_ else "findFirstUpgradingNeighbor",
            "costFct": log_["costFct"] if "costFct" in log_ else "eternity_puzzle.get_total_n_conflict",
            "maxTime": maxTime,
            "bestScore": bestScore,
            "Temps pris": round(time.time() - startTime, 2),
            "NbRestart": nbIter - 1,
            "NbIter": log_["nbIter"] if "nbIter" in log_ else 0,
            "Score Moyen": np.mean(scores),
            "Score std": np.std(scores),
            }

    saveBestSolution(eternity_puzzle, "local_search", bestSol, bestScore, logs)
    logResults(eternity_puzzle, "local_search", logs)

    return bestSol, bestScore


def getInitialSolutionAndScore(eternity_puzzle: EternityPuzzle):
    solution, score = solverHeuristique1DeepEdgeFirstV2(eternity_puzzle, heuristicNbConflictPieceV3)

    return solution, score
