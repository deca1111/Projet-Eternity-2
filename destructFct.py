from copy import deepcopy
from typing import List, Tuple
import random
from eternity_puzzle import EternityPuzzle
from heuristiques import heuristicNbConflictPieceV2
import numpy as np


def destructRandom(puzzle: EternityPuzzle, solution: List[Tuple[int]], prctDestruct: float = 0.1):
    """
    Randomly destruct nbDestruct pieces from the solution
    :param puzzle: the puzzle
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
        destructedSol[idx] = (0, 0, 0, 0)
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

    # Number of pieces to destruct
    nbDestruct = int(len(solution) * prctDestruct)

    # Get the number of conflict for each piece
    conflicts = [1 + heuristicNbConflictPieceV2(puzzle, solution, solution[idx], idx) for idx in range(len(solution))]
    # Compute the probability of destruction for each piece
    conflicts = np.array(conflicts) / sum(conflicts)

    # Get the indexes of the pieces to destruct
    idxDestructed = np.random.choice(range(len(solution)), nbDestruct, p=conflicts, replace=False)

    destructedSol = deepcopy(solution)
    destroyedPieces = []

    for idx in idxDestructed:
        destructedSol[idx] = (0, 0, 0, 0)
        destroyedPieces.append(solution[idx])

    return destructedSol, destroyedPieces, idxDestructed