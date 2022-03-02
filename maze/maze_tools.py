import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
import random
from abc import abstractmethod

import maze.maze as m
import visual.colors as vc


class MazeGenerator:
    ALGORITHMS = []

    def __init__(self, num: int):
        self.num = num

        MazeGenerator.ALGORITHMS = {
            method_name.title().replace("_", " "): getattr(self, method)
            for method_name, method in zip(dir(self), dir(self))
            if callable(getattr(self, method_name))
            and not method_name.startswith("__")
            and method_name.lower() != "build"
        }

        self.algorithm = list(MazeGenerator.ALGORITHMS.values())[num]

    def build(self, maze: m.Maze) -> None:
        self.algorithm(maze)
        maze.is_generated = True
        maze.reset_cells_state()

    @staticmethod
    def depth_first_search(maze: m.Maze) -> None:
        """Depth First Search algorithm (iterative, cuz the recursive one overflows the stack)

        Args:
            maze (Maze): An untouched maze object to be built upon
        """
        maze.cells[0][0].set_visited(True)
        stack = [maze.cells[0][0]]
        while len(stack) != 0:

            current_cell = stack.pop()

            if current_cell.has_unvisited_neighbors():
                stack.append(current_cell)
                chosen_cell = random.choice(current_cell.get_unvisited_neighbors())
                current_cell.open_wall_with(chosen_cell)
                chosen_cell.set_visited(True)
                stack.append(chosen_cell)

            if Window.BUILD_ANIMATION:
                MazeDrawer.colorize_cell(current_cell)
                MazeDrawer.refresh_drawing_on_screen(
                    maze
                )  # Needs to be here to refresh the drawing on screen each time

    @staticmethod
    def randomized_kruskal(maze: m.Maze) -> None:
        def __belong_to_distinct_sets(
            sets: list[m.Cell], cell1: m.Cell, cell2: m.Cell
        ) -> bool:
            for set_ in sets:
                if cell1 in set_ and cell2 in set_:
                    return False
            return True

        def __join_sets(sets: list[m.Cell], cell1: m.Cell, cell2: m.Cell) -> None:
            s = 0

            for i in range(0, len(sets)):
                if cell1 in sets[i]:
                    s = i
                    sets[i].append(cell2)
                    break
            for i in range(0, len(sets)):
                if cell2 in sets[i] and cell1 not in sets[i]:
                    # Merging the rest
                    for j in range(0, len(sets[i])):
                        if sets[i][j].id != cell2.id:
                            sets[s].append(sets[i][j])
                    del sets[i]
                    break

        sets = [[cell] for cell in maze.get_all_cells()]
        walls = maze.get_all_walls()
        random.shuffle(walls)
        while len(walls) > 0:
            current_wall = walls.pop()
            if __belong_to_distinct_sets(sets, current_wall.cell1, current_wall.cell2):
                current_wall.open()
                __join_sets(sets, current_wall.cell1, current_wall.cell2)

            if Window.BUILD_ANIMATION:
                MazeDrawer.colorize_cell(
                    current_wall.cell1, imposed_color=vc.Color.BLUE
                )
                MazeDrawer.colorize_cell(
                    current_wall.cell2, imposed_color=vc.Color.BLUE
                )
                MazeDrawer.refresh_drawing_on_screen(
                    maze
                )  # Needs to be here to refresh the drawing on screen each time

    @staticmethod
    def randomized_prim(maze: m.Maze) -> None:
        random_cell = random.choice(maze.get_all_cells())
        random_cell.set_visited(True)
        wall_list = []
        wall_list += (
            random_cell.get_closed_walls()
        )  # Merging both lists (reminder: [1, 2] + [3, 4] = [1, 2, 3, 4])

        visited_cells_between_wall = []

        while len(wall_list) > 0:
            random_wall = random.choice(wall_list)
            visited_cells_between_wall = [
                cell for cell in random_wall.get_cells() if cell.is_visited
            ]

            if len(visited_cells_between_wall) == 1:
                random_wall.open()
                random_wall.cell1.is_visited = True
                random_wall.cell2.is_visited = True
                wall_list += random_wall.cell1.get_closed_walls()
                wall_list += random_wall.cell2.get_closed_walls()

                # Because we don't want visited_cell to be None
                if Window.BUILD_ANIMATION:
                    MazeDrawer.colorize_cell(
                        visited_cells_between_wall[0], imposed_color=vc.Color.BLUE
                    )
                    MazeDrawer.refresh_drawing_on_screen(
                        maze
                    )  # Needs to be here to refresh the drawing on screen each time

            wall_list.remove(random_wall)

    @staticmethod
    def aldous_broder(maze: m.Maze) -> None:
        current_cell = random.choice(maze.get_all_cells())
        current_cell.set_visited(True)

        while maze.has_unvisited_cells():
            random_neighbor = random.choice(current_cell.get_neighbors())
            if not random_neighbor.is_visited:
                current_cell.open_wall_with(random_neighbor)
                random_neighbor.set_visited(True)
            current_cell = random_neighbor
            if Window.BUILD_ANIMATION:
                MazeDrawer.colorize_cell(current_cell, imposed_color=vc.Color.BLUE)
                MazeDrawer.refresh_drawing_on_screen(
                    maze
                )  # Needs to be here to refresh the drawing on screen each time


