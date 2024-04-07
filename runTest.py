import time

import numpy as np

import eternity_puzzle
from tqdm import tqdm
from algoHeuristic import solverHeuristique1Deep, solverHeuristique1DeepEdgeFirst, solverHeuristique1DeepEdgeFirstV2
from heuristiques import heuristicNbConflictPieceV1, heuristicNbConflictPieceV2, heuristicNbConflictPieceV3
from algoLocalSearch import getVoisinageAllPermutAndRotations, getVoisinageOnlyConflictV1, getVoisinageOnlyConflictV2
from utils import INFINITY, getConflictPieces
import matplotlib.pyplot as plt
import argparse
import timeit


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
    yResults.append(
        runTest(puzzle, solverHeuristique1DeepEdgeFirst, heuristicNbConflictPieceV3, nbIter, saveResult, saveFile))

    print("\nTest de solverHeuristique1DeepEdgeFirstV2 avec heuristicNbConflictPieceV3 :")
    xName.append("SolveurV3 + HeuristiqueV3")
    yResults.append(
        runTest(puzzle, solverHeuristique1DeepEdgeFirstV2, heuristicNbConflictPieceV3, nbIter, saveResult, saveFile))

    if plot:
        # Plot de 2 graphe partagent l'axe des abscisses. Le premier pour les moyennes et pour les meilleurs scores.
        # Le second pour les temps d'exécution.
        fig, ax1 = plt.subplots(figsize=(10, 7))
        ax2 = ax1.twinx()

        # Plot des scores
        ax1.plot(xName, [x[0] for x in yResults], '-bo', linewidth=3, label="Moyenne des conflits")
        ax1.plot(xName, [x[1] for x in yResults], '-r+', linewidth=3, label="Meilleur conflit")

        ax1.set_title(f"Résultats des tests pour l'instance : {instanceName}\nNombre d'itérations : {nbIter}")
        ax1.set_xlabel("Algorithme / Heuristique")
        ax1.set_ylabel("Nombre de conflits")
        ax1.margins(y=0.25)

        # Ajout des valeurs sur les points
        for i, v in enumerate([x[0] for x in yResults]):
            ax1.text(i, v + 1, str(round(v, 2)), ha='center', va='bottom', fontsize=10)
        for i, v in enumerate([x[1] for x in yResults]):
            ax1.text(i, v + 1, str(round(v, 2)), ha='center', va='bottom', fontsize=10)

        # Plot des temps d'exécution
        ax2.set_ylabel("Temps d'exécution moyen")
        ax2.margins(y=0.15)

        ax2.plot(xName, [x[2] for x in yResults], '-gD', linewidth=3, label="Temps d'exécution moyen")

        # Affichages des légendes
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")

        plt.tight_layout()
        # fig.autofmt_xdate()
        fig.savefig("plot_test_result.png", dpi=150)


def runTest(eternityPuzzle, algorithme, heuristique, nbIter, save=False, saveFile=None) -> (int, int):
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
    if saveFile is not None and save:
        with open(saveFile, "a", encoding="utf-8") as file:
            file.write(f"Algorithme : {algorithme.__name__} / Heuristique : {heuristique.__name__}\n")
            file.write(f"Moyenne des score : {sommeConflit / nbIter}\n")
            file.write(f"Meilleur score : {best}\n")
            file.write(f"Temps d'exécution :  {round(time.time() - start, 2)} secondes\n")
            file.write(f"Temps d'exécution moyen : {round((time.time() - start) / nbIter, 4)} secondes\n\n")

    return (sommeConflit / nbIter,
            best,
            round((time.time() - start) / nbIter, 4))


def parse_arguments():
    parser = argparse.ArgumentParser()

    # Instances parameters
    parser.add_argument('--save', type=str, default='False')
    parser.add_argument('--outfile', type=str, default='test_results.txt')
    parser.add_argument('--nbIter', type=str, default='500')
    parser.add_argument('--plot', type=str, default='False')

    return parser.parse_args()


