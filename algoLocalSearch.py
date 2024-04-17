import math
import random
import time
from typing import Tuple, List

from utils import (getRandomSolution, getMatrixFromList, getConflictPieces, selectWithNbConflict, getEdgeIndexes,
                   printGridIndexes, getAngleIndexes)
from eternity_puzzle import EternityPuzzle
import itertools
from algoHeuristic import solverHeuristique1DeepEdgeFirstV2
from heuristiques import heuristicNbConflictPieceV3, heuristicNbConflictPieceV1

NORTH = 0
SOUTH = 1
WEST = 2
EAST = 3

GRAY = 0


def solverLSNaive(eternityPuzzle: EternityPuzzle, maxTime, goodStart=False) -> Tuple[List[Tuple[int]], int]:
    """
    Algorithme de recherche locale avec un démarrage aléatoire ou un bon départ généré par un algorithme basé sur une
    heuristique.
    La selection des voisins se fait en comptant le nombre de conflits total.
    :param eternityPuzzle:
    :param maxTime:
    :param goodStart:
    """
    # Calcul du temps
    startTime = time.time()
    curentTime = time.time() - startTime

    bestSolution = None
    bestCost = (eternityPuzzle.board_size ** 2 + eternityPuzzle.board_size) * 2

    if goodStart:
        currentSolution, currentCost = solverHeuristique1DeepEdgeFirstV2(eternityPuzzle, heuristicNbConflictPieceV3)
    else:
        currentSolution = getRandomSolution(eternityPuzzle)
        currentCost = eternityPuzzle.get_total_n_conflict(currentSolution)

    print(f"First best cost : {bestCost}")
    print(f"Coût initial : {currentCost}")

    while curentTime < maxTime and currentCost > 0:
        if voisinage := getVoisinageAllPermutAndRotations(eternityPuzzle, currentSolution):

            currentSolution = min(voisinage, key=eternityPuzzle.get_total_n_conflict)
            currentCost = eternityPuzzle.get_total_n_conflict(currentSolution)

            if currentCost < bestCost:
                bestSolution = currentSolution
                bestCost = currentCost
                print(f"Nouveau meilleur coût : {bestCost}")

            curentTime = time.time() - startTime
        else:
            break

    print(f"Éxecution terminée en {round(curentTime, 4)} secondes")

    return bestSolution, bestCost


def localSearch(
        eternityPuzzle: EternityPuzzle, startingSol, voisinageFct, selectFct, costFct, remainingTime=60,
        debug=False, maxNbWithoutImprovement=15, logs=None
        ) -> Tuple[List[Tuple[int]], int]:
    # sourcery skip: low-code-quality
    """
    Algorithme de recherche locale générique.
    :param eternityPuzzle: Instance du problème
    :param startingSol: Solution de départ
    :param voisinageFct: Fonction de génération du voisinage
    :param selectFct: Fonction de sélection du voisin
    :param costFct: Fonction de coût
    :param remainingTime: Temps restant pour l'exécution
    :param debug: Affichage des logs
    :param maxNbWithoutImprovement: Nombre d'itérations sans amélioration avant d'arrêter
    :param logs: Logs à ajouter
    :return: Tuple (meilleure solution, coût de la meilleure solution)
    """

    # Calcul du temps
    startTime = time.time()

    currentSolution = startingSol
    currentCost = costFct(currentSolution)
    bestSolution = currentSolution
    bestCost = currentCost

    idxIter = 1

    nbWithoutImprovement = 0

    if logs is not None:
        if "voisinageFct" not in logs:
            logs["voisinageFct"] = voisinageFct.__name__
        if "selectFct" not in logs:
            logs["selectFct"] = selectFct.__name__
        if "costFct" not in logs:
            logs["costFct"] = costFct.__name__

    if debug:
        print(f"Coût initial : {currentCost}")

    if currentCost == 0:
        return currentSolution, currentCost

    while currentCost > 0 and (time.time() - startTime) < remainingTime:
        # Génération du voisinage
        voisinage = voisinageFct(eternityPuzzle, currentSolution)

        currentSolution = selectFct(eternityPuzzle, voisinage, currentSolution)

        # Si on ne trouve pas de voisin améliorant, on arrête
        if currentSolution is None:
            break

        currentCost = costFct(currentSolution)

        if currentCost < bestCost:
            bestSolution = currentSolution
            bestCost = currentCost
            nbWithoutImprovement = 0
            if debug:
                print(f"Nouveau meilleur coût : {bestCost} - "
                      f"Temps restant: {round(remainingTime - (time.time() - startTime), 2)} s - "
                      f"Iteration: {idxIter}")
        else:
            nbWithoutImprovement += 1

            # Si on atteint le nombre d'itérations sans amélioration, on arrête
            if nbWithoutImprovement >= maxNbWithoutImprovement:
                if debug:
                    print(f"Nombre d'itérations max sans amélioration atteint ({maxNbWithoutImprovement}) - "
                          f"Final score {currentCost} - "
                          f"Total iteration: {idxIter}")
                break

        idxIter += 1

    if logs is not None:
        if "nbIter" in logs:
            logs["nbIter"] += idxIter
        else:
            logs["nbIter"] = idxIter

    return bestSolution, bestCost


