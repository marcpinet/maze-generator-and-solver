from collections import deque
import heapq

import os
import keyboard

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
import random
from abc import abstractmethod

import maze.maze as m
import visual.colors as vc


class SetTool:
    @staticmethod
    def belong_to_distinct_sets(
        sets: list[m.Cell], cell1: m.Cell, cell2: m.Cell
    ) -> bool:
        for set_ in sets:
            if cell1 in set_ and cell2 in set_:
                return False
        return True

    @staticmethod
    def join_sets(sets: list[m.Cell], cell1: m.Cell, cell2: m.Cell) -> None:
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


class MazeGenerator:
    ALGORITHMS = []

    def __init__(self, num: int):
        self.num = num

        # This block of code allows me to retreive every method of this class (except the "system" and hidden ones)
        MazeGenerator.ALGORITHMS = {
            method_name.title().replace("_", " "): getattr(self, method)
            for method_name, method in zip(dir(self), dir(self))
            if callable(getattr(self, method_name))
            and not method_name.startswith("__")
            and method_name.lower() != "generate"
        }

        self.algorithm = list(MazeGenerator.ALGORITHMS.values())[num]

    def generate(self, maze: m.Maze) -> None:
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
        chosen_cell = None

        while len(stack) != 0:

            current_cell = stack.pop()

            if current_cell.has_unvisited_neighbor():
                stack.append(current_cell)
                chosen_cell = random.choice(current_cell.get_unvisited_neighbors())
                current_cell.open_wall_with(chosen_cell)
                chosen_cell.set_visited(True)
                stack.append(chosen_cell)

            else:
                current_cell.used_but_not_visited()

            if Window.GENERATE_ANIMATION:
                MazeDrawer.colorize_all_cells(
                    [c for c in maze.get_cells() if c is not chosen_cell]
                )
                MazeDrawer.colorize_cell(
                    current_cell, imposed_color=vc.Color.BLUE, priority=1
                )
                MazeDrawer.refresh_drawing_on_screen(
                    maze
                )  # Needs to be here to refresh the drawing on screen each time

    @staticmethod
    def randomized_kruskal(maze: m.Maze) -> None:
        # Only for coloring
        visited_cells = []

        sets = [[cell] for cell in maze.get_cells()]
        walls = maze.get_walls()

        random.shuffle(walls)
        while len(walls) > 0:
            current_wall = walls.pop()
            if SetTool.belong_to_distinct_sets(
                sets, current_wall.cell1, current_wall.cell2
            ):
                current_wall.open()
                SetTool.join_sets(sets, current_wall.cell1, current_wall.cell2)

            if Window.GENERATE_ANIMATION:

                visited_cells.append(current_wall.cell1)
                visited_cells.append(current_wall.cell2)
                current_wall.cell1.set_visited(True)
                current_wall.cell2.set_visited(True)

                MazeDrawer.colorize_all_cells(
                    visited_cells, imposed_color=vc.Color.YELLOW, priority=0
                )

                MazeDrawer.refresh_drawing_on_screen(
                    maze
                )  # Needs to be here to refresh the drawing on screen each time

    @staticmethod
    def randomized_prim(maze: m.Maze) -> None:

        # For colorizing
        visited_cells = []

        random_cell = random.choice(maze.get_cells())
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

            for cell in visited_cells_between_wall:
                cell.used_but_not_visited()

            if len(visited_cells_between_wall) == 1:
                random_wall.open()
                random_wall.cell1.set_visited(True)
                random_wall.cell2.set_visited(True)
                wall_list += random_wall.cell1.get_closed_walls()
                wall_list += random_wall.cell2.get_closed_walls()

                # Because we don't want visited_cell to be None
                if Window.GENERATE_ANIMATION:

                    for cell in random_wall.get_cells():
                        visited_cells.append(cell)

                    tmp = visited_cells.copy()

                    for cell in tmp:
                        if cell.number_of_uses > 1:
                            visited_cells.remove(cell)

                    MazeDrawer.colorize_all_cells(visited_cells)
                    MazeDrawer.refresh_drawing_on_screen(
                        maze
                    )  # Needs to be here to refresh the drawing on screen each time

            wall_list.remove(random_wall)

    @staticmethod
    def aldous_broder(maze: m.Maze) -> None:

        # For colorizing
        visited_cells = []

        current_cell = random.choice(maze.get_cells())
        current_cell.set_visited(True)

        while maze.has_unvisited_cells():

            if Window.GENERATE_ANIMATION:
                visited_cells.append(current_cell)

                tmp = visited_cells.copy()

                for cell in tmp:
                    if cell.number_of_uses > 1:
                        visited_cells.remove(cell)

                MazeDrawer.colorize_all_cells(visited_cells)
                MazeDrawer.colorize_cell(
                    current_cell, imposed_color=vc.Color.BLUE, priority=1
                )
                MazeDrawer.refresh_drawing_on_screen(
                    maze
                )  # Needs to be here to refresh the drawing on screen each time

            random_neighbor = random.choice(current_cell.get_neighbors())

            if not random_neighbor.is_visited:
                current_cell.open_wall_with(random_neighbor)
                random_neighbor.set_visited(True)
            else:
                current_cell.used_but_not_visited()

            current_cell = random_neighbor

    @staticmethod
    def eller(maze: m.Maze) -> None:

        row_number = 0

        while row_number < maze.height - 1:
            row = [[cell] for cell in maze.cells[row_number]]
            sets = []

            # Randomly joining cells in distinct sets
            i = 0
            sets.append(row[0])
            row.remove(row[0])
            for set_ in row:
                if random.getrandbits(1):
                    sets[i].extend(set_)
                else:
                    sets.append(set_)
                    i += 1

            for i in range(0, len(sets)):

                # Determining vertical connections and appending newly connected cell to the corresponding sets
                random_vertical_connection = random.randint(0, len(sets[i]) - 1)
                chosen_cell = sets[i][random_vertical_connection]
                chosen_cell.open_wall_with(chosen_cell.bottom_cell)
                sets[i].append(chosen_cell.bottom_cell)

                for j in range(0, len(sets[i]) - 1):
                    sets[i][j].set_visited(True)

                    # Opening the walls between adjacent cells in same set
                    if len(sets[i]) > 1:
                        sets[i][j].open_wall_with(sets[i][j + 1])

                    if Window.GENERATE_ANIMATION:
                        MazeDrawer.colorize_all_cells(
                            [cell for cell in maze.cells[row_number] if cell.is_visited]
                        )
                        MazeDrawer.colorize_cell(
                            sets[i][0], imposed_color=vc.Color.BLUE, priority=1
                        )
                        MazeDrawer.refresh_drawing_on_screen(maze)

            row_number += 1

        # Handling last row
        sets = [cell for cell in maze.cells[-1]]

        # Joining ALL adjacent sets of cells
        for i in range(0, maze.width - 1):
            sets[i].set_visited(True)

            # Opening the walls between adjacent cells in same set
            if i < maze.width:
                sets[i].open_wall_with(sets[i + 1])

            if Window.GENERATE_ANIMATION:
                MazeDrawer.colorize_all_cells(
                    [cell for cell in maze.cells[-1] if cell.is_visited]
                )
                MazeDrawer.colorize_cell(
                    sets[i], imposed_color=vc.Color.BLUE, priority=1
                )
                MazeDrawer.refresh_drawing_on_screen(maze)

    @staticmethod
    def hunt_and_kill(maze: m.Maze) -> None:
        current_cell = maze.cells[0][0]

        while maze.has_unvisited_cells():
            current_cell.set_visited(True)

            # Performing a random walk until no neighbor is found
            while current_cell.has_unvisited_neighbor():
                if not current_cell.is_visited:
                    current_cell.set_visited(True)

                random_neighbor = random.choice(current_cell.get_unvisited_neighbors())
                current_cell.open_wall_with(random_neighbor)
                current_cell = random_neighbor

                if Window.GENERATE_ANIMATION:
                    MazeDrawer.colorize_all_cells(
                        [cell for cell in maze.get_cells() if cell.is_visited]
                    )
                    MazeDrawer.colorize_cell(
                        current_cell, imposed_color=vc.Color.BLUE, priority=1
                    )
                    MazeDrawer.refresh_drawing_on_screen(maze)

            # Scan the whole maze to look for an unvisited cell that is adjacent to a visited cell
            for cell in maze.get_cells():
                if not cell.is_visited:
                    current_cell = cell
                    current_cell.open_wall_with(
                        random.choice(current_cell.get_visited_neighbors())
                    )
                    if Window.GENERATE_ANIMATION:
                        MazeDrawer.colorize_all_cells(
                            [c for c in maze.get_cells() if c.is_visited]
                        )
                        MazeDrawer.colorize_cell(
                            current_cell, imposed_color=vc.Color.BLUE, priority=1
                        )
                        MazeDrawer.colorize_all_cells(
                            [
                                c
                                for c in maze.cells[
                                    maze.get_flat_coords(current_cell)[0]
                                ]
                                if maze.get_flat_coords(c)[1]
                                <= maze.get_flat_coords(current_cell)[1]
                            ],
                            imposed_color=vc.Color.GREEN,
                            priority=2,
                        )
                        MazeDrawer.refresh_drawing_on_screen(maze)

                    break

    @staticmethod
    def binary_tree(maze: m.Maze) -> None:
        for cell in maze.get_cells():
            top_and_left_neighbors = [cell.top_cell, cell.left_cell]
            top_and_left_neighbors = list(
                filter(lambda x: x is not None, top_and_left_neighbors)
            )

            if len(top_and_left_neighbors) == 0:
                continue

            toss_coin = random.randint(0, len(top_and_left_neighbors) - 1)
            cell.open_wall_with(top_and_left_neighbors[toss_coin])

            if Window.GENERATE_ANIMATION:
                MazeDrawer.colorize_cell(cell, imposed_color=vc.Color.BLUE, priority=1)
                MazeDrawer.refresh_drawing_on_screen(maze)

    @staticmethod
    def sidewinder(maze: m.Maze) -> None:
        run_set = []

        for cell in maze.get_cells():

            # First row case
            if cell.top_cell is None and cell.right_cell is not None:
                cell.open_wall_with(cell.right_cell)
                continue
            elif cell.top_cell is None and cell.right_cell is None:
                continue

            # First case of each row
            if cell.left_cell is None:
                run_set = [cell]

            # Other cells of each row
            if random.getrandbits(1):
                if cell.right_cell is not None:
                    cell.open_wall_with(cell.right_cell)
                    run_set.append(cell.right_cell)
                else:
                    chosen_cell = random.choice(run_set)
                    chosen_cell.open_wall_with(chosen_cell.top_cell)
            else:
                chosen_cell = random.choice(run_set)
                chosen_cell.open_wall_with(chosen_cell.top_cell)
                last_cell = run_set[-1].right_cell
                run_set = [last_cell]

            # Visual
            if Window.GENERATE_ANIMATION:
                MazeDrawer.colorize_cell(cell, imposed_color=vc.Color.BLUE, priority=1)
                MazeDrawer.refresh_drawing_on_screen(maze)


