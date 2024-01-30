import time
import eternity_puzzle
from tqdm import tqdm
from algoHeuristic import solverHeuristique1Deep, solverHeuristique1DeepEdgeFirst, solverHeuristique1DeepEdgeFirstV2
from heuristiques import heuristicNbConflictPieceV1, heuristicNbConflictPieceV2, heuristicNbConflictPieceV3
from utils import INFINITY
import argparse


def runAllTests(saveResult=False, saveFile=None, nbIter=1000):
    instanceName = "eternity_complet.txt"
    puzzle = eternity_puzzle.EternityPuzzle("./instances/" + instanceName)

    # Ouverture et réinitialisation du fichier de sauvegarde si besoin
    if saveResult:
        with open(saveFile, "w", encoding="utf-8") as file:
            file.write(f"Résultats des tests pour l'instance : {instanceName}\nNombre d'itérations : {nbIter}\n\n")

    print(f"\nLancement des tests sur l'instance : {instanceName} / nombre d'itérations : {nbIter}")

    print("\nTest de solverHeuristique1Deep avec heuristicNbConflictPieceV1 :")
    runTest(puzzle, solverHeuristique1Deep, heuristicNbConflictPieceV1, nbIter, saveFile)

    print("\nTest de solverHeuristique1Deep avec heuristicNbConflictPieceV2 :")
    runTest(puzzle, solverHeuristique1Deep, heuristicNbConflictPieceV2, nbIter, saveFile)

    print("\nTest de solverHeuristique1DeepEdgeFirst avec heuristicNbConflictPieceV3 :")
    runTest(puzzle, solverHeuristique1DeepEdgeFirst, heuristicNbConflictPieceV3, nbIter, saveFile)

    print("\nTest de solverHeuristique1DeepEdgeFirstV2 avec heuristicNbConflictPieceV3 :")
    runTest(puzzle, solverHeuristique1DeepEdgeFirstV2, heuristicNbConflictPieceV3, nbIter, saveFile)


def runTest(eternityPuzzle, algorithme, heuristique, nbIter, saveFile=None):
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

    # Sauvegarde des résultats
    if saveFile is not None:
        with open(saveFile, "a", encoding="utf-8") as file:
            file.write(f"Algorithme : {algorithme.__name__} / Heuristique : {heuristique.__name__}\n")
            file.write(f"Moyenne des conflits : {sommeConflit / nbIter}\n")
            file.write(f"Meilleur score : {best}\n")
            file.write(f"Temps d'exécution :  {round(time.time() - start, 2)} secondes\n")
            file.write(f"Temps d'exécution moyen : {round((time.time() - start) / nbIter, 2)} secondes\n\n")


def parse_arguments():
    parser = argparse.ArgumentParser()

    # Instances parameters
    parser.add_argument('--save', type=str, default='False')
    parser.add_argument('--outfile', type=str, default='test_results.txt')
    parser.add_argument('--nbIter', type=str, default='500')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()

    if args.nbIter.isnumeric():
        nbIter = int(args.nbIter)
    else:
        raise ValueError("Le nombre d'itérations doit être un nombre entier")

    # Sauvegarde ou non des résultats (sans prendre en compte les majuscules)
    if args.save.lower() == "true":
        print(f"Les résultats des tests seront sauvegardés dans le fichier {args.outfile}")
        runAllTests(True, args.outfile, nbIter)
    else:
        runAllTests(nbIter=nbIter)
