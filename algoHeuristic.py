import copy
from typing import Tuple, List
from tqdm import tqdm
import numpy as np

from eternity_puzzle import EternityPuzzle
from utils import getAllPlacementPossibilities, INFINITY, chooseBestPiece, getListFromMatrix


def solverHeuristique1Deep(eternity_puzzle: EternityPuzzle, heuristique) -> Tuple[List[Tuple[int]], int]:
    """
    Algortihme simple qui place les pièces une par une en partant d'en bas à gauche jusqu'en haut à droite. Il choisit
    à chaque fois la pièce qui apporte le moins de conflit à la solution. Il ne regarde qu'une seule pièce en avance.

    :param eternity_puzzle:
    :param heuristique:
    :return:
    """

    solution = []
    # Mélange des pièces
    remainingPiece = copy.deepcopy(eternity_puzzle.piece_list)
    np.random.shuffle(remainingPiece)
    nbPiece = len(remainingPiece)

    for _ in range(nbPiece):
        bestConflict = INFINITY
        bestPiece = None
        indexBestPiece = None

        possibilities = getAllPlacementPossibilities(eternity_puzzle, remainingPiece)

        for index, piece in enumerate(possibilities):
            nConflict = heuristique(eternity_puzzle, solution, piece)
            if nConflict < bestConflict:
                bestConflict = nConflict
                bestPiece = piece
                indexBestPiece = index
                if bestConflict == 0:
                    break

        solution.append(bestPiece)
        # On supprime la pièce de la liste des pièces restantes (sans prendre en compte une eventuelle rotation)
        remainingPiece.remove(possibilities[indexBestPiece - indexBestPiece % 4])

    return solution, eternity_puzzle.get_total_n_conflict(solution)


def solverHeuristique1DeepRestart(eternity_puzzle: EternityPuzzle, heuristique) -> Tuple[List[Tuple[int]], int]:
    """
    Amélioration de l'algorithme précédent. On utilise un restart aléatoire pour essayer d'avoir de meilleurs résultats.
    :param eternity_puzzle:
    :param heuristique:
    :return:
    """

    originalPieceList = copy.deepcopy(eternity_puzzle.piece_list)

    nbRestart = 500

    bestSolution = None
    bestNConflict = INFINITY

    for i in tqdm(range(nbRestart)):

        # On mélange les pièces
        shuffledPieceList = copy.deepcopy(originalPieceList)
        np.random.shuffle(shuffledPieceList)
        eternity_puzzle.piece_list = shuffledPieceList
        curSolution, curNConflict = solverHeuristique1Deep(eternity_puzzle, heuristique)

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


def solverHeuristique1DeepEdgeFirst(eternity_puzzle: EternityPuzzle, heuristique) -> Tuple[List[Tuple[int]], int]:
    """
    Amélioration de l'algorithme solverHeuristique1Deep. On place les pièces en partant des bords de la grille. Puis de
    manière symétrique de chaque côté de la diagonale (voir exemple ci-dessous).

    L'ordre de placement des pièces est le suivant avec une grille de taille 7x7
    [[ 0  1  2  3  4  5  6]
    [ 7 24 26 30 36 44 13]
    [ 8 28 32 38 45 43 14]
    [ 9 34 40 46 41 35 15]
    [10 42 47 39 33 29 16]
    [11 48 37 31 27 25 17]
    [12 19 20 21 22 23 18]]

    :param eternity_puzzle:
    :param heuristique:
    :return:
    """

    # Création de la solution vide sous forme de matrice de taille board_size * board_size pour avoir des coordonnées
    # x et y.
    solutionMatrix = [[(-1, -1, -1, -1) for _ in range(eternity_puzzle.board_size)] for _ in
                      range(eternity_puzzle.board_size)]

    # Mélange des pièces
    remainingPiece = copy.deepcopy(eternity_puzzle.piece_list)
    np.random.shuffle(remainingPiece)

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

        # Choix de la pièce
        bestPiece, remainingPiece = chooseBestPiece(eternity_puzzle, solutionMatrix, remainingPiece, heuristique,
                                                    (x, y))
        # Placement de la pièce
        solutionMatrix[x][y] = bestPiece

    # Placement des autres pièces
    indexPiece = eternity_puzzle.board_size * 4 - 5

    for indexDiagonal in range(eternity_puzzle.board_size - 2):
        for indexPieceInDiagonal in range(indexDiagonal + 1):
            x = 1 + indexPieceInDiagonal
            y = 1 + indexDiagonal - indexPieceInDiagonal
            indexPiece += 1
            # Choix de la pièce
            bestPiece, remainingPiece = chooseBestPiece(eternity_puzzle, solutionMatrix, remainingPiece, heuristique,
                                                        (x, y))
            # Placement de la pièce
            solutionMatrix[x][y] = bestPiece

            # Si on est pas sur la grande diagonale, on place la pièce symétrique
            if indexDiagonal != eternity_puzzle.board_size - 3:
                x = eternity_puzzle.board_size - 2 - indexPieceInDiagonal
                y = eternity_puzzle.board_size - 2 - indexDiagonal + indexPieceInDiagonal
                indexPiece += 1
                # Choix de la pièce
                bestPiece, remainingPiece = chooseBestPiece(eternity_puzzle, solutionMatrix, remainingPiece,
                                                            heuristique,
                                                            (x, y))
                # Placement de la pièce
                solutionMatrix[x][y] = bestPiece

    # Conversion de la solution en liste
    solutionList = getListFromMatrix(eternity_puzzle, solutionMatrix)

    return solutionList, eternity_puzzle.get_total_n_conflict(solutionList)