class MazeSolver:
    ALGORITHMS = []

    def __init__(self, num: int):
        self.num = num

        # This block of code allows me to retreive every method of this class (except the "system" and hidden ones)
        MazeSolver.ALGORITHMS = {
            method_name.title().replace("_", " "): getattr(self, method)
            for method_name, method in zip(dir(self), dir(self))
            if callable(getattr(self, method_name))
            and not method_name.startswith("_")
            and method_name.lower() != "solve"
        }

        self.algorithm = list(MazeSolver.ALGORITHMS.values())[num]

    def solve(self, maze: m.Maze) -> list[m.Cell]:
        res = self.algorithm(maze)
        maze.is_solved = True
        return res

    @staticmethod
    def __reconstruct_path(cameFrom: dict, current: m.Cell) -> list[m.Cell]:
        total_path = [current]
        while current in cameFrom.keys():
            current = cameFrom[current]
            total_path.insert(0, current)
        return total_path

    @staticmethod
    def __heuristic(c1: m.Cell, c2: m.Cell) -> int:
        return abs(c1.x - c2.x) + abs(c1.y - c2.y)  # Manhattan distance

    @staticmethod
    def a_star(maze: m.Maze) -> list[m.Cell]:
        """A* algorithm

        Args:
            maze (Maze): An untouched maze object to be built upon

        Returns:
            list[Cell]: The shortest path found
        """

        start = maze.cells[0][0]
        goal = maze.cells[-1][-1]

        closedSet = set()
        openSet = {start}
        cameFrom = {}
        gScore = {start: 0}
        fScore = {start: MazeSolver.__heuristic(start, goal)}

        while len(openSet) > 0:
            current = min(openSet, key=lambda x: fScore[x])
            if current == goal:
                return MazeSolver.__reconstruct_path(cameFrom, current)

            openSet.remove(current)
            closedSet.add(current)

            for neighbor in current.get_neighbors_according_to_walls():
                if neighbor in closedSet:
                    continue

                tentative_gScore = gScore[current] + 1
                if neighbor not in openSet:
                    openSet.add(neighbor)
                elif tentative_gScore >= gScore[neighbor]:
                    continue

                cameFrom[neighbor] = current
                gScore[neighbor] = tentative_gScore
                fScore[neighbor] = gScore[neighbor] + MazeSolver.__heuristic(
                    neighbor, goal
                )

                if Window.SOLVE_ANIMATION:
                    MazeDrawer.colorize_cell(
                        current, imposed_color=vc.Color.BLUE, priority=3
                    )
                    MazeDrawer.colorize_all_cells(
                        list(closedSet),
                        imposed_color=vc.Color.GREEN,
                        priority=2,
                    )
                    MazeDrawer.colorize_all_cells(
                        list(openSet),
                        imposed_color=vc.Color.YELLOW,
                        priority=2,
                    )
                    MazeDrawer.refresh_drawing_on_screen(maze)

        return []

    @staticmethod
    def breadth_first_search(maze: m.Maze) -> list[m.Cell]:
        """Breadth-first search algorithm

        Args:
            maze (Maze): An untouched maze object to be built upon

        Returns:
            list[Cell]: The shortest path found
        """
        frontier = deque()
        frontier.append(maze.cells[0][0])

        came_from = {}
        came_from[maze.cells[0][0]] = None

        while len(frontier) > 0:

            current = frontier.popleft()
            if current == maze.cells[-1][-1]:
                return MazeSolver.__reconstruct_path(came_from, current)

            for neighbor in current.get_neighbors_according_to_walls():

                if neighbor not in came_from.keys():
                    frontier.append(neighbor)
                    came_from[neighbor] = current

                    if Window.SOLVE_ANIMATION:
                        MazeDrawer.colorize_all_cells(
                            list(came_from.keys()),
                            imposed_color=vc.Color.YELLOW,
                            priority=2,
                        )
                        MazeDrawer.colorize_all_cells(
                            [cell for cell in frontier] + [current],
                            imposed_color=vc.Color.BLUE,
                            priority=3,
                        )
                        MazeDrawer.refresh_drawing_on_screen(maze)
        return []

    @staticmethod
    def dijkstra(maze: m.Maze) -> list[m.Cell]:
        """Dijkstra algorithm

        Args:
            maze (Maze): An untouched maze object to be built upon

        Returns:
            list[Cell]: The shortest path found
        """
        
        pq = []  # min-heap priority queue
        start = maze.cells[0][0]
        goal = maze.cells[-1][-1]
        
        came_from = {}
        came_from[maze.cells[0][0]] = None
        
        # Setting every node distance to infinity
        for cell in maze.get_cells():
            cell.distance = float("inf")
           
        # Start to 0 
        start.distance = 0
        
        # maintain min-heap invariant (minimum d Vertex at list index 0)
        heapq.heappush(pq, (start.distance, start))
        
        while len(pq) > 0:
            current = heapq.heappop(pq)[1]
            if current == goal:
                return MazeSolver.__reconstruct_path(came_from, current)
            
            for neighbor in current.get_neighbors_according_to_walls():
                if neighbor.distance > current.distance + 1:
                    neighbor.distance = current.distance + 1
                    came_from[neighbor] = current
                    heapq.heappush(pq, (neighbor.distance, neighbor))
                    
                    if Window.SOLVE_ANIMATION:
                        MazeDrawer.colorize_all_cells(
                            list(came_from.keys()),
                            imposed_color=vc.Color.YELLOW,
                            priority=2,
                        )
                        MazeDrawer.colorize_all_cells(
                            [cell[1] for cell in pq] + [current],
                            imposed_color=vc.Color.BLUE,
                            priority=3,
                        )
                        MazeDrawer.refresh_drawing_on_screen(maze)
        return []
        
            
        