def runTestTempsVoisinage():
    np.random.seed(99)
    instanceName = "eternity_complet.txt"
    global puzzle, currentSolution
    puzzle = eternity_puzzle.EternityPuzzle("./instances/" + instanceName)
    currentSolution, currentCost = solverHeuristique1DeepEdgeFirstV2(puzzle, heuristicNbConflictPieceV3)

    n = 100

    timeGetVoisinageAllPermutAndRotations = timeit.timeit(stmt="getVoisinageAllPermutAndRotations(puzzle, "
                                                               "currentSolution)", globals=globals(), number=n)

    timeGetVoisinageOnlyConflictV1 = timeit.timeit(stmt="getVoisinageOnlyConflictV1(puzzle, currentSolution)",
                                                   globals=globals(), number=n)

    timeGetVoisinageOnlyConflictV2 = timeit.timeit(stmt="getVoisinageOnlyConflictV2(puzzle, currentSolution)",
                                                   globals=globals(), number=n)

    print(f"Comparaison des temps d'exécution pour {n} itérations :")
    print("- getVoisinageAllPermutAndRotations : %E seconds" % (timeGetVoisinageAllPermutAndRotations / n))
    print("- getVoisinageOnlyConflictV1 : %E seconds" % (timeGetVoisinageOnlyConflictV1 / n))
    print("- getVoisinageOnlyConflictV2 : %E seconds" % (timeGetVoisinageOnlyConflictV2 / n))

    # Création et affichage d'un graphe avec les temps d'exécution
    fig, ax = plt.subplots(figsize=(10, 7))

    # plot des temps d'exécution
    ax.plot(["getVoisinageAllPermutAndRotations", "getVoisinageOnlyConflictV1", "getVoisinageOnlyConflictV2"],
            [timeGetVoisinageAllPermutAndRotations / n,
             timeGetVoisinageOnlyConflictV1 / n,
             timeGetVoisinageOnlyConflictV2 / n],
            '-bo', linewidth=3)

    # Ajout des valeurs sur les points
    ax.text(0, timeGetVoisinageAllPermutAndRotations / n, f"{(timeGetVoisinageAllPermutAndRotations / n):.2E}\n",
            ha='center', va='bottom', fontsize=10)
    ax.text(1, timeGetVoisinageOnlyConflictV1 / n, f"{(timeGetVoisinageOnlyConflictV1 / n):.2E}\n", ha='center',
            va='bottom', fontsize=10)
    ax.text(2, timeGetVoisinageOnlyConflictV2 / n, f"{(timeGetVoisinageOnlyConflictV2 / n):.2E}\n", ha='center',
            va='bottom', fontsize=10)

    ax.set_title(
        f"Comparaison des temps d'exécution moyens des fonction de voisinage \n{n} itérations - Instance : {instanceName}")
    ax.set_ylabel("Temps d'exécution")

    # Ajout de marges pour une meilleure visibilité du texte
    ax.margins(x=0.15, y=0.15)

    plt.show()
    fig.savefig("plot_time_voisinage.png", dpi=150)


def runTestTailleVoisinage():
    instanceName = "eternity_complet.txt"
    puzzle = eternity_puzzle.EternityPuzzle("./instances/" + instanceName)

    n = 10
    tailleVoisGetVoisinageAllPermutAndRotations = 0
    tailleVoisGetVoisinageOnlyConflictV1 = 0
    tailleVoisGetVoisinageOnlyConflictV2 = 0
    for _ in range(n):
        currentSolution, currentCost = solverHeuristique1DeepEdgeFirstV2(puzzle, heuristicNbConflictPieceV3)

        tailleVoisGetVoisinageAllPermutAndRotations += len(getVoisinageAllPermutAndRotations(puzzle, currentSolution))

        tailleVoisGetVoisinageOnlyConflictV1 += len(getVoisinageOnlyConflictV1(puzzle, currentSolution))

        tailleVoisGetVoisinageOnlyConflictV2 += len(getVoisinageOnlyConflictV2(puzzle, currentSolution))

    # Création et affichage d'un graphe avec les tailles de voisinages
    fig, ax = plt.subplots(figsize=(10, 7))

    # plot des tailles de voisinages
    ax.plot(["getVoisinageAllPermutAndRotations", "getVoisinageOnlyConflictV1", "getVoisinageOnlyConflictV2"],
            [tailleVoisGetVoisinageAllPermutAndRotations / n,
             tailleVoisGetVoisinageOnlyConflictV1 / n,
             tailleVoisGetVoisinageOnlyConflictV2 / n],
            '-bo', linewidth=3)

    # Ajout des valeurs sur les points
    ax.text(0, tailleVoisGetVoisinageAllPermutAndRotations / n,
            f"{(tailleVoisGetVoisinageAllPermutAndRotations / n):.2f}\n",
            ha='center', va='bottom', fontsize=10)
    ax.text(1, tailleVoisGetVoisinageOnlyConflictV1 / n, f"{(tailleVoisGetVoisinageOnlyConflictV1 / n):.2f}\n",
            ha='center',
            va='bottom', fontsize=10)
    ax.text(2, tailleVoisGetVoisinageOnlyConflictV2 / n, f"{(tailleVoisGetVoisinageOnlyConflictV2 / n):.2f}\n",
            ha='center',
            va='bottom', fontsize=10)

    ax.set_title(f"Comparaison des tailles de voisinages moyennes \n{n} itérations - Instance : {instanceName}")
    ax.set_ylabel("Taille du voisinage")

    # Ajout de marges pour une meilleure visibilité du texte
    ax.margins(x=0.15, y=0.15)

    plt.show()
    fig.savefig("plot_taille_voisinage.png", dpi=150)


