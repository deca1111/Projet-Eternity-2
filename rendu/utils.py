# Auteurs
# Armel Ngounou Tchawe - 2238017
# Léo Valette - 2307835

import copy
import random
from typing import Tuple, List
import os
import json
from datetime import datetime

import numpy as np

from eternity_puzzle import EternityPuzzle
import math

INFINITY = math.inf
NORTH = 0
SOUTH = 1
WEST = 2
EAST = 3

GRAY = 0


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
    :return: la meilleure pièce et la liste des pièces restantes
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


def getConflictPieces(eternityPuzzle: EternityPuzzle, solution: List[Tuple]) -> List[int]:
    """
    Fonction qui retourne la liste des indices des pièces qui sont en conflit avec une autre ou un bord. On compte comme
    un conflit le fait qu'un bord gris d'une pièce ne soit pas en face du bord d'un plateau.

    :param eternityPuzzle:
    :param solution:
    :return:
    """
    sizeBoard = eternityPuzzle.board_size
    conflictPieces = set()
    nbPieceChecked = 0
    # En réalité on peut ne checker qu'une pièce sur deux, car si on regarde les quatres coins d'une pièces on regarde
    # aussi des coins des autres pièces adjacentes. Comme on veut aussi vérifier que les bords gris de chaque pièce est
    # bien placé sur le bord d'un plateau, on va checker toutes les pièces si elles ne sont pas déjà comme marquée en
    # conflit. La plupart des conflits trouvés vont donc éliminer 2 pièces.
    # Si cette fonction est trop lente, on peut la refaire avec la logique qu'on check les connexions et pas les
    # pièces, la on optimiserait les calculs.
    for indexPiece in range(len(solution)):
        # Si cette pièce n'est pas déjà dans la liste des pièces en conflit, on vérifie ses connexions avec les autres
        if indexPiece not in conflictPieces:
            nbPieceChecked += 1
            # On récupère la pièce
            piece = solution[indexPiece]

            # SUD
            # 1er cas, la pièce est placé sur la première ligne, on vérifie donc le conflit avec le bord
            if indexPiece < sizeBoard:
                if piece[SOUTH] != GRAY:
                    conflictPieces.add(indexPiece)
            # 2ème cas, la pièce n'est pas sur la première ligne, on vérifie donc le conflit avec la pièce au sud et
            # que le sud de la pièce n'est pas gris
            elif piece[SOUTH] == GRAY or piece[SOUTH] != solution[indexPiece - sizeBoard][NORTH]:
                conflictPieces.add(indexPiece)
                conflictPieces.add(indexPiece - sizeBoard)

            # OUEST
            # 1er cas, la pièce est placé sur la première colonne, on vérifie donc le conflit avec le bord
            if indexPiece % sizeBoard == 0:
                if piece[WEST] != GRAY:
                    conflictPieces.add(indexPiece)
            # 2ème cas, la pièce n'est pas sur la première colonne, on vérifie donc le conflit avec la pièce à l'ouest
            # et que l'ouest de la pièce n'est pas gris
            elif piece[WEST] == GRAY or piece[WEST] != solution[indexPiece - 1][EAST]:
                conflictPieces.add(indexPiece)
                conflictPieces.add(indexPiece - 1)

            # NORD
            # 1er cas, la pièce est placé sur la dernière ligne, on vérifie donc le conflit avec le bord
            if indexPiece >= sizeBoard * (sizeBoard - 1):
                if piece[NORTH] != GRAY:
                    conflictPieces.add(indexPiece)
            # 2ème cas, la pièce n'est pas sur la dernière ligne, on vérifie donc le conflit avec la pièce au nord
            # et que le nord de la pièce n'est pas gris
            elif piece[NORTH] == GRAY or piece[NORTH] != solution[indexPiece + sizeBoard][SOUTH]:
                conflictPieces.add(indexPiece)
                conflictPieces.add(indexPiece + sizeBoard)

            # EST
            # 1er cas, la pièce est placé sur la dernière colonne, on vérifie donc le conflit avec le bord
            if indexPiece % sizeBoard == sizeBoard - 1:
                if piece[EAST] != GRAY:
                    conflictPieces.add(indexPiece)
            # 2ème cas, la pièce n'est pas sur la dernière colonne, on vérifie donc le conflit avec la pièce à l'est
            # et que l'est de la pièce n'est pas gris
            elif piece[EAST] == GRAY or piece[EAST] != solution[indexPiece + 1][WEST]:
                conflictPieces.add(indexPiece)
                conflictPieces.add(indexPiece + 1)
    # print(f"Nombre de pièces vérifiées : {nbPieceChecked}")
    return list(conflictPieces)


def selectWithNbConflict(voisinage, eternityPuzzle: EternityPuzzle):
    """
    Fonction qui retourne le voisin qui a le moins de conflit.
    :param eternityPuzzle:
    :param voisinage:
    :return:
    """
    return min(voisinage, key=eternityPuzzle.get_total_n_conflict)


def getEdgeIndexes(eternityPuzzle: EternityPuzzle) -> Tuple[List[int], List[int], List[int], List[int]]:
    """
    Fonction qui retourne les indices des pièces qui sont des bords. Dans l'ordre suivant : sud, ouest, nord, est.
    :param eternityPuzzle:
    :return:
    """
    sizeBoard = eternityPuzzle.board_size
    return (list(range(sizeBoard)),
            list(range(0, sizeBoard * sizeBoard, sizeBoard)),
            list(range(sizeBoard * (sizeBoard - 1), sizeBoard * sizeBoard)),
            list(range(sizeBoard - 1, sizeBoard * sizeBoard, sizeBoard)))


