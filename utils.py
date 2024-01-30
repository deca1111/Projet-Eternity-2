import copy
import random
from typing import Tuple, List

import numpy as np

from eternity_puzzle import EternityPuzzle
import math

INFINITY = math.inf


def getAllPlacementPossibilities(eternity_puzzle: EternityPuzzle, remainingPiece: List[Tuple]) -> List[Tuple]:
    """
    Cette fonction retourne toutes les possibilitées de placement possibles en fonction des pièces restantes et des
    rotations.
    :param eternity_puzzle:
    :param remainingPiece: :return:
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
    possibilities = getAllPlacementPossibilities(eternityPuzzle, remainingPiece)

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


def getRandomSolution(eternityPuzzle: EternityPuzzle) -> List[Tuple]:
    """
    Fonction qui retourne une solution aléatoire.
    :param eternityPuzzle:
    :return:
    """

    # Copie de la liste des pièces
    listPieces = copy.deepcopy(eternityPuzzle.piece_list)
    # Mélange de la liste des pièces
    np.random.shuffle(listPieces)

    return listPieces


def getMatrixFromList(eternityPuzzle: EternityPuzzle, listSolution: List[Tuple]) -> List[List[Tuple]]:
    """
    Fonction qui retourne une matrice à partir d'une solution.
    :param eternityPuzzle:
    :param listSolution:
    :return:
    """
    return [[listSolution[i * eternityPuzzle.board_size + j] for j in range(eternityPuzzle.board_size)]
            for i in range(eternityPuzzle.board_size)]


def getListFromMatrix(eternityPuzzle: EternityPuzzle, matrixSolution: List[List[Tuple]]) -> List[Tuple]:
    """
    Fonction qui retourne une solution à partir d'une matrice.
    :param eternityPuzzle:
    :param matrixSolution:
    :return:
    """
    return [matrixSolution[i][j] for i in range(eternityPuzzle.board_size) for j in range(eternityPuzzle.board_size)]
