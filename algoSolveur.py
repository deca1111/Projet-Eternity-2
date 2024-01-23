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


def solverHeuristique1DeepRestart(eternity_puzzle: EternityPuzzle, heuristique) -> ([Tuple[int]], int):
    """
    Amélioration de l'algorithme précédent. On utilise un restart aléatoire pour essayer d'avoir de meilleurs résultats.
    :param eternity_puzzle:
    :param heuristique:
    :return:
    """

    originalPieceList = copy.deepcopy(eternity_puzzle.piece_list)

    nbRestart = 10000

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


def solverHeuristique1DeepEdgeFirst(eternity_puzzle: EternityPuzzle, heuristique) -> ([Tuple[int]], int):
    """
    Amélioration de l'algorithme solverHeuristique1Deep. On place les pièces en partant des bords de la grille. Puis en
    diagonale en partant du bord en bas à gauche jusqu'au bord en haut à droite.

    :param eternity_puzzle:
    :param heuristique:
    :return:
    """

    # Création de la solution vide sous forme de matrice de taille board_size * board_size pour avoir des coordonnées
    # x et y.
    solutionMatrix = [[0 for i in range(eternity_puzzle.board_size)] for j in range(eternity_puzzle.board_size)]
    print("Matrice de solution vide:")
    print(np.matrix(solutionMatrix))

    # Mélange des pièces
    shuffledPieceList = copy.deepcopy(eternity_puzzle.piece_list)
    np.random.shuffle(shuffledPieceList)


    # Conversion de la solution en liste
    solutionList = [solutionMatrix[i][j] for i in range(eternity_puzzle.board_size) for j in range(eternity_puzzle.board_size)]

    # Placement des bords (size * 4 - 4 pièces)
    for indexPiece in range(eternity_puzzle.board_size * 4 - 4):
        # Calcul des coordonnées x et y où l'on veut placer la pièce
        # On commence par la bande du bas:
        if indexPiece < eternity_puzzle.board_size:
            x = 0
            y = indexPiece
        # Puis la bande de gauche:
        elif indexPiece < eternity_puzzle.board_size * 2 - 1:
            x = 1 + (indexPiece - eternity_puzzle.board_size)
            y = 0
        elif indexPiece < eternity_puzzle.board_size * 3 - 2:
            x = 1 + (indexPiece - (eternity_puzzle.board_size * 2 - 1))
            y = eternity_puzzle.board_size - 1
        else:
            x = eternity_puzzle.board_size - 1
            y = 1 + (indexPiece - (eternity_puzzle.board_size * 3 - 2))

    # Placement des autres pièces
    indexPiece = eternity_puzzle.board_size * 4 - 4
    for indexDiagonal in range(eternity_puzzle.board_size - 2):




        solutionMatrix[x][y] = indexPiece

    # Affichage de la solution
    print("Solution:")
    print(np.matrix(solutionMatrix))


