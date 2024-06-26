# Auteurs
# Armel Ngounou Tchawe - 2238017
# Léo Valette - 2307835


from typing import Tuple
import numpy as np

from eternity_puzzle import EternityPuzzle

GRAY = 0

NORTH = 0
SOUTH = 1
WEST = 2
EAST = 3


def heuristicNbConflictPieceV1(
        eternity_puzzle: EternityPuzzle, solution: [Tuple[int]], newPiece: Tuple[int],
        indexNewPiece
        ) -> int:
    """
    Le but de cette fonction heuristique est de calculer le nombre de conflit qu'apporte une nouvelle pièce à
    la solution.
    Le score sera donc compris entre 0 et 4.
    Comme on place les pièces une par une en partant d'en bas à gauche jusqu'en haut à droite, on a besoin de check
    seuelement les conflits avec la pièce au sud et la pièce à l'ouest. Il faut aussi vérifier les bords de la grille.
    :param indexNewPiece:
    :param newPiece:
    :param eternity_puzzle:
    :param solution:
    :return:
    """

    n_conflict = 0

    sizeBoard = eternity_puzzle.board_size

    # On verifie les conflits avec la pièce au sud
    # 1er cas, la pièce est placé sur la première ligne, on vérifie donc le conflit avec le bord
    if indexNewPiece < sizeBoard:
        if newPiece[SOUTH] != GRAY:
            n_conflict += 1
    # 2ème cas, la pièce n'est pas sur la première ligne, on vérifie donc le conflit avec la pièce au sud
    else:
        if newPiece[SOUTH] != solution[indexNewPiece - sizeBoard][NORTH]:
            n_conflict += 1

    # On verifie les conflits avec la pièce à l'ouest
    # 1er cas, la pièce est placé sur la première colonne, on vérifie donc le conflit avec le bord
    if indexNewPiece % sizeBoard == 0:
        if newPiece[WEST] != GRAY:
            n_conflict += 1
    # 2ème cas, la pièce n'est pas sur la première colonne, on vérifie donc le conflit avec la pièce à l'ouest
    else:
        if newPiece[WEST] != solution[indexNewPiece - 1][EAST]:
            n_conflict += 1

    # Si la pièce est placé sur la dernière ligne, on vérifie le conflit avec le bord
    if indexNewPiece >= sizeBoard * (sizeBoard - 1):
        if newPiece[NORTH] != GRAY:
            n_conflict += 1

    # Si la pièce est placé sur la dernière colonne, on vérifie le conflit avec le bord
    if indexNewPiece % sizeBoard == sizeBoard - 1:
        if newPiece[EAST] != GRAY:
            n_conflict += 1

    return n_conflict


def heuristicNbConflictPieceV2(
        eternity_puzzle: EternityPuzzle, solution: [Tuple[int]], newPiece: Tuple[int],
        indexNewPiece
        ) -> int:
    """
    Amélioration de la fonction heuristique précédente. On donne une grosse pénalité en cas de conflit avec les bords
    :param newPiece:
    :param eternity_puzzle:
    :param solution:
    :return:
    """

    n_conflict = 0

    poidConflitClassique = 1
    poidConflitBord = 10

    sizeBoard = eternity_puzzle.board_size

    # SOUTH
    # 1er cas, la pièce est placé sur la première ligne, on vérifie donc le conflit avec le bord
    if indexNewPiece < sizeBoard:
        if newPiece[SOUTH] != GRAY:
            n_conflict += poidConflitBord
    # 2ème cas, la pièce n'est pas sur la première ligne, on vérifie donc le conflit avec la pièce au sud et que le sud
    # de la pièce n'est pas gris
    else:
        if newPiece[SOUTH] == GRAY:
            n_conflict += poidConflitBord
        elif (newPiece[SOUTH] != solution[indexNewPiece - sizeBoard][NORTH] and
              solution[indexNewPiece - sizeBoard][NORTH] != -1):
            n_conflict += poidConflitClassique

    # WEST
    # On verifie les conflits avec la pièce à l'ouest
    # 1er cas, la pièce est placé sur la première colonne, on vérifie donc le conflit avec le bord
    if indexNewPiece % sizeBoard == 0:
        if newPiece[WEST] != GRAY:
            n_conflict += poidConflitBord
    # 2ème cas, la pièce n'est pas sur la première colonne, on vérifie donc le conflit avec la pièce à l'ouest et que
    # l'ouest de la pièce n'est pas gris
    else:
        if newPiece[WEST] == GRAY:
            n_conflict += poidConflitBord
        elif (newPiece[WEST] != solution[indexNewPiece - 1][EAST]
              and solution[indexNewPiece - 1][EAST] != -1):
            n_conflict += poidConflitClassique

    # NORTH
    # Si la pièce est placé sur la dernière ligne, on vérifie le conflit avec le bord
    if indexNewPiece >= sizeBoard * (sizeBoard - 1):
        if newPiece[NORTH] != GRAY:
            n_conflict += poidConflitBord
    # Sinon on vérifie que le nord de la pièce n'est pas gris
    else:
        if newPiece[NORTH] == GRAY:
            n_conflict += poidConflitBord
        elif (newPiece[NORTH] != solution[indexNewPiece + sizeBoard][SOUTH]
              and solution[indexNewPiece + sizeBoard][SOUTH] != -1):
            n_conflict += poidConflitClassique

    # EAST
    # Si la pièce est placé sur la dernière colonne, on vérifie le conflit avec le bord
    if indexNewPiece % sizeBoard == sizeBoard - 1:
        if newPiece[EAST] != GRAY:
            n_conflict += poidConflitBord
    # Sinon on vérifie que l'est de la pièce n'est pas gris
    else:
        if newPiece[EAST] == GRAY:
            n_conflict += poidConflitBord
        elif (newPiece[EAST] != solution[indexNewPiece + 1][WEST]
              and solution[indexNewPiece + 1][WEST] != -1):
            n_conflict += poidConflitClassique

    return n_conflict


