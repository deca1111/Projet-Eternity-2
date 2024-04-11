from eternity_puzzle import EternityPuzzle
from colorama import Fore, Style
from solver_local_search import getInitialSolutionAndScore
from destructFct import *


if __name__ == '__main__':

    instance = "instances/eternity_B.txt"

    puzzle = EternityPuzzle(instance)

    initialSolution, initialScore = getInitialSolutionAndScore(puzzle)

    destroyedSol, _, _ = destructOnlyConflict(puzzle, initialSolution, 0.7)

    puzzle.display_solution(initialSolution, "initial_solution.png")

    puzzle.display_solution(destroyedSol, "partial.png")