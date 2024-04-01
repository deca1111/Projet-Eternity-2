import time
from typing import Tuple, List

from utils import getRandomSolution, getMatrixFromList, getConflictPieces, selectWithNbConflict, getEdgeIndexes, printGridIndexes, getAngleIndexes
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


def solverLocalSearchGlobal(eternityPuzzle: EternityPuzzle, voisinageFct, selectFct, costFct, maxTime) -> \
        Tuple[List[Tuple[int]], int]:
    """
    Algorithme de recherche locale générique.
    :param eternityPuzzle:
    :param voisinageFct:
    :param selectFct:
    :param costFct:
    :param maxTime:
    :return:
    """

    # Calcul du temps
    startTime = time.time()
    curentTime = time.time() - startTime

    bestSolution = None
    bestCost = (eternityPuzzle.board_size ** 2 + eternityPuzzle.board_size) * 2

    # currentSolution = getRandomSolution(eternityPuzzle)

    currentSolution, currentCost = solverHeuristique1DeepEdgeFirstV2(eternityPuzzle, heuristicNbConflictPieceV3)

    print(f"First best cost : {bestCost}")
    print(f"Coût initial : {currentCost}")

    if currentCost == 0:
        return currentSolution, currentCost

    # start1 = time.time()
    # voisinage1 = getVoisinageAllPermutAndRotations(eternityPuzzle, currentSolution)
    # print(f"Temps de calcul du voisinage1 : {round(time.time() - start1, 4)} secondes")
    # print(f"Nombre de voisins : {len(voisinage1)}")
    # currentSolution = min(voisinage1, key=eternityPuzzle.get_total_n_conflict)
    # currentCost = eternityPuzzle.get_total_n_conflict(currentSolution)
    # print(f"Temps de calcul de la sélection1 : {round(time.time() - start1, 4)} secondes")

    # start2 = time.time()
    # voisinage2 = getVoisinageOnlyConflict(eternityPuzzle, currentSolution)
    # print(f"Temps de calcul du voisinage2 : {round(time.time() - start2, 4)} secondes")
    # print(f"Nombre de voisins : {len(voisinage2)}")
    # currentSolution = min(voisinage2, key=eternityPuzzle.get_total_n_conflict)
    # currentCost = eternityPuzzle.get_total_n_conflict(currentSolution)
    # print(f"Temps de calcul de la sélection2 : {round(time.time() - start2, 4)} secondes")
    # return currentSolution, currentCost

    while curentTime < maxTime and currentCost > 0:
        voisinage = voisinageFct(eternityPuzzle, currentSolution)
        # print(f"Temps de calcul du voisinage : {round(time.time() - startTime, 4)} secondes")
        if len(voisinage) > 0:

            currentSolution = selectFct(voisinage, eternityPuzzle)
            # print(f"Temps de calcul de la sélection : {round(time.time() - startTime, 4)} secondes")
            currentCost = costFct(currentSolution)
            # print(f"Temps de calcul du coût : {round(time.time() - startTime, 4)} secondes")

            if currentCost < bestCost:
                bestSolution = currentSolution
                bestCost = currentCost
                print(f"Nouveau meilleur coût : {bestCost}")

            curentTime = time.time() - startTime
        else:
            break

    print(f"Éxecution terminée en {round(curentTime, 4)} secondes")

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

    return voisinage


def generatePossibleRotationForSwap(eternityPuzzle: EternityPuzzle, solution, idxPiece1, idxPiece2):
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