def solverHeuristique1DeepEdgeFirstV2(eternity_puzzle: EternityPuzzle, heuristique) -> Tuple[List[Tuple[int]], int]:
    """
    Amélioration de l'algorithme solverHeuristique1DeepEdgeFirst. On place les pièces en partant des bords de la grille.
    Puis en diagonale en partant du bord en bas à gauche jusqu'au bord en haut à droite.

    L'ordre de placement des pièces est le suivant avec une grille de taille 7x7
    [[ 0  1  2  3  4  5  6]
    [ 7 24 25 27 30 34 13]
    [ 8 26 28 31 35 42 14]
    [ 9 29 32 36 41 45 15]
    [10 33 37 40 44 47 16]
    [11 38 39 43 46 48 17]
    [12 19 20 21 22 23 18]]

    :param eternity_puzzle:
    :param heuristique:
    :return:
    """

    # Création de la solution vide sous forme de matrice de taille board_size * board_size pour avoir des coordonnées
    # x et y.
    solutionMatrix = [[(-1, -1, -1, -1) for _ in range(eternity_puzzle.board_size)] for _ in
                      range(eternity_puzzle.board_size)]

    # Mélange des pièces
    remainingPiece = copy.deepcopy(eternity_puzzle.piece_list)
    np.random.shuffle(remainingPiece)

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

        # Choix de la pièce
        bestPiece, remainingPiece = chooseBestPiece(eternity_puzzle, solutionMatrix, remainingPiece, heuristique,
                                                    (x, y))
        # Placement de la pièce
        solutionMatrix[x][y] = bestPiece

    # Placement des autres pièces
    indexPiece = eternity_puzzle.board_size * 4 - 5

    for indexDiagonal in range(eternity_puzzle.board_size - 2):
        for indexPieceInDiagonal in range(indexDiagonal + 1):
            x = 1 + indexPieceInDiagonal
            y = 1 + indexDiagonal - indexPieceInDiagonal
            indexPiece += 1
            # Choix de la pièce
            bestPiece, remainingPiece = chooseBestPiece(eternity_puzzle, solutionMatrix, remainingPiece, heuristique,
                                                        (x, y))
            # Placement de la pièce
            solutionMatrix[x][y] = bestPiece

    for indexDiagonal in range(eternity_puzzle.board_size - 4, -1, -1):
        for indexPieceInDiagonal in range(indexDiagonal + 1):
            x = eternity_puzzle.board_size - 2 - indexPieceInDiagonal
            y = eternity_puzzle.board_size - 2 - indexDiagonal + indexPieceInDiagonal
            indexPiece += 1
            # Choix de la pièce
            bestPiece, remainingPiece = chooseBestPiece(eternity_puzzle, solutionMatrix, remainingPiece,
                                                        heuristique,
                                                        (x, y))
            # Placement de la pièce
            solutionMatrix[x][y] = bestPiece

    # Conversion de la solution en liste
    solutionList = getListFromMatrix(eternity_puzzle, solutionMatrix)

    return solutionList, eternity_puzzle.get_total_n_conflict(solutionList)
