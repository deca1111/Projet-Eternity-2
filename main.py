import argparse
import time
import eternity_puzzle
import solver_random
import solver_heuristic
import solver_local_search
import solver_advanced
import os


def parse_arguments():
    parser = argparse.ArgumentParser()

    # Instances parameters
    parser.add_argument('--agent', type=str, default='random')
    parser.add_argument('--infile', type=str, default='input')
    parser.add_argument('--outfile', type=str, default=None)
    parser.add_argument('--visufile', type=str, default=None)

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()

    if args.outfile is None:
        # Création d'un dossier de sortie en fonction de l'agent
        rootSol = "solutions"
        os.makedirs(os.path.join(rootSol, args.agent), exist_ok=True)

        fileName = "sol_" + args.infile.split('\\')[-1]
        filePath = os.path.join(rootSol, args.agent, fileName)
        args.outfile = filePath

    if args.visufile is None:
        # Création d'un dossier de sortie en fonction de l'agent
        rootVisu = "visualizations"
        os.makedirs(os.path.join(rootVisu, args.agent), exist_ok=True)

        fileName = "visu_" + (args.infile.split("\\")[-1]).split(".")[0] + ".png"
        filePath = os.path.join(rootVisu, args.agent, fileName)
        args.visufile = filePath


    e = eternity_puzzle.EternityPuzzle(args.infile)

    print("***********************************************************")
    print("[INFO] Start the solving Eternity II")
    print("[INFO] input file: %s" % args.infile)
    print("[INFO] output file: %s" % args.outfile)
    print("[INFO] visualization file: %s" % args.visufile)
    print("[INFO] board size: %s x %s" % (e.board_size,e.board_size))
    print("[INFO] solver selected: %s" % args.agent)
    print("***********************************************************")

    start_time = time.time()


    if args.agent == "random":
        # Take the best of 1,000,000 random trials
        solution, n_conflict = solver_random.solve_random(e)
    elif args.agent == "heuristic":
        # Agent based on a constructive heuristic (Phase 1)
        solution, n_conflict = solver_heuristic.solve_heuristic(e)
    elif args.agent == "local_search":
        # Agent based on a local search (Phase 2)
        solution, n_conflict = solver_local_search.solve_local_search(e)
    elif args.agent == "advanced":
        # Your nice agent (Phase 3 - main part of the project)
        solution, n_conflict = solver_advanced.solve_advanced(e)
    else:
        raise Exception("This agent does not exist")
    # solving_time = round((time.time() - start_time) / 60,2)
    solving_time = (time.time() - start_time)
    minutes = int(solving_time / 60)
    seconds = int(solving_time % 60)

    e.display_solution(solution,args.visufile)
    e.print_solution(solution, args.outfile)


    print("***********************************************************")
    print("[INFO] Solution obtained")
    print(f"[INFO] Execution time: {minutes} minutes and {seconds} seconds")
    print("[INFO] Number of conflicts: %s" % n_conflict)
    print("[INFO] Feasible solution: %s" % (n_conflict == 0))
    print("[INFO] Sanity check passed: %s" % e.verify_solution(solution))
    print("***********************************************************")
