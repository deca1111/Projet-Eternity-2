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

    while (time.time() - startTime) < maxTime and bestScore > 0:
        # Génération d'une solution initiale
        initialSolution, initialScore = getInitialSolutionAndScore(puzzle)

        remainingTime = maxTime - (time.time() - startTime)

        if debug:
            print(
                Fore.BLUE + f"Restart {nbRestart} - Temps restant: {round(remainingTime, 2)} s - Score initial: {initialScore}")

        # Lancement du LNS
        currentSol, currentScore = largeNeighborhoodSearch(puzzle, initialSolution, destructFct, reconstructFct,
                                                           acceptFct,
                                                           maxWithoutAcceptOrImprove=maxWithoutAcceptOrImprove,
                                                           prctDestruct=prctDestruct, remainingTime=remainingTime,
                                                           debug=debug)

        scores.append(currentScore)

        # Si on a trouvé une solution valide, on arrête
        if currentScore == 0:
            bestSol = currentSol
            bestScore = currentScore
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
        logs["Algorithm"] = "restartLNS"
        logs["DestructFct"] = destructFct.__name__
        logs["ReconstructFct"] = reconstructFct.__name__
        logs["AcceptFct"] = acceptFct.__name__
        logs["NbRestart"] = nbRestart
        meanScore = sum(scores) / len(scores)
        logs["MeanScore"] = round(meanScore, 4)
        stdScore = np.std(scores)
        logs["StdScore"] = round(stdScore, 4)

    return bestSol, bestScore


def largeNeighborhoodSearch(
        puzzle: EternityPuzzle, initialSolution, destructFct, reconstructFct, acceptFct,
        maxWithoutAcceptOrImprove=100, prctDestruct=0.1, remainingTime=60., debug=False
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
    :return: La meilleure solution trouvée et son score
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
                          f"Temps restant: {round(remainingTime - (time.time() - startTime), 2)} s")

    while (time.time() - startTime) < remainingTime and bestScore > 0:

        # Destruction
        partialSol, destroyedPieces, idxDestroyedPieces = destructFct(puzzle, currentSol, prctDestruct)

        # Réparation
        reconstructedSol = reconstructFct(puzzle, partialSol, destroyedPieces, idxDestroyedPieces)

        reconstructedScore = puzzle.get_total_n_conflict(reconstructedSol)

        # Si on a trouvé une solution valide, on arrête
        if reconstructedScore == 0:
            bestSol = reconstructedSol
            bestScore = reconstructedScore
            break

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
            if debug:
                print(Fore.RED + f"Arrêt du LNS - Nombre d'itérations dépassé - Dernier score {currentScore}" +
                      Style.RESET_ALL)
            break

        idxIter += 1

    if debug:
        print(Fore.YELLOW + f"Fin LNS - Score final: {bestScore} - Temps écoulé: {round(time.time() - startTime, 2)} s "
                            f"- Itérations: {idxIter}" + Style.RESET_ALL)

    return bestSol, bestScore


def restartBestLNS(
        puzzle: EternityPuzzle, destructFct, reconstructFct, acceptFct,
        maxWithoutAcceptOrImprove=100, prctDestruct=None, maxTime=60., debug=False, logs=None
        ):  # sourcery skip: low-code-quality
    """
    LNS avec restart non aléatoire, on redémarre avec la meilleure solution trouvée
    :param puzzle: Instance du puzzle
    :param destructFct: Fonction de destruction
    :param reconstructFct: Fonction de reconstruction
    :param acceptFct: Fonction d'acceptation
    :param maxWithoutAcceptOrImprove: Nombre maximum d'itérations sans accepter ou améliorer avant de redémarrer
    :param prctDestruct: Pourcentage (maximum) de pièces à détruire
    :param maxTime: Temps maximum alloué à la recherche
    :param debug: Affichage des informations de débogage
    :param logs: Dictionnaire pour les logs
    :return: La meilleure solution trouvée et son score
    """

    startTime = time.time()
    nbRestart = 1
    scores = []

    if debug:
        print(
            Fore.BLUE + f"--------------- Début LNS avec restart meilleur - Temps restant: {maxTime} s ---------------")
        print(f" - Fonction de destruction: {destructFct.__name__}")
        print(f" - Fonction de reconstruction: {reconstructFct.__name__}")
        print(f" - Fonction d'acceptation: {acceptFct.__name__}")
        print(f" - MaxWithoutAccept: {maxWithoutAcceptOrImprove}")
        print(f" - PrctDestruct: {prctDestruct}")
        print(f" - MaxTime: {maxTime}")
        print("--------------------------------------------------------------------------------------------" +
              Style.RESET_ALL)

    # Initialisation meilleure solution
    bestSol, bestScore = getInitialSolutionAndScore(puzzle)

    while (time.time() - startTime) < maxTime and bestScore > 0:

        remainingTime = maxTime - (time.time() - startTime)

        if debug:
            print(
                Fore.BLUE + f"Restart {nbRestart} - Temps restant: {round(remainingTime, 2)} s - Score initial: {bestScore}")

        # Lancement du LNS
        currentSol, currentScore = largeNeighborhoodSearch(puzzle, bestSol, destructFct, reconstructFct,
                                                           acceptFct,
                                                           maxWithoutAcceptOrImprove=maxWithoutAcceptOrImprove,
                                                           prctDestruct=prctDestruct, remainingTime=remainingTime,
                                                           debug=debug)

        scores.append(currentScore)

        # Si on a trouvé une solution valide, on arrête
        if currentScore == 0:
            bestSol = currentSol
            bestScore = currentScore
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
        logs["Algorithm"] = "restartBestLNS"
        logs["DestructFct"] = destructFct.__name__
        logs["ReconstructFct"] = reconstructFct.__name__
        logs["AcceptFct"] = acceptFct.__name__
        logs["NbRestart"] = nbRestart
        meanScore = sum(scores) / len(scores)
        logs["MeanScore"] = round(meanScore, 4)
        stdScore = np.std(scores)
        logs["StdScore"] = round(stdScore, 4)

    return bestSol, bestScore