class Window:
    FPS = 30
    WIDTH = 800
    HEIGHT = 600
    SCREEN = None
    RUNNING = False
    CLOCK = None
    GENERATE_ANIMATION = True
    SOLVE_ANIMATION = True

    def __init__(self):
        pygame.init()
        Window.SCREEN = pygame.display.set_mode((Window.WIDTH, Window.HEIGHT))
        Window.SCREEN.fill(vc.Color.WHITE)
        pygame.display.set_caption("MazeGen&Solve")
        Window.RUNNING = False
        Window.CLOCK = pygame.time.Clock()
        
    @staticmethod
    def handle_speed_keys() -> None:
        """Must be in a loop"""
        dec = 0
        try:
            if keyboard.is_pressed("right"):
                if dec == 0:
                    Window.FPS += 1
                    dec += 1
                else:
                    dec += 1
            if keyboard.is_pressed("left"):
                if dec == 0:
                    Window.FPS -= 1
                    dec += 1
                else:
                    dec += 1
        except:
            pass

    @staticmethod
    def handle_quit_keyboard() -> None:
        """Must be put in a loop !!!!"""
        try:
            if keyboard.is_pressed("esc"):
                Window.RUNNING = False
                pygame.quit()
                quit()
        except:
            pass

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

        MazeDrawer.CELL_SIZE = min(
            (Window.HEIGHT - 100) / maze.height, (Window.WIDTH - 100) / maze.width
        )  # Width and height of the cell

        self.final_res = []

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
        Window.handle_quit_keyboard()
        Window.handle_speed_keys()

    @staticmethod
    def _draw_line(
        start_coords: tuple, end_coords: tuple, color: vc.Color = vc.Color.BLACK
    ) -> None:
        pygame.draw.line(Window.SCREEN, color, start_coords, end_coords)

    @staticmethod
    def colorize_all_cells(
        cells: list[m.Cell], imposed_color: vc.Color = None, priority: int = 0
    ) -> None:
        for cell in cells:
            MazeDrawer.colorize_cell(cell, imposed_color, priority)

    @staticmethod
    def colorize_cell(
        cell: m.Cell, imposed_color: vc.Color = None, priority: int = 0
    ) -> None:
        """Colorizes the cell according to its state"""
        spacement = 1

        if cell is not None:
            if imposed_color is not None:
                pygame.draw.rect(
                    Window.SCREEN,
                    imposed_color,
                    (
                        cell.x + spacement,
                        cell.y + spacement,
                        cell.length - spacement,
                        cell.length - spacement,
                    ),
                )

            if imposed_color is None or priority <= 0:
                if cell.is_visited and not cell.is_start and not cell.is_end:
                    if cell.number_of_uses == 1:
                        pygame.draw.rect(
                            Window.SCREEN,
                            vc.Color.YELLOW,
                            (
                                cell.x + spacement,
                                cell.y + spacement,
                                cell.length - spacement,
                                cell.length - spacement,
                            ),
                        )
                    # Will be used as a trick to colorize the cell again after passing on it again
                    else:
                        pygame.draw.rect(
                            Window.SCREEN,
                            vc.Color.WHITE,
                            (
                                cell.x + spacement,
                                cell.y + spacement,
                                cell.length - spacement,
                                cell.length - spacement,
                            ),
                        )

            if cell.is_start:
                pygame.draw.rect(
                    Window.SCREEN,
                    vc.Color.RED,
                    (cell.x, cell.y, cell.length, cell.length),
                )
            elif cell.is_end:
                pygame.draw.rect(
                    Window.SCREEN,
                    vc.Color.GREEN,
                    (cell.x, cell.y, cell.length, cell.length),
                )

    @staticmethod
    def draw_start_and_end_cells(maze) -> None:
        """Draws the start and end cells of the maze"""
        cells = maze.get_cells()
        for cell in cells:
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
                        print("\nGenerating...")
                        self.maze_generator.generate(self.maze)
                        print(vc.CMDColors.GREEN + "Generated!" + vc.CMDColors.RESET)
                    elif not self.maze.is_solved:
                        print("\nSolving...")
                        self.final_res = self.maze_solver.solve(self.maze)
                        print(vc.CMDColors.GREEN + "Solved!" + vc.CMDColors.RESET)

    def start(self) -> None:
        Window.RUNNING = True
        while Window.RUNNING:

            MazeDrawer.draw_maze(self.maze)

            self.handle_events()

            if self.maze.is_solved:
                Window.SOLVE_ANIMATION = False
                MazeDrawer.colorize_all_cells(
                    self.final_res, imposed_color=vc.Color.YELLOW
                )

            MazeDrawer.refresh_drawing_on_screen(self.maze)
