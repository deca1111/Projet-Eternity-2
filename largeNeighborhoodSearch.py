from eternity_puzzle import EternityPuzzle
from colorama import Fore, Style
import time
from solver_local_search import getInitialSolutionAndScore


def restartLNS(
        puzzle: EternityPuzzle, destructFct, reconstructFct, acceptFct,
        maxWithoutAccept=100, prctDestruct=None, maxTime=60, debug=False
        ):
    """
    Ajout d'un restart aléatoire à l'algorithme de recherche locale LNS
    :param puzzle: Instance du puzzle
    :param destructFct: Fonction de destruction
    :param reconstructFct: Fonction de reconstruction
    :param acceptFct: Fonction d'acceptation
    :param maxWithoutAccept: Nombre maximum d'itérations sans accepter avant de redémarrer
    :param prctDestruct: Pourcentage (maximum) de pièces à détruire
    :param maxTime: Temps maximum alloué à la recherche
    :param debug: Affichage des informations de débogage
    :return: La meilleure solution trouvée et son score
    """

    startTime = time.time()
    nbRestart = 1

    if debug:
        print(Fore.BLUE + f"----------------- Début LNS avec restart - Temps restant: {maxTime} s -----------------")

    # Initialisation meilleure solution
    bestSol, bestScore = getInitialSolutionAndScore(puzzle)

    while (time.time() - startTime) < maxTime:
        # Génération d'une solution initiale
        initialSolution, initialScore = getInitialSolutionAndScore(puzzle)

        remainingTime = maxTime - (time.time() - startTime)

        if debug:
            print(Fore.BLUE + f"Restart {nbRestart} - Temps restant: {remainingTime} s - Score initial: {initialScore}")

        # Lancement du LNS
        currentSol, currentScore = largeNeighborhoodSearch(puzzle, initialSolution, destructFct, reconstructFct,
                                                           acceptFct, prctDestruct=prctDestruct,
                                                           maxWithoutAccept=maxWithoutAccept,
                                                           remainingTime=remainingTime, debug=debug)

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
            print(Fore.BLACK + f"No improvement: {currentScore} - "
                               f"Temps restant: {round(maxTime - (time.time() - startTime), 2)} s - "
                               f"Restart {nbRestart}")

        nbRestart += 1

    if debug:
        print(Fore.BLUE + f"----------------- Fin LNS avec restart - "
                          f"Temps écoulé: {round(time.time() - startTime, 2)} s - "
                          f"Restarts: {nbRestart} - "
                          f"Meilleur score: {bestScore}"
                          f"-----------------" + Style.RESET_ALL)

    return bestSol, bestScore


def largeNeighborhoodSearch(
        puzzle: EternityPuzzle, initialSolution, destructFct, reconstructFct, acceptFct,
        maxWithoutAccept=100, prctDestruct=None, remainingTime=60, debug=False
        ):
    # Initialisation
    startTime = time.time()
    currentSol = initialSolution
    currentScore = puzzle.get_total_n_conflict(currentSol)
    bestSol = currentSol
    bestScore = currentScore
    idxIter = 1
    nbWithoutAccept = 0

    if debug:
        print(
            Fore.YELLOW + f"Début LNS - Score initial: {currentScore} - Temps restant: {remainingTime - (time.time() - startTime)} s")

    while (time.time() - startTime) < remainingTime and bestScore > 0:

        # Destruction
        if prctDestruct is not None:
            partialSol, destroyedPieces, idxDestroyedPieces = destructFct(puzzle, currentSol, prctDestruct=prctDestruct)
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

                if debug:
                    print(Fore.WHITE + f"New best score: {bestScore} - Temps restant: "
                                       f"{round(remainingTime - (time.time() - startTime), 2)} s - Itération {idxIter}")
        else:
            nbWithoutAccept += 1

            # Si on a dépassé le nombre d'itérations sans accepter, on arrête
            if nbWithoutAccept > maxWithoutAccept:
                break

        idxIter += 1

    if debug:
        print(Fore.YELLOW + f"Fin LNS - Score final: {bestScore} - Temps écoulé: {round(time.time() - startTime, 2)} s "
                          f"- Itérations: {idxIter}" + Style.RESET_ALL)

    return bestSol, bestScore
