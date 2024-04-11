from eternity_puzzle import EternityPuzzle
from colorama import Fore, Style
import time
from solver_local_search import getInitialSolutionAndScore
import numpy as np


def restartLNS(
        puzzle: EternityPuzzle, destructFct, reconstructFct, acceptFct,
        maxWithoutAcceptOrImprove=100, prctDestruct=None, maxTime=60., debug=False, logs=None
        ):
    """
    Ajout d'un restart aléatoire à l'algorithme de recherche locale LNS
    :param puzzle: Instance du puzzle
    :param destructFct: Fonction de destruction
    :param reconstructFct: Fonction de reconstruction
    :param acceptFct: Fonction d'acceptation
    :param maxWithoutAcceptOrImprove: Nombre maximum d'itérations sans accepter ou améliorer avant de redémarrer
    :param prctDestruct: Pourcentage (maximum) de pièces à détruire
    :param maxTime: Temps maximum alloué à la recherche
    :param debug: Affichage des informations de débogage
    :return: La meilleure solution trouvée et son score
    """

    startTime = time.time()
    nbRestart = 1
    scores = []

    if debug:
        print(Fore.BLUE + f"----------------- Début LNS avec restart - Temps restant: {maxTime} s -----------------")
        print(f" - Fonction de destruction: {destructFct.__name__}")
        print(f" - Fonction de reconstruction: {reconstructFct.__name__}")
        print(f" - Fonction d'acceptation: {acceptFct.__name__}")
        print(f" - MaxWithoutAccept: {maxWithoutAcceptOrImprove}")
        print(f" - PrctDestruct: {prctDestruct}")
        print(f" - MaxTime: {maxTime}")
        print("---------------------------------------------------------------------------------")

    # Initialisation meilleure solution
    bestSol, bestScore = getInitialSolutionAndScore(puzzle)

    while (time.time() - startTime) < maxTime:
        # Génération d'une solution initiale
        initialSolution, initialScore = getInitialSolutionAndScore(puzzle)

        remainingTime = maxTime - (time.time() - startTime)

        if debug:
            print(Fore.BLUE + f"Restart {nbRestart} - Temps restant: {round(remainingTime,2)} s - Score initial: {initialScore}")

        # Lancement du LNS
        currentSol, currentScore = largeNeighborhoodSearch(puzzle, initialSolution, destructFct, reconstructFct,
                                                           acceptFct, maxWithoutAcceptOrImprove=maxWithoutAcceptOrImprove,
                                                           prctDestruct=prctDestruct, remainingTime=remainingTime,
                                                           debug=debug)

        scores.append(currentScore)

        # Si on a trouvé une solution valide, on arrête
        if bestScore == 0:
            break

        if currentScore < bestScore:
            bestSol = currentSol
            bestScore = currentScore

            if debug:
                print(Fore.GREEN + f"New best score: {bestScore} - "
                                   f"Temps restant: {round(maxTime - (time.time() - startTime), 2)} s - "
                                   f"Restart {nbRestart}")

        else:
            print(Fore.WHITE + f"No improvement: {currentScore} - "
                               f"Temps restant: {round(maxTime - (time.time() - startTime), 2)} s - "
                               f"Restart {nbRestart}")

        nbRestart += 1

    if debug:
        print(Fore.BLUE + f"----------------- Fin LNS avec restart - "
                          f"Temps écoulé: {round(time.time() - startTime, 2)} s - "
                          f"Restarts: {nbRestart} - "
                          f"Meilleur score: {bestScore}"
                          f"-----------------" + Style.RESET_ALL)

    if logs is not None:
        logs["NbRestart"] = nbRestart
        logs["DestructFct"] = destructFct.__name__
        logs["ReconstructFct"] = reconstructFct.__name__
        logs["AcceptFct"] = acceptFct.__name__
        meanScore = sum(scores) / len(scores)
        logs["MeanScore"] = meanScore
        stdScore = np.std(scores)
        logs["StdScore"] = stdScore

    return bestSol, bestScore


def largeNeighborhoodSearch(
        puzzle: EternityPuzzle, initialSolution, destructFct, reconstructFct, acceptFct,
        maxWithoutAcceptOrImprove=100, prctDestruct=None, remainingTime=60., debug=False
        ):
    """
    Large Neighborhood Search
    :param puzzle: Instance du puzzle
    :param initialSolution: solution initiale
    :param destructFct: Fonction de destruction
    :param reconstructFct: Fonction de reconstruction
    :param acceptFct: Fonction d'acceptation
    :param maxWithoutAcceptOrImprove: nombre maximum d'itérations sans accepter ou améliorer avant de s'arrêter
    :param prctDestruct: Pourcentage de pièces à détruire
    :param remainingTime: Temps restant pour la recherche
    :param debug: Affichage des informations de débogage
    :return:
    """
    # Initialisation
    startTime = time.time()
    currentSol = initialSolution
    currentScore = puzzle.get_total_n_conflict(currentSol)
    bestSol = currentSol
    bestScore = currentScore
    idxIter = 1
    nbWithoutAccept = 0
    nbWithoutImprovement = 0

    if debug:
        print(
            Fore.YELLOW + f"Début LNS - Score initial: {currentScore} - "
                          f"Temps restant: {round(remainingTime - (time.time() - startTime),2)} s")

    while (time.time() - startTime) < remainingTime and bestScore > 0:

        # Destruction
        if prctDestruct is not None:
            partialSol, destroyedPieces, idxDestroyedPieces = destructFct(puzzle, currentSol, prctDestruct)
        else:
            partialSol, destroyedPieces, idxDestroyedPieces = destructFct(puzzle, currentSol)

        # Réparation
        reconstructedSol = reconstructFct(puzzle, partialSol, destroyedPieces, idxDestroyedPieces)

        # Critère d'acceptation
        reconstructedScore = puzzle.get_total_n_conflict(reconstructedSol)

        # Si on accepte la solution reconstruite
        if acceptFct(currentScore, reconstructedScore):
            # Maj de la solution courante
            currentSol = reconstructedSol
            currentScore = reconstructedScore

            # Réinitialisation du compteur de solutions non acceptées
            nbWithoutAccept = 0

            # Maj de la meilleure solution
            if currentScore < bestScore:
                bestSol = currentSol
                bestScore = currentScore

                # Réinitialisation du compteur de solutions sans amélioration
                nbWithoutImprovement = 0

                if debug:
                    print(Fore.BLACK + f"New best score: {bestScore} - Temps restant: "
                                       f"{round(remainingTime - (time.time() - startTime), 2)} s - Itération {idxIter}")

            else:
                nbWithoutImprovement += 1

        else:
            nbWithoutAccept += 1
            nbWithoutImprovement += 1

        # Si on a dépassé le nombre d'itérations sans accepter ou améliorer, on s'arrête
        if nbWithoutAccept > maxWithoutAcceptOrImprove or nbWithoutImprovement > maxWithoutAcceptOrImprove:
            break

        idxIter += 1

    if debug:
        print(Fore.YELLOW + f"Fin LNS - Score final: {bestScore} - Temps écoulé: {round(time.time() - startTime, 2)} s "
                          f"- Itérations: {idxIter}" + Style.RESET_ALL)

    return bestSol, bestScore
