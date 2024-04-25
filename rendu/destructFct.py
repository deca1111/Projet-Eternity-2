# Auteurs
# Armel Ngounou Tchawe - 2238017
# Léo Valette - 2307835


from copy import deepcopy
from typing import List, Tuple
import random
from eternity_puzzle import EternityPuzzle
from heuristiques import heuristicNbConflictPieceV2
import numpy as np


def destructRandom(_, solution: List[Tuple[int]], prctDestruct: float = 0.1):
    """
    Randomly destruct nbDestruct pieces from the solution
    :param _: PAS PRIS EN COMPTE (pour avoir la même signature que les autres fonctions de destruction)
    :param solution: the solution
    :param prctDestruct: the percentage of pieces to destruct
    :return: La solution dégradée et une liste des pièces détruite et une liste d'index des pièces détruites
    """

    # Number of pieces to destruct
    nbDestruct = int(len(solution) * prctDestruct)

    # Randomly select the pieces to destruct
    idxDestructed = random.sample(range(len(solution)), nbDestruct)

    destructedSol = deepcopy(solution)
    destroyedPieces = []

    for idx in idxDestructed:
        destructedSol[idx] = (-1, -1, -1, -1)
        destroyedPieces.append(solution[idx])

    return destructedSol, destroyedPieces, idxDestructed


def destructProbaMostConflict(puzzle: EternityPuzzle, solution: List[Tuple[int]], prctDestruct: float = 0.1):
    """
    Choix des pièces à détruire avec une probabilité proportionnelle au nombre de conflits qu'elles apportent
    :param puzzle: the puzzle
    :param solution: the solution
    :param prctDestruct: the percentage of pieces to destruct
    :return: La solution dégradée et une liste des pièces détruite et une liste d'index des pièces détruites
    """

    poidConflit = 25

    # Number of pieces to destruct
    nbDestruct = int(len(solution) * prctDestruct)

    # Get the number of conflict for each piece
    conflicts = [1 + poidConflit * heuristicNbConflictPieceV2(puzzle, solution, solution[idx], idx) for idx in range(len(solution))]
    # Compute the probability of destruction for each piece
    conflicts = np.array(conflicts) / sum(conflicts)

    # Get the indexes of the pieces to destruct
    idxDestructed = np.random.choice(range(len(solution)), nbDestruct, p=conflicts, replace=False).tolist()

    destructedSol = deepcopy(solution)
    destroyedPieces = []

    for idx in idxDestructed:
        destructedSol[idx] = (-1, -1, -1, -1)
        destroyedPieces.append(solution[idx])

    return destructedSol, destroyedPieces, idxDestructed


def destructOnlyConflict(puzzle: EternityPuzzle, solution: List[Tuple[int]], prctDestruct: float = 0.1):
    """
    Choix des pièces à détruire uniquement en fonction du nombre de conflits qu'elles apportent
    :param puzzle: the puzzle
    :param solution: the solution
    :param prctDestruct: the percentage of pieces to destruct
    :return: La solution dégradée et une liste des pièces détruite et une liste d'index des pièces détruites
    """

    # Number of pieces to destruct
    nbDestruct = int(len(solution) * prctDestruct)

    # Récupération des index des pièces triées par nombre de conflits
    conflicts = [(idx, heuristicNbConflictPieceV2(puzzle, solution, solution[idx], idx))
                 for idx in range(len(solution))]

    # On enlève les pièces sans conflits
    conflicts = [c for c in conflicts if c[1] > 0]

    # Mélanges des pièces pour éviter de toujours détruire les mêmes
    random.shuffle(conflicts)

    # Tri des pièces par nombre de conflits (de la plus conflictuelle à la moins conflictuelle)
    conflicts.sort(key=lambda x: x[1], reverse=True)

    # On ne garde que les nbDestruct premières pièces
    if len(conflicts) < nbDestruct:
        nbDestruct = len(conflicts)

    idxDestructed = [idx for idx, _ in conflicts[:nbDestruct]]

    destructedSol = deepcopy(solution)
    destroyedPieces = []

    for idx in idxDestructed:
        destructedSol[idx] = (-1, -1, -1, -1)
        destroyedPieces.append(solution[idx])

    return destructedSol, destroyedPieces, idxDestructed


def destructAllConflict(puzzle: EternityPuzzle, solution: List[Tuple[int]], _):
    """
    Destruct all the pieces that are in conflict
    :param puzzle: the puzzle
    :param solution: the solution
    :return: La solution dégradée et une liste des pièces détruite et une liste d'index des pièces détruites
    :param _: PAS PRIS EN COMPTE (pour avoir la même signature que les autres fonctions de destruction)
    """

    destructedSol = deepcopy(solution)
    destroyedPieces = []
    idxDestructed = []

    for idx, piece in enumerate(solution):
        if heuristicNbConflictPieceV2(puzzle, solution, piece, idx) > 0:
            destructedSol[idx] = (-1, -1, -1, -1)
            destroyedPieces.append(piece)
            idxDestructed.append(idx)

    return destructedSol, destroyedPieces, idxDestructed