def simulatedAnnealing(
        eternityPuzzle: EternityPuzzle, startingSol, initialTemp, tauxDecroissance,
        maxWithoutImprovement=100, remainingTime=60, debug=False
        ) -> Tuple[List[Tuple[int]], int]:  # sourcery skip: low-code-quality
    # Initialisation
    currentSolution = startingSol
    currentCost = eternityPuzzle.get_total_n_conflict(startingSol)
    bestSolution = currentSolution
    bestCost = currentCost
    startTime = time.time()
    nbTryWithoutImprovement = 0

    idxIter = 1
    nbChosenSol = 0

    tailleVoisinage = 0

    if debug:
        print(
            f"Début simulated annealing - Temps restant: {round(remainingTime, 2)} s - "
            f"Coût initial: {bestCost} - Température initiale: {initialTemp}")

    temperature = initialTemp

    # Tant qu'il reste du temps, on continue
    while (time.time() - startTime) < remainingTime and bestCost > 0:

        voisinage = getVoisinageOnlyConflictV2(eternityPuzzle, currentSolution)

        tailleVoisinage += len(voisinage)

        # Séléction d'un voisin aléatoire
        chosenSol = random.choice(voisinage)
        chosenCost = eternityPuzzle.get_total_n_conflict(chosenSol)

        delta = chosenCost - currentCost

        # Si le voisin est meilleur, on le garde
        if delta < 0:
            currentSolution = chosenSol
            currentCost = chosenCost
        else:
            # Si le voisin est moins bon, on le garde avec une probabilité
            proba = math.exp(-delta / temperature)
            if random.random() < proba:
                currentSolution = chosenSol
                currentCost = chosenCost
                nbChosenSol += 1

        # Mise à jour de la meilleure solution
        if currentCost < bestCost:
            bestSolution = currentSolution
            bestCost = currentCost
            nbTryWithoutImprovement = 0
            if debug:
                print(
                    f"New best cost: {bestCost} - Temperature: {round(temperature, 3)} - "
                    f"Remaining time: {round(remainingTime - (time.time() - startTime), 2)} s - "
                    f"Iteration: {idxIter} - Taille moyenne du voisinage: {tailleVoisinage / idxIter}")

        # Si on améliore pas au bout, on augmente le nombre d'essais sans amélioration
        else:
            nbTryWithoutImprovement += 1

            # Si on atteint le nombre d'essais sans amélioration, on arrête
            if nbTryWithoutImprovement >= maxWithoutImprovement:
                if debug:
                    print(
                        f"Nombre d'essais max sans amélioration atteint ({maxWithoutImprovement}) - "
                        f"Final score {currentCost} - Temperature: {temperature} - Total iteration: {idxIter} - "
                        f"Taille moyenne du voisinage: {tailleVoisinage / idxIter} - "
                        f"% chosen sol: {nbChosenSol / idxIter}")
                break

        # Mise à jour de la température
        temperature *= tauxDecroissance

        idxIter += 1

    return bestSolution, bestCost


