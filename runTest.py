import json
import time
import os

import matplotlib.ticker as ticker
import numpy as np

import eternity_puzzle
from tqdm import tqdm
from algoHeuristic import solverHeuristique1Deep, solverHeuristique1DeepEdgeFirst, solverHeuristique1DeepEdgeFirstV2
from heuristiques import heuristicNbConflictPieceV1, heuristicNbConflictPieceV2, heuristicNbConflictPieceV3
from algoLocalSearch import getVoisinageAllPermutAndRotations, getVoisinageOnlyConflictV1, getVoisinageOnlyConflictV2
from utils import INFINITY, getConflictPieces, saveBestSolution
import matplotlib.pyplot as plt
import argparse
import timeit


def runAllTests(saveResult=False, saveFile=None, nbIter=100, plot=False):
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
        ax2.set_ylabel("Temps d'exécution moyen [s]")
        ax2.margins(y=0.15)

        ax2.plot(xName, [x[2] for x in yResults], '-gD', linewidth=3, label="Temps d'exécution moyen")

        # Affichages des légendes
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")

        plt.tight_layout()
        # fig.autofmt_xdate()
        fig.savefig("plot_test_result_heuristique.png", dpi=250)


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
    bestSol = None
    start = time.time()
    for _ in tqdm(range(nbIter)):
        sol, nbConflict = algorithme(eternityPuzzle, heuristique)
        if nbConflict < best:
            best = nbConflict
            bestSol = sol

        sommeConflit += nbConflict
    print("- Moyenne des conflits : ", sommeConflit / nbIter)
    print("- Meilleur score : ", best)
    print(f"- Temps d'exécution :  {round(time.time() - start, 2)} secondes")
    print(f"- Temps d'exécution moyen : {round((time.time() - start) / nbIter, 2)} secondes")
    print("\n")

    logs = {"Algorithme": algorithme.__name__, "Heuristique": heuristique.__name__,
            "Moyenne des conflits": sommeConflit / nbIter, "Meilleur score": best,
            "Temps d'exécution": round(time.time() - start, 2),
            "Temps d'exécution moyen": round((time.time() - start) / nbIter, 4),
            "Nombre d'itérations": nbIter}

    saveBestSolution(eternityPuzzle, "heuristic", bestSol, best, logs)

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


