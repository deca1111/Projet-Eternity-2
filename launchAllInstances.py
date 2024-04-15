from solver_advanced import solve_advanced
import os

if __name__ == '__main__':

    # rootInstances = "instances"
    #
    # for instanceName in os.listdir(rootInstances):
    #
    #     instance = os.path.join(rootInstances, instanceName)
    #
    #     commande = f"python .\main.py --agent=advanced --infile={instance}"
    #
    #     # Execute the command
    #     os.system(commande)

    nbrep = 500
    for i in range(nbrep):
        commande = f"python .\main.py --agent=heuristic --infile=.\instances\eternity_complet.txt"
        os.system(commande)