def getVoisinageAllPermutAndRotations(eternityPuzzle: EternityPuzzle, solution: List[Tuple[int]]) -> \
        List[List[Tuple[int]]]:
    """
    Retourne tous les voisins permis par la permutation de 2 pièces et toutes leurs rotations.
    :param eternityPuzzle:
    :param solution:
    :return:
    """
    # Génération de toutes les combinaisons possibles de swap
    listSwap = list(itertools.combinations(range(len(solution)), 2))

    voisinage = []
    for swap in listSwap:
        # Génération de toutes les rotations possibles pour les 2 pièces
        rotationPiece1 = eternityPuzzle.generate_rotation(solution[swap[0]])
        rotationPiece2 = eternityPuzzle.generate_rotation(solution[swap[1]])
        for piece1 in rotationPiece1:
            for piece2 in rotationPiece2:
                # On effectue le swap et on retourne la solution
                newSolution = solution.copy()
                newSolution[swap[0]] = piece2
                newSolution[swap[1]] = piece1
                # On ajoute la solution à la liste des voisins
                voisinage.append(newSolution)

    # print(f"Nombre de voisins : {len(voisinage)}")
    return voisinage


def getVoisinageOnlyConflictV1(eternityPuzzle: EternityPuzzle, solution: List[Tuple[int]]) -> List[List[Tuple[int]]]:
    """
    Retourne les voisins dont la permutation comporte un conflit parmis toutes les permutations et les rotations
    possibles.
    :param eternityPuzzle:
    :param solution:
    :return:
    """
    # Génération de toutes les pièces comportant un conflit
    pieceInConflict = getConflictPieces(eternityPuzzle, solution)

    # print(f"Nombre de pièces en conflit : {len(pieceInConflict)}")

    voisinage = []
    for swap in itertools.combinations(range(len(solution)), 2):
        # On vérifie si les pièces en conflit sont dans le swap
        if swap[0] in pieceInConflict or swap[1] in pieceInConflict:
            # Génération de toutes les rotations possibles pour les 2 pièces
            rotationPiece1 = eternityPuzzle.generate_rotation(solution[swap[0]])
            rotationPiece2 = eternityPuzzle.generate_rotation(solution[swap[1]])
            for piece1 in rotationPiece1:
                for piece2 in rotationPiece2:
                    # On effectue le swap et on retourne la solution
                    newSolution = solution.copy()
                    newSolution[swap[0]] = piece2
                    newSolution[swap[1]] = piece1
                    # On ajoute la solution à la liste des voisins
                    voisinage.append(newSolution)

    # print(f"Nombre de voisins : {len(voisinage)}")
    return voisinage


def getVoisinageOnlyConflictV2(eternityPuzzle: EternityPuzzle, solution: List[Tuple[int]]) -> List[List[Tuple[int]]]:
    """
    Ajout par rapport à V1:
    - + de contrainte sur les bords, si une pièce contient du gris on ne peut la swap que dans une postion avec le
        gris vers le bord.

    :param eternityPuzzle:
    :param solution:
    :return:
    """
    # Génération de toutes les pièces comportant un conflit
    pieceInConflict = getConflictPieces(eternityPuzzle, solution)

    voisinage = []
    for swap in itertools.combinations(range(len(solution)), 2):
        # Verification conflit
        if swap[0] in pieceInConflict or swap[1] in pieceInConflict:

            rotationPiece1 = generatePossibleRotationForSwap(eternityPuzzle, solution, swap[0], swap[1])
            rotationPiece2 = generatePossibleRotationForSwap(eternityPuzzle, solution, swap[1], swap[0])

            for piece1 in rotationPiece1:
                for piece2 in rotationPiece2:
                    # On effectue le swap et on retourne la solution
                    newSolution = solution.copy()
                    newSolution[swap[0]] = piece2
                    newSolution[swap[1]] = piece1
                    # On ajoute la solution à la liste des voisins
                    voisinage.append(newSolution)
                    # if swap[0] == 0 or swap[1] == 0:
                    #     print(f"Swap {swap[0]} <-> {swap[1]}")
                    #     print(f"{piece1} <-> {piece2}")

    # mélange du voisinage
    random.shuffle(voisinage)

    return voisinage