def getAngleIndexes(eternityPuzzle: EternityPuzzle) -> List[int]:
    """
    Fonction qui retourne les indices des pièces qui sont des angles dans l'ordre suivant : sud-ouest, nord-ouest,
    nord-est, sud-est.
    :param eternityPuzzle:
    :return:
    """
    sizeBoard = eternityPuzzle.board_size
    return [0, sizeBoard * (sizeBoard - 1), sizeBoard * sizeBoard - 1, sizeBoard - 1]


def printGridIndexes(eternityPuzzle: EternityPuzzle):
    """
    Fonction qui affiche la grille avec les indices des pièces.
    :param eternityPuzzle:
    :return:
    """

    # L'angle sud-ouest est en bas à gauche et possède l'indice 0, l'angle nord-ouest est en haut à gauche et possède
    # l'indice sizeBoard * (sizeBoard - 1)
    # l'affichage commence par la ligne du haut
    sizeBoard = eternityPuzzle.board_size
    for i in range(sizeBoard - 1, -1, -1):
        for j in range(sizeBoard):
            print(f"{i * sizeBoard + j:3d}", end=" ")
        print()


def countChange(solution1: List[Tuple], solution2: List[Tuple]) -> int:
    """
    Fonction qui compte le nombre de changement entre deux solutions.
    :param solution1:
    :param solution2:
    :return:
    """
    return sum([1 for i in range(len(solution1)) if solution1[i] != solution2[i]])


def getInstanceName(puzzle: EternityPuzzle) -> str:
    instanceNames = {2: "eternity_trivial_A.txt",
                     3: "eternity_trivial_B.txt",
                     4: "eternity_A.txt",
                     7: "eternity_B.txt",
                     8: "eternity_C.txt",
                     9: "eternity_D.txt",
                     10: "eternity_E.txt",
                     16: "eternity_complet.txt"}

    if puzzle.board_size in instanceNames:
        instanceName = instanceNames[puzzle.board_size]
    else:
        instanceName = "eternity_custom.txt"

    return instanceName


def logResults(puzzle: EternityPuzzle, solver: str, ligDict: dict):
    """
    Fonction qui log les résultats dans un fichier.
    :param puzzle: Instance du puzzle
    :param solver: Nom du solver
    :param ligDict: Dictionnaire contenant les informations à logger
    :return:
    """
    root = "logResultats"
    os.makedirs(root, exist_ok=True)

    directory = os.path.join(root, solver)
    os.makedirs(directory, exist_ok=True)

    instanceName = getInstanceName(puzzle)

    with open(os.path.join(directory, instanceName), "a", encoding='UTF-8') as f:
        f.write(f"\n--------------------------------------------------\n")

        for key, value in ligDict.items():
            # Si la valeur est un dictionnaire, on affiche les valeurs du dictionnaire
            if isinstance(value, dict):
                f.write(f"{key} : \n")
                for key2, value2 in value.items():
                    f.write(f"\t{key2} : {value2}\n")
            else:
                f.write(f"{key} : {value}\n")


def saveBestSolution(puzzle: EternityPuzzle, solver: str, bestSolution: List[Tuple], bestScore: int, logDict=None):
    """
    Fonction qui sauvegarde la meilleure solution trouvée.
    :param puzzle: Instance du puzzle
    :param solver: Nom du solver
    :param bestSolution: Meilleure solution trouvée
    :param bestScore: Meilleur score
    :param logDict: Dictionnaire contenant les informations à logger
    :return:
    """

    # Dossiers de sauvegarde des solutions
    root = "savedBestSolutions"
    os.makedirs(root, exist_ok=True)

    rootVizu = os.path.join(root, "visualizations")
    os.makedirs(rootVizu, exist_ok=True)
    rootVizuSolver = os.path.join(rootVizu, solver)
    os.makedirs(rootVizuSolver, exist_ok=True)

    rootSol = os.path.join(root, "solutions")
    os.makedirs(rootSol, exist_ok=True)
    rootSolSolver = os.path.join(rootSol, solver)
    os.makedirs(rootSolSolver, exist_ok=True)

    # Fichier de sauvegarde des meilleures scores
    fileScores = os.path.join(root, "bestScores.json")

    # Récupération du nom de l'instance
    instanceName = getInstanceName(puzzle)

    # Si le fichier n'existe pas, on le crée
    if not os.path.exists(fileScores):
        with open(fileScores, "w") as f:
            print("Création du fichier de sauvegarde des meilleurs scores")
            json.dump({}, f)

    # Check si la solution est meilleure que celle déjà sauvegardée
    with open(fileScores, "r", encoding='UTF-8') as f:
        bestScores = json.load(f)

    # Si le solver n'existe pas dans le fichier, on le crée
    if solver not in bestScores:
        bestScores[solver] = {}

    # Si l'instance n'existe pas dans le solver ou si la solution est meilleure que celle déjà sauvegardée
    if instanceName not in bestScores[solver] or bestScore <= bestScores[solver][instanceName]["score"]:
        bestScores[solver][instanceName] = {"score": bestScore}

        if logDict is not None:
            for key in logDict:
                bestScores[solver][instanceName][key] = logDict[key]

            # Sauvegarde des meilleurs scores
        with open(fileScores, "w") as f:
            json.dump(bestScores, f, indent=4)

    else:
        print(f"La solution trouvée n'est pas meilleure que celle déjà sauvegardée pour le solver {solver}")
        return



    # Sauvegarde de la solution
    solPath = os.path.join(rootSolSolver, f"sol_{instanceName}")
    vizuPath = os.path.join(rootVizuSolver, "visu_" + instanceName.split(".")[0] + ".png")

    puzzle.print_solution(bestSolution, solPath)
    puzzle.display_solution(bestSolution, vizuPath)
