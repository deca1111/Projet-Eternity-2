# Auteurs
# Armel Ngounou Tchawe - 2238017
# Léo Valette - 2307835


from eternity_puzzle import EternityPuzzle
from colorama import Fore, Style
import time
from solver_local_search import getInitialSolutionAndScore
import numpy as np


def ALNS(
        puzzle: EternityPuzzle, initialSolution, listDestructFct, listReconstructFct, listAcceptFct,
        updateWeights, lambda_=0.5,
        destructFctWeights=None, reconstructFctWeights=None, acceptFctWeights=None,
        maxWithoutAcceptOrImprove=100, prctDestruct=None, remainingTime=60., debug=False
        ):  # sourcery skip: low-code-quality
    """
    Adaptive Large Neighborhood Search

    LNS en faisant varier les fonctions de destruction, de reconstruction et d'acceptation selon des probabilitées qui
    évoluent au fur et à mesure des itérations.

    :param puzzle: Instance du puzzle
    :param initialSolution: Solution initiale
    :param listDestructFct: Liste des fonctions de destruction
    :param listReconstructFct: Liste des fonctions de reconstruction
    :param listAcceptFct: Liste des fonctions d'acceptation
    :param updateWeights: Poids de mise à jour des fonctions
    :param lambda_: Paramètre de sensibilité pour la mise à jour des poids
    :param destructFctWeights: Dict des poids et du nombre d'utilisations des fonctions de destruction
    :param reconstructFctWeights: Dict des poids et du nombre d'utilisations des fonctions de reconstruction
    :param acceptFctWeights: Dict des poids et du nombre d'utilisations des fonctions d'acceptation
    :param maxWithoutAcceptOrImprove: Nombre maximum d'itérations sans accepter ou améliorer avant de redémarrer
    :param prctDestruct: Pourcentage (maximum) de pièces à détruire
    :param remainingTime: Temps restant pour la recherche
    :param debug: Affichage des informations de débogage
    :return:
    """

    # Initialisation des poids des fonctions et du nombre d'utilisation des fonctions
    if destructFctWeights is None:
        destructFctWeights = {f.__name__: (1, 0) for f in listDestructFct}
    if reconstructFctWeights is None:
        reconstructFctWeights = {f.__name__: (1, 0) for f in listReconstructFct}
    if acceptFctWeights is None:
        acceptFctWeights = {f.__name__: (1, 0) for f in listAcceptFct}

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
            Fore.YELLOW + f"Début ALNS - Score initial: {currentScore} - "
                          f"Temps restant: {round(remainingTime - (time.time() - startTime), 2)} s")

    while (time.time() - startTime) < remainingTime and bestScore > 0:
        # Conversion des poids en probabilités
        totalWeightDestructFct = sum(v[0] for v in destructFctWeights.values())
        destructFctProba = [v[0] / totalWeightDestructFct for v in destructFctWeights.values()]

        totalWeightReconstructFct = sum(v[0] for v in reconstructFctWeights.values())
        reconstructFctProba = [v[0] / totalWeightReconstructFct for v in reconstructFctWeights.values()]

        totalWeightAcceptFct = sum(v[0] for v in acceptFctWeights.values())
        acceptFctProba = [v[0] / totalWeightAcceptFct for v in acceptFctWeights.values()]

        # Sélection des fonctions
        destructFct = np.random.choice(listDestructFct, p=destructFctProba)
        reconstructFct = np.random.choice(listReconstructFct, p=reconstructFctProba)
        acceptFct = np.random.choice(listAcceptFct, p=acceptFctProba)

        # Destruction
        partialSol, destroyedPieces, idxDestroyedPieces = destructFct(puzzle, currentSol, prctDestruct)

        # Réparation
        reconstructedSol = reconstructFct(puzzle, partialSol, destroyedPieces, idxDestroyedPieces)

        # Calcul du score
        reconstructedScore = puzzle.get_total_n_conflict(reconstructedSol)

        # Si on a trouvé une solution valide, on arrête
        if reconstructedScore == 0:
            bestSol = reconstructedSol
            bestScore = reconstructedScore
            break

        if acceptFct(currentScore, reconstructedScore):
            # Selection du poids de MAJ : Cas ou la nouvelle solution est meilleure que la précédente
            if reconstructedScore < currentScore:
                majWeights = updateWeights[1]
            else:
                # Selection du poids de MAJ : Cas ou la nouvelle solution est acceptée
                majWeights = updateWeights[2]

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

                # Mise à jour des poids : Cas ou la nouvelle solution est la meilleure actuellement trouvée
                majWeights = updateWeights[0]

                if debug:
                    print(Fore.BLACK + f"New best score: {bestScore} - Temps restant: "
                                       f"{round(remainingTime - (time.time() - startTime), 2)} s - Itération {idxIter}")
            else:
                nbWithoutImprovement += 1

        else:
            nbWithoutAccept += 1
            nbWithoutImprovement += 1

            # Selection du poids de MAJ : Cas ou on a pas accepté la solution
            majWeights = updateWeights[3]

        # Si on a dépassé le nombre d'itérations sans accepter ou améliorer, on s'arrête
        if nbWithoutAccept > maxWithoutAcceptOrImprove or nbWithoutImprovement > maxWithoutAcceptOrImprove:
            print(Fore.RED + f"Arrêt de l'ALNS - Nombre d'itérations dépassé - Dernier score {currentScore}" +
                  Style.RESET_ALL)
            break

        # Mise à jour des poids
        newWeightDestFct = destructFctWeights[destructFct.__name__][0] * lambda_ + (1 - lambda_) * majWeights
        newWeightReconFct = reconstructFctWeights[reconstructFct.__name__][0] * lambda_ + (1 - lambda_) * majWeights
        newWeightAcceptFct = acceptFctWeights[acceptFct.__name__][0] * lambda_ + (1 - lambda_) * majWeights

        destructFctWeights[destructFct.__name__] = (newWeightDestFct,
                                                    destructFctWeights[destructFct.__name__][1] + 1)
        reconstructFctWeights[reconstructFct.__name__] = (newWeightReconFct,
                                                          reconstructFctWeights[reconstructFct.__name__][1] + 1)
        acceptFctWeights[acceptFct.__name__] = (newWeightAcceptFct,
                                                acceptFctWeights[acceptFct.__name__][1] + 1)

        idxIter += 1

    if debug:
        print(Fore.YELLOW + f"Fin LNS - Score final: {bestScore} - Temps écoulé: {round(time.time() - startTime, 2)} s "
                            f"- Itérations: {idxIter}" + Style.RESET_ALL)

    return bestSol, bestScore


