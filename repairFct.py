from copy import deepcopy
from typing import List, Tuple
import random
from eternity_puzzle import EternityPuzzle
from heuristiques import heuristicNbConflictPieceV3
from utils import *


def repairHeuristicAllRotation(
        puzzle: EternityPuzzle, partialSolution: List[Tuple[int]],
        destructedPieces: List[Tuple[int]], idxDestroyedPieces: List[int]
        ):
    """
    Reconstruct the solution by replacing the None values by the best possible piece
    :param puzzle: the puzzle
    :param partialSolution: the partial solution
    :param destructedPieces: the pieces destructed
    :param idxDestroyedPieces: the indexes of the destructed pieces
    :return: the reconstructed solution
    """

    reconstructedSol = deepcopy(partialSolution)
    random.shuffle(destructedPieces)
    random.shuffle(idxDestroyedPieces)

    solutionMatrix = getMatrixFromList(puzzle, reconstructedSol)

    for idxNewPiece in idxDestroyedPieces:
        newIdx = (idxNewPiece // puzzle.board_size, idxNewPiece % puzzle.board_size)
        # print(f"Reconstruction de la pièce {newIdx}")

        bestPiece, destructedPieces = chooseBestPiece(puzzle, solutionMatrix, destructedPieces,
                                                      heuristicNbConflictPieceV3, newIdx)

        solutionMatrix[newIdx[0]][newIdx[1]] = bestPiece

    # Conversion de la solution en liste
    solutionList = getListFromMatrix(puzzle, solutionMatrix)

    return solutionList


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
