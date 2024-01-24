import time
import eternity_puzzle
from tqdm import tqdm
from algoSolveur import solverHeuristique1Deep, solverHeuristique1DeepEdgeFirst, solverHeuristique1DeepEdgeFirstV2
from heuristiques import heuristicNbConflictPieceV1, heuristicNbConflictPieceV2, heuristicNbConflictPieceV3
from utils import INFINITY


def runAllTests(nbIter=1000):
    instanceName = "eternity_complet.txt"
    puzzle = eternity_puzzle.EternityPuzzle("./instances/"+ instanceName)

    print(f"\nLancement des tests sur l'instance : {instanceName} / nombre d'itérations : {nbIter}")

    print("\nTest de solverHeuristique1Deep avec heuristicNbConflictPieceV1 :")
    runTest(puzzle, solverHeuristique1Deep, heuristicNbConflictPieceV1, nbIter)

    print("\nTest de solverHeuristique1Deep avec heuristicNbConflictPieceV2 :")
    runTest(puzzle, solverHeuristique1Deep, heuristicNbConflictPieceV2, nbIter)

    print("\nTest de solverHeuristique1DeepEdgeFirst avec heuristicNbConflictPieceV3 :")
    runTest(puzzle, solverHeuristique1DeepEdgeFirst, heuristicNbConflictPieceV3, nbIter)

    print("\nTest de solverHeuristique1DeepEdgeFirstV2 avec heuristicNbConflictPieceV3 :")
    runTest(puzzle, solverHeuristique1DeepEdgeFirstV2, heuristicNbConflictPieceV3, nbIter)


def runTest(eternityPuzzle, algorithme, heuristique, nbIter):
    sommeConflit = 0
    best = INFINITY
    start = time.time()
    for _ in tqdm(range(nbIter)):
        _, nbConflict = algorithme(eternityPuzzle, heuristique)
        best = min(best, nbConflict)
        sommeConflit += nbConflict
    print("- Moyenne des conflits : ", sommeConflit / nbIter)
    print("- Meilleur score : ", best)
    print(f"- Temps d'exécution :  {round(time.time() - start, 2)} secondes")
    print(f"- Temps d'exécution moyen : {round((time.time() - start) / nbIter, 2)} secondes")
    print("\n")


if __name__ == '__main__':
    runAllTests()