def restartBestAndRandom_LNS(
        puzzle: EternityPuzzle, destructFctRandom, reconstructFctRandom, acceptFctRandom,
        destructFctBest=None, reconstructFctBest=None, acceptFctBest=None,
        maxWithoutAcceptOrImprove=100, prctDestruct=None, ratioBest=0.5,
        maxTime=60., debug=False, logs=None
        ):    # sourcery skip: low-code-quality
    """
    LNS avec restart aléatoire ou avec la meilleure solution trouvée.
    :param puzzle: Instance du puzzle
    :param destructFctRandom: Fonction de destruction pour le restart aléatoire
    :param reconstructFctRandom: Fonction de reconstruction pour le restart aléatoire
    :param acceptFctRandom: Fonction d'acceptation pour le restart aléatoire
    :param destructFctBest: Fonction de destruction pour le restart avec la meilleure solution, si None, on utilise
    destructFctRandom
    :param reconstructFctBest: Fonction de reconstruction pour le restart avec la meilleure solution, si None,
    on utilise reconstructFctRandom
    :param acceptFctBest: Fonction d'acceptation pour le restart avec la meilleure solution, si None, on utilise
    acceptFctRandom
    :param maxWithoutAcceptOrImprove: Nombre maximum d'itérations sans accepter ou améliorer avant de redémarrer
    :param prctDestruct: Pourcentage (maximum) de pièces à détruire
    :param ratioBest: Ratio x de restart avec la meilleure solution, si x > 1, on fait x restarts avec la meilleure
    solution avant de faire un restart aléatoire, sinon on fait 1/x restarts aléatoires avant de faire un restart avec
    la meilleure solution.
    :param maxTime: Temps maximum alloué à la recherche
    :param debug: Affichage des informations de débogage
    :param logs: Dictionnaire pour les logs
    :return: La meilleure solution trouvée et son score
    """

    startTime = time.time()
    nbRestart = 1
    scores = []
    nbRestartBest = 0
    nbRestartRandom = 0
    nbImprovement = {"Best": 0, "Random": 0}

    if debug:
        print(Fore.BLUE + f"--------------- Début LNS avec restart Split - Temps restant: {maxTime} s ---------------")
        print(f" - Fonction de destruction Random: {destructFctRandom.__name__}")
        print(f" - Fonction de reconstruction Random: {reconstructFctRandom.__name__}")
        print(f" - Fonction d'acceptation Random: {acceptFctRandom.__name__}")
        if destructFctBest is not None:
            print(f" - Fonction de destruction Best: {destructFctBest.__name__}")
        if reconstructFctBest is not None:
            print(f" - Fonction de reconstruction Best: {reconstructFctBest.__name__}")
        if acceptFctBest is not None:
            print(f" - Fonction d'acceptation Best: {acceptFctBest.__name__}")
        print(f" - RatioBest: {ratioBest}")
        print(f" - MaxWithoutAccept: {maxWithoutAcceptOrImprove}")
        print(f" - PrctDestruct: {prctDestruct}")
        print(f" - MaxTime: {maxTime}")
        print("--------------------------------------------------------------------------------------------" +
              Style.RESET_ALL)

    # Initialisation meilleure solution
    bestSol, bestScore = getInitialSolutionAndScore(puzzle)

    # Initialisation des compteurs
    if ratioBest > 1:
        nbMaxBest = int(ratioBest)
        nbMaxRandom = 1
    else:
        nbMaxBest = 1
        nbMaxRandom = int(1 / ratioBest)

    if debug:
        print(Fore.BLUE + f"Nombre de restarts avec la meilleure solution: {nbMaxBest}")
        print(Fore.BLUE + f"Nombre de restarts aléatoires: {nbMaxRandom}")

    while (time.time() - startTime) < maxTime and bestScore > 0:

        if nbRestart % (nbMaxBest + nbMaxRandom) < nbMaxBest:  # On fait un restart avec la meilleure solution
            startingSol = bestSol
            startBest = True
            correctedMaxWithoutAcceptOrImprove = maxWithoutAcceptOrImprove * 1.5
            nbRestartBest += 1
            destructFct = destructFctBest if destructFctBest is not None else destructFctRandom
            reconstructFct = reconstructFctBest if reconstructFctBest is not None else reconstructFctRandom
            acceptFct = acceptFctBest if acceptFctBest is not None else acceptFctRandom

        else:  # On fait un restart aléatoire
            startingSol, _ = getInitialSolutionAndScore(puzzle)
            startBest = False
            correctedMaxWithoutAcceptOrImprove = maxWithoutAcceptOrImprove
            nbRestartRandom += 1
            destructFct = destructFctRandom
            reconstructFct = reconstructFctRandom
            acceptFct = acceptFctRandom

        remainingTime = maxTime - (time.time() - startTime)

        if debug:
            print(
                Fore.BLUE + f"Restart {nbRestart} - Temps restant: {round(remainingTime, 2)} s - "
                            f"Restart Best ? {startBest} - Score initial: {bestScore} \n"
                            f"Nb restart best: {nbMaxBest} - Nb restart random: {nbMaxRandom} - "
                            f"Idx restart: {nbRestart % (nbMaxBest + nbMaxRandom)}")

        # Lancement du LNS
        currentSol, currentScore = largeNeighborhoodSearch(puzzle, startingSol, destructFct, reconstructFct,
                                                           acceptFct,
                                                           maxWithoutAcceptOrImprove=correctedMaxWithoutAcceptOrImprove,
                                                           prctDestruct=prctDestruct, remainingTime=remainingTime,
                                                           debug=debug)

        scores.append(currentScore)

        # Si on a trouvé une solution valide, on arrête
        if currentScore == 0:
            bestSol = currentSol
            bestScore = currentScore
            break

        if currentScore <= bestScore:

            if currentScore < bestScore:
                if startBest:
                    nbImprovement["Best"] += 1
                else:
                    nbImprovement["Random"] += 1

            bestSol = currentSol
            bestScore = currentScore


            if debug:
                print(Fore.GREEN + f"New best score: {bestScore} - "
                                   f"Temps restant: {round(maxTime - (time.time() - startTime), 2)} s - "
                                   f"Restart {nbRestart} - Restart Best ? {startBest}")

        else:
            if debug:
                print(Fore.WHITE + f"No improvement: {currentScore} - "
                                   f"Temps restant: {round(maxTime - (time.time() - startTime), 2)} s - "
                                   f"Restart {nbRestart} - Restart Best ? {startBest}")

        nbRestart += 1

    if debug:
        print(Fore.BLUE + f"----------------- Fin LNS avec restart best et random - "
                          f"Temps écoulé: {round(time.time() - startTime, 2)} s - "
                          f"Restarts: {nbRestart} - "
                          f"Meilleur score: {bestScore}"
                          f"-----------------" + Style.RESET_ALL)

    if logs is not None:
        logs["Algorithm"] = "restartBestAndRandom_LNS"
        logs["DestructFct"] = destructFct.__name__
        logs["ReconstructFct"] = reconstructFct.__name__
        logs["AcceptFct"] = acceptFct.__name__
        logs["NbRestart"] = nbRestart
        meanScore = sum(scores) / len(scores)
        logs["MeanScore"] = round(meanScore, 4)
        stdScore = np.std(scores)
        logs["StdScore"] = round(stdScore, 4)
        logs["NbRestartBest"] = nbRestartBest
        logs["NbRestartRandom"] = nbRestartRandom
        logs["NbImprovement"] = nbImprovement

    return bestSol, bestScore