def runTestVoisinage():
    instanceName = "eternity_C.txt"
    global puzzle, currentSolution, time
    puzzle = eternity_puzzle.EternityPuzzle("./instances/" + instanceName)

    fctToTest = [getVoisinageAllPermutAndRotations, getVoisinageOnlyConflictV1, getVoisinageOnlyConflictV2]

    nbIter = 50

    tailleVoisinage = [0 for _ in range(len(fctToTest))]

    timeVoisinage = [0 for _ in range(len(fctToTest))]

    timeFindAmeliorant = [0 for _ in range(len(fctToTest))]

    nbAmeliorant = [0 for _ in range(len(fctToTest))]

    for idx in range(nbIter):
        print(f"Iteration {idx+1}/{nbIter}")
        currentSolution, currentCost = solverHeuristique1DeepEdgeFirstV2(puzzle, heuristicNbConflictPieceV3)

        for index, fctVoisinage in enumerate(fctToTest):
            startTime = time.time()
            voisinage = fctVoisinage(puzzle, currentSolution)
            endTime = time.time()

            timeVoisinage[index] += endTime - startTime
            tailleVoisinage[index] += len(voisinage)

            ameliorant = 0
            startTime = time.time()
            endTime = None
            for voisin in voisinage:
                if puzzle.get_total_n_conflict(voisin) < currentCost:
                    ameliorant += 1
                    if endTime is None:
                        endTime = time.time()
            if endTime is None:
                endTime = time.time()

            timeFindAmeliorant[index] += endTime - startTime

            nbAmeliorant[index] += ameliorant

    print(f"Comparaison des tailles de voisinages pour {nbIter} itérations :")
    for index, fct in enumerate(fctToTest):
        print(f"- {fct.__name__} : {tailleVoisinage[index] / nbIter}")

    print(f"\nComparaison des temps d'exécution pour {nbIter} itérations :")
    for index, fct in enumerate(fctToTest):
        print(f"- {fct.__name__} : {timeVoisinage[index] / nbIter}")

    print(f"\nComparaison des nombres de voisins améliorants pour {nbIter} itérations :")
    for index, fct in enumerate(fctToTest):
        print(f"- {fct.__name__} : {nbAmeliorant[index] / nbIter}")

    # Plot de 2 graphe partagent l'axe des abscisses. Le premier pour les temps d'execution et le second pour les
    # tailles des voisinnages.

    fig, (ax1, ax3) = plt.subplots(2, sharex=True, figsize=(10, 7))

    fig.suptitle(f"Comparaison des fonctions de voisinage - {nbIter} itérations\nInstance : {instanceName}")

    # ax2 = ax1.twinx()
    ax4 = ax3.twinx()

    ax1.plot([fct.__name__ for fct in fctToTest], [time_ / nbIter for time_ in timeVoisinage], '-bo', linewidth=2, label=f"Temps moyen d'exécution")

    ax1.plot([fct.__name__ for fct in fctToTest], [time_ / nbIter for time_ in timeFindAmeliorant], '-ko', linewidth=2, label=f"Temps moyen trouver 1er améliorant")

    # Ajout des valeurs sur les points

    for i, time_ in enumerate(timeVoisinage):
        ax1.text(i, time_ / nbIter, f"{(time_ / nbIter):.2E}s\n", ha='center', va='bottom', fontsize=10)

    for i, time_ in enumerate(timeFindAmeliorant):
        ax1.text(i, time_ / nbIter, f"{(time_ / nbIter):.2E}s\n", ha='center', va='bottom', fontsize=10)

    ax1.set_title(f"Temps d'exécution")
    ax1.set_ylabel("[s]")
    ax1.set_yscale('log')

    # Plot des tailles de voisinages
    ax3.plot([fct.__name__ for fct in fctToTest], [taille / nbIter for taille in tailleVoisinage], '-ro', linewidth=2, label=f"Taille moyenne du voisinage")

    ax4.plot([fct.__name__ for fct in fctToTest], [(nbAmeliorant[i] / tailleVoisinage[i]) * 100 for i in range(len(tailleVoisinage))], '-go', linewidth=2, label=f"% voisins améliorants")

    # Ajout des valeurs sur les points
    for i, taille in enumerate(tailleVoisinage):
        ax3.text(i, taille / nbIter, f"{int(taille / nbIter)}\n", ha='center', va='bottom', fontsize=10)

    for i, nbAmel in enumerate(nbAmeliorant):
        prct = (nbAmel / tailleVoisinage[i]) * 100
        ax4.text(i, prct, f"{(prct):.3f}%\n", ha='center', va='bottom', fontsize=10)

    ax3.set_title(f"Taille du voisinage")
    ax3.set_ylabel("[Nombre d'éléments]")
    ax4.set_ylabel("[%]")

    # Ajout de marges pour une meilleure visibilité du texte
    ax1.margins(x=0.15, y=0.2)
    ax3.margins(x=0.15, y=0.2)
    ax4.margins(x=0.15, y=0.2)

    # Affichages des légendes
    ax1.legend(loc="upper right")
    ax3.legend(loc="lower left")
    ax4.legend(loc="lower right")

    plt.tight_layout()

    plt.show()
    fig.savefig("plot_voisinage_v2.png", dpi=250)


if __name__ == '__main__':
    # args = parse_arguments()
    #
    # if args.nbIter.isnumeric():
    #     nbIter = int(args.nbIter)
    # else:
    #     raise ValueError("Le nombre d'itérations doit être un nombre entier")
    #
    # save = args.save.lower() == "true"
    # plot = args.plot.lower() == "true"
    #
    # runAllTests(save, args.outfile, nbIter, plot)

    # runTestTailleVoisinage()
    # runTestTempsVoisinage()

    runTestVoisinage()