def restartALNS(
        puzzle: EternityPuzzle, listDestructFct, listReconstructFct, listAcceptFct,
        updateWeights, lambda_=0.5,
        maxWithoutAcceptOrImprove=100, prctDestruct=None, maxTime=60., debug=False, logs=None
        ):  # sourcery skip: low-code-quality
    """
    Adaptive Large Neighborhood Search avec redémarrage

    LNS en faisant varier les fonctions de destruction, de reconstruction et d'acceptation selon des probabilitées qui
    évoluent au fur et à mesure des itérations.

    :param puzzle: Instance du puzzle
    :param listDestructFct: Liste des fonctions de destruction
    :param listReconstructFct: Liste des fonctions de reconstruction
    :param listAcceptFct: Liste des fonctions d'acceptation
    :param updateWeights: Poids de mise à jour des fonctions
    :param lambda_: Paramètre de sensibilité pour la mise à jour des poids
    :param maxWithoutAcceptOrImprove: Nombre maximum d'itérations sans accepter ou améliorer avant de redémarrer
    :param prctDestruct: Pourcentage (maximum) de pièces à détruire
    :param maxTime: Temps maximum alloué pour la recherche
    :param debug: Affichage des informations de débogage
    :param logs: Dictionnaire de logs
    :return:
    """

    # Initialisation des poids des fonctions et du nombre d'utilisation des fonctions
    destructFctWeights = {f.__name__: (1, 0) for f in listDestructFct}
    reconstructFctWeights = {f.__name__: (1, 0) for f in listReconstructFct}
    acceptFctWeights = {f.__name__: (1, 0) for f in listAcceptFct}

    startTime = time.time()
    nbRestart = 1
    scores = []

    if debug:
        print(Fore.BLUE + f"----------------- Début ALNS avec restart - Temps restant: {maxTime} s -----------------")
        print(f" - Fonctions de destruction: {[f.__name__ for f in listDestructFct]}")
        print(f" - Fonctions de reconstruction: {[f.__name__ for f in listReconstructFct]}")
        print(f" - Fonctions d'acceptation: {[f.__name__ for f in listAcceptFct]}")
        print(f" - Poids de mise à jour: {updateWeights}")
        print(f" - Paramètre lambda: {lambda_}")
        print(f" - MaxWithoutAcceptOrImprove: {maxWithoutAcceptOrImprove}")
        print(f" - PrctDestruct: {prctDestruct}")
        print(f" - Temps maximum: {maxTime}")
        print("----------------------------------------------------------------------------------------" +
              Style.RESET_ALL)

    # Initialisation meilleure solution
    bestSol, bestScore = getInitialSolutionAndScore(puzzle)

    while (time.time() - startTime) < maxTime and bestScore > 0:
        # Génération d'une solution initiale
        initialSolution, initialScore = getInitialSolutionAndScore(puzzle)

        remainingTime = maxTime - (time.time() - startTime)

        if debug:
            print(Fore.BLUE + f"Restart {nbRestart} - Temps restant: {round(remainingTime, 2)} s "
                              f"- Score initial: {initialScore}")

        # Lancement de l'ALNS
        currentSol, currentScore = ALNS(puzzle, initialSolution, listDestructFct, listReconstructFct, listAcceptFct,
                                        updateWeights, lambda_,
                                        destructFctWeights, reconstructFctWeights, acceptFctWeights,
                                        maxWithoutAcceptOrImprove=maxWithoutAcceptOrImprove, prctDestruct=prctDestruct,
                                        remainingTime=remainingTime, debug=debug)

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
        print(Fore.BLUE + f"----------------- Fin ALNS avec restart - "
                          f"Temps écoulé: {round(time.time() - startTime, 2)} s - "
                          f"Restarts: {nbRestart} - "
                          f"Meilleur score: {bestScore}" + Style.RESET_ALL)

    if logs is not None:
        logs["Algorithm"] = "restartALNS"
        logs["NbRestart"] = nbRestart
        if len(scores) > 0:
            meanScore = sum(scores) / len(scores)
            logs["MeanScore"] = round(meanScore, 4)
            stdScore = np.std(scores)
            logs["StdScore"] = round(stdScore, 4)
        logs["FinalWeights"] = {
            "DestructFct": {k: round(v[0], 2) for k, v in destructFctWeights.items()},
            "ReconstructFct": {k: round(v[0], 2) for k, v in reconstructFctWeights.items()},
            "AcceptFct": {k: round(v[0], 2) for k, v in acceptFctWeights.items()}
            }
        logs["NbUsedFct"] = {
            "DestructFct": {k: v[1] for k, v in destructFctWeights.items()},
            "ReconstructFct": {k: v[1] for k, v in reconstructFctWeights.items()},
            "AcceptFct": {k: v[1] for k, v in acceptFctWeights.items()}
            }
        nbTotalIter = sum(v[1] for v in destructFctWeights.values())
        logs["NbTotalIter"] = nbTotalIter
        if nbTotalIter > 0:
            logs["%UsageFct"] = {
                "DestructFct": {k: round(v[1] / nbTotalIter, 2) for k, v in destructFctWeights.items()},
                "ReconstructFct": {k: round(v[1] / nbTotalIter, 2) for k, v in reconstructFctWeights.items()},
                "AcceptFct": {k: round(v[1] / nbTotalIter, 2) for k, v in acceptFctWeights.items()}
                }

    return bestSol, bestScore