class MazeSolver:
    ALGORITHMS = []

    def __init__(self, num: int):
        self.num = num

        MazeSolver.ALGORITHMS = {
            method_name.title().replace("_", " "): getattr(self, method)
            for method_name, method in zip(dir(self), dir(self))
            if callable(getattr(self, method_name))
            and not method_name.startswith("__")
            and method_name.lower() != "solve"
        }

        self.algorithm = list(MazeSolver.ALGORITHMS.values())[num]

    def solve(self, maze: m.Maze) -> None:
        self.algorithm(maze)
        maze.is_solved = True

    @staticmethod
    def a_star(maze: m.Maze) -> None:
        """A* algorithm

        Args:
            maze (Maze): An untouched maze object to be built upon
        """
        maze.cells[0][0].set_visited(True)
        queue = [maze.cells[0][0]]
        while len(queue) != 0:
            current_cell = queue.pop(0)

            if current_cell.has_unvisited_neighbors():
                queue.append(current_cell)
                chosen_cell = random.choice(current_cell.get_unvisited_neighbors())
                current_cell.open_wall_with(chosen_cell)
                chosen_cell.set_visited(True)
                queue.append(chosen_cell)

            if Window.SOLVE_ANIMATION:
                MazeDrawer.colorize_cell(current_cell)
                MazeDrawer.refresh_drawing_on_screen(maze)


class Window:
    FPS = 30
    WIDTH = 800
    HEIGHT = 600
    SCREEN = None
    RUNNING = False
    CLOCK = None
    BUILD_ANIMATION = True
    SOLVE_ANIMATION = True

    def __init__(self):
        pygame.init()
        Window.SCREEN = pygame.display.set_mode((Window.WIDTH, Window.HEIGHT))
        Window.SCREEN.fill(vc.Color.WHITE)
        pygame.display.set_caption("MazeBuild&Solve")
        Window.RUNNING = False
        Window.CLOCK = pygame.time.Clock()

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError(
            "Not implemented abstract method for object type 'Window'"
        )

    @staticmethod
    def _refresh_background() -> None:
        Window.SCREEN.fill(vc.Color.WHITE)

    @staticmethod
    def refresh_all() -> None:
        pygame.event.pump()
        pygame.display.update()
        pygame.display.flip()
        Window._refresh_background()