def generatePossibleRotationForSwap(eternityPuzzle: EternityPuzzle, solution, idxPiece1, idxPiece2):
    # sourcery skip: low-code-quality
    piece1 = solution[idxPiece1]

    edgesIndexes = getEdgeIndexes(eternityPuzzle)
    anglesIndexes = getAngleIndexes(eternityPuzzle)

    # Cas ou la piece à déplacer est un angle -> on ne peut la déplacer que dans un angle est qu'avec 1 seule bonne
    # rotation
    if piece1.count(GRAY) == 2:

        # Cas ou la pièce 2 est située dans un angle, on génère la seule rotation possible
        # Cas angle Sud-Ouest
        if idxPiece2 == anglesIndexes[0]:
            if piece1[SOUTH] == GRAY and piece1[WEST] == GRAY:
                return [piece1]
            elif piece1[SOUTH] == GRAY and piece1[EAST] == GRAY:
                return [(piece1[2], piece1[3], piece1[1], piece1[0])]
            elif piece1[NORTH] == GRAY and piece1[WEST] == GRAY:
                return [(piece1[3], piece1[2], piece1[0], piece1[1])]
            else:
                return [(piece1[1], piece1[0], piece1[3], piece1[2])]

        # Cas angle Nord-Ouest
        elif idxPiece2 == anglesIndexes[1]:
            if piece1[NORTH] == GRAY and piece1[WEST] == GRAY:
                return [piece1]
            elif piece1[NORTH] == GRAY and piece1[EAST] == GRAY:
                return [(piece1[3], piece1[2], piece1[0], piece1[1])]
            elif piece1[SOUTH] == GRAY and piece1[WEST] == GRAY:
                return [(piece1[2], piece1[3], piece1[1], piece1[0])]
            else:
                return [(piece1[1], piece1[0], piece1[3], piece1[2])]

        # Cas angle Nord-Est
        elif idxPiece2 == anglesIndexes[2]:
            if piece1[NORTH] == GRAY and piece1[EAST] == GRAY:
                return [piece1]
            elif piece1[NORTH] == GRAY and piece1[WEST] == GRAY:
                return [(piece1[2], piece1[3], piece1[1], piece1[0])]
            elif piece1[SOUTH] == GRAY and piece1[EAST] == GRAY:
                return [(piece1[3], piece1[2], piece1[0], piece1[1])]
            else:
                return [(piece1[1], piece1[0], piece1[3], piece1[2])]

        # Cas angle Sud-Est
        elif idxPiece2 == anglesIndexes[3]:
            if piece1[SOUTH] == GRAY and piece1[EAST] == GRAY:
                return [piece1]
            elif piece1[SOUTH] == GRAY and piece1[WEST] == GRAY:
                return [(piece1[3], piece1[2], piece1[0], piece1[1])]
            elif piece1[NORTH] == GRAY and piece1[EAST] == GRAY:
                return [(piece1[2], piece1[3], piece1[1], piece1[0])]
            else:
                return [(piece1[1], piece1[0], piece1[3], piece1[2])]

        # Cas ou la pièce 2 n'est pas située dans un angle
        else:
            # On ne peut pas déplacer un angle dans une pièce qui n'est pas un angle
            return []

    # Cas ou la pièce à déplacer est un bord -> on ne peut la déplacer que dans un bord et qu'avec 1 seule bonne
    # rotation
    elif piece1.count(GRAY) == 1:

        # Cas ou la piece 2 est dans un angle, on ne peut donc pas la déplacer
        if idxPiece2 in anglesIndexes:
            return []

        # Cas ou la pièce 2 est un bord sud
        elif idxPiece2 in edgesIndexes[0]:
            if piece1[SOUTH] == GRAY:
                return [piece1]
            elif piece1[WEST] == GRAY:
                return [(piece1[3], piece1[2], piece1[0], piece1[1])]
            elif piece1[EAST] == GRAY:
                return [(piece1[2], piece1[3], piece1[1], piece1[0])]
            else:
                return [(piece1[1], piece1[0], piece1[3], piece1[2])]

        # Cas ou la pièce 2 est un bord ouest
        elif idxPiece2 in edgesIndexes[1]:
            if piece1[WEST] == GRAY:
                return [piece1]
            elif piece1[NORTH] == GRAY:
                return [(piece1[3], piece1[2], piece1[0], piece1[1])]
            elif piece1[SOUTH] == GRAY:
                return [(piece1[2], piece1[3], piece1[1], piece1[0])]
            else:
                return [(piece1[1], piece1[0], piece1[3], piece1[2])]

        # Cas ou la pièce 2 est un bord nord
        elif idxPiece2 in edgesIndexes[2]:
            if piece1[NORTH] == GRAY:
                return [piece1]
            elif piece1[WEST] == GRAY:
                return [(piece1[2], piece1[3], piece1[1], piece1[0])]
            elif piece1[EAST] == GRAY:
                return [(piece1[3], piece1[2], piece1[0], piece1[1])]
            else:
                return [(piece1[1], piece1[0], piece1[3], piece1[2])]

        # Cas ou la pièce 2 est un bord est
        elif idxPiece2 in edgesIndexes[3]:
            if piece1[EAST] == GRAY:
                return [piece1]
            elif piece1[NORTH] == GRAY:
                return [(piece1[2], piece1[3], piece1[1], piece1[0])]
            elif piece1[SOUTH] == GRAY:
                return [(piece1[3], piece1[2], piece1[0], piece1[1])]
            else:
                return [(piece1[1], piece1[0], piece1[3], piece1[2])]

        # Cas ou la pièce 2 n'est pas un bord
        else:
            return []

    # Cas ou la pièce à déplacer est une pièce centrale -> on peut la déplacer n'importe où sauf dans un bord
    else:

        if idxPiece2 in edgesIndexes[0] + edgesIndexes[1] + edgesIndexes[2] + edgesIndexes[3]:
            return []

        else:
            initial_shape = piece1
            rotation_90 = (piece1[2], piece1[3], piece1[1], piece1[0])
            rotation_180 = (piece1[1], piece1[0], piece1[3], piece1[2])
            rotation_270 = (piece1[3], piece1[2], piece1[0], piece1[1])

            return [initial_shape, rotation_90, rotation_180, rotation_270]


def findFirstUpgradingNeighbor(
        eternityPuzzle: EternityPuzzle, voisinage: List[List[Tuple[int]]], currentSolution: List[Tuple[int]]
        ) -> List[Tuple[int]]:
    """
    Retourne le premier voisin qui améliore la solution actuelle.
    Si aucun voisin n'améliore la solution, retourne None.
    :param eternityPuzzle: Instance du problème
    :param voisinage: Liste des voisins
    :param currentSolution: Solution actuelle
    :return: Solution améliorée ou None
    """
    currentCost = eternityPuzzle.get_total_n_conflict(currentSolution)

    for voisin in voisinage:
        if eternityPuzzle.get_total_n_conflict(voisin) < currentCost:
            return voisin

    return None
