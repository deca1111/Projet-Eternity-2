from typing import Tuple, List
from eternity_puzzle import EternityPuzzle
import math

INFINITY = math.inf


def getAllPossiblePossibilities(eternity_puzzle: EternityPuzzle, remainingPiece: List[Tuple]) -> List[Tuple]:
    """
    Cette fonction retourne toutes les possibilitées de placement possibles en fonction des pièces restantes et des rotations.
    :param eternity_puzzle:
    :param remainingPiece:
    :return:
    """

    result = []

    for piece in remainingPiece:
        result.extend(eternity_puzzle.generate_rotation(piece))

    return result


def chooseBestPiece(
        eternityPuzzle: EternityPuzzle, solution: List[List[Tuple]],
        remainingPiece: List[Tuple],
        heuristique, coord: Tuple[int, int]
        ) -> Tuple[Tuple[int, int, int, int], List[Tuple]]:
    """
    Fonction qui retourne la pièce qui apporte le moins de conflit à la solution.
    :param coord:
    :param eternityPuzzle:
    :param solution:
    :param remainingPiece:
    :param heuristique:
    :return:
    """

    # Initialisation des variables
    bestConflict = INFINITY
    bestPiece = None
    indexBestPiece = None

    # On récupère toutes les possibilités de placement possibles en fonction des pièces restantes et des rotations
    possibilities = getAllPossiblePossibilities(eternityPuzzle, remainingPiece)

    # On parcourt toutes les possibilités
    for index, piece in enumerate(possibilities):
        # On calcule le nombre de conflit que la pièce apporte à la solution
        nConflict = heuristique(eternityPuzzle, solution, piece, coord)
        # Si le nombre de conflit est inférieur au meilleur nombre de conflit, on met à jour le meilleur nombre de
        # conflit
        if nConflict < bestConflict:
            bestConflict = nConflict
            bestPiece = piece
            indexBestPiece = index
            # Si le nombre de conflit est égal à 0, on peut arrêter de chercher
            if bestConflict == 0:
                break

    # Suppression de la pièce de la liste des pièces restantes (sans prendre en compte une eventuelle rotation)
    remainingPiece.remove(possibilities[indexBestPiece - indexBestPiece % 4])

    return bestPiece, remainingPiece
