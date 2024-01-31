import time
from typing import Tuple, List

from utils import getRandomSolution
from eternity_puzzle import EternityPuzzle
import itertools
from algoHeuristic import solverHeuristique1DeepEdgeFirstV2
from heuristiques import heuristicNbConflictPieceV3


def solverLSNaiveRandomStart(eternityPuzzle: EternityPuzzle, maxTime) -> Tuple[List[Tuple[int]], int]:
    """
    Algorithme de recherche locale avec un démarrage aléatoire.
    La selection des voisins se fait en comptant le nombre de conflits total.
    :param evalFct:
    :param eternityPuzzle:
    :return:
    """
    # Calcul du temps
    startTime = time.time()
    curentTime = time.time() - startTime

    # currentSolution = getRandomSolution(eternityPuzzle)
    # currentCost = eternityPuzzle.get_total_n_conflict(currentSolution)

    currentSolution, currentCost = solverHeuristique1DeepEdgeFirstV2(eternityPuzzle, heuristicNbConflictPieceV3)

    print(f"Coût initial : {currentCost}")

    while curentTime < maxTime and currentCost > 0:
        if voisinage := getVoisinageAllPiecesAndRotations(eternityPuzzle, currentSolution, currentCost):

            bestVoisin = min(voisinage, key=lambda x: x[1])

            if bestVoisin[1] < currentCost:
                currentSolution = bestVoisin[0]
                currentCost = bestVoisin[1]
                print(f"Nouveau meilleur coût : {currentCost}")

            curentTime = time.time() - startTime
        else:
            break

    print(f"Éxecution terminée en {round(curentTime, 4)} secondes")

    return currentSolution, currentCost


def getVoisinageAllPiecesAndRotations(eternityPuzzle: EternityPuzzle, solution: List[Tuple[int]], bestCurrentCost) -> \
List[Tuple[List[Tuple[int]], int]]:
    """
    Fonction qui retourne tous les voisins possibles de la solution en prenant en compte les rotations.
    :param bestCurrentCost:
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
                newCost = eternityPuzzle.get_total_n_conflict(newSolution)
                if newCost < bestCurrentCost:
                    voisinage.append((newSolution, newCost))

    # print(f"Nombre de voisins : {len(voisinage)}")
    return voisinage


def getVoisinageOnlyCOnflict(eternityPuzzle: EternityPuzzle, solution: List[Tuple[int]], bestCurrentCost) -> \
List[Tuple[List[Tuple[int]], int]]:
    """
    Fonction qui retourne le voisinage de la solution en prenant seulement les permutations de pièeces qui ont des
    conflit (au moins 1 des 2)
    :param eternityPuzzle:
    :param solution:
    :param bestCurrentCost:
    :return:
    """
    # On commence par lister l'ID des pièces qui génèrent au moins un conflit
    listPieceWithConflict = []
    for i, piece in enumerate(solution):
        if eternityPuzzle.get_n_conflict(piece) > 0:
            listPieceWithConflict.append(i)