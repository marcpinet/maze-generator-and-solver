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
        self.top_wall = True
        self.bottom_wall = True
        self.left_wall = True
        self.right_wall = True

        self.visited = False
        self.is_start = False
        self.is_end = False

    def set_visited(self, visited: bool) -> None:
        """Sets the visited status of the cell

        Args:
            visited (bool): The visited status to set
        """
        self.visited = visited

    def has_unvisited_neighbors(self) -> bool:
        """Check if all neighbors are visited or not

        Returns:
            bool: True if there is at least one, else False
        """
        return (
            self.top_cell is not None
            and not self.top_cell.visited
            or self.bottom_cell is not None
            and not self.bottom_cell.visited
            or self.left_cell is not None
            and not self.left_cell.visited
            or self.right_cell is not None
            and not self.right_cell.visited
        )

    def get_unvisited_neighbors(self) -> list["Cell"]:
        """Get all univisited neighbors of the cell (top, bottom, left and right)

        Returns:
            list["Cell"]: List of unvisited neighbors (cells)
        """
        neighbors = []
        if self.top_cell is not None and not self.top_cell.visited:
            neighbors.append(self.top_cell)
        if self.bottom_cell is not None and not self.bottom_cell.visited:
            neighbors.append(self.bottom_cell)
        if self.left_cell is not None and not self.left_cell.visited:
            neighbors.append(self.left_cell)
        if self.right_cell is not None and not self.right_cell.visited:
            neighbors.append(self.right_cell)
        return neighbors

    def open_wall_with(self, cell: "Cell") -> None:
        """Opens the wall in the given direction for both cells (method called and parameter one)

        Args:
            cell (Cell): The cell to open the wall with
        """
        if self.top_cell is cell:
            self.top_wall = False
            cell.bottom_wall = False
        elif self.bottom_cell is cell:
            self.bottom_wall = False
            cell.top_wall = False
        elif self.left_cell is cell:
            self.left_wall = False
            cell.right_wall = False
        elif self.right_cell is cell:
            self.right_wall = False
            cell.left_wall = False

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

    def __str__(self):
        tmp = ""
        tmp += "1" if self.top_wall else "0"
        tmp += "1" if self.bottom_wall else "0"
        tmp += "1" if self.left_wall else "0"
        tmp += "1" if self.right_wall else "0"
        return f" {tmp} "


class Maze:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.cells = [[Cell() for _ in range(width)] for _ in range(height)]
        self.cells[0][0].is_start = True
        self.cells[-1][-1].is_end = True
        self.link_cells()

        self.is_built = False
        self.is_solved = False

    def __str__(self):
        s = ""
        for i in range(self.height):
            for j in range(self.width):
                s += str(self.cells[i][j])
            s += "\n"
        return s

    def link_cells(self) -> None:
        """Links all cells recursively"""
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