class MazeDrawer(Window):
    CELL_SIZE = -1

    def __init__(
        self, maze_generator: MazeGenerator, maze_solver: MazeSolver, maze: m.Maze
    ):
        super().__init__()
        self.maze_generator = maze_generator
        self.maze_solver = maze_solver
        self.maze = maze

        MazeDrawer.CELL_SIZE = (
            Window.HEIGHT - 100
        ) / maze.height  # Width and height of the cell

        pygame.display.set_caption(
            f"Gen: {list(MazeGenerator.ALGORITHMS.keys())[self.maze_generator.num]} - Solve: {list(MazeSolver.ALGORITHMS.keys())[self.maze_solver.num]}"
        )

    @staticmethod
    def refresh_drawing_on_screen(maze: m.Maze) -> None:
        """Refreshes the drawing on screen and also does every related methods and functions to the refresh

        Args:
            maze (Maze): The maze to be drawn on screen
        """
        Window.CLOCK.tick(Window.FPS)  # Limit FPS
        Window.refresh_all()
        MazeDrawer.draw_maze(maze)

    @staticmethod
    def _draw_line(start_coords: tuple, end_coords: tuple) -> None:
        pygame.draw.line(Window.SCREEN, vc.Color.BLACK, start_coords, end_coords)

    @staticmethod
    def colorize_cell(cell: m.Cell, imposed_color: vc.Color = None) -> None:
        """Colorizes the cell according to its state"""

        if imposed_color is not None:
            pygame.draw.rect(
                Window.SCREEN, imposed_color, (cell.x, cell.y, cell.length, cell.length)
            )
        elif cell.is_visited and not cell.is_start and not cell.is_end:
            pygame.draw.rect(
                Window.SCREEN, vc.Color.BLUE, (cell.x, cell.y, cell.length, cell.length)
            )
        elif cell.is_start:
            pygame.draw.rect(
                Window.SCREEN, vc.Color.RED, (cell.x, cell.y, cell.length, cell.length)
            )
        elif cell.is_end:
            pygame.draw.rect(
                Window.SCREEN,
                vc.Color.GREEN,
                (cell.x, cell.y, cell.length, cell.length),
            )
        else:
            pygame.draw.rect(
                Window.SCREEN,
                vc.Color.WHITE,
                (cell.x, cell.y, cell.length, cell.length),
            )

    @staticmethod
    def draw_start_and_end_cells(maze) -> None:
        """Draws the start and end cells of the maze"""
        for row in maze.cells:
            for cell in row:
                if cell.is_start or cell.is_end:
                    MazeDrawer.colorize_cell(cell)

    @staticmethod
    def draw_maze(maze: m.Maze) -> None:
        """Draw the maze on pygame's window"""
        center_x_start = Window.WIDTH / 2 - (maze.width * MazeDrawer.CELL_SIZE) / 2

        x_coord = center_x_start
        y_coord = 0

        for x in range(0, len(maze.cells)):
            for y in range(0, len(maze.cells[0])):
                cell = maze.cells[x][y]
                cell.x = x_coord
                cell.y = y_coord
                cell.length = MazeDrawer.CELL_SIZE

                if not cell.top_wall.is_opened:
                    MazeDrawer._draw_line(
                        (x_coord, y_coord),
                        (x_coord + MazeDrawer.CELL_SIZE, y_coord),
                    )
                if not cell.bottom_wall.is_opened:
                    MazeDrawer._draw_line(
                        (x_coord, y_coord + MazeDrawer.CELL_SIZE),
                        (
                            x_coord + MazeDrawer.CELL_SIZE,
                            y_coord + MazeDrawer.CELL_SIZE,
                        ),
                    )
                if not cell.left_wall.is_opened:
                    MazeDrawer._draw_line(
                        (x_coord, y_coord),
                        (x_coord, y_coord + MazeDrawer.CELL_SIZE),
                    )
                if not cell.right_wall.is_opened:
                    MazeDrawer._draw_line(
                        (x_coord + MazeDrawer.CELL_SIZE, y_coord),
                        (
                            x_coord + MazeDrawer.CELL_SIZE,
                            y_coord + MazeDrawer.CELL_SIZE,
                        ),
                    )
                x_coord += MazeDrawer.CELL_SIZE
            y_coord += MazeDrawer.CELL_SIZE
            x_coord = center_x_start

        MazeDrawer.draw_start_and_end_cells(maze)

    def handle_events(self) -> None:
        # Looking for any event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Window.RUNNING = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.maze.is_generated:
                        print("Building...")
                        self.maze_generator.build(self.maze)
                    elif not self.maze.is_solved:
                        print("Solving...")
                        self.maze_solver.solve(self.maze)

    def start(self) -> None:
        Window.RUNNING = True
        while Window.RUNNING:

            MazeDrawer.draw_maze(self.maze)

            self.handle_events()

            MazeDrawer.refresh_drawing_on_screen(self.maze)