def restartBestALNS(
        puzzle: EternityPuzzle, listDestructFct, listReconstructFct, listAcceptFct,
        updateWeights, lambda_=0.5,
        maxWithoutAcceptOrImprove=100, prctDestruct=None, maxTime=60., debug=False, logs=None
        ):  # sourcery skip: low-code-quality
    """
    Adaptive Large Neighborhood Search avec redémarrage depuis la meilleure solution trouvée

    LNS en faisant varier les fonctions de destruction, de reconstruction et d'acceptation selon des probabilitées qui
    évoluent au fur et à mesure des itérations.

    :param puzzle: Instance du puzzle
    :param listDestructFct: Liste des fonctions de destruction
    :param listReconstructFct: Liste des fonctions de reconstruction
    :param listAcceptFct: Liste des fonctions d'acceptation
    :param updateWeights: Poids de mise à jour des fonctions
    :param lambda_: Paramètre de sensibilité pour la mise à jour des poids
    :param maxWithoutAcceptOrImprove: Nombre maximum d'itérations sans accepter ou améliorer avant de redémarrer
    :param prctDestruct: Pourcentage (maximum) de pièces à détruire
    :param maxTime: Temps maximum alloué pour la recherche
    :param debug: Affichage des informations de débogage
    :param logs: Dictionnaire de logs
    :return:
    """

    # Initialisation des poids des fonctions et du nombre d'utilisation des fonctions
    destructFctWeights = {f.__name__: (1, 0) for f in listDestructFct}
    reconstructFctWeights = {f.__name__: (1, 0) for f in listReconstructFct}
    acceptFctWeights = {f.__name__: (1, 0) for f in listAcceptFct}

    startTime = time.time()
    nbRestart = 1
    scores = []

    if debug:
        print(
            Fore.BLUE + f"----------------- Début ALNS avec restart meilleur - Temps restant: {maxTime} s -----------------")
        print(f" - Fonctions de destruction: {[f.__name__ for f in listDestructFct]}")
        print(f" - Fonctions de reconstruction: {[f.__name__ for f in listReconstructFct]}")
        print(f" - Fonctions d'acceptation: {[f.__name__ for f in listAcceptFct]}")
        print(f" - Poids de mise à jour: {updateWeights}")
        print(f" - Paramètre lambda: {lambda_}")
        print(f" - MaxWithoutAcceptOrImprove: {maxWithoutAcceptOrImprove}")
        print(f" - PrctDestruct: {prctDestruct}")
        print(f" - Temps maximum: {maxTime}")
        print("----------------------------------------------------------------------------------------" +
              Style.RESET_ALL)

    # Initialisation meilleure solution
    bestSol, bestScore = getInitialSolutionAndScore(puzzle)

    while (time.time() - startTime) < maxTime and bestScore > 0:

        remainingTime = maxTime - (time.time() - startTime)

        if debug:
            print(Fore.BLUE + f"Restart {nbRestart} - Temps restant: {round(remainingTime, 2)} s "
                              f"- Score initial: {bestScore}")

        # Lancement de l'ALNS
        currentSol, currentScore = ALNS(puzzle, bestSol, listDestructFct, listReconstructFct, listAcceptFct,
                                        updateWeights, lambda_,
                                        destructFctWeights, reconstructFctWeights, acceptFctWeights,
                                        maxWithoutAcceptOrImprove=maxWithoutAcceptOrImprove, prctDestruct=prctDestruct,
                                        remainingTime=remainingTime, debug=debug)

        scores.append(currentScore)

        # Si on a trouvé une solution valide, on arrête
        if currentScore == 0:
            bestSol = currentSol
            bestScore = currentScore
            break

        if currentScore <= bestScore:
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
        print(Fore.BLUE + f"----------------- Fin ALNS avec restart - "
                          f"Temps écoulé: {round(time.time() - startTime, 2)} s - "
                          f"Restarts: {nbRestart} - "
                          f"Meilleur score: {bestScore}" + Style.RESET_ALL)

    if logs is not None:
        logs["Algorithm"] = "restartBestALNS"
        logs["NbRestart"] = nbRestart
        if len(scores) > 0:
            meanScore = sum(scores) / len(scores)
            logs["MeanScore"] = round(meanScore, 4)
            stdScore = np.std(scores)
            logs["StdScore"] = round(stdScore, 4)
        logs["FinalWeights"] = {
            "DestructFct": {k: round(v[0], 2) for k, v in destructFctWeights.items()},
            "ReconstructFct": {k: round(v[0], 2) for k, v in reconstructFctWeights.items()},
            "AcceptFct": {k: round(v[0], 2) for k, v in acceptFctWeights.items()}
            }
        logs["NbUsedFct"] = {
            "DestructFct": {k: v[1] for k, v in destructFctWeights.items()},
            "ReconstructFct": {k: v[1] for k, v in reconstructFctWeights.items()},
            "AcceptFct": {k: v[1] for k, v in acceptFctWeights.items()}
            }
        nbTotalIter = sum(v[1] for v in destructFctWeights.values())
        logs["NbTotalIter"] = nbTotalIter
        if nbTotalIter > 0:
            logs["%UsageFct"] = {
                "DestructFct": {k: round(v[1] / nbTotalIter, 2) for k, v in destructFctWeights.items()},
                "ReconstructFct": {k: round(v[1] / nbTotalIter, 2) for k, v in reconstructFctWeights.items()},
                "AcceptFct": {k: round(v[1] / nbTotalIter, 2) for k, v in acceptFctWeights.items()}
                }

    return bestSol, bestScore


