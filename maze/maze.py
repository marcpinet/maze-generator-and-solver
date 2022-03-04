class Wall:
    def __init__(self):

        self.is_opened = False

        # Each wall separates a cell from another, except borders
        self.cell1 = None
        self.cell2 = None

    def is_border(self):
        """Checks if the wall is a border

        Returns:
            bool: True if the wall is a border, False otherwise
        """
        return self.cell1 is None and self.cell2 is None

    def open(self) -> None:
        """Opens the wall"""
        self.is_opened = True

    def close(self) -> None:
        """Closes the wall"""
        self.is_opened = False

    def get_cells(self) -> list["Cell"]:
        """Get all cells of the wall (both cells actually)

        Returns:
            list[Cell]: List of cells
        """
        return [self.cell1, self.cell2]


class Cell:
    NUMBER_OF_CELLS = 0

    def __init__(self):
        self.id = Cell.NUMBER_OF_CELLS
        Cell.NUMBER_OF_CELLS += 1

        # Will be filled when the maze will be built
        self.x = None
        self.y = None
        self.length = None

        self.top_cell = None
        self.bottom_cell = None
        self.left_cell = None
        self.right_cell = None
        self.top_wall = Wall()
        self.bottom_wall = Wall()
        self.left_wall = Wall()
        self.right_wall = Wall()

        self.is_visited = False
        self.is_start = False
        self.is_end = False
        self.is_colored = False
        self.distance = 0  # For Dijkstra algorithm

        self.number_of_uses = 0
        
    # Make cell hashable
    def __hash__(self):
        return hash(self.id)
    
    def __lt__(self, other):
        return False

    def __str__(self):
        return f"{self.id}"

    def __eq__(self, cell: "Cell"):
        if isinstance(cell, self.__class__):
            return self.id == cell.id
        return False
    
    def get_visited_neighbors(self) -> list["Cell"]:
        """Get all neighbors of the cell that are visited

        Returns:
            list[Cell]: List of visited neighbors
        """
        return list(filter(lambda c: c.is_visited, self.get_neighbors()))
    
    def has_visited_neighbor(self) -> bool:
        """Check if any neighbors are visited or not

        Returns:
            bool: True if there is at least one, else False
        """
        return len(self.get_visited_neighbors()) > 0

    def reset_state(self):
        self.is_visited = False

    def get_walls(self) -> list[Wall]:
        l = [self.top_wall, self.bottom_wall, self.left_wall, self.right_wall]

        return list(filter(lambda m: not m.is_border(), l))

    def get_opened_walls(self) -> list[Wall]:
        l = []
        if self.top_wall.is_opened:
            l.append(self.top_wall)
        if self.bottom_wall.is_opened:
            l.append(self.bottom_wall)
        if self.left_wall.is_opened:
            l.append(self.left_wall)
        if self.right_wall.is_opened:
            l.append(self.right_wall)

        return list(filter(lambda m: not m.is_border(), l))

    def get_closed_walls(self) -> list[Wall]:
        l = []
        if not self.top_wall.is_opened:
            l.append(self.top_wall)
        if not self.bottom_wall.is_opened:
            l.append(self.bottom_wall)
        if not self.left_wall.is_opened:
            l.append(self.left_wall)
        if not self.right_wall.is_opened:
            l.append(self.right_wall)

        return list(filter(lambda m: not m.is_border(), l))

    def is_edge_and_not_corner(self) -> bool:
        return self.is_edge() and not self.is_corner()

    def is_edge(self) -> bool:
        return (
            self.top_cell is None
            or self.bottom_cell is None
            or self.left_cell is None
            or self.right_cell is None
        )

    def is_corner(self) -> bool:
        return (
            (
                self.top_cell is None
                and self.bottom_cell is not None
                and self.left_cell is None
                and self.right_cell is not None
            )
            or (
                self.top_cell is None
                and self.bottom_cell is not None
                and self.left_cell is not None
                and self.right_cell is None
            )
            or (
                self.top_cell is not None
                and self.bottom_cell is None
                and self.left_cell is None
                and self.right_cell is not None
            )
            or (
                self.top_cell is not None
                and self.bottom_cell is None
                and self.left_cell is not None
                and self.right_cell is None
            )
        )

    def used_but_not_visited(self) -> bool:
        self.number_of_uses += 1

    def set_visited(self, visited: bool) -> None:
        """Sets the visited status of the cell

        Args:
            visited (bool): The visited status to set
        """
        self.is_visited = visited
        self.number_of_uses += 1

    def get_neighbors(self) -> list["Cell"]:
        """Returns a list of neighbors (not None) of the cell. The order of the return has a an importance to some point in the Eller algorithm

        Returns:
            list[Cell]: List of neighbors
        """
        l = []
        if self.left_cell is not None:
            l.append(self.left_cell)
        if self.right_cell is not None:
            l.append(self.right_cell)
        if self.top_cell is not None:
            l.append(self.top_cell)
        if self.bottom_cell is not None:
            l.append(self.bottom_cell)

        return l

    def get_neighbors_according_to_walls(self) -> list["Cell"]:
        """Get all neighbors of the cell according to the walls

        Returns:
            list[Cell]: List of neighbors according to the walls
        """
        l = []
        if self.top_cell is not None and self.top_wall.is_opened:
            l.append(self.top_cell)
        if self.bottom_cell is not None and self.bottom_wall.is_opened:
            l.append(self.bottom_cell)
        if self.left_cell is not None and self.left_wall.is_opened:
            l.append(self.left_cell)
        if self.right_cell is not None and self.right_wall.is_opened:
            l.append(self.right_cell)
        return l

    def has_unvisited_neighbor(self) -> bool:
        """Check if any neighbors are visited or not

        Returns:
            bool: True if there is at least one, else False
        """
        return len(self.get_unvisited_neighbors()) > 0

    def get_unvisited_neighbors(self) -> list["Cell"]:
        """Get all univisited neighbors of the cell (top, bottom, left and right)

        Returns:
            list["Cell"]: List of unvisited neighbors (cells)
        """
        neighbors = []
        if self.top_cell is not None and not self.top_cell.is_visited:
            neighbors.append(self.top_cell)
        if self.bottom_cell is not None and not self.bottom_cell.is_visited:
            neighbors.append(self.bottom_cell)
        if self.left_cell is not None and not self.left_cell.is_visited:
            neighbors.append(self.left_cell)
        if self.right_cell is not None and not self.right_cell.is_visited:
            neighbors.append(self.right_cell)
        return neighbors

    def open_wall_with(self, cell: "Cell") -> None:
        """Opens the wall in the given direction for both cells (method called and parameter one)

        Args:
            cell (Cell): The cell to open the wall with
        """
        if self.top_cell is cell:
            self.top_wall.open()
            cell.bottom_wall.open()
        elif self.bottom_cell is cell:
            self.bottom_wall.open()
            cell.top_wall.open()
        elif self.left_cell is cell:
            self.left_wall.open()
            cell.right_wall.open()
        elif self.right_cell is cell:
            self.right_wall.open()
            cell.left_wall.open()

    def get_direction(self, cell: "Cell") -> str:
        """Gets the direction to the given cell from this cell

        Args:
            cell (Cell): The cell to get the direction to

        Returns:
            str: The direction to the given cell or empty string if not found
        """
        if self.top_cell is cell:
            return "top"
        elif self.bottom_cell is cell:
            return "bottom"
        elif self.left_cell is cell:
            return "left"
        elif self.right_cell is cell:
            return "right"
        else:
            return ""


