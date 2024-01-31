import time
import eternity_puzzle
from tqdm import tqdm
from algoHeuristic import solverHeuristique1Deep, solverHeuristique1DeepEdgeFirst, solverHeuristique1DeepEdgeFirstV2
from heuristiques import heuristicNbConflictPieceV1, heuristicNbConflictPieceV2, heuristicNbConflictPieceV3
from utils import INFINITY
import matplotlib.pyplot as plt
import argparse


def runAllTests(saveResult=False, saveFile=None, nbIter=1000, plot=False):
    instanceName = "eternity_complet.txt"
    puzzle = eternity_puzzle.EternityPuzzle("./instances/" + instanceName)

    # Ouverture et réinitialisation du fichier de sauvegarde si besoin
    if saveResult:
        with open(saveFile, "w", encoding="utf-8") as file:
            file.write(f"Résultats des tests pour l'instance : {instanceName}\nNombre d'itérations : {nbIter}\n\n")

    print(f"\nLancement des tests sur l'instance : {instanceName} / nombre d'itérations : {nbIter}")

    xName = []
    yResults = []
    print("\nTest de solverHeuristique1Deep avec heuristicNbConflictPieceV1 :")
    xName.append("SolveurV1 + HeuristiqueV1")
    yResults.append(runTest(puzzle, solverHeuristique1Deep, heuristicNbConflictPieceV1, nbIter, saveResult, saveFile))

    print("\nTest de solverHeuristique1Deep avec heuristicNbConflictPieceV2 :")
    xName.append("SolveurV1 + HeuristiqueV2")
    yResults.append(runTest(puzzle, solverHeuristique1Deep, heuristicNbConflictPieceV2, nbIter, saveResult, saveFile))

    print("\nTest de solverHeuristique1DeepEdgeFirst avec heuristicNbConflictPieceV3 :")
    xName.append("SolveurV2 + HeuristiqueV3")
    yResults.append(runTest(puzzle, solverHeuristique1DeepEdgeFirst, heuristicNbConflictPieceV3, nbIter, saveResult, saveFile))

    print("\nTest de solverHeuristique1DeepEdgeFirstV2 avec heuristicNbConflictPieceV3 :")
    xName.append("SolveurV3 + HeuristiqueV3")
    yResults.append(runTest(puzzle, solverHeuristique1DeepEdgeFirstV2, heuristicNbConflictPieceV3, nbIter, saveResult, saveFile))

    if plot:
        # Plot de 2 graphe partagent l'axe des abscisses. Le premier pour les moyennes et pour les meilleurs scores.
        # Le second pour les temps d'exécution.
        fig, ax1 = plt.subplots(figsize=(10, 7))
        ax2 = ax1.twinx()

        # Plot des scores
        ax1.bar(xName, [x[0] for x in yResults], color='b', label="Moyenne des conflits")
        ax1.bar(xName, [x[1] for x in yResults], color='r', label="Meilleur conflit")

        ax1.set_title(f"Résultats des tests pour l'instance : {instanceName}\nNombre d'itérations : {nbIter}")
        ax1.set_xlabel("Algorithme / Heuristique")
        ax1.set_ylabel("Nombre de conflits")

        # Ajout des valeurs sur les barres
        for i, v in enumerate([x[0] for x in yResults]):
            ax1.text(i, v - 5, str(round(v, 2)), ha='center', va='bottom', fontsize=10)
        for i, v in enumerate([x[1] for x in yResults]):
            ax1.text(i, v - 5, str(round(v, 2)), ha='center', va='bottom', fontsize=10)

        # Plot des temps d'exécution
        ax2.set_ylabel("Temps d'exécution moyen")

        ax2.plot(xName, [x[2] for x in yResults], color='g', label="Temps d'exécution moyen")

        # Affichages des légendes
        ax1.legend(loc="center left")
        ax2.legend(loc="center right")

        plt.tight_layout()
        # fig.autofmt_xdate()
        fig.savefig("plot_test_result.png")


def runTest(eternityPuzzle, algorithme, heuristique, nbIter, save=False,saveFile=None) -> (int, int):
    """
    Fonction qui lance un test sur un algorithme et une heuristique.
    :param eternityPuzzle:
    :param algorithme:
    :param heuristique:
    :param nbIter:
    :param saveFile:
    :return:
    """
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
            file.write(f"Moyenne des score : {sommeConflit / nbIter}\n")
            file.write(f"Meilleur score : {best}\n")
            file.write(f"Temps d'exécution :  {round(time.time() - start, 2)} secondes\n")
            file.write(f"Temps d'exécution moyen : {round((time.time() - start) / nbIter, 2)} secondes\n\n")

    return (sommeConflit / nbIter,
            best,
            round((time.time() - start) / nbIter, 2))


def parse_arguments():
    parser = argparse.ArgumentParser()

    # Instances parameters
    parser.add_argument('--save', type=str, default='False')
    parser.add_argument('--outfile', type=str, default='test_results.txt')
    parser.add_argument('--nbIter', type=str, default='500')
    parser.add_argument('--plot', type=str, default='False')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()

    if args.nbIter.isnumeric():
        nbIter = int(args.nbIter)
    else:
        raise ValueError("Le nombre d'itérations doit être un nombre entier")

    save = args.save.lower() == "true"
    plot = args.plot.lower() == "true"

    runAllTests(save, args.outfile, nbIter, plot)
