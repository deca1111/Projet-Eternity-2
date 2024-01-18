import copy
from typing import Tuple
from tqdm import tqdm
import numpy as np

from eternity_puzzle import EternityPuzzle
from utils import getAllPossiblePossibilities, INFINITY


def solverHeuristique1DeepV1(eternity_puzzle: EternityPuzzle, heuristique) -> ([Tuple[int]], int):
    """
    Algortihme simple qui place les pièces une par une en partant d'en bas à gauche jusqu'en haut à droite. Il choisit
    à chaque fois la pièce qui apporte le moins de conflit à la solution. Il ne regarde qu'une seule pièce en avance.

    :param eternity_puzzle:
    :param heuristique:
    :return:
    """

    solution = []
    remaining_piece = copy.deepcopy(eternity_puzzle.piece_list)
    nbPiece = len(remaining_piece)

    for _ in range(nbPiece):
        bestConflict = INFINITY
        bestPiece = None
        indexBestPiece = None

        possibilities = getAllPossiblePossibilities(eternity_puzzle, remaining_piece)

        for index, piece in enumerate(possibilities):
            nConflict = heuristique(eternity_puzzle, solution, piece)
            if nConflict < bestConflict:
                bestConflict = nConflict
                bestPiece = piece
                indexBestPiece = index

        solution.append(bestPiece)
        # On supprime la pièce de la liste des pièces restantes (sans prendre en compte une eventuelle rotation)
        remaining_piece.remove(possibilities[indexBestPiece - indexBestPiece % 4])

    return solution, eternity_puzzle.get_total_n_conflict(solution)


def solverHeuristique1DeepV2(eternity_puzzle: EternityPuzzle, heuristique) -> ([Tuple[int]], int):
    """
    Amélioration de l'algorithme précédent. On utilise un restart aléatoire pour essayer d'avoir de meilleurs résultats.
    :param eternity_puzzle:
    :param heuristique:
    :return:
    """

    originalPieceList = copy.deepcopy(eternity_puzzle.piece_list)

    nbRestart = 100

    bestSolution = None
    bestNConflict = INFINITY

    for i in tqdm(range(nbRestart)):

        # On mélange les pièces
        shuffledPieceList = copy.deepcopy(originalPieceList)
        np.random.shuffle(shuffledPieceList)
        eternity_puzzle.piece_list = shuffledPieceList
        curSolution, curNConflict = solverHeuristique1DeepV1(eternity_puzzle, heuristique)

        if curNConflict < bestNConflict:
            bestNConflict = curNConflict
            bestSolution = curSolution
            if bestNConflict == 0:
                print(f"Solution trouvée en {i} restarts")
                break
    else:
        print(f"Solution non trouvée en {nbRestart} restarts")
        print(f"La meilleure solution trouvée a un score de {bestNConflict}")

    # Remise en place de la liste de pièce originale
    eternity_puzzle.piece_list = originalPieceList

    return bestSolution, bestNConflict