class Maze:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.cells = [[Cell() for _ in range(width)] for _ in range(height)]
        self.cells[0][0].is_start = True
        self.cells[-1][-1].is_end = True
        self.link_cells()
        self.link_walls()

        self.is_generated = False
        self.is_solved = False

    def __str__(self):
        s = ""
        for i in range(self.height):
            for j in range(self.width):
                s += str(self.cells[i][j])
            s += "\n"
        return s

    def link_cells(self) -> None:
        """Links all cells"""
        for i in range(self.height):
            for j in range(self.width):
                cell = self.cells[i][j]
                if i > 0:
                    cell.top_cell = self.cells[i - 1][j]
                if i < self.height - 1:
                    cell.bottom_cell = self.cells[i + 1][j]
                if j > 0:
                    cell.left_cell = self.cells[i][j - 1]
                if j < self.width - 1:
                    cell.right_cell = self.cells[i][j + 1]

    def reset_cells_state(self):
        """Resets the state of all cells"""
        for i in range(self.height):
            for j in range(self.width):
                self.cells[i][j].reset_state()

    def get_cells(self) -> list[Cell]:
        """Gets all cells

        Returns:
            list[Cell]: List of all cells
        """
        return [cell for row in self.cells for cell in row]

    def get_walls(self) -> list[Wall]:
        """Gets all walls of the maze

        Returns:
            list[Wall]: List of all walls
        """
        walls = []
        for i in range(self.height):
            for j in range(self.width):
                walls.append(self.cells[i][j].top_wall)
                walls.append(self.cells[i][j].bottom_wall)
                walls.append(self.cells[i][j].left_wall)
                walls.append(self.cells[i][j].right_wall)

        walls = list(
            filter(lambda k: walls.count(k) != 1, walls)
        )  # To remove the borders, because each border is in contact with one single cell

        # Now we remove occurrences of walls that are in contact with more than one cell (every wall is in contact with two cells or more lol)
        walls_without_duplicates = []
        for wall in walls:
            if wall not in walls_without_duplicates:
                walls_without_duplicates.append(wall)

        return list(filter(lambda m: not m.is_border(), walls_without_duplicates))

    def link_walls(self) -> None:
        """Links all walls"""
        for i in range(self.height):
            for j in range(self.width):
                cell = self.cells[i][j]
                if i > 0:
                    # Link the bottom wall of the cell above to the cell
                    cell.top_cell.bottom_wall.cell1 = cell
                    cell.top_cell.bottom_wall.cell2 = self.cells[i - 1][j]
                    cell.top_cell.bottom_wall = cell.top_wall
                if i < self.height - 1:
                    # Link the top wall of the cell above to the cell
                    cell.bottom_cell.top_wall.cell1 = cell
                    cell.bottom_cell.top_wall.cell2 = self.cells[i + 1][j]
                    cell.bottom_cell.top_wall = cell.bottom_wall
                if j > 0:
                    # Link the right wall of the cell above to the cell
                    cell.left_cell.right_wall.cell1 = cell
                    cell.left_cell.right_wall.cell2 = self.cells[i][j - 1]
                    cell.left_cell.right_wall = cell.left_wall
                if j < self.width - 1:
                    cell.right_cell.left_wall.cell1 = cell
                    cell.right_cell.left_wall.cell2 = self.cells[i][j + 1]
                    # Link the left wall of the cell above to the cell
                    cell.right_cell.left_wall = cell.right_wall

    def has_unvisited_cells(self) -> bool:
        cells = self.get_cells()
        for cell in cells:
            if not cell.is_visited:
                return True
        return False
    
    def get_flat_coords(self, cell: Cell) -> list[int]:
        for i in range(self.height):
            for j in range(self.width):
                if self.cells[i][j] is cell:
                    return [i, j]
        return [-1, -1]
