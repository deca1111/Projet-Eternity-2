from typing import Tuple, List

from utils import getRandomSolution
from eternity_puzzle import EternityPuzzle
import itertools

def solverLSNaiveRandomStart(eternityPuzzle: EternityPuzzle) -> Tuple[List[Tuple[int]], int]:
    """
    Algorithme de recherche locale avec un démarrage aléatoire.
    La selection des voisins se fait en comptant le nombre de conflits total.
    :param evalFct:
    :param eternityPuzzle:
    :return:
    """
    currentSolution = getRandomSolution(eternityPuzzle)
    currentCost = eternityPuzzle.get_total_n_conflict(currentSolution)

    voisinage = getVoisinageAllPiecesAndRotations(eternityPuzzle, currentSolution)


def getVoisinageAllPiecesAndRotations(eternityPuzzle: EternityPuzzle, solution: List[Tuple[int]]) -> (
        List)[Tuple[List[Tuple[int]], int]]:
    """
    Fonction qui retourne tous les voisins possibles de la solution en prenant en compte les rotations.
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
                newSolution[swap[0]] = piece1
                newSolution[swap[1]] = piece2
                newCost = eternityPuzzle.get_total_n_conflict(newSolution)
                voisinage.append((newSolution, newCost))

    print(f"Nombre de voisins : {len(voisinage)}")
    return voisinage