def heuristicNbConflictPieceV3(
        eternity_puzzle: EternityPuzzle, solutionMatrix: [[int]], newPiece: Tuple[int],
        coordNewPiece: Tuple[int, int]
        ) -> int:  # sourcery skip: low-code-quality
    """
    On compte le nombre de conflit que la pièce apporte à la solution. La solution fournit est une matrice.
    On doit aussi donner les coordonnées de la pièce dans la matrice.
    :param eternity_puzzle:
    :param solutionMatrix:
    :param newPiece:
    :param coordNewPiece:
    :return:
    """
    n_conflict = 0
    poidConflitClassique = 1
    poidConflitBord = 10

    sizeBoard = eternity_puzzle.board_size

    # SOUTH
    # 1er cas, la pièce est placé sur la première ligne, on vérifie donc le conflit avec le bord
    if coordNewPiece[0] == 0:
        if newPiece[SOUTH] != GRAY:
            n_conflict += poidConflitBord
    # 2ème cas, la pièce n'est pas sur la première ligne, on vérifie donc le conflit avec la pièce au sud et que le sud
    # de la pièce n'est pas gris
    else:
        if newPiece[SOUTH] == GRAY:
            n_conflict += poidConflitBord
        elif (newPiece[SOUTH] != solutionMatrix[coordNewPiece[0] - 1][coordNewPiece[1]][NORTH]
              and solutionMatrix[coordNewPiece[0] - 1][coordNewPiece[1]][NORTH] != -1):
            n_conflict += poidConflitClassique

    # WEST
    # 1er cas, la pièce est placé sur la première colonne, on vérifie donc le conflit avec le bord
    if coordNewPiece[1] == 0:
        if newPiece[WEST] != GRAY:
            n_conflict += poidConflitBord
    # 2ème cas, la pièce n'est pas sur la première colonne, on vérifie donc le conflit avec la pièce à l'ouest et que
    # l'ouest de la pièce n'est pas gris
    else:
        if newPiece[WEST] == GRAY:
            n_conflict += poidConflitBord
        elif (newPiece[WEST] != solutionMatrix[coordNewPiece[0]][coordNewPiece[1] - 1][EAST]
              and solutionMatrix[coordNewPiece[0]][coordNewPiece[1] - 1][EAST] != -1):
            n_conflict += poidConflitClassique

    # NORTH
    # 1er cas, la pièce est placé sur la dernière ligne, on vérifie donc le conflit avec le bord
    if coordNewPiece[0] == sizeBoard - 1:
        if newPiece[NORTH] != GRAY:
            n_conflict += poidConflitBord
    # 2ème cas, la pièce n'est pas sur la dernière ligne, on vérifie donc le conflit avec la pièce au nord et que le
    # nord de la pièce n'est pas gris
    else:
        if newPiece[NORTH] == GRAY:
            n_conflict += poidConflitBord
        elif (newPiece[NORTH] != solutionMatrix[coordNewPiece[0] + 1][coordNewPiece[1]][SOUTH]
              and solutionMatrix[coordNewPiece[0] + 1][coordNewPiece[1]][SOUTH] != -1):
            n_conflict += poidConflitClassique

    # EAST
    # 1er cas, la pièce est placé sur la dernière colonne, on vérifie donc le conflit avec le bord
    if coordNewPiece[1] == sizeBoard - 1:
        if newPiece[EAST] != GRAY:
            n_conflict += poidConflitBord
    # 2ème cas, la pièce n'est pas sur la dernière colonne, on vérifie donc le conflit avec la pièce à l'est et que
    # l'est de la pièce n'est pas gris
    else:
        if newPiece[EAST] == GRAY:
            n_conflict += poidConflitBord
        elif (newPiece[EAST] != solutionMatrix[coordNewPiece[0]][coordNewPiece[1] + 1][WEST]
              and solutionMatrix[coordNewPiece[0]][coordNewPiece[1] + 1][WEST] != -1):
            n_conflict += poidConflitClassique

    return n_conflict
