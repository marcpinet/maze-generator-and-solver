import maze.maze as m
import maze.maze_tools as mt
import visual.colors as vc

from abc import abstractmethod


def ask_for_int(sentence: str) -> int:
    """
    Ask the user for an integer.
    """
    while True:
        try:
            return int(input(sentence))
        except ValueError:
            print("Invalid input. Please try again.")


def main():

    # Intializing variables

    _ = mt.MazeGenerator(0)  # Needed to init the MazeBuilder.ALGORITHMS list
    _ = mt.MazeSolver(0)  # Needed to init the MazeSolver.ALGORITHMS list

    alg_gen, alg_sol, width, height = -1, -1, -1, -1
    build_anim, solve_anim = "", ""

    # Getting the user's inputs

    for i in range(len(mt.MazeGenerator.ALGORITHMS)):
        print(
            f"{vc.CMDColors.YELLOW} {i}: {list(mt.MazeGenerator.ALGORITHMS.keys())[i]} {vc.CMDColors.RESET}"
        )

    print()

    while alg_gen not in range(len(mt.MazeGenerator.ALGORITHMS)):
        alg_gen = ask_for_int("Input the n° of the algorithm for the generation: ")

    print()

    for i in range(len(mt.MazeSolver.ALGORITHMS)):
        print(
            f"{vc.CMDColors.YELLOW} {i}: {list(mt.MazeSolver.ALGORITHMS.keys())[i]} {vc.CMDColors.RESET}"
        )

    print()

    while alg_sol not in range(len(mt.MazeSolver.ALGORITHMS)):
        alg_sol = ask_for_int("Input the n° of the algorithm for the solving: ")

    print()

    while width not in range(1000):
        width = ask_for_int("Width of the maze: ")

    while height not in range(1000):
        height = ask_for_int("Height of the maze: ")

    print()

    while build_anim.lower() not in ["y", "n"]:
        build_anim = input("Enable animation for building? (Y/N): ")

    while solve_anim.lower() not in ["y", "n"]:
        solve_anim = input("Enable animation for solving? (Y/N): ")

    print()

    # Setting animation properties for pygame window
    mt.Window.GENERATE_ANIMATION = True if build_anim.lower() == "y" else False
    mt.Window.SOLVE_ANIMATION = True if solve_anim.lower() == "y" else False

    # Showing the maze on the pygame window

    # Initializing
    maze = m.Maze(width, height)
    maze_generator = mt.MazeGenerator(alg_gen)
    maze_solver = mt.MazeSolver(alg_sol)

    # Drawing
    print(
        vc.CMDColors.CYAN
        + "Press "
        + vc.CMDColors.FAIL
        + "SPACE"
        + vc.CMDColors.CYAN
        + " to start building the maze.\nPress "
        + vc.CMDColors.FAIL
        + "SPACE"
        + vc.CMDColors.CYAN
        + " again to solve it.\nPress "
        + vc.CMDColors.HEADER
        + "CTRL+C"
        + vc.CMDColors.CYAN
        + " in the terminal to exit."
        + vc.CMDColors.RESET
    )

    # Starting the animations
    maze_drawer = mt.MazeDrawer(maze_generator, maze_solver, maze)
    maze_drawer.start()


if __name__ == "__main__":
    main()
