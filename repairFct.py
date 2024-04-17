from copy import deepcopy
from typing import List, Tuple
import random
from eternity_puzzle import EternityPuzzle
from heuristiques import heuristicNbConflictPieceV2, heuristicNbConflictPieceV3
from utils import *


def repairRandom(
        puzzle: EternityPuzzle, partialSolution: List[Tuple[int]],
        destructedPieces: List[Tuple[int]], idxDestroyedPieces: List[int]
        ):
    """
    Reconstruct the solution by replacing the None values by random piece
    :param puzzle: the puzzle
    :param partialSolution: the partial solution
    :param destructedPieces: the pieces destructed
    :param idxDestroyedPieces: the indexes of the destructed pieces
    :return: the reconstructed solution
    """

    reconstructedSol = deepcopy(partialSolution)
    random.shuffle(destructedPieces)
    random.shuffle(idxDestroyedPieces)

    for idx in idxDestroyedPieces:
        newPiece = destructedPieces.pop()
        newPiece = random.choice(puzzle.generate_rotation(newPiece))
        reconstructedSol[idx] = newPiece

    return reconstructedSol


def repairHeuristicEmplacementBest(
        puzzle: EternityPuzzle, partialSolution: List[Tuple[int]],
        destructedPieces: List[Tuple[int]], idxDestroyedPieces: List[int]
        ):
    """
    Reconstruct the solution en plaçant à chaque emplacement la pièce qui minimise le nombre de conflits
    :param puzzle: the puzzle
    :param partialSolution: the partial solution
    :param destructedPieces: the pieces destructed
    :param idxDestroyedPieces: the indexes of the destructed pieces
    :return: the reconstructed solution
    """

    reconstructedSol = deepcopy(partialSolution)
    random.shuffle(destructedPieces)
    random.shuffle(idxDestroyedPieces)

    for idxEmplacement in idxDestroyedPieces:

        idxBestPiece = None
        idxBestRot = None
        bestScore = float("inf")

        for idxPiece, piece in enumerate(destructedPieces):

            for idxRot, newPiece in enumerate(puzzle.generate_rotation(piece)):
                score = heuristicNbConflictPieceV2(puzzle, reconstructedSol, newPiece, idxEmplacement)
                if score < bestScore:
                    bestScore = score
                    idxBestPiece = idxPiece
                    idxBestRot = idxRot
                if bestScore == 0:
                    break

        reconstructedSol[idxEmplacement] = puzzle.generate_rotation(destructedPieces.pop(idxBestPiece))[idxBestRot]

    return reconstructedSol


def repairHeuristicPieceBest(
        puzzle: EternityPuzzle, partialSolution: List[Tuple[int]],
        destructedPieces: List[Tuple[int]], idxDestroyedPieces: List[int]
        ):
    """
    Reconstruction de la solution en plaçant chaque pièce au meilleur endroit possible
    :param puzzle:
    :param partialSolution:
    :param destructedPieces:
    :param idxDestroyedPieces:
    :return:
    """

    reconstructedSol = deepcopy(partialSolution)
    random.shuffle(destructedPieces)
    random.shuffle(idxDestroyedPieces)

    for piece in destructedPieces:

        rotPiece = puzzle.generate_rotation(piece)

        bestIdx = None
        bestScore = float("inf")
        bestRotPiece = None

        for idx in idxDestroyedPieces:
            for idxRot, newPiece in enumerate(rotPiece):
                score = heuristicNbConflictPieceV2(puzzle, reconstructedSol, newPiece, idx)
                if score < bestScore:
                    bestScore = score
                    bestIdx = idx
                    bestRotPiece = newPiece
                if bestScore == 0:
                    break

        reconstructedSol[bestIdx] = bestRotPiece
        idxDestroyedPieces.remove(bestIdx)

    return reconstructedSol