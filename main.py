import os
import maze.maze as m
import maze.maze_tools as mt
import visual.colors as vc

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from abc import abstractmethod


def main():

    # Intializing variables

    _ = mt.MazeBuilder(0)  # Needed to init the MazeBuilder.ALGORITHMS list
    _ = mt.MazeSolver(0)  # Needed to init the MazeSolver.ALGORITHMS list

    alg_gen, alg_sol, width, height = -1, -1, -1, -1
    build_anim, solve_anim = "", ""

    # Getting the user's inputs

    for i in range(len(mt.MazeBuilder.ALGORITHMS)):
        print(
            f"{vc.CMDColors.YELLOW} {i}: {list(mt.MazeBuilder.ALGORITHMS.keys())[i]} {vc.CMDColors.RESET}"
        )

    print()

    while alg_gen not in range(len(mt.MazeBuilder.ALGORITHMS)):
        alg_gen = int(input("Input the n° of the algorithm for the generation: "))

    print()

    for i in range(len(mt.MazeSolver.ALGORITHMS)):
        print(
            f"{vc.CMDColors.YELLOW} {i}: {list(mt.MazeSolver.ALGORITHMS.keys())[i]} {vc.CMDColors.RESET}"
        )

    print()

    while alg_sol not in range(len(mt.MazeSolver.ALGORITHMS)):
        alg_sol = int(input("Input the n° of the algorithm for the solving: "))

    print()

    while width not in range(1000):
        width = int(input("Width of the maze: "))

    while height not in range(1000):
        height = int(input("Height of the maze: "))

    print()

    while build_anim.lower() not in ["y", "n"]:
        build_anim = input("Enable animation for building? (Y/N): ")

    while solve_anim.lower() not in ["y", "n"]:
        solve_anim = input("Enable animation for solving? (Y/N): ")

    print()

    # Setting animation properties for pygame window
    mt.Window.BUILD_ANIMATION = True if build_anim.lower() == "y" else False
    mt.Window.SOLVE_ANIMATION = True if solve_anim.lower() == "y" else False

    # Showing the maze on the pygame window

    # Initializing
    maze = m.Maze(width, height)
    maze_builder = mt.MazeBuilder(alg_gen)
    maze_solver = mt.MazeSolver(alg_sol)

    # Building
    # maze_builder.build(maze)

    # Solving
    # maze_solver.solve(maze)

    # Drawing
    print(
        vc.CMDColors.CYAN
        + "Press "
        + vc.CMDColors.FAIL
        + "SPACE"
        + vc.CMDColors.CYAN
        + " to start building the maze.\nPress again to solve it.\nPress "
        + vc.CMDColors.HEADER
        + "CTRL+C"
        + vc.CMDColors.CYAN
        + " in the terminal to exit."
        + vc.CMDColors.RESET
    )
    maze_drawer = mt.MazeDrawer(maze_builder, maze_solver, maze)
    maze_drawer.start()


if __name__ == "__main__":
    main()