def restartBestAndRandom_ALNS(
        puzzle: EternityPuzzle, listDestructFctRandom, listReconstructFctRandom, listAcceptFctRandom,
        listDestructFctBest=None, listReconstructFctBest=None, listAcceptFctBest=None,
        updateWeights=None, lambda_=0.9, ratioBest=0.5,
        maxWithoutAcceptOrImprove=100, prctDestruct=None, maxTime=60., debug=False, logs=None
        ):  # sourcery skip: low-code-quality
    """
    Adaptive Large Neighborhood Search avec redémarrage aléatoire ou avec la meilleure solution trouvée.

    LNS en faisant varier les fonctions de destruction, de reconstruction et d'acceptation selon des probabilitées qui
    évoluent au fur et à mesure des itérations.

    :param puzzle: Instance du puzzle
    :param listDestructFctRandom: Liste des fonctions de destruction pour les redémarrages aléatoires
    :param listReconstructFctRandom: Liste des fonctions de reconstruction pour les redémarrages aléatoires
    :param listAcceptFctRandom: Liste des fonctions d'acceptation pour les redémarrages aléatoires
    :param listDestructFctBest: Liste des fonctions de destruction pour les redémarrages depuis la meilleure solution
    :param listReconstructFctBest: Liste des fonctions de reconstruction pour les redémarrages depuis la meilleure solution
    :param listAcceptFctBest: Liste des fonctions d'acceptation pour les redémarrages depuis la meilleure solution
    :param updateWeights: Poids de mise à jour des fonctions
    :param lambda_: Paramètre de sensibilité pour la mise à jour des poids
    :param ratioBest: Ratio de probabilité de choisir la meilleure solution
    :param maxWithoutAcceptOrImprove: Nombre maximum d'itérations sans accepter ou améliorer avant de redémarrer
    :param prctDestruct: Pourcentage (maximum) de pièces à détruire
    :param maxTime: Temps maximum alloué pour la recherche
    :param debug: Affichage des informations de débogage
    :param logs: Dictionnaire de logs
    :return:
    """

    # Initialisation des poids des fonctions et du nombre d'utilisation des fonctions
    destructFctRandomWeights = {f.__name__: (1, 0) for f in listDestructFctRandom}
    reconstructFctRandomWeights = {f.__name__: (1, 0) for f in listReconstructFctRandom}
    acceptFctRandomWeights = {f.__name__: (1, 0) for f in listAcceptFctRandom}
    if listDestructFctBest is not None:
        destructFctBestWeights = {f.__name__: (1, 0) for f in listDestructFctBest}
    if listReconstructFctBest is not None:
        reconstructFctBestWeights = {f.__name__: (1, 0) for f in listReconstructFctBest}
    if listAcceptFctBest is not None:
        acceptFctBestWeights = {f.__name__: (1, 0) for f in listAcceptFctBest}

    if updateWeights is None:
        updateWeights = [1000, 200, 25, 1]

    startTime = time.time()
    nbRestart = 1
    scores = {"best": [], "random": []}
    nbRestartBest = 0
    nbRestartRandom = 0
    nbImprovement = {"Best": 0, "Random": 0}

    if debug:
        print(
            Fore.BLUE + f"----------------- Début ALNS avec restart meilleur - Temps restant: {maxTime} s -----------------")
        print(f" - Fonctions de destruction (Random): {[f.__name__ for f in listDestructFctRandom]}")
        print(f" - Fonctions de reconstruction (Random): {[f.__name__ for f in listReconstructFctRandom]}")
        print(f" - Fonctions d'acceptation (Random): {[f.__name__ for f in listAcceptFctRandom]}")
        if listDestructFctBest is not None:
            print(f" - Fonctions de destruction (Best): {[f.__name__ for f in listDestructFctBest]}")
        if listReconstructFctBest is not None:
            print(f" - Fonctions de reconstruction (Best): {[f.__name__ for f in listReconstructFctBest]}")
        if listAcceptFctBest is not None:
            print(f" - Fonctions d'acceptation (Best): {[f.__name__ for f in listAcceptFctBest]}")
        print(f" - Poids de mise à jour: {updateWeights}")
        print(f" - Paramètre lambda: {lambda_}")
        print(f" - RatioBest: {ratioBest}")
        print(f" - MaxWithoutAcceptOrImprove: {maxWithoutAcceptOrImprove}")
        print(f" - PrctDestruct: {prctDestruct}")
        print(f" - Temps maximum: {maxTime}")
        print("----------------------------------------------------------------------------------------" +
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
            if listDestructFctBest is not None:
                listDestructFct = listDestructFctBest
                destructFctWeights = destructFctBestWeights
            else:
                listDestructFct = listDestructFctRandom
                destructFctWeights = destructFctRandomWeights
            if listReconstructFctBest is not None:
                listReconstructFct = listReconstructFctBest
                reconstructFctWeights = reconstructFctBestWeights
            else:
                listReconstructFct = listReconstructFctRandom
                reconstructFctWeights = reconstructFctRandomWeights
            if listAcceptFctBest is not None:
                listAcceptFct = listAcceptFctBest
                acceptFctWeights = acceptFctBestWeights
            else:
                listAcceptFct = listAcceptFctRandom
                acceptFctWeights = acceptFctRandomWeights

        else:  # On fait un restart aléatoire
            startingSol, _ = getInitialSolutionAndScore(puzzle)
            startBest = False
            correctedMaxWithoutAcceptOrImprove = maxWithoutAcceptOrImprove
            nbRestartRandom += 1
            listDestructFct = listDestructFctRandom
            listReconstructFct = listReconstructFctRandom
            listAcceptFct = listAcceptFctRandom
            destructFctWeights = destructFctRandomWeights
            reconstructFctWeights = reconstructFctRandomWeights
            acceptFctWeights = acceptFctRandomWeights

        remainingTime = maxTime - (time.time() - startTime)

        if debug:
            print(Fore.BLUE + f"Restart {nbRestart} - Temps restant: {round(remainingTime, 2)} s "
                              f"- Restart Best ? {startBest}- Score initial: {bestScore}\n"
                              f"Nb restart best: {nbMaxBest} - Nb restart random: {nbMaxRandom} - "
                              f"Idx restart: {nbRestart % (nbMaxBest + nbMaxRandom)}")

        # Lancement de l'ALNS
        currentSol, currentScore = ALNS(puzzle, startingSol, listDestructFct, listReconstructFct, listAcceptFct,
                                        updateWeights, lambda_,
                                        destructFctWeights, reconstructFctWeights, acceptFctWeights,
                                        maxWithoutAcceptOrImprove=correctedMaxWithoutAcceptOrImprove,
                                        prctDestruct=prctDestruct, remainingTime=remainingTime, debug=debug)

        if startBest:
            scores["best"].append(currentScore)
        else:
            scores["random"].append(currentScore)

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
        print(Fore.BLUE + f"----------------- Fin ALNS avec restart best et random- "
                          f"Temps écoulé: {round(time.time() - startTime, 2)} s - "
                          f"Restarts: {nbRestart} - "
                          f"Meilleur score: {bestScore}"
                          f"-----------------" + Style.RESET_ALL)

    if logs is not None:
        logs["Algorithm"] = "restartBestAndRandom_ALNS"
        logs["NbRestart"] = nbRestart
        if len(scores["best"]) > 0:
            meanScoreBest = sum(scores["best"]) / len(scores["best"])
            logs["MeanScoreBest"] = round(meanScoreBest, 4)
            stdScoreBest = np.std(scores["best"])
            logs["StdScoreBest"] = round(stdScoreBest, 4)
        if len(scores["random"]) > 0:
            meanScoreRandom = sum(scores["random"]) / len(scores["random"])
            logs["MeanScoreRandom"] = round(meanScoreRandom, 4)
            stdScoreRandom = np.std(scores["random"])
            logs["StdScoreRandom"] = round(stdScoreRandom, 4)
        logs["FinalWeightsRandom"] = {
            "DestructFct": {k: round(v[0], 2) for k, v in destructFctRandomWeights.items()},
            "ReconstructFct": {k: round(v[0], 2) for k, v in reconstructFctRandomWeights.items()},
            "AcceptFct": {k: round(v[0], 2) for k, v in acceptFctRandomWeights.items()}
            }
        logs["NbUsedFctRandom"] = {
            "DestructFct": {k: v[1] for k, v in destructFctRandomWeights.items()},
            "ReconstructFct": {k: v[1] for k, v in reconstructFctRandomWeights.items()},
            "AcceptFct": {k: v[1] for k, v in acceptFctRandomWeights.items()}
            }
        if listDestructFctBest is not None and listReconstructFctBest is not None and listAcceptFctBest is not None:
            logs["FinalWeightsBest"] = {
                "DestructFct": {k: round(v[0], 2) for k, v in destructFctBestWeights.items()},
                "ReconstructFct": {k: round(v[0], 2) for k, v in reconstructFctBestWeights.items()},
                "AcceptFct": {k: round(v[0], 2) for k, v in acceptFctBestWeights.items()}
                }
            logs["NbUsedFctBest"] = {
                "DestructFct": {k: v[1] for k, v in destructFctBestWeights.items()},
                "ReconstructFct": {k: v[1] for k, v in reconstructFctBestWeights.items()},
                "AcceptFct": {k: v[1] for k, v in acceptFctBestWeights.items()}
                }
        nbTotalIterRandom = sum(v[1] for v in destructFctRandomWeights.values())
        nbTotalIterBest = sum(v[1] for v in destructFctBestWeights.values())
        nbTotalIter = nbTotalIterRandom + nbTotalIterBest
        logs["NbTotalIterRandom"] = nbTotalIterRandom
        logs["NbTotalIterBest"] = nbTotalIterBest
        logs["NbTotalIter"] = nbTotalIter
        if nbTotalIterRandom > 0:
            logs["%UsageFctRandom"] = {
                "DestructFct": {k: round(v[1] / nbTotalIterRandom, 2) for k, v in destructFctRandomWeights.items()},
                "ReconstructFct": {k: round(v[1] / nbTotalIterRandom, 2) for k, v in reconstructFctRandomWeights.items()},
                "AcceptFct": {k: round(v[1] / nbTotalIterRandom, 2) for k, v in acceptFctRandomWeights.items()}
                }
        if (listDestructFctBest is not None and listReconstructFctBest is not None and listAcceptFctBest is not None and
                nbTotalIterBest > 0):
            logs["%UsageFctBest"] = {
                "DestructFct": {k: round(v[1] / nbTotalIterBest, 2) for k, v in destructFctBestWeights.items()},
                "ReconstructFct": {k: round(v[1] / nbTotalIterBest, 2) for k, v in reconstructFctBestWeights.items()},
                "AcceptFct": {k: round(v[1] / nbTotalIterBest, 2) for k, v in acceptFctBestWeights.items()}
                }
        logs["NbRestartBest"] = nbRestartBest
        logs["NbRestartRandom"] = nbRestartRandom
        logs["NbImprovement"] = nbImprovement

    return bestSol, bestScore
