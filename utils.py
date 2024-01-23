from typing import Tuple
from eternity_puzzle import EternityPuzzle
import math

INFINITY = math.inf


def getAllPossiblePossibilities(eternity_puzzle: EternityPuzzle, remainingPiece: [Tuple[int]]) -> [Tuple[int]]:
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