from eternity_puzzle import EternityPuzzle
from colorama import Fore, Style
import time


def largeNeighborhoodSearch(puzzle: EternityPuzzle, initialSolution, destructFct, reconstructFct, acceptFct,
                            maxWithoutAccept=100, prctDestruct=None, remainingTime=60, debug=False):

    # Initialisation
    startTime = time.time()
    currentSol = initialSolution
    currentScore = puzzle.get_total_n_conflict(currentSol)
    bestSol = currentSol
    bestScore = currentScore
    idxIter = 1
    nbWithoutAccept = 0

    if debug:
        print(Fore.BLUE + f"Début LNS - Score initial: {currentScore} - Temps restant: {remainingTime - (time.time() - startTime)} s")

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
                    print(Fore.GREEN + f"New best score: {bestScore} - Temps restant: "
                                       f"{round(remainingTime - (time.time() - startTime), 2)} s - Itération {idxIter}")
        else:
            nbWithoutAccept += 1

            # Si on a dépassé le nombre d'itérations sans accepter, on arrête
            if nbWithoutAccept > maxWithoutAccept:
                break

        idxIter += 1

    if debug:
        print(Fore.BLUE + f"Fin LNS - Score final: {bestScore} - Temps écoulé: {round(time.time() - startTime, 2)} s "
                          f"- Itérations: {idxIter}" + Style.RESET_ALL)

    return bestSol, bestScore