def comparaisonScoreSolvers():

    # Chargement des données du fichier bestScores.json
    filePath = "savedBestSolutions/bestScores.json"
    with open(filePath, "r", encoding="utf-8") as file:
        dataRaw = json.load(file)

    instancesRaw = ['eternity_A.txt', 'eternity_B.txt', 'eternity_C.txt', 'eternity_D.txt', 'eternity_E.txt', 'eternity_complet.txt']
    instancesClean = ['A', 'B', 'C', 'D', 'E', 'Complet']
    solverRaw = ["random", "heuristic", "local_search", "advanced"]
    solverClean = ["Random", "Heuristique", "Recherche locale", "Métaheuristique"]
    dataClean = {}

    for instance in instancesRaw:
        dataClean[instance] = []

        for solver in solverRaw:
            dataClean[instance].append(dataRaw[solver][instance]["score"])

    # Création et affichage d'un graphe par instance avec les scores des solveurs
    fig, axs = plt.subplots(3, 2, figsize=(15, 8))

    fig.suptitle("Comparaison des scores des solveurs pour chaque instance", fontsize=16)

    for idx, instance in enumerate(instancesRaw):
        ax = axs[idx // 2, idx % 2]

        ax.bar(solverClean, dataClean[instance], color=['blue', 'orange', 'green', 'red'], width=0.7)

        ax.set_title(f"Instance : {instancesClean[idx]}")
        ax.set_ylabel("Nb conflits")

        # ajout du pourcentage de différence entre les solveurs
        prcts = [0]
        for i in range(1, 4):
            diff = dataClean[instance][i-1] - dataClean[instance][i]
            if dataClean[instance][i-1] != 0:
                prct = (diff / dataClean[instance][i-1]) * 100
            else:
                prct = 0
            prcts.append(prct)

        ax_prct = ax.twinx()
        ax_prct.plot(solverClean, prcts, '--ro', linewidth=1, label="Diff solveur précédent")
        ax_prct.set_ylabel("%")
        ax_prct.margins(y=0.35)
        ax_prct.legend(loc="upper right")

        # Ajout d'une marge pour qu'on puisse voir les valeurs
        ax.margins(y=0.15)

        # Ajout des valeurs sur les barres
        for i, v in enumerate(dataClean[instance]):
            ax.text(i, v + 1, str(v), ha='center', va='bottom', fontsize=10)

    # Sauvegarde du graphe
    plt.tight_layout()

    plt.show()
    fig.savefig("plots/global/comparaisonSolver.png", dpi=250)


def timeComplexityLNS():
    instancesRaw = ['eternity_B.txt', 'eternity_C.txt', 'eternity_D.txt', 'eternity_E.txt',
                    'eternity_complet.txt']

    instancesClean = ['B - 7x7', 'C - 8x8', 'D - 9x9', 'E - 10x10', 'Complet - 16x16']

    tailleInstance = [7, 8, 9, 10, 16]

    # pour chaque instance raw, on va chercher les runs dans les logs qui comportent le tag "test" et récupérer la données
    # "NbIter"

    logRoot = "logResultats/advanced"

    nbiter = {}
    times = {}

    for instance in instancesRaw:
        nbiter[instance] = []
        times[instance] = []
        instanceLogs = os.path.join(logRoot, instance)
        # Ouverture du fichier de logs
        with open(instanceLogs, "r", encoding="utf-8") as file:
            data = file.readlines()

        for idx, line in enumerate(data):
            if line.find("tag : test") != -1:
                nbIter_ = int(data[idx+1].split(":")[1])
                nbiter[instance].append(nbIter_)
                times[instance].append(60/nbIter_)


    y_mean = [np.mean(i) for i in times.values()]

    totalIter = 0
    for idx, instance in enumerate(instancesRaw):
        print(f"Instance : {instance}")
        print(f"Nombre de runs : {len(nbiter[instance])}")
        iters = sum(nbiter[instance])
        totalIter += iters
        print(f"Nombre total d'itérations : {iters}")
        print(f"Temps moyen : {y_mean[idx]}")

    print(f"Nombre total d'itérations (toutes les instances) : {totalIter}")

    # Création et affichage d'un graphe avec les temps d'exécution
    fig, ax = plt.subplots(figsize=(10, 7))

    # Regression polynomiale pour modéliser le temps de résolution
    # Degré du polynome
    deg = [1, 2, 3, 4]
    x_reg = np.linspace(7, max(tailleInstance), 100)

    x_train = tailleInstance
    y_train = y_mean
    print(y_train)

    # On crée un polynome pour chaque degré
    for d in deg:

        p = np.polyfit(x_train, y_train, d)
        f = np.poly1d(p)
        y_reg = f(x_reg)
        # Affichage de la fonction polynomiale
        print(f"\nRégression (degré {d}) : {f}")
        # Evaluation de la fonction polynomiale
        y_pred = f(x_train)
        # Calcul de l'erreur
        r_squared = 1 - (np.sum((y_mean - y_pred) ** 2) / np.sum((y_mean - np.mean(y_mean)) ** 2))

        ax.plot(x_reg, y_reg, label=f"Polynome degré {d} - R^2 : {round(r_squared, 4)}")


    #Affichage des temps moyens (en pointillé)
    # ax.plot(tailleInstance, y_mean, 'b--', label="Temps moyen")

    # Affichage de tous les échantillons (scatter plot)
    for i in range(len(tailleInstance)):
        ax.scatter([tailleInstance[i]]*len(times[instancesRaw[i]]), times[instancesRaw[i]], color='blue', s=10, alpha=0.40)

    # Affichage pour chaque x, de la valeur avec ecart type
    for i in range(len(tailleInstance)):
        label = "Temps execution moyen + Écart type" if i == 0 else None
        ax.errorbar(tailleInstance[i], y_mean[i], yerr=np.std(times[instancesRaw[i]]), fmt='o', color='red', label=label)

    # Formatage du label de l'axe des ordonnées en notation scientifique
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0e'))

    # Nom des instances ecris en abscisse
    ax.set_xticks(tailleInstance)
    ax.set_xticklabels(instancesClean)

    # Legendes et labels
    ax.set_xlabel('Taille de l\'instance - TxT')
    ax.set_ylabel('Temps moyen [s]')
    ax.set_title(f"Évolution du temps d'exécution moyen en fonction de la taille de l'instance - "
                 f"{len(nbiter[instancesRaw[0]])} runs / instance\n "
                 f"Nombre total d'itérations évaluées : {totalIter:,.0f}")
    ax.legend(loc="upper left")
    # Sauvegarde du graphe
    plt.tight_layout()

    plt.show()
    fig.savefig("plots/global/timeComplexityLNS", dpi=250)


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

    # runAllTests(False, None, 500, True)

    # instance = "eternity_E.txt"
    #
    # puzzle = eternity_puzzle.EternityPuzzle("./instances/" + instance)
    # runTest(puzzle, solverHeuristique1DeepEdgeFirstV2, heuristicNbConflictPieceV3, 200)
    # runTestTailleVoisinage()
    # runTestTempsVoisinage()

    # runTestVoisinage()

    # comparaisonScoreSolvers()

    timeComplexityLNS()
