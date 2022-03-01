import pygame
import random
from abc import abstractmethod

import maze.maze as m
import visual.colors as vc


class MazeBuilder:
    ALGORITHMS = []

    def __init__(self, num: int):
        self.num = num

        MazeBuilder.ALGORITHMS = {
            method_name.title().replace("_", " "): getattr(self, method)
            for method_name, method in zip(dir(self), dir(self))
            if callable(getattr(self, method_name))
            and not method_name.startswith("__")
            and method_name.lower() != "build"
        }

        self.algorithm = list(MazeBuilder.ALGORITHMS.values())[num]

    def build(self, maze: m.Maze) -> None:
        self.algorithm(maze)
        maze.is_built = True

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
            if Window.BUILD_ANIMATION:
                MazeDrawer.colorize_cell(current_cell)

            if current_cell.has_unvisited_neighbors():
                stack.append(current_cell)
                chosen_cell = random.choice(current_cell.get_unvisited_neighbors())
                current_cell.open_wall_with(chosen_cell)
                chosen_cell.set_visited(True)
                stack.append(chosen_cell)

            if Window.BUILD_ANIMATION:
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
        """A Star algorithm

        Args:
            maze (Maze): An untouched maze object to be built upon
        """
        pass


class Window:
    FPS = 60
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
    def __init__(
        self, maze_builder: MazeBuilder, maze_solver: MazeSolver, maze: m.Maze
    ):
        super().__init__()
        self.maze_builder = maze_builder
        self.maze_solver = maze_solver
        self.maze = maze
        pygame.display.set_caption(
            f"Gen: {list(MazeBuilder.ALGORITHMS.keys())[self.maze_builder.num]} - Solve: {list(MazeSolver.ALGORITHMS.keys())[self.maze_solver.num]}"
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
    def colorize_cell(cell: m.Cell) -> None:
        """Colorizes the cell according to its state"""
        if cell.visited and not cell.is_start and not cell.is_end:
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
        cell_width_height = (
            Window.HEIGHT - 100
        ) / maze.height  # Width and height of the cell

        center_x_start = Window.WIDTH / 2 - (maze.width * cell_width_height) / 2

        x_coord = center_x_start
        y_coord = 0

        for x in range(0, len(maze.cells)):
            for y in range(0, len(maze.cells[0])):
                cell = maze.cells[x][y]
                cell.x = x_coord
                cell.y = y_coord
                cell.length = cell_width_height

                if cell.top_wall:
                    MazeDrawer._draw_line(
                        (x_coord, y_coord),
                        (x_coord + cell_width_height, y_coord),
                    )
                if cell.bottom_wall:
                    MazeDrawer._draw_line(
                        (x_coord, y_coord + cell_width_height),
                        (x_coord + cell_width_height, y_coord + cell_width_height),
                    )
                if cell.left_wall:
                    MazeDrawer._draw_line(
                        (x_coord, y_coord),
                        (x_coord, y_coord + cell_width_height),
                    )
                if cell.right_wall:
                    MazeDrawer._draw_line(
                        (x_coord + cell_width_height, y_coord),
                        (x_coord + cell_width_height, y_coord + cell_width_height),
                    )
                x_coord += cell_width_height
            y_coord += cell_width_height
            x_coord = center_x_start

        MazeDrawer.draw_start_and_end_cells(maze)

    def handle_events(self) -> None:
        # Looking for any event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Window.RUNNING = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.maze.is_built:
                        self.maze_builder.build(self.maze)
                    if not self.maze.is_solved and self.maze.is_built:
                        self.maze_solver.solve(self.maze)

    def start(self) -> None:
        Window.RUNNING = True
        while Window.RUNNING:

            MazeDrawer.draw_maze(self.maze)

            self.handle_events()

            MazeDrawer.refresh_drawing_on_screen(self.maze)